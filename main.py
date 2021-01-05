import random

from enum import Enum
from mpi4py import MPI
import pydevd_pycharm


def enum(*sequential, **named):
    """Handy way to fake an enumerated type in Python
    http://stackoverflow.com/questions/36932/how-can-i-represent-an-enum-in-python
    """
    enums = dict(zip(sequential, range(len(sequential))), **named)
    return type('Enum', (), enums)


class tags(Enum):
    ZLECENIE_ZAPYTANIE = 1
    ZLECENIE_ZEZWOLENIE = 2
    ZLECENIA = 3
    AGRAFKA_ZAPYTANIE = 4
    AGRAFKA_ZEZWOLENIE = 5
    ZEZWOLENIA_INNE = 6
    KONIEC = 7


def Logger(logType, args):
    if logType == 0:
        print('ID:' + str(args[0]) + ' | 0 | Wysłałem do wszystkich liste zlecen', flush=True)
    elif logType == 1:
        print('ID:' + str(args[0]) + ' | ' + str(args[1]) +
              ' | Otrzymalem wiadomosc typu: ' + args[2] + ' od procesu ID: '
              + str(args[3]) + ' | czas wyslania: ' + str(args[4]), flush=True, )
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
              ' z procesem o ID: ' + str(args[3]) + ' | Przesylam posiadana liczbe zgod: ' + str(args[4]), flush=True, )
    elif logType == 5:
        print('ID:' + str(args[0]) + ' | ' + str(args[1]) +
              ' | Wybralem zadanie nr ' + str(args[2]) +
              ' i wysylam wiadomosc typu: ' + args[3] + ' do wszystkich procesow ', flush=True, )
    elif logType == 6:
        print('ID:' + str(args[0]) + ' | ' + str(args[1]) +
              ' | Ignoruje zapytanie, gdyz ktos już otrzymal moja zgode', flush=True, )
    elif logType == 7:
        print('ID:' + str(args[0]) + ' | ' + str(args[1]) +
              ' | Wysylam zgode na zadanie ' + str(args[2]) +
              ' procesowi o ID: ' + str(args[3]), flush=True, )
    elif logType == 8:
        print('ID:' + str(args[0]) + ' | ' + str(args[1]) +
              ' | Liczba posiadanych zgód ' + str(args[2]), flush=True, )
    elif logType == 9:
        print('ID:' + str(args[0]) + ' | ' + str(args[1]) +
              ' | Zdobyłem dostęp do zadania nr ' + str(args[2]) +
              ' | Ubiegam się o agrafkę ', flush=True, )
    elif logType == 10:
        print('ID:' + str(args[0]) + ' | ' + str(args[1]) +
              ' | Otrzymałem zezwolenie do zadania nr ' + str(args[2]) +
              ' | Przegrałem walke o nie, więc przesyłam zgode do procesu o ID' + str(args[3]), flush=True, )
    elif logType == 11:
        print('ID:' + str(args[0]) + ' | ' + str(args[1]) +
              ' | Wygralem walkę o agrafke z procesem o ID ' + str(args[2]) +
              ' | Zapisuje jego ID, aby wyrazic zgode po skorzystaniu z agrafki', flush=True, )
    elif logType == 12:
        print('ID:' + str(args[0]) + ' | ' + str(args[1]) +
              ' | Przegralem walkę o agrafke z procesem o ID ' + str(args[2]) +
              ' | Przesylam mu zgode', flush=True, )
    elif logType == 13:
        print('ID:' + str(args[0]) + ' | ' + str(args[1]) +
              ' | Przesylam zgode na agrafke do procesu o ID ' + str(args[2]), flush=True, )
    elif logType == 14:
        print('ID:' + str(args[0]) + ' | ' + str(args[1]) +
              ' | Zdobywam agrafke ', flush=True, )
    elif logType == 15:
        print('ID:' + str(args[0]) + ' | ' + str(args[1]) +
              ' | Przesylam zgode na agrafke do procesu o ID ' + str(args[2]), flush=True, )


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


