import codecs
import random
import sys

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


def Logger(logType, args):
    if logType == 0:
        print('ID:' + str(args[0]) + ' | 0 | Wyslalem do wszystkich liste zlecen', flush=True)
    elif logType == 1:
        print('ID:' + str(args[0]) + ' | ' + str(args[1]) +
              ' | Otrzymalem wiadomosc typu: ' + args[2] + ' od procesu ID: '
              + str(args[3]) + ' | czas wyslania: ' + str(args[4]), flush=True)
    elif logType == 2:
        print('ID:' + str(args[0]) + ' | ' + str(args[1]) +
              ' | Aktualizacja czasu', flush=True, )
    elif logType == 3:
        print('ID:' + str(args[0]) + ' | ' + str(args[1]) +
              ' | Wygrałem wojnę o zadanie ' + str(args[2]) +
              ' z procesem o ID: ' + str(args[3]), flush=True, )
    elif logType == 4:
        print('ID:' + str(args[0]) + ' | ' + str(args[1]) +
              ' | Przegrałem wojnę o zadanie ' + str(args[2]) +
              ' z procesem o ID: ' + str(args[3]) + ' | Przesylam posiadana liczbe zgod: ' + str(args[4]), flush=True)
    elif logType == 5:
        print('ID:' + str(args[0]) + ' | ' + str(args[1]) +
              ' | Wybralem zadanie nr ' + str(args[2]) +
              ' i wysylam wiadomosc typu: ' + args[3] + ' do wszystkich procesow ', flush=True)
    elif logType == 6:
        print('ID:' + str(args[0]) + ' | ' + str(args[1]) +
              ' | Ignoruje zapytanie, gdyz ktos już otrzymal moja zgode', flush=True)
    elif logType == 7:
        print('ID:' + str(args[0]) + ' | ' + str(args[1]) +
              ' | Wysylam zgode na zadanie ' + str(args[2]) +
              ' procesowi o ID: ' + str(args[3]), flush=True)
    elif logType == 8:
        print('ID:' + str(args[0]) + ' | ' + str(args[1]) +
              ' | Liczba posiadanych zgód ' + str(args[2]), flush=True)
    elif logType == 9:
        print('ID:' + str(args[0]) + ' | ' + str(args[1]) +
              ' | Zdobyłem dostęp do zadania nr ' + str(args[2]) +
              ' | Ubiegam się o agrafkę ', flush=True)
    elif logType == 10:
        print('ID:' + str(args[0]) + ' | ' + str(args[1]) +
              ' | Otrzymałem zezwolenie do zadania nr ' + str(args[2]) +
              ' | Przegrałem walke o nie, więc przesyłam zgode do procesu o ID' + str(args[3]), flush=True)
    elif logType == 11:
        print('ID:' + str(args[0]) + ' | ' + str(args[1]) +
              ' | Wygralem walkę o agrafke z procesem o ID ' + str(args[2]) +
              ' | Zapisuje jego ID, aby wyrazic zgode po skorzystaniu z agrafki', flush=True)
    elif logType == 12:
        print('ID:' + str(args[0]) + ' | ' + str(args[1]) +
              ' | Przegralem walkę o agrafke z procesem o ID ' + str(args[2]) +
              ' | Przesylam mu zgode', flush=True)
    elif logType == 13:
        print('ID:' + str(args[0]) + ' | ' + str(args[1]) +
              ' | Przesylam zgode na agrafke do procesu o ID ' + str(args[2]), flush=True)
    elif logType == 14:
        print('ID:' + str(args[0]) + ' | ' + str(args[1]) +
              ' | Zdobywam agrafke ', flush=True)
    elif logType == 15:
        print('ID:' + str(args[0]) + ' | ' + str(args[1]) +
              ' | Przesylam zgode na agrafke do procesu o ID ' + str(args[2]), flush=True)
    elif logType == 16:
        print('ID:0 | 0 | Otrzymalem informacje ze zadanie ' + str(
            args[0]) + ' zostalo zrealizowane | Pozostalo zadan: ' + str(args[1]), flush=True)
    elif logType == 17:
        print('ID:' + str(args[0]) + ' | ' + str(args[1]) + ' | Nie potrzebuje juz agrafki, wiec ignoruje zezwolenie',
              flush=True)
    elif logType == 18:
        print('ID:' + str(args[0]) + ' | ' + str(args[1]) +
              ' | Pobieram ' + str(args[2]) + ' sztuk trucizny do zadania nr: '+ str(args[3]),
              flush=True)
    elif logType == 19:
        print('ID:' + str(args[0]) + ' | ' + str(args[1]) +
              ' | Rozpoczynam zabijanie ' + str(args[2]) + ' chomików',
              flush=True)
    elif logType == 20:
        print('ID:' + str(args[0]) + ' | ' + str(args[1]) + ' | Zrealizowalem zadanie  nr: '+ str(args[2]),
              flush=True)


def generateTasks():
    tasks = []
    numberOfTasks = random.randint(10, 30)
    for i in range(numberOfTasks):
        tasks.append([random.randint(1, 10), False])
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

    return -1, time, 0


def war(myTime, oponnentTime, myID, oponnentID):
    if myTime != oponnentTime:
        return True if myTime > oponnentTime else False
    return True if myID < oponnentID else False


def askForSafetyPin(comm, time):
    time += 1
    sendToAll(comm, comm.Get_rank(), comm.Get_size(), [1, time], Tags.AGRAFKA_ZAPYTANIE.value)
    return time, 0


