import flask
from flask import render_template
from flask import request
from flask import url_for
import uuid
from apiclient.discovery import build  # google api
from dateutil import tz
from freeAndBusyTimeCalculator import freeBusyTimes
import os
import random
import sys
import json
import logging

# Date handling
import arrow  # Replacement for datetime, based on moment.js
# import datetime # But we still need time
from dateutil import tz  # For interpreting local times


# OAuth2  - Google library implementation for convenience
from oauth2client import client
import httplib2   # used in oauth2 flow

# Google API for services
from apiclient import discovery
from oauth2client.client import OAuth2WebServerFlow
from pymongo import MongoClient

###
# Globals
###
import config

app = flask.Flask(__name__)
if __name__ == "__main__":
    isMain = True
    CONFIG = config.configuration()
    app.debug = CONFIG.DEBUG
    app.secret_key = CONFIG.SECRET_KEY
    CLIENT_SECRET_FILE = CONFIG.GOOGLE_KEY_FILE  # You'll need this
    MONGO_CLIENT_URL = "mongodb://{}:{}@{}:{}/{}".format(
    CONFIG.DB_USER,
    CONFIG.DB_USER_PW,
    CONFIG.DB_HOST,
    CONFIG.DB_PORT,
    CONFIG.DB)
else:
    isMain = False
    # CONFIG = config.configuration(proxied=True)
    app.debug = os.environ.get('debug', None)
    app.secret_key = os.environ.get('Secret_Key', None)
    CLIENT_SECRET_FILE = os.environ.get('google_key_file', None)
    clientId = os.environ.get('clientID', None)
    clientSecret = os.environ.get('clientSecret', None)
    MONGO_CLIENT_URL = "mongodb://{}:{}@{}:{}/{}".format(
    os.environ.get('DB_USER', None),
    os.environ.get('DB_USER_PW', None),
    os.environ.get('DB_HOST', None),
    os.environ.get('DB_PORT', None),
    os.environ.get('DB', None))


app.logger.setLevel(logging.DEBUG)



SCOPES = ['https://www.googleapis.com/auth/calendar.readonly', ' https://www.googleapis.com/auth/userinfo.email',
            "https://www.googleapis.com/auth/plus.login", 'https://www.googleapis.com/auth/plus.me', 'https://www.googleapis.com/auth/userinfo.profile']

APPLICATION_NAME = 'MeetMe class project'


try:
    dbclient = MongoClient(MONGO_CLIENT_URL)
    db = getattr(dbclient, CONFIG.DB)

except:
    print("Failure opening database.  Is Mongo running? Correct password?")
    sys.exit(1)



#############################
#
#  Pages (routed from URLs)
#
#############################


@app.route("/")
@app.route("/index")
def index():
    app.logger.debug("Entering index")
    if 'begin_date' not in flask.session:
        init_session_values()
    return render_template('index.html')

startingBound = ""
endingBound = ""


@app.route("/choose")
def choose():
    # We'll need authorization to list calendars
    # I wanted to put what follows into a function, but had
    # to pull it back here because the redirect has to be a
    # 'return'
    app.logger.debug("Checking credentials for Google calendar access")
    credentials = valid_credentials()
    if not credentials:
        app.logger.debug("Redirecting to authorization")
        return flask.redirect(flask.url_for('oauth2callback'))

    service = get_gcal_service(credentials)
    gcal_service = service[0]
    
    app.logger.debug("Returned from get_gcal_service")

    flask.g.calendars = list_calendars(gcal_service)


    flask.g.meetingID = random.randint(0,10000)
    mongoCollectionName = "a" + str(flask.g.meetingID)
    collection = db[mongoCollectionName]
    collection.insert({"init":1, "dateRange":flask.session['daterange'], "startTime":flask.session['startInput'], "endTime":flask.session['endInput']})

    return flask.redirect(flask.url_for('meeting', meetingID=flask.g.meetingID))

