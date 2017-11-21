'''
Author: Sam Gerendasy
This module returns a list of free and busy time blocks
from a given list of calendar entries, between a given
start and end date, and furthermore, between a given
start and end time.
'''


def freeBusyTimes(eSet, startingBounds, endingBounds):
    if(len(eSet) == 0):
        return []
    freeBusyList = []
    i = 0
    for startDay, endDay in zip(startingBounds, endingBounds):
        busy = False
        today = True
        startOfDayHandled = False
        while(today):
            if(i < len(eSet)-1):
                if eSet[i].date() == startDay.date():
                    if eSet[i].format("HHmm") <= startDay.format("HHmm"):
                        eSet[i] = eSet[i].replace(hour=startDay.hour)
                        eSet[i] = eSet[i].replace(minute=startDay.minute)
                        busy = True
                        startOfDayHandled = True
                    elif eSet[i] > startDay and not startOfDayHandled:
                        freeBusyList.append(["free ", startDay, eSet[i]])
                        busy = True
                        startOfDayHandled = True
                    if busy:
                        if(eSet[i+1] >= endDay):
                            freeBusyList.append(["busy ", eSet[i], endDay])
                            i += 1
                            today = False
                        else:
                            freeBusyList.append(["busy ", eSet[i], eSet[i+1]])
                        busy = False
                    elif not busy:
                        if eSet[i].format("YYYYMMDDHHmm") == endDay.format("YYYYMMDDHHmm"):
                            today = False
                        elif(eSet[i+1] >= endDay):
                            freeBusyList.append(["free ", eSet[i], endDay])
                            today = False
                        else:
                            freeBusyList.append(["free ", eSet[i], eSet[i+1]])
                        busy = True
                    i += 1
                else:
                    freeBusyList.append(["free ", startDay, endDay])
                    today = False
            elif i != len(eSet):
                if eSet[i].date() != startDay.date():
                    freeBusyList.append(["free ", startDay, endDay])
                else:
                    freeBusyList.append(["free ", eSet[i], endDay])
                today = False
            else:
                freeBusyList.append(["free ", startDay, endDay])
                today = False
    return freeBusyList
