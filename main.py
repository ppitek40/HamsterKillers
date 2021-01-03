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


def war():
    raise NotImplemented()


def askForSafetyPin():
    pass


def main():
    tags = enum('ZLECENIE_ZAPYTANIE', 'ZLECENIE_ZEZWOLENIE', 'ZLECENIA', 'AGRAFKA_ZAPYTANIE', 'AGRAFKA_ZEZWOLENIE',
                'ZEZWOLENIA_INNE', 'KONIEC')
    status = MPI.Status()
    numberOfSessions = 2
    session = 1
    comm = MPI.COMM_WORLD
    size = comm.Get_size()
    rank = comm.Get_rank()
    # port_mapping = [51289, 51290, 51291, 51292]
    # pydevd_pycharm.settrace('localhost', port=port_mapping[rank], stdoutToServer=True, stderrToServer=True)
    if rank == 0:

        tasks = generateTasks()
        print(tasks)
        sendToAll(comm, rank, size, tasks, tags.ZLECENIA)

        # wait4Answers

        data = {'a': 7, 'b': 3.14}
        comm.send(data, dest=1, tag=tags.ZLECENIE_ZAPYTANIE)
        comm.send(data, dest=2, tag=tags.ZLECENIE_ZEZWOLENIE)
        comm.send(data, dest=3, tag=tags.ZLECENIA)
        sendToAll(comm, rank, size, 0, tags.KONIEC)

        session += 1


    elif rank != 0:
        tasks = None
        currentTask = None
        LostTasks = []
        numberOfConsents = 0
        end = False
        while not end:

            data = comm.recv(source=MPI.ANY_SOURCE, tag=MPI.ANY_TAG, status=status)
            tag = status.Get_tag()
            if tag == tags.ZLECENIE_ZAPYTANIE:
                if currentTask == data:
                    war()
                if tasks[data][1]:
                    continue
                tasks[data][1] = True
                comm.send(data, dest=status.Get_source(), tag=tags.ZLECENIE_ZEZWOLENIE)


            elif tag == tags.ZLECENIE_ZEZWOLENIE:
                if data == currentTask:
                    numberOfConsents += 1
                    if numberOfConsents < size - 2:
                        continue
                    else:
                        tasks[currentTask][1] = True
                        sendToAll(comm, rank, size, 1, tags.AGRAFKA_ZAPYTANIE)
                else:
                    dest = [x[1] for x in LostTasks if x[0] == data]
                    comm.send([data, 1], dest=dest, tag=tags.ZEZWOLENIA_INNE)
            # SPRAWDZIC CZY NA PEWNO JEST GIT!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
            #TEST
            elif tag == tags.AGRAFKA_ZAPYTANIE:
                print(tag)
            elif tag == tags.AGRAFKA_ZEZWOLENIE:
                print(tag)
            elif tag == tags.ZEZWOLENIA_INNE:
                if data[0] == currentTask:
                    numberOfConsents += 1
                    if numberOfConsents < size - 2:
                        continue
                    else:
                        tasks[currentTask][1] = True
                        sendToAll(comm, rank, size, 1, tags.AGRAFKA_ZAPYTANIE)
                else:
                    dest = [x[1] for x in LostTasks if x[0] == data]
                    comm.send([data, 1], dest=dest, tag=tags.ZEZWOLENIA_INNE)
            # POPRAWIC!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!

            elif tag == tags.ZLECENIA:
                tasks = [[x, False] for x in data]
                task = chooseTask(tasks)
                if task < 0:
                    continue
                currentTask = task
                sendToAll(comm, rank, size, task, tags.ZLECENIE_ZAPYTANIE)

            elif tag == tags.KONIEC:
                end = True


if __name__ == '__main__':
    main()