@app.route("/meeting/<meetingID>")
def meeting(meetingID):
    # We'll need authorization to list calendars
    # I wanted to put what follows into a function, but had
    # to pull it back here because the redirect has to be a
    # 'return'

    # I'll need to check to see if meetingID is valid mongoDB entry. If not, redirect to a "meeting not found" page

    app.logger.debug("Checking credentials for Google calendar access")
    credentials = valid_credentials()
    if not credentials:
        app.logger.debug("Redirecting to authorization")
        return flask.redirect(flask.url_for('oauth2callback'))

    service = get_gcal_service(credentials)
    gcal_service = service[0]
    p_service = service[1]
    flask.g.userEmail = p_service.people().get(userId="me").execute()["emails"][0]['value']
    
    flask.g.calendars = list_calendars(gcal_service)
    dbCollections = db.collection_names()
    mongoCollectionName = "a" + str(meetingID)
    collectionExists = False
    for collection in dbCollections:
        if mongoCollectionName == collection:
            collectionExists = True
    if not collectionExists:
        return render_template('noSuchMeeting.html')
    startingInfo = db[mongoCollectionName].find({"init":1})

    flask.session['daterange'] = startingInfo[0]["dateRange"]
    flask.session['endInput'] = startingInfo[0]["endTime"]
    flask.session['startInput'] = startingInfo[0]["startTime"]
    
    flask.g.meetingID = meetingID
    return render_template('meeting.html')


@app.route("/updateCalendar")
def updateCalendar():
    meetingID = request.args.get("meetingID", type=str)
    userEmail = request.args.get("userEmail", type=str)
    calendarToAdd = json.loads(request.args.get("val"))
    startingBound = request.args.get("startTime", type=str)
    endingBound = request.args.get("endTime", type=str)

    dateRanges = request.args.get("dates", type=str)
    dateRanges = dateRanges.split(" ")
    dateRanges.remove("-")
    dateRanges[0] = dateRanges[0].split("/")
    dateRanges[1] = dateRanges[1].split("/")
    startingBoundDate = dateRanges[0][2] + dateRanges[0][0] + dateRanges[0][1]
    endingBoundDate = dateRanges[1][2] + dateRanges[1][0] + dateRanges[1][1]

    arrowStartBound = arrow.get(startingBoundDate + startingBound, "YYYYMMDDHH:mm", tzinfo="local")
    arrowEndBound = arrow.get(startingBoundDate + endingBound, "YYYYMMDDHH:mm", tzinfo="local")
    arrowEndBoundDate = arrow.get(endingBoundDate + endingBound, "YYYYMMDDHH:mm", tzinfo="local")
    arrowDayRange = arrowEndBoundDate - arrowStartBound
    numberOfDays = arrowDayRange.days
    if(arrowDayRange.seconds > 0):
        numberOfDays += 1

    startingBoundDateArray = []
    endingBoundDateArray = []
    for i in range(numberOfDays):
        startingBoundDateArray.append(arrowStartBound.replace(days=+i))
        endingBoundDateArray.append(arrowEndBound.replace(days=+i))

    if(startingBound == ""):
        # set default starting bound to 9:00am
        startingBound = "09:00"
    if(endingBound == ""):
        # set default ending bound to 5:00pm
        endingBound = "17:00"

    credentials = valid_credentials()
    if not credentials:
        app.logger.debug("Redirecting to authorization")
        return flask.redirect(flask.url_for('oauth2callback'))
    service = get_gcal_service(credentials)
    gcal_service = service[0]
    page_token = None

    mongoCollectionName = "a" + meetingID
    collection = db[mongoCollectionName]
    allEntries = []

    allInDBToRemove = collection.find({"email":userEmail})
    for e in allInDBToRemove:
        collection.remove(e)

    for calendar in calendarToAdd:
        events = gcal_service.events().list(calendarId=calendar,
                                            pageToken=page_token).execute()
        arrowEntries = pullBusyTimes(events, startingBoundDateArray, endingBoundDateArray)
        for aEntry in arrowEntries:
            collectionEntry = {"start":str(aEntry[0]), "end":str(aEntry[1]), "email":userEmail, "init":0}
            collection.insert(collectionEntry)


    allInDBToAdd = collection.find({"init":0})
    for e in allInDBToAdd:
        tempStart = arrow.get(e['start'])
        tempEnd = arrow.get(e['end'])
        allEntries.append([tempStart, tempEnd])

    allEntries.sort()
    unionEntries = disjointSetBusyTimes(allEntries)
    displayEntries = freeBusyTimes(unionEntries, startingBoundDateArray, endingBoundDateArray)
    formattedEntries = formatEntries(displayEntries)

    return flask.jsonify(result=formattedEntries)


