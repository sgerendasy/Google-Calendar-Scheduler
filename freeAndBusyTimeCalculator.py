'''
Author: Sam Gerendasy
This module returns a list of free and busy time blocks
from a given list of calendar entries, between a given
start and end date, and furthermore, between a given
start and end time.
'''


def freeBusyTimes(eSet, startingBounds, endingBounds):
    print("In Free Busy Times")
    print("eSet", eSet)
    print("startingBounds: ", startingBounds)
    print("endingBounds: ", endingBounds)
    freeBusyList = []
    i = 0
    for startDay, endDay in zip(startingBounds, endingBounds):
        busy = False
        today = True
        startOfDayHandled = False
        print("In start: ", startDay, "  end: ", endDay)
        while(today):
            if(i < len(eSet)-1):
                print("eSet[{}].date():".format(i), eSet[i].date(), "  startDay.date(): ", startDay.date())
                if eSet[i].date() == startDay.date():
                    if eSet[i].format("HHmm") <= startDay.format("HHmm"):
                        print("AH: 1")
                        eSet[i] = eSet[i].replace(hour=startDay.hour)
                        eSet[i] = eSet[i].replace(minute=startDay.minute)
                        busy = True
                        startOfDayHandled = True
                    elif eSet[i] > startDay and not startOfDayHandled:
                        print("AH: 2")
                        freeBusyList.append(["free: ", startDay, eSet[i]])
                        busy = True
                        startOfDayHandled = True
                    if busy:
                        print("AH: 3")
                        if(eSet[i+1] >= endDay):
                            print("AH: 4")
                            freeBusyList.append(["busy: ", eSet[i], endDay])
                            i += 1
                            today = False
                        else:
                            print("AH: 5")
                            freeBusyList.append(["busy: ", eSet[i], eSet[i+1]])
                        busy = False
                    elif not busy:
                        print("AH: 6")
                        if eSet[i].format("YYYYMMDDHHmm") == endDay.format("YYYYMMDDHHmm"):
                            print("AH: 7")
                            today = False
                        elif(eSet[i+1] >= endDay):
                            print("AH: 8")
                            freeBusyList.append(["free: ", eSet[i], endDay])
                            today = False
                        else:
                            print("AH: 9")
                            freeBusyList.append(["free: ", eSet[i], eSet[i+1]])
                        busy = True
                    i += 1
                else:
                    print("AH: 10")
                    freeBusyList.append(["free: ", startDay, endDay])
                    today = False
            elif i != len(eSet):
                print("AH: 11")
                if eSet[i].date() != startDay.date():
                    print("AH: 12")
                    freeBusyList.append(["free: ", startDay, endDay])
                else:
                    print("AH: 13")
                    freeBusyList.append(["free: ", eSet[i], endDay])
                today = False
            else:
                print("AH: 14")
                freeBusyList.append(["free: ", startDay, endDay])
                today = False
    return freeBusyList