def chooseTask(tasks):
    if False in list(zip(*tasks))[1]:
        number = random.randint(0, len(tasks) - 1)
        if tasks[number][1]:
            number = list(zip(*tasks))[1].index(False)
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
    # tags = Enum('ZLECENIE_ZAPYTANIE', 'ZLECENIE_ZEZWOLENIE', 'ZLECENIA', 'AGRAFKA_ZAPYTANIE', 'AGRAFKA_ZEZWOLENIE', 'ZEZWOLENIA_INNE', 'KONIEC')
    status = MPI.Status()
    numberOfSessions = 2
    session = 1
    numberOfSafetyPins = 2
    comm = MPI.COMM_WORLD
    size = comm.Get_size()
    rank = comm.Get_rank()
    # port_mapping = [51289, 51290, 51291, 51292]
    # pydevd_pycharm.settrace('localhost', port=port_mapping[rank], stdoutToServer=True, stderrToServer=True)
    if rank == 0:

        tasks = generateTasks()
        doneTasks = 0
        print(tasks)
        Logger(0, [rank])
        sendToAll(comm, rank, size, [tasks, 0], tags.ZLECENIA.value)

        # wait4Answers

        while doneTasks < len(tasks):
            data = comm.recv(source=MPI.ANY_SOURCE, tag=MPI.ANY_TAG, status=status)
            if status.Get_tag() == tags.KONIEC:
                doneTasks += 1

        sendToAll(comm, rank, size, 0, tags.KONIEC.value)

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
            tag = tags(status.Get_tag())
            Logger(1, [rank, time, tag.name, status.Get_source(), data[-1]])

            time = max(time, data[-1]) + 1
            Logger(2, [rank, time])

            if tag == tags.ZLECENIE_ZAPYTANIE:
                if currentTask == data[0]:
                    if war(timeOfTaskRequest, data[-1], rank, status.Get_source()):
                        Logger(3, [rank, time, currentTask, status.Get_source()])
                        continue
                    Logger(4, [rank, time, currentTask, status.Get_source(),numberOfConsents])
                    LostTasks.append([currentTask,status.Get_source()])
                    time += 1
                    comm.send([numberOfConsents, time], dest=status.Get_source(), tag=tags.ZEZWOLENIA_INNE.value)
                    task = chooseTask(tasks)
                    if task < 0:
                        continue
                    currentTask = task
                    time += 1
                    timeOfTaskRequest = time
                    numberOfConsents = 0
                    tasks[currentTask][1]=True
                    Logger(5, [rank, time, currentTask, tags.ZLECENIE_ZAPYTANIE.name])

                    sendToAll(comm, rank, size, [task, time], tags.ZLECENIE_ZAPYTANIE.value)
                    continue
                # CZY MOJE ZADANIE OD RAZU POWINNO BYC ZAZNACZONE JAKO ZAJETE??????????????????????????????????????
                if tasks[data[0]][1]:
                    Logger(6, [rank, time])
                    continue
                tasks[data[0]][1] = True
                time += 1
                Logger(7, [rank, time, data[0], status.Get_source()])
                comm.send([data[0], time], dest=status.Get_source(), tag=tags.ZLECENIE_ZEZWOLENIE.value)

            elif tag == tags.ZLECENIE_ZEZWOLENIE:
                if data[0] == currentTask:
                    numberOfConsents += 1
                    if numberOfConsents < size - 2:
                        Logger(8, [rank, time, numberOfConsents])
                        continue
                    else:
                        tasks[currentTask][1] = True
                        wantSafetyPin = True
                        numberOfConsents = 0
                        time += 1
                        timeOfSafetyPinRequest = time
                        Logger(9, [rank, time, currentTask])
                        sendToAll(comm, rank, size, [1, time], tags.AGRAFKA_ZAPYTANIE.value)
                else:
                    dest = [x[1] for x in LostTasks if x[0] == data[0]]
                    time += 1
                    Logger(10, [rank, time, data[0], dest])
                    comm.send([data[0], 1, time], dest=dest, tag=tags.ZEZWOLENIA_INNE.value)
            # SPRAWDZIC CZY NA PEWNO JEST GIT!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
            # TEST
            elif tag == tags.AGRAFKA_ZAPYTANIE:
                if wantSafetyPin:
                    if war(timeOfSafetyPinRequest, data[-1], rank, status.Get_source()):
                        Logger(11, [rank, time, status.Get_source()])
                        safetyPinRequests.append(status.Get_source())
                    else:
                        time += 1
                        Logger(12, [rank, time, status.Get_source()])
                        comm.send([1, time], dest=status.Get_source(), tag=tags.AGRAFKA_ZEZWOLENIE.value)
                else:
                    time += 1
                    Logger(13, [rank, time, status.Get_source()])
                    comm.send([1, time], dest=status.Get_source(), tag=tags.AGRAFKA_ZEZWOLENIE.value)

            elif tag == tags.AGRAFKA_ZEZWOLENIE:
                if not wantSafetyPin:
                    continue
                numberOfConsents += 1
                if numberOfConsents < (size - 1) - numberOfSafetyPins:
                    Logger(8, [rank, time, numberOfConsents])
                    continue
                time += 1
                numberOfConsents = 0
                Logger(14, [rank, time])
                takePoisonAndKillHamsters()
                time += 1
                comm.send([currentTask, time], dest=0, tag=tags.KONIEC.value)
                time += 1

                for x in safetyPinRequests:
                    Logger(13, [rank, time, x])
                    comm.send([1, time], dest=x, tag=tags.AGRAFKA_ZEZWOLENIE.value)
                task = chooseTask(tasks)
                if task < 0:
                    continue
                currentTask = task
                time += 1
                timeOfTaskRequest = time
                numberOfConsents = 0
                tasks[currentTask][1] = True
                Logger(5, [rank, time, currentTask, tags.ZLECENIE_ZAPYTANIE.name])
                sendToAll(comm, rank, size, [task, time], tags.ZLECENIE_ZAPYTANIE.value)

            elif tag == tags.ZEZWOLENIA_INNE:
                if data[0] == currentTask:
                    numberOfConsents += 1
                    if numberOfConsents < size - 2:
                        Logger(8, [rank, time, numberOfConsents])
                        continue
                    else:
                        tasks[currentTask][1] = True
                        wantSafetyPin = True
                        numberOfConsents = 0
                        time += 1
                        timeOfSafetyPinRequest = time
                        Logger(9, [rank, time, currentTask])
                        sendToAll(comm, rank, size, [1, time], tags.AGRAFKA_ZAPYTANIE.value)
                else:
                    dest = [x[1] for x in LostTasks if x[0] == data[0]]
                    time += 1
                    Logger(10, [rank, time, data[0], dest])
                    comm.send([data[0], 1, time], dest=dest, tag=tags.ZEZWOLENIA_INNE.value)
            # POPRAWIC!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!

            elif tag == tags.ZLECENIA:
                tasks = data[0]
                task = chooseTask(tasks)
                if task < 0:
                    continue
                currentTask = task
                time += 1
                timeOfTaskRequest = time
                numberOfConsents = 0
                tasks[currentTask][1] = True
                Logger(5, [rank, time, currentTask, tags.ZLECENIE_ZAPYTANIE.name])

                sendToAll(comm, rank, size, [task, time], tags.ZLECENIE_ZAPYTANIE.value)

            elif tag == tags.KONIEC:
                end = True


if __name__ == '__main__':
    main()