def leadingZero(n):
    if(n < 10):
        return "0" + str(n)
    else:
        return str(n)


def formatEntries(listOfEntries):
    entriesToDisplay = []
    currentDay = listOfEntries[0][1].day
    entriesToDisplay.append(str(listOfEntries[0][1].date()))
    for entry in listOfEntries:
        if(entry[1].day != currentDay):
            currentDay = entry[1].day
            entriesToDisplay.append(str(entry[1].date()))
        entryStartTime = leadingZero(entry[1].hour) + ":"
        entryStartTime += leadingZero(entry[1].minute)

        entryEndTime = leadingZero(entry[2].hour) + ":"
        entryEndTime += leadingZero(entry[2].minute)
        formatted = entry[0] + entryStartTime + " - " + entryEndTime
        entriesToDisplay.append(formatted)
    return entriesToDisplay


def pullBusyTimes(googleEvents, startingBoundDates, endingBoundDates):
    entriesToDisplay = []
    arrowEntries = []
    while True:
        for startDate, endDate in zip(startingBoundDates, endingBoundDates):
            for calendar_entry in googleEvents['items']:
                try:
                    arrowStart = arrow.get(calendar_entry['start']['date'])
                    arrowStart = arrowStart.replace(tzinfo='local')
                    arrowEnd = arrowStart.replace(hours=endDate.hour, minutes=endDate.minute)
                    arrowStart = arrowStart.replace(hours=startDate.hour, minutes=startDate.minute)

                    if(arrowStart.format("YYYYMMDD") == startDate.format("YYYYMMDD")):
                        arrowEntries.append([arrowStart, arrowEnd])
                except:
                    arrowStart = arrow.get(calendar_entry['start']["dateTime"])
                    arrowEnd = arrow.get(calendar_entry['end']["dateTime"])
                    # if starting time for entry falls within bounds
                    if(arrowEnd.format("YYYYMMDD") == startDate.format("YYYYMMDD")):
                        # if starting time for entry falls within bounds
                        if(arrowEnd.format("HHmm") >= startDate.format("HHmm") and
                           arrowStart.format("HHmm") <= endDate.format("HHmm")):
                            arrowEntries.append([arrowStart, arrowEnd])
        page_token = googleEvents.get('nextPageToken')
        if not page_token:
            break

    return arrowEntries


def disjointSetBusyTimes(arrowEntries):
    # must be sorted!
    disjointSet = []
    for entry in arrowEntries:
        joined = False
        for i in range(len(disjointSet) - 1):
            if(entry[0] >= disjointSet[i] and entry[0] <= disjointSet[i+1]):
                if(disjointSet[i+1] < entry[1]):
                    disjointSet[i+1] = entry[1]
                    joined = True
        if not joined:
            disjointSet.append(entry[0])
            disjointSet.append(entry[1])

    return disjointSet


@app.route("/parse_times")
def parse_time():
    time = request.args.get("time", type=str)
    try:
        arrowTime = arrow.get(time, "HH:mm").isoformat()
        result = {"time": arrowTime}
    except:
        result = {"time": "failed"}
    return flask.jsonify(result=result)


def valid_credentials():
    """
    Returns OAuth2 credentials if we have valid
    credentials in the session.  This is a 'truthy' value.
    Return None if we don't have credentials, or if they
    have expired or are otherwise invalid.  This is a 'falsy' value.
    """
    if 'credentials' not in flask.session:
        return None

    credentials = client.OAuth2Credentials.from_json(
        flask.session['credentials'])

    print("Creds: ", credentials)

    if (credentials.invalid or credentials.access_token_expired):
        return None
    return credentials