def takePoisonAndKillHamsters(time, currentTask, hamstersToKill, comm):
    time += 1
    Logger(18, [comm.Get_rank(), time, hamstersToKill, currentTask])
    Logger(19, [comm.Get_rank(), time, hamstersToKill])
    Logger(20, [comm.Get_rank(), time, currentTask])
    comm.send([currentTask, time], dest=0, tag=Tags.KONIEC.value)
    return time


def taskWarLost(comm, LostTasks, currentTask, numberOfConsents, source, time):
    Logger(4, [comm.Get_rank(), time, currentTask, source, numberOfConsents])
    LostTasks.append([currentTask, source])
    print(LostTasks, flush=True)
    time += 1
    comm.send([currentTask, numberOfConsents + 1, time], dest=source, tag=Tags.ZEZWOLENIA_INNE.value)
    return LostTasks, time


def main():
    status = MPI.Status()
    sys.stdout.reconfigure(encoding='utf-8')
    numberOfSessions = 2
    session = 1
    numberOfSafetyPins = 2
    comm = MPI.COMM_WORLD
    size = comm.Get_size()
    rank = comm.Get_rank()
    # port_mapping = [59607, 59609, 59612, 59614]
    # pydevd_pycharm.settrace('localhost', port=port_mapping[rank], stdoutToServer=True, stderrToServer=True)
    if rank == 0:

        tasks = generateTasks()
        doneTasks = 0
        print(tasks)
        Logger(0, [rank])
        sendToAll(comm, rank, size, [tasks, 0], Tags.ZLECENIA.value)

        # wait4Answers

        while doneTasks < len(tasks):
            data = comm.recv(source=MPI.ANY_SOURCE, tag=MPI.ANY_TAG, status=status)
            tag = Tags(status.Get_tag())
            if tag == Tags.KONIEC:
                doneTasks += 1
                Logger(16, [data[0], len(tasks) - doneTasks])

        sendToAll(comm, rank, size, [0,0], Tags.KONIEC.value)

        session += 1
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

            data = comm.recv(source=MPI.ANY_SOURCE, tag=MPI.ANY_TAG, status=status)
            tag = Tags(status.Get_tag())
            Logger(1, [rank, time, tag.name, status.Get_source(), data[-1]])

            time = max(time, data[-1]) + 1
            Logger(2, [rank, time])

            if tag == Tags.ZLECENIE_ZAPYTANIE:
                if currentTask == data[0]:
                    if war(timeOfTaskRequest, data[-1], rank, status.Get_source()):
                        Logger(3, [rank, time, currentTask, status.Get_source()])
                        continue
                    LostTasks, time = taskWarLost(comm, LostTasks, currentTask, numberOfConsents, status.Get_source(),
                                                  time)

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
                        Logger(8, [rank, time, numberOfConsents])
                        continue
                    else:
                        wantSafetyPin = True
                        Logger(9, [comm.Get_rank(), time, currentTask])
                        time, numberOfConsents = askForSafetyPin(comm, time)
                        timeOfSafetyPinRequest = time

                else:
                    dest = [x[1] for x in LostTasks if x[0] == data[0]]
                    dest = dest[0]
                    print('ID:' + str(rank) + ' | ' + str(dest), flush=True)
                    time += 1
                    Logger(10, [rank, time, data[0], dest])
                    comm.send([data[0], 1, time], dest=dest, tag=Tags.ZEZWOLENIA_INNE.value)
            # SPRAWDZIC CZY NA PEWNO JEST GIT!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
            # TEST
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
                    Logger(8, [rank, time, numberOfConsents])
                    continue
                Logger(14, [rank, time])
                wantSafetyPin = False
                time = takePoisonAndKillHamsters(time, currentTask, tasks[currentTask], comm)

                time += 1

                for x in safetyPinRequests:
                    Logger(13, [rank, time, x])
                    comm.send([1, time], dest=x, tag=Tags.AGRAFKA_ZEZWOLENIE.value)

                currentTask, time, numberOfConsents = chooseTask(tasks, time, comm)
                if currentTask < 0:
                    continue
                timeOfTaskRequest = time
                tasks[currentTask][1] = True
                continue

            elif tag == Tags.ZEZWOLENIA_INNE:
                if data[0] == currentTask:
                    numberOfConsents += data[1]
                    if numberOfConsents < size - 2:
                        Logger(8, [rank, time, numberOfConsents])
                        continue
                    else:
                        wantSafetyPin = True
                        Logger(9, [rank, time, currentTask])
                        time, numberOfConsents = askForSafetyPin(comm, time)
                        timeOfSafetyPinRequest = time
                else:
                    dest = [x[1] for x in LostTasks if x[0] == data[0]]
                    dest = dest[0]
                    time += 1
                    Logger(10, [rank, time, data[0], dest])
                    comm.send([data[0], data[1], time], dest=dest, tag=Tags.ZEZWOLENIA_INNE.value)
            # POPRAWIC!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!

            elif tag == Tags.ZLECENIA:
                tasks = data[0]
                currentTask, time, numberOfConsents = chooseTask(tasks, time, comm)
                if currentTask < 0:
                    continue
                timeOfTaskRequest = time
                tasks[currentTask][1] = True
                continue

            elif tag == Tags.KONIEC:
                end = True


if __name__ == '__main__':
    main()
