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
    ZLECENIE_ZAPYTANIE=1
    ZLECENIE_ZEZWOLENIE=2
    ZLECENIA=3
    AGRAFKA_ZAPYTANIE=4
    AGRAFKA_ZEZWOLENIE=5
    ZEZWOLENIA_INNE=6
    KONIEC=7


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
    #tags = Enum('ZLECENIE_ZAPYTANIE', 'ZLECENIE_ZEZWOLENIE', 'ZLECENIA', 'AGRAFKA_ZAPYTANIE', 'AGRAFKA_ZEZWOLENIE', 'ZEZWOLENIA_INNE', 'KONIEC')
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
        sendToAll(comm, rank, size, [tasks,0], tags.ZLECENIA.value)
        print('ID:'+str(rank)+' | 0 | Wyslalem do wszystkich liste zlecen', flush=True, )

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
            print('ID:' + str(rank) + ' | '+str(time)+
                  ' | Otrzymalem wiadomosc typu: '+ tag.name +' od procesu ID: '
                  +str(status.Get_source())+' | czas wysłania: '+str(data[-1]), flush=True, )

            time = max(time, data[-1]) + 1
            print('ID:' + str(rank) + ' | ' + str(time) +
                  ' | Aktualizacja czasu', flush=True, )

            if tag == tags.ZLECENIE_ZAPYTANIE:
                if currentTask == data[0]:
                    if war(timeOfTaskRequest, data[-1], rank, status.Get_source()):
                        print('ID:' + str(rank) + ' | ' + str(time) +
                              ' | Wygrałem wojnę o zadanie '+str(currentTask)+
                              ' z procesem o ID: '+str(status.Get_source()), flush=True, )
                        continue
                    print('ID:' + str(rank) + ' | ' + str(time) +
                          ' | Przegrałem wojnę o zadanie ' + str(currentTask) +
                          ' z procesem o ID: ' + str(status.Get_source()), flush=True, )
                    task = chooseTask(tasks)
                    if task < 0:
                        continue
                    currentTask = task
                    time += 1
                    timeOfTaskRequest = time
                    numberOfConsents=0
                    sendToAll(comm, rank, size, [task,time], tags.ZLECENIE_ZAPYTANIE.value)

                if tasks[data[0]][1]:
                    continue
                tasks[data[0]][1] = True
                time += 1
                comm.send([data[0], time], dest=status.Get_source(), tag=tags.ZLECENIE_ZEZWOLENIE.value)

            elif tag == tags.ZLECENIE_ZEZWOLENIE:
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
                        sendToAll(comm, rank, size, [1,time], tags.AGRAFKA_ZAPYTANIE.value)
                else:
                    dest = [x[1] for x in LostTasks if x[0] == data]
                    time += 1
                    comm.send([data[0], 1, time], dest=dest, tag=tags.ZEZWOLENIA_INNE.value)
            # SPRAWDZIC CZY NA PEWNO JEST GIT!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
            # TEST
            elif tag == tags.AGRAFKA_ZAPYTANIE:
                if wantSafetyPin:
                    if war(timeOfSafetyPinRequest, data[-1], rank, status.Get_source()):
                        safetyPinRequests.append(status.Get_source())
                    else:
                        time+=1
                        comm.send([1,time], dest=status.Get_source(), tag=tags.AGRAFKA_ZEZWOLENIE.value)
                else:
                    time += 1
                    comm.send([1,time], dest=status.Get_source(), tag=tags.AGRAFKA_ZEZWOLENIE.value)

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
                for x in safetyPinRequests:
                    comm.send([1,time], dest=x,tag=tags.AGRAFKA_ZEZWOLENIE.value)


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
                        sendToAll(comm, rank, size, [1,time], tags.AGRAFKA_ZAPYTANIE.value)
                else:
                    dest = [x[1] for x in LostTasks if x[0] == data]
                    time += 1
                    comm.send([data[0], 1, time], dest=dest, tag=tags.ZEZWOLENIA_INNE.value)
            # POPRAWIC!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!

            elif tag == tags.ZLECENIA:
                tasks = [[x, False] for x in data[0]]
                task = chooseTask(tasks)
                if task < 0:
                    continue
                currentTask = task
                time += 1
                timeOfTaskRequest = time
                numberOfConsents=0
                sendToAll(comm, rank, size, [task, time], tags.ZLECENIE_ZAPYTANIE.value)

            elif tag == tags.KONIEC:
                end = True


if __name__ == '__main__':
    main()