def get_gcal_service(credentials):
    """
    We need a Google calendar 'service' object to obtain
    list of calendars, busy times, etc.  This requires
    authorization. If authorization is already in effect,
    we'll just return with the authorization. Otherwise,
    control flow will be interrupted by authorization, and we'll
    end up redirected back to /choose *without a service object*.
    Then the second call will succeed without additional authorization.
    """
    app.logger.debug("Entering get_gcal_service")
    http_auth = credentials.authorize(httplib2.Http())
    service = discovery.build('calendar', 'v3', http=http_auth)
    plusService = discovery.build('plus', 'v1', http=http_auth)
    app.logger.debug("Returning service")
    return [service, plusService]


@app.route('/oauth2callback')
def oauth2callback():
    """
    The 'flow' has this one place to call back to.  We'll enter here
    more than once as steps in the flow are completed, and need to keep
    track of how far we've gotten. The first time we'll do the first
    step, the second time we'll skip the first step and do the second,
    and so on.
    """
    app.logger.debug("Entering oauth2callback")
    if(isMain):
        flow = client.flow_from_clientsecrets(
            CLIENT_SECRET_FILE,
            scope=SCOPES,
            redirect_uri=flask.url_for('oauth2callback', _external=True))
    else:
        flow = OAuth2WebServerFlow(client_id=clientId,
                               client_secret=clientSecret,
                               scope=SCOPES,
                               redirect_uri=flask.url_for('oauth2callback', _external=True))

    # Note we are *not* redirecting above. We are noting *where*
    # we will redirect to, which is this function.

    # The *second* time we enter here, it's a callback
    # with 'code' set in the URL parameter.  If we don't
    # see that, it must be the first time through, so we
    # need to do step 1.
    app.logger.debug("Got flow")
    if 'code' not in flask.request.args:
        app.logger.debug("Code not in flask.request.args")
        auth_uri = flow.step1_get_authorize_url()
        return flask.redirect(auth_uri)
        # This will redirect back here, but the second time through
        # we'll have the 'code' parameter set
    else:
        # It's the second time through ... we can tell because
        # we got the 'code' argument in the URL.
        app.logger.debug("Code was in flask.request.args")
        auth_code = flask.request.args.get('code')
        credentials = flow.step2_exchange(auth_code)
        flask.session['credentials'] = credentials.to_json()
        # Now I can build the service and execute the query,
        # but for the moment I'll just log it and go back to
        # the main screen
        app.logger.debug("Got credentials")
        return flask.redirect(flask.url_for('choose'))

#
#  Option setting:  Buttons or forms that add some
#     information into session state.  Don't do the
#     computation here; use of the information might
#     depend on what other information we have.
#   Setting an option sends us back to the main display
#      page, where we may put the new information to use.
#


@app.route('/setrange', methods=['POST'])
def setrange():
    """
    User chose a date range with the bootstrap daterange
    widget.
    """
    app.logger.debug("Entering setrange")
    flask.flash("Setrange gave us '{}'".format(
      request.form.get('daterange')))
    daterange = request.form.get('daterange')
    flask.session['daterange'] = daterange
    daterange_parts = daterange.split()
    flask.session['begin_date'] = interpret_date(daterange_parts[0])
    flask.session['end_date'] = interpret_date(daterange_parts[2])
    app.logger.debug("Setrange parsed {} - {}  dates as {} - {}".format(
      daterange_parts[0], daterange_parts[1],
      flask.session['begin_date'], flask.session['end_date']))
    startingBound = request.form.get('StartTime')
    endingBound = request.form.get('EndTime')
    flask.session['startInput'] = startingBound
    flask.session['endInput'] = endingBound



    return flask.redirect(flask.url_for("choose"))

#
#   Initialize session variables
#


def init_session_values():
    """
    Start with some reasonable defaults for date and time ranges.
    Note this must be run in app context ... can't call from main.
    """
    # Default date span = tomorrow to 1 week from now
    now = arrow.now('local')     # We really should be using tz from browser
    tomorrow = now.replace(days=+1)
    nextweek = now.replace(days=+7)
    flask.session["begin_date"] = tomorrow.floor('day').isoformat()
    flask.session["end_date"] = nextweek.ceil('day').isoformat()
    flask.session["daterange"] = "{} - {}".format(
        tomorrow.format("MM/DD/YYYY"),
        nextweek.format("MM/DD/YYYY"))
    # Default time span each day, 8 to 5
    flask.session["begin_time"] = interpret_time("9am")
    flask.session["end_time"] = interpret_time("5pm")


