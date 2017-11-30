'''
Author: Sam Gerendasy
This module returns a list of free and busy time blocks
from a given list of calendar entries, between a given
start and end date, and furthermore, between a given
start and end time.
'''


def freeBusyTimes(eSet, startingBounds, endingBounds):
    '''
    eSet is an array of entries.
    startingBounds is an array of arrow objects, one object for each day, each object with the specified start time
    endingBounds is an array of arrow objects, one object for each day, each object with the specified end time
    returns an array of entries, each entry  has a start arrow object and an end arrow object. 
    Objects are either "busy" or "free"
    '''
    freeBusyList = []
    i = 0
    # iterate through each day
    for startDay, endDay in zip(startingBounds, endingBounds):
        busy = False
        today = True
        startOfDayHandled = False
        while(today):
            if(i < len(eSet)-1):
                # if entry is of the current date
                if eSet[i].date() == startDay.date():
                    # if the entry starts before the starting bound
                    if eSet[i].format("HHmm") <= startDay.format("HHmm"):
                        eSet[i] = eSet[i].replace(hour=startDay.hour)
                        eSet[i] = eSet[i].replace(minute=startDay.minute)
                        busy = True
                        startOfDayHandled = True
                    # if the entry starts after the starting bound, and there the free time
                    # between the starting bound and the entry hasn't been added
                    elif eSet[i] > startDay and not startOfDayHandled:
                        freeBusyList.append(["free: ", startDay, eSet[i]])
                        busy = True
                        startOfDayHandled = True
                    # if the current entry is a busy entry
                    if busy:
                        # if the entry's end time ends after the ending bound
                        if(eSet[i+1] >= endDay):
                            freeBusyList.append(["busy: ", eSet[i], endDay])
                            i += 1
                            today = False
                        # else the entry's end time doesn't end after the ending bound
                        else:
                            freeBusyList.append(["busy: ", eSet[i], eSet[i+1]])
                        busy = False
                    # else if the current entry is a free entry
                    elif not busy:
                        # if the entry starts at the ending bound, end of day reached
                        if eSet[i].format("YYYYMMDDHHmm") == endDay.format("YYYYMMDDHHmm"):
                            today = False
                        # else if the end time ends after the ending bound
                        elif(eSet[i+1] >= endDay):
                            freeBusyList.append(["free: 1", eSet[i], endDay])
                            today = False
                        # else the event fits in the day, print it
                        else:
                            freeBusyList.append(["free: 2", eSet[i], eSet[i+1]])
                        busy = True
                    i += 1
                # else there are no entries for the current day
                else:
                    freeBusyList.append(["free: ", startDay, endDay])
                    today = False
            # else the end of the list of entries has been reached
            elif i != len(eSet):
                if eSet[i].date() != startDay.date():
                    freeBusyList.append(["free: ", startDay, endDay])
                else:
                    freeBusyList.append(["free: ", eSet[i], endDay])
                today = False
            else:
                freeBusyList.append(["free: ", startDay, endDay])
                today = False
    return freeBusyList
