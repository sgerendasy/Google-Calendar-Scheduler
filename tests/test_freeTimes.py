"""
Nose tests for flask_main.py
"""
from freeAndBusyTimeCalculator import freeBusyTimes
import arrow

# import nose    # Testing framework
import logging

arrowStartBound = arrow.get("2017111309:00", "YYYYMMDDHH:mm", tzinfo="local")
arrowEndBound = arrow.get("2017111317:00", "YYYYMMDDHH:mm", tzinfo="local")
arrowEndBoundDate = arrow.get("2017111717:00", "YYYYMMDDHH:mm", tzinfo="local")
arrowDayRange = arrowEndBoundDate - arrowStartBound
numberOfDays = arrowDayRange.days #  calculate number of days
if(arrowDayRange.seconds > 0):
    numberOfDays += 1

startingBoundDateArray = []
endingBoundDateArray = []
for i in range(numberOfDays):
    startingBoundDateArray.append(arrowStartBound.replace(days=+i))
    endingBoundDateArray.append(arrowEndBound.replace(days=+i))


startingBoundDate9AM = [arrow.get("2017111409:00", "YYYYMMDDHH:mm", tzinfo="local")]
endingBoundDate5PM = [arrow.get("2017111417:00", "YYYYMMDDHH:mm", tzinfo="local")]

startingBoundDate8AM = [arrow.get("2017111408:00", "YYYYMMDDHH:mm", tzinfo="local")]
endingBoundDate11AM = [arrow.get("2017111411:00", "YYYYMMDDHH:mm", tzinfo="local")]

entryA = arrow.get("2017111409:00", "YYYYMMDDHH:mm", tzinfo="local") #  starts at starting bound
entryB = arrow.get("2017111410:00", "YYYYMMDDHH:mm", tzinfo="local")
entryC = arrow.get("2017111411:00", "YYYYMMDDHH:mm", tzinfo="local")
entryD = arrow.get("2017111417:00", "YYYYMMDDHH:mm", tzinfo="local") #  end at ending bound
entryE = arrow.get("2017111508:00", "YYYYMMDDHH:mm", tzinfo="local") #  starts before starting bound
entryF = arrow.get("2017111509:30", "YYYYMMDDHH:mm", tzinfo="local")
entryG = arrow.get("2017111511:00", "YYYYMMDDHH:mm", tzinfo="local")
entryH = arrow.get("2017111512:30", "YYYYMMDDHH:mm", tzinfo="local") #  end before ending bound
entryI = arrow.get("2017111610:30", "YYYYMMDDHH:mm", tzinfo="local") #  start after starting bound
entryJ = arrow.get("2017111611:30", "YYYYMMDDHH:mm", tzinfo="local")
entryK = arrow.get("2017111612:30", "YYYYMMDDHH:mm", tzinfo="local")
entryL = arrow.get("2017111617:30", "YYYYMMDDHH:mm", tzinfo="local") #  end after ending bound


unionizedEntries = [entryA, entryB, entryC, entryD, entryE, entryF, entryG, entryH,
            entryI, entryJ, entryK, entryL]


def test_starting_bound_edge_case_equalTo_first_entry():
	expectedResult = [["busy ", "2017-11-14 09:00:00", "2017-11-14 10:00:00"],
						["free ", "2017-11-14 10:00:00", "2017-11-14 17:00:00"]]
	freeBusyResult = freeBusyTimes([entryA, entryB], startingBoundDate9AM, endingBoundDate5PM)
	for entry, expected in zip(freeBusyResult, expectedResult):
	        assert(entry[0] == expected[0])
	        string1 = str(entry[1].date()) + " " + str(entry[1].time())
	        string2 = str(entry[2].date()) + " " + str(entry[2].time())
	        assert(string1 == expected[1])
	        assert(string2 == expected[2])
	pass


def test_starting_bound_edge_case_lessThan_first_entry():
	expectedResult = [["free ", "2017-11-14 08:00:00", "2017-11-14 09:00:00"],
						["busy ", "2017-11-14 09:00:00", "2017-11-14 10:00:00"],
						["free ", "2017-11-14 10:00:00", "2017-11-14 17:00:00"]]
	freeBusyResult = freeBusyTimes([entryA, entryB], startingBoundDate8AM, endingBoundDate5PM)
	for entry, expected in zip(freeBusyResult, expectedResult):
	        assert(entry[0] == expected[0])
	        string1 = str(entry[1].date()) + " " + str(entry[1].time())
	        string2 = str(entry[2].date()) + " " + str(entry[2].time())
	        assert(string1 == expected[1])
	        assert(string2 == expected[2])
	pass