def interpret_time(text):
    """
    Read time in a human-compatible format and
    interpret as ISO format with local timezone.
    May throw exception if time can't be interpreted. In that
    case it will also flash a message explaining accepted formats.
    """
    app.logger.debug("Decoding time '{}'".format(text))
    time_formats = ["ha", "h:mma",  "h:mm a", "H:mm"]
    try:
        as_arrow = arrow.get(text, time_formats).replace(tzinfo=tz.tzlocal())
        as_arrow = as_arrow.replace(year=2016)  # HACK see below
        app.logger.debug("Succeeded interpreting time")
    except:
        app.logger.debug("Failed to interpret time")
        flask.flash("Time '{}' didn't match accepted formats 13:30 or 1:30pm"
                    .format(text))
        raise
    return as_arrow.isoformat()
    # HACK Workaround
    # isoformat() on raspberry Pi does not work for some dates
    # far from now.  It will fail with an overflow from time stamp out
    # of range while checking for daylight savings time.  Workaround is
    # to force the date-time combination into the year 2016, which seems to
    # get the timestamp into a reasonable range. This workaround should be
    # removed when Arrow or Dateutil.tz is fixed.
    # FIXME: Remove the workaround when arrow is fixed (but only after testing
    # on rasp Pi failure is likely due to 32-bit integers on that platform)


def interpret_date(text):
    """
    Convert text of date to ISO format used internally,
    with the local time zone.
    """
    try:
        as_arrow = arrow.get(text, "MM/DD/YYYY").replace(
            tzinfo=tz.tzlocal())
    except:
        flask.flash("Date '{}' didn't fit expected format 12/31/2001")
        raise
    return as_arrow.isoformat()


def next_day(isotext):
    """
    ISO date + 1 day (used in query to Google calendar)
    """
    as_arrow = arrow.get(isotext)
    return as_arrow.replace(days=+1).isoformat()

#
#  Functions (NOT pages) that return some information
#


def list_calendars(service):
    """
    Given a google 'service' object, return a list of
    calendars.  Each calendar is represented by a dict.
    The returned list is sorted to have
    the primary calendar first, and selected (that is, displayed in
    Google Calendars web app) calendars before unselected calendars.
    """
    app.logger.debug("Entering list_calendars")
    calendar_list = service.calendarList().list().execute()["items"]
    result = []
    for cal in calendar_list:
        kind = cal["kind"]
        id = cal["id"]
        if "description" in cal:
            desc = cal["description"]
        else:
            desc = "(no description)"
        summary = cal["summary"]
        # Optional binary attributes with False as default
        selected = ("selected" in cal) and cal["selected"]
        primary = ("primary" in cal) and cal["primary"]

        result.append(
          {"kind": kind, "id": id, "summary": summary, "selected": selected,
           "primary": primary})
    return sorted(result, key=cal_sort_key)


def cal_sort_key(cal):
    """
    Sort key for the list of calendars:  primary calendar first,
    then other selected calendars, then unselected calendars.
    (" " sorts before "X", and tuples are compared piecewise)
    """
    if cal["selected"]:
        selected_key = " "
    else:
        selected_key = "X"
    if cal["primary"]:
        primary_key = " "
    else:
        primary_key = "X"
    return (primary_key, selected_key, cal["summary"])


#################
#
# Functions used within the templates
#
#################


@app.template_filter('fmtdate')
def format_arrow_date(date):
    try:
        normal = arrow.get(date)
        return normal.format("ddd MM/DD/YYYY")
    except:
        return "(bad date)"


@app.template_filter('fmttime')
def format_arrow_time(time):
    try:
        normal = arrow.get(time)
        return normal.format("HH:mm")
    except:
        return "(bad time)"

#############


if __name__ == "__main__":
    # App is created above so that it will
    # exist whether this is 'main' or not
    # (e.g., if we are running under green unicorn)
    app.run(port=CONFIG.PORT, host="0.0.0.0")
