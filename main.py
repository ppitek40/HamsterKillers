import random

from mpi4py import MPI
import pydevd_pycharm


def enum(*sequential, **named):
    """Handy way to fake an enumerated type in Python
    http://stackoverflow.com/questions/36932/how-can-i-represent-an-enum-in-python
    """
    enums = dict(zip(sequential, range(len(sequential))), **named)
    return type('Enum', (), enums)


def generateTasks():
    tasks = []
    numberOfTasks = random.randint(10, 30)
    for i in range(numberOfTasks):
        tasks.append(random.randint(1, 10))
    return tasks


def sendToAll(comm, rank, size, data, tag):
    for i in range(size):
        if i == rank:
            continue
        comm.send(data, dest=i, tag=tag)


def chooseTask(tasks):
    if False in list(zip(*tasks))[1]:
        number = random.randint(0, len(tasks) - 1)
        if tasks[number][1]:
            number = tasks.index(False)
        return number
    return -1


def war(myTime, oponnentTime, myID, oponnentID):
    if myTime != oponnentTime:
        return True if myTime > oponnentTime else False
    return True if myID < oponnentID else False


def askForSafetyPin():
    pass


def takePoisonAndKillHamsters():
    pass


def main():
    tags = enum('ZLECENIE_ZAPYTANIE', 'ZLECENIE_ZEZWOLENIE', 'ZLECENIA', 'AGRAFKA_ZAPYTANIE', 'AGRAFKA_ZEZWOLENIE',
                'ZEZWOLENIA_INNE', 'KONIEC')
    status = MPI.Status()
    numberOfSessions = 2
    session = 1
    numberOfSafetyPins = 5
    comm = MPI.COMM_WORLD
    size = comm.Get_size()
    rank = comm.Get_rank()
    # port_mapping = [51289, 51290, 51291, 51292]
    # pydevd_pycharm.settrace('localhost', port=port_mapping[rank], stdoutToServer=True, stderrToServer=True)
    if rank == 0:

        tasks = generateTasks()
        doneTasks = 0
        print(tasks)
        sendToAll(comm, rank, size, tasks, tags.ZLECENIA)

        # wait4Answers

        while doneTasks < len(tasks):
            data = comm.recv(dest=MPI.ANY_SOURCE, tag=MPI.ANY_TAG, status=status)
            if status.Get_tag() == tags.KONIEC:
                doneTasks += 1

        sendToAll(comm, rank, size, 0, tags.KONIEC)

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
        SafetyPinRequests = []
        end = False

        while not end:

            data = comm.recv(source=MPI.ANY_SOURCE, tag=MPI.ANY_TAG, status=status)
            time = max(time, data[-1]) + 1
            tag = status.Get_tag()

            if tag == tags.ZLECENIE_ZAPYTANIE:
                if currentTask == data:
                    if war(timeOfTaskRequest, data[-1], rank, status.Get_source()):
                        continue
                    task = chooseTask(tasks)
                    if task < 0:
                        continue
                    currentTask = task
                    time += 1
                    timeOfTaskRequest = time
                    numberOfConsents=0
                    sendToAll(comm, rank, size, task, tags.ZLECENIE_ZAPYTANIE)

                if tasks[data][1]:
                    continue
                tasks[data][1] = True
                time += 1
                comm.send([data, time], dest=status.Get_source(), tag=tags.ZLECENIE_ZEZWOLENIE)

            elif tag == tags.ZLECENIE_ZEZWOLENIE:
                if data == currentTask:
                    numberOfConsents += 1
                    if numberOfConsents < size - 2:
                        continue
                    else:
                        tasks[currentTask][1] = True
                        wantSafetyPin = True
                        numberOfConsents = 0
                        time += 1
                        timeOfSafetyPinRequest = time
                        sendToAll(comm, rank, size, 1, tags.AGRAFKA_ZAPYTANIE)
                else:
                    dest = [x[1] for x in LostTasks if x[0] == data]
                    time += 1
                    comm.send([data, 1, time], dest=dest, tag=tags.ZEZWOLENIA_INNE)
            # SPRAWDZIC CZY NA PEWNO JEST GIT!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
            # TEST
            elif tag == tags.AGRAFKA_ZAPYTANIE:
                if wantSafetyPin:
                    if war(timeOfSafetyPinRequest, data[-1], rank, status.Get_source()):
                        SafetyPinRequests.append(status.Get_source())
                    else:
                        time+=1
                        comm.send([1,time], dest=status.Get_source(), tag=tags.AGRAFKA_ZEZWOLENIE)
                else:
                    time += 1
                    comm.send([1,time], dest=status.Get_source(), tag=tags.AGRAFKA_ZEZWOLENIE)

            elif tag == tags.AGRAFKA_ZEZWOLENIE:
                if not wantSafetyPin:
                    continue
                numberOfConsents += 1
                if numberOfConsents < (size - 1) - numberOfSafetyPins:
                    continue
                time += 1
                numberOfConsents = 0
                takePoisonAndKillHamsters()
                time+=1
                for x in SafetyPinRequests:
                    comm.send([1,time], dest=x,tag=tags.AGRAFKA_ZEZWOLENIE)


            elif tag == tags.ZEZWOLENIA_INNE:
                if data[0] == currentTask:
                    numberOfConsents += 1
                    if numberOfConsents < size - 2:
                        continue
                    else:
                        tasks[currentTask][1] = True
                        wantSafetyPin = True
                        numberOfConsents = 0
                        time += 1
                        timeOfSafetyPinRequest = time
                        sendToAll(comm, rank, size, [1,time], tags.AGRAFKA_ZAPYTANIE)
                else:
                    dest = [x[1] for x in LostTasks if x[0] == data]
                    time += 1
                    comm.send([data, 1, time], dest=dest, tag=tags.ZEZWOLENIA_INNE)
            # POPRAWIC!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!

            elif tag == tags.ZLECENIA:
                tasks = [[x, False] for x in data]
                task = chooseTask(tasks)
                if task < 0:
                    continue
                currentTask = task
                time += 1
                timeOfTaskRequest = time
                numberOfConsents=0
                sendToAll(comm, rank, size, [task, time], tags.ZLECENIE_ZAPYTANIE)

            elif tag == tags.KONIEC:
                end = True


if __name__ == '__main__':
    main()