def test_typical_use_case():
	expectedResult = [["free ", "2017-11-14 09:00:00", "2017-11-14 10:00:00"],
						["busy ", "2017-11-14 10:00:00", "2017-11-14 11:00:00"],
						["free ", "2017-11-14 11:00:00", "2017-11-14 17:00:00"]]
	freeBusyResult = freeBusyTimes([entryB, entryC], startingBoundDate9AM, endingBoundDate5PM)
	for entry, expected in zip(freeBusyResult, expectedResult):
	        assert(entry[0] == expected[0])
	        string1 = str(entry[1].date()) + " " + str(entry[1].time())
	        string2 = str(entry[2].date()) + " " + str(entry[2].time())
	        assert(string1 == expected[1])
	        assert(string2 == expected[2])
	pass


def test_ending_bound_edge_case_equal():
	expectedResult = [["free ", "2017-11-14 09:00:00", "2017-11-14 10:00:00"],
						["busy ", "2017-11-14 10:00:00", "2017-11-14 11:00:00"]]
	freeBusyResult = freeBusyTimes([entryB, entryC], startingBoundDate9AM, endingBoundDate11AM)
	for entry, expected in zip(freeBusyResult, expectedResult):
	        assert(entry[0] == expected[0])
	        string1 = str(entry[1].date()) + " " + str(entry[1].time())
	        string2 = str(entry[2].date()) + " " + str(entry[2].time())
	        assert(string1 == expected[1])
	        assert(string2 == expected[2])
	pass

def test_ending_bound_edge_case_greaterThan():
	expectedResult = [["busy ", "2017-11-14 09:00:00", "2017-11-14 10:00:00"],
						["free ", "2017-11-14 10:00:00", "2017-11-14 17:00:00"]]
	freeBusyResult = freeBusyTimes([entryA, entryB], startingBoundDate9AM, endingBoundDate5PM)
	for entry, expected in zip(freeBusyResult, expectedResult):
	        assert(entry[0] == expected[0])
	        string1 = str(entry[1].date()) + " " + str(entry[1].time())
	        string2 = str(entry[2].date()) + " " + str(entry[2].time())
	        assert(string1 == expected[1])
	        assert(string2 == expected[2])
	pass


def test_multiple_dates():
	expectedResult = [["free ", "2017-11-13 09:00:00", "2017-11-13 17:00:00"],
	["busy ", "2017-11-14 09:00:00", "2017-11-14 10:00:00"],
	["free ", "2017-11-14 10:00:00", "2017-11-14 11:00:00"],
	["busy ", "2017-11-14 11:00:00", "2017-11-14 17:00:00"],
	["busy ", "2017-11-15 09:00:00", "2017-11-15 09:30:00"],
	["free ", "2017-11-15 09:30:00", "2017-11-15 11:00:00"],
	["busy ", "2017-11-15 11:00:00", "2017-11-15 12:30:00"],
	["free ", "2017-11-15 12:30:00", "2017-11-15 17:00:00"],
	["free ", "2017-11-16 09:00:00", "2017-11-16 10:30:00"],
	["busy ", "2017-11-16 10:30:00", "2017-11-16 11:30:00"],
	["free ", "2017-11-16 11:30:00", "2017-11-16 12:30:00"],
	["busy ", "2017-11-16 12:30:00", "2017-11-16 17:00:00"],
	["free ", "2017-11-17 09:00:00", "2017-11-17 17:00:00"]]
	freeBusyResult = freeBusyTimes(unionizedEntries, startingBoundDateArray, endingBoundDateArray)
	for entry, expected in zip(freeBusyResult, expectedResult):
	        assert(entry[0] == expected[0])
	        string1 = str(entry[1].date()) + " " + str(entry[1].time())
	        string2 = str(entry[2].date()) + " " + str(entry[2].time())
	        assert(string1 == expected[1])
	        assert(string2 == expected[2])
	pass