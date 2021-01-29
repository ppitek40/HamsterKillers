
def Logger(logType, args):
    if logType == 0:
        print(' ID:' + str(args[0]) + ' | 0 | Wyslalem do wszystkich liste zlecen ' , flush=True)
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
              ' z procesem o ID: ' + str(args[3]) + ' | Przesylam posiadana liczbe zgod: ' + str(args[4]) +
              ' oraz swoja zgode', flush=True)
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
              ' | Liczba posiadanych zgód ' + str(args[2]) + ' | '+(args[3]), flush=True)
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
        print('ID:0 | ' + str(args[1]) + ' | Otrzymalem informacje ze zadanie ' + str(
            args[0]) + ' zostalo zrealizowane | Pozostalo zadan: ' + str(args[2]), flush=True)
    elif logType == 17:
        print('ID:' + str(args[0]) + ' | ' + str(args[1]) + ' | Nie potrzebuje juz agrafki, wiec ignoruje zezwolenie',
              flush=True)
    elif logType == 18:
        print('ID:' + str(args[0]) + ' | ' + str(args[1]) +
              ' | Pobieram ' + str(args[2]) + ' sztuk trucizny do zadania nr: ' + str(args[3]),
              flush=True)
    elif logType == 19:
        print('ID:' + str(args[0]) + ' | ' + str(args[1]) +
              ' | Rozpoczynam zabijanie ' + str(args[2]) + ' chomików',
              flush=True)
    elif logType == 20:
        print('ID:' + str(args[0]) + ' | ' + str(args[1]) + ' | Zrealizowalem zadanie  nr: ' + str(args[2]),
              flush=True)
    elif logType == 21:
        print('ID:' + str(args[0]) + ' | ' + str(args[1]) +
              ' | Odsyłam informację o końcu sesji w celu zsynchronizowania procesów',
              flush=True)
    elif logType == 22:
        print('ID:' + str(args[0]) + ' | ' + str(args[1]) +
              ' | Brak wolnych zadan', flush=True)
    elif logType == 23:
        print('ID:' + str(args[0]) + ' | ' + str(args[1]) +
              ' | Wszystkie zadania zostaly zakonczone | Synchronizacja procesow', flush=True)
    elif logType == 24:
        print('ID:' + str(args[0]) + ' | ' + str(args[1]) +
              ' | Wszystkie chomiki zostaly zabite | Koniec programu', flush=True)