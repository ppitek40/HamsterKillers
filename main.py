import random
import sys
from time import sleep

from Logger import Logger

from enum import Enum
from mpi4py import MPI


import pydevd_pycharm


class Tags(Enum):
    ZLECENIE_ZAPYTANIE = 1
    ZLECENIE_ZEZWOLENIE = 2
    ZLECENIA = 3
    AGRAFKA_ZAPYTANIE = 4
    AGRAFKA_ZEZWOLENIE = 5
    ZEZWOLENIA_INNE = 6
    KONIEC = 7
    KONIEC_SESJI = 8


def generateTasks(minTasks, maxTasks, minHamsters, maxHamsters):
    tasks = []
    numberOfTasks = random.randint(minTasks, maxTasks)
    for i in range(numberOfTasks):
        tasks.append([random.randint(minHamsters, maxHamsters), False])
    return tasks


def sendToAll(comm, rank, size, data, tag):
    for i in range(size):
        if i == rank:
            continue
        comm.send(data, dest=i, tag=tag)


def chooseTask(tasks, time, comm):
    if False in list(zip(*tasks))[1]:
        number = random.randint(0, len(tasks) - 1)
        if tasks[number][1]:
            number = list(zip(*tasks))[1].index(False)
        time += 1
        Logger(5, [comm.Get_rank(), time, number, Tags.ZLECENIE_ZAPYTANIE.name])
        sendToAll(comm, comm.Get_rank(), comm.Get_size(), [number, time], Tags.ZLECENIE_ZAPYTANIE.value)

        return number, time, 0

    Logger(22, [comm.Get_rank(), time])
    return -1, time, 0


def war(myTime, oponnentTime, myID, oponnentID):
    if myTime != oponnentTime:
        return True if myTime < oponnentTime else False
    return True if myID < oponnentID else False


def askForSafetyPin(comm, time):
    time += 1
    sendToAll(comm, comm.Get_rank(), comm.Get_size(), [1, time], Tags.AGRAFKA_ZAPYTANIE.value)
    return time, time, 0


def takePoisonAndKillHamsters(time, currentTask, hamstersToKill, comm):
    time += 1
    Logger(18, [comm.Get_rank(), time, hamstersToKill[0], currentTask])
    Logger(19, [comm.Get_rank(), time, hamstersToKill[0]])
    Logger(20, [comm.Get_rank(), time, currentTask])
    sleep(1)
    comm.send([currentTask, time], dest=0, tag=Tags.KONIEC.value)
    return time


def taskWarLost(comm, LostTasks, currentTask, numberOfConsents, source, time):
    Logger(4, [comm.Get_rank(), time, currentTask, source, numberOfConsents])
    LostTasks.append([currentTask, source])
    time += 1
    comm.send([currentTask, numberOfConsents + 1, time], dest=source, tag=Tags.ZEZWOLENIA_INNE.value)
    return LostTasks, time


def getArgs(argv):
    param = [2, 5, 5, 20, 1, 15]
    for i, x in enumerate(argv):
        param[i] = int(x)
    return param[0], param[1], param[2], param[3], param[4], param[5]


def getDestinationOfConsent(LostTasks, task):
    dest = [LostTask[1] for LostTask in LostTasks if LostTask[0] == task]
    dest = dest[0]
    return dest


def main():
    if len(sys.argv) > 7:
        raise Exception("Too many arguments!")

    numberOfSessions, numberOfSafetyPins, minTasks, maxTasks, minHamsters, maxHamsters, = getArgs(sys.argv[1:])
    session = 0
    status = MPI.Status()
    comm = MPI.COMM_WORLD
    size = comm.Get_size()
    rank = comm.Get_rank()
    port_mapping = [53662, 53664, 53665, 53666]
    pydevd_pycharm.settrace('localhost', port=port_mapping[rank], stdoutToServer=True, stderrToServer=True)
    if rank == 0:
        time = 0
        while session < numberOfSessions:

            doneTasks = 0
            tasks = generateTasks(minTasks, maxTasks, minHamsters, maxHamsters)
            print(tasks)
            Logger(0, [rank])
            sendToAll(comm, rank, size, [tasks, time], Tags.ZLECENIA.value)

            while doneTasks < len(tasks):
                data = comm.recv(source=MPI.ANY_SOURCE, tag=MPI.ANY_TAG, status=status)
                time = max(time, data[-1]) + 1
                tag = Tags(status.Get_tag())
                if tag == Tags.KONIEC:
                    doneTasks += 1
                    tasks[data[0]][1] = True
                    Logger(16, [data[0], time, len(tasks) - doneTasks])

            sendToAll(comm, rank, size, [0, time], Tags.KONIEC_SESJI.value)
            Logger(23, [rank, time])
            readyProcesses = 0
            while readyProcesses < size - 1:
                data = comm.recv(source=MPI.ANY_SOURCE, tag=MPI.ANY_TAG, status=status)
                time = max(time, data[-1]) + 1
                tag = Tags(status.Get_tag())
                if tag == Tags.KONIEC_SESJI:
                    readyProcesses += 1

            session += 1
        Logger(24, [rank, time])
        sendToAll(comm, rank, size, [0, time], Tags.KONIEC.value)

    else:
        tasks = None
        currentTask = None
        LostTasks = []
        time = 0
        timeOfTaskRequest = 0
        timeOfSafetyPinRequest = 0
        numberOfConsents = 0
        wantSafetyPin = False
        safetyPinRequests = []
        end = False

        while not end:

            if tasks is None:
                data = comm.recv(source=0, tag=MPI.ANY_TAG, status=status)
            else:
                data = comm.recv(source=MPI.ANY_SOURCE, tag=MPI.ANY_TAG, status=status)
            tag = Tags(status.Get_tag())
            time = max(time, data[-1]) + 1
            Logger(1, [rank, time, tag.name, status.Get_source(), data[-1]])

            if tag == Tags.ZLECENIE_ZAPYTANIE:
                if currentTask == data[0]:
                    if war(timeOfTaskRequest, data[-1], rank, status.Get_source()):
                        Logger(3, [rank, time, currentTask, status.Get_source()])
                        continue
                    else:
                        LostTasks, time = taskWarLost(comm, LostTasks, currentTask, numberOfConsents,
                                                      status.Get_source(), time)
                        currentTask, time, numberOfConsents = chooseTask(tasks, time, comm)
                        if currentTask < 0:
                            continue
                        timeOfTaskRequest = time
                        tasks[currentTask][1] = True
                        continue

                if tasks[data[0]][1]:
                    Logger(6, [rank, time])
                    continue
                tasks[data[0]][1] = True
                time += 1
                Logger(7, [rank, time, data[0], status.Get_source()])
                comm.send([data[0], time], dest=status.Get_source(), tag=Tags.ZLECENIE_ZEZWOLENIE.value)

            elif tag == Tags.ZLECENIE_ZEZWOLENIE:
                if data[0] == currentTask:
                    numberOfConsents += 1
                    if numberOfConsents < size - 2:
                        Logger(8, [rank, time, numberOfConsents, tag.name])
                        continue
                    else:
                        wantSafetyPin = True
                        Logger(9, [rank, time, currentTask])
                        time, timeOfSafetyPinRequest, numberOfConsents = askForSafetyPin(comm, time)

                else:
                    dest = getDestinationOfConsent(LostTasks, data[0])
                    time += 1
                    Logger(10, [rank, time, data[0], dest])
                    comm.send([data[0], 1, time], dest=dest, tag=Tags.ZEZWOLENIA_INNE.value)

            elif tag == Tags.AGRAFKA_ZAPYTANIE:
                if wantSafetyPin:
                    if war(timeOfSafetyPinRequest, data[-1], rank, status.Get_source()):
                        Logger(11, [rank, time, status.Get_source()])
                        safetyPinRequests.append(status.Get_source())
                    else:
                        time += 1
                        Logger(12, [rank, time, status.Get_source()])
                        comm.send([1, time], dest=status.Get_source(), tag=Tags.AGRAFKA_ZEZWOLENIE.value)
                else:
                    time += 1
                    Logger(13, [rank, time, status.Get_source()])
                    comm.send([1, time], dest=status.Get_source(), tag=Tags.AGRAFKA_ZEZWOLENIE.value)

            elif tag == Tags.AGRAFKA_ZEZWOLENIE:
                if not wantSafetyPin:
                    Logger(17, [rank, time])
                    continue
                numberOfConsents += 1
                if numberOfConsents < (size - 1) - numberOfSafetyPins:
                    Logger(8, [rank, time, numberOfConsents, tag.name])
                    continue
                Logger(14, [rank, time])
                wantSafetyPin = False
                time = takePoisonAndKillHamsters(time, currentTask, tasks[currentTask], comm)

                if len(safetyPinRequests) != 0:
                    time += 1
                    for x in safetyPinRequests:
                        Logger(13, [rank, time, x])
                        comm.send([1, time], dest=x, tag=Tags.AGRAFKA_ZEZWOLENIE.value)
                    safetyPinRequests.clear()

                currentTask, time, numberOfConsents = chooseTask(tasks, time, comm)
                if currentTask < 0:
                    continue
                timeOfTaskRequest = time
                tasks[currentTask][1] = True

            elif tag == Tags.ZEZWOLENIA_INNE:
                if data[0] == currentTask:
                    numberOfConsents += data[1]
                    if numberOfConsents < size - 2:
                        Logger(8, [rank, time, numberOfConsents, tag.name])
                        continue
                    else:
                        wantSafetyPin = True
                        Logger(9, [rank, time, currentTask])
                        time, timeOfSafetyPinRequest, numberOfConsents = askForSafetyPin(comm, time)
                else:
                    dest = getDestinationOfConsent(LostTasks, data[0])
                    time += 1
                    Logger(10, [rank, time, data[0], dest])
                    comm.send([data[0], data[1], time], dest=dest, tag=Tags.ZEZWOLENIA_INNE.value)

            elif tag == Tags.ZLECENIA:
                tasks = data[0]
                currentTask, time, numberOfConsents = chooseTask(tasks, time, comm)
                if currentTask < 0:
                    continue
                timeOfTaskRequest = time
                tasks[currentTask][1] = True

            elif tag == Tags.KONIEC_SESJI:
                tasks = None
                currentTask = None
                LostTasks = []
                timeOfTaskRequest = 0
                timeOfSafetyPinRequest = 0
                numberOfConsents = 0
                wantSafetyPin = False
                Logger(21, [rank, time])
                comm.send([0, time], dest=0, tag=Tags.KONIEC_SESJI.value)

            elif tag == Tags.KONIEC:
                end = True


if __name__ == '__main__':
    main()
