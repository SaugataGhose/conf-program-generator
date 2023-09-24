# GENSCHED.PY
# Author: Saugata Ghose (ghose at illinois dot edu)
# Last Updated: September 24, 2023
#
# script to generate a Bootstrap-compatible HTML schedule
#   for conference programs


import csv
import sys
import html
import argparse
from collections import OrderedDict

from affilclean import *
from confconfig import *

# currently supports 20 separate sessions
sessionIDs = ["i", "ii", "iii", "iv", "v", "vi", "vii", "viii", "ix", "x", "xi", "xii", "xiii", "xiv", "xv", "xvi", "xvii", "xviii", "xix", "xx"];

# currently supports 8 concurrent sessions
subsessionIDs = ["a", "b", "c", "d", "e", "f", "g", "h"]

paperTitleByID = {};
paperAuthorsByTitle = {};
paperLinksByTitle = {};

subsessionLabels = [];
sessionLabels = [];

sessionInfo = {};
sessionPapers = OrderedDict();
sessionHTMLIDs = {};

keynoteDetails = {};
keynoteHTMLIDs = {};

eventDay = [];
eventType = [];
eventStart = [];
eventEnd = [];
eventNames = [];
eventLocations = [];
eventNotes = [];

locationFloors = {};


def read_authors(filename):
    global paperTitleByID;
    global paperAuthorsByTitle;

    with open(filename, mode = "r") as csvFile:
        authorFile = csv.reader(csvFile);

        # skip header row
        next(authorFile);

        currentPaper = "";
        currentAffiliation = "";
        paperTitle = "";
        paperAuthors = "";

        for row in authorFile:
            if currentPaper != row[0]:
                if currentPaper != "":
                    if currentAffiliation != "":
                        paperAuthors += " (" + currentAffiliation + ")";

                    # print("Title: " + paperTitle);
                    # print("Authors: " + paperAuthors + '\n');

                    if currentPaper in paperTitleByID:
                        print("ERROR: Duplicate ID " + currentPaper, file=sys.stderr);
                    else:
                        paperTitleByID[currentPaper] = paperTitle;

                    if paperTitle in paperAuthorsByTitle:
                        print("ERROR: Duplicate Title '" + paperTitle + "'", file=sys.stderr);
                    else:
                        paperAuthorsByTitle[paperTitle] = paperAuthors;

                currentPaper = row[0];
                paperTitle = row[1];
                paperAuthors = "";
                currentAffiliation = "";
            
            if len(row) > 6 and row[7] == "nonauthor":
                continue;

            cleanedAffiliation = clean_affil(row[5]);
            if cleanedAffiliation == "":
                cleanedAffiliation = "unaffiliated";

            if paperAuthors != "":
                if currentAffiliation != cleanedAffiliation:
                    paperAuthors += " (" + currentAffiliation + "); ";
                else:
                    paperAuthors += ", ";

            currentAffiliation = cleanedAffiliation;
            paperAuthors += row[2] + " " + row[3]
        
        if currentPaper != "":
            if currentAffiliation != "":
                paperAuthors += " (" + currentAffiliation + ")";

            # print("Title: " + paperTitle);
            # print("Authors: " + paperAuthors + '\n');

            if currentPaper in paperTitleByID:
                print("ERROR: Duplicate ID " + currentPaper, file=sys.stderr);
            else:
                paperTitleByID[currentPaper] = paperTitle;

            if paperTitle in paperAuthorsByTitle:
                print("ERROR: Duplicate Title '" + paperTitle + "'", file=sys.stderr);
            else:
                paperAuthorsByTitle[paperTitle] = paperAuthors;
    
    print("STAT: " + str(len(paperAuthorsByTitle)) + " papers in " + filename, file=sys.stderr);


def read_session(infoFilename, paperFilename):
    global sessionIDs;
    global subsessionIDs;
    global sessionLabels;
    global subsessionLabels;
    global sessionInfo;
    global sessionPapers;
    global sessionHTMLIDs;
    global paperTitleByID;

    with open(infoFilename, mode = "r", encoding="utf8") as csvFile:
        infoFile = csv.DictReader(csvFile);

        for row in infoFile:
            currentSession = row.pop('Session');
            sortedRow = OrderedDict(sorted(row.items(), key=lambda item: infoFile.fieldnames.index(item[0])))
            sortedRow['Affiliation'] = clean_affil(sortedRow['Affiliation']);
            sessionInfo[currentSession] = sortedRow;

    with open(paperFilename, mode = "r", encoding="utf8") as csvFile:
        sessionFile = csv.reader(csvFile);

        row = next(sessionFile);
        subsessionLabels = row[1:];

        currentSession = "";
        numSessions = -1;
        numSubsessions = 0;
        numPapers = 0;

        for row in sessionFile:
            if row[0] != "" and row[0] != currentSession:
                for i in range(numSubsessions):
                    sessionPapers[currentSession + subsessionLabels[i]] = subsession[i];
                    sessionHTMLIDs[currentSession + subsessionLabels[i]] = sessionIDs[numSessions] + '-' + subsessionIDs[i];
                    numPapers = numPapers + len(subsession[i]);

                currentSession = row[0];
                sessionLabels.append(row[0]);
                numSubsessions = 0;
                for column in row[1:]:
                    if column != "":
                        # currently assumes no empty columns
                        numSubsessions = numSubsessions + 1;
                subsession = [[]  for i in range(numSubsessions)];
                numSessions = numSessions + 1;

                # first row contains titles; skip
                continue;
            
            # append titles into list
            for i in range(numSubsessions):
                if row[i+1] != "":
                    if row[i+1].isnumeric():
                        if row[i+1] in paperTitleByID:
                            subsession[i].append(paperTitleByID[row[i+1]]);
                        else:
                            print("  **ERROR**: Paper ID '" + row[i+1] + "' in Session " + currentSession +  subsessionLabels[i] + " not found. Is the ID correct?", file=sys.stderr);
                    else:
                        subsession[i].append(row[i+1]);

        if currentSession != "":
            for i in range(numSubsessions):
                sessionPapers[currentSession + subsessionLabels[i]] = subsession[i];
                sessionHTMLIDs[currentSession + subsessionLabels[i]] = sessionIDs[numSessions] + '-' + subsessionIDs[i];
                numPapers = numPapers + len(subsession[i]);
        numSessions = numSessions;
    
    print("STAT: " + str(numPapers) + " papers in " + paperFilename, file=sys.stderr);


def read_schedule(filename):
    global eventDay;
    global eventType;
    global eventStart;
    global eventEnd;
    global eventNames;
    global eventLocations;
    global eventNotes;
    global locationFloors;

    locations = [];

    with open(filename, mode = "r", encoding="utf8") as csvFile:
        schedFile = csv.reader(csvFile);

        # first two rows contain location names and location floors
        row = next(schedFile);
        locations = row;
        row = next(schedFile);
        for i in range(4, len(row) - 2):
            locationFloors[locations[i]] = row[i];

        for row in schedFile:
            if row[0] != "":
                rowNames = [];
                rowLocs = [];

                # skip first four columns (which are day, type, start, end) to find event names
                # skip last column, which contains additional notes about the event
                for i in range(4, len(row) - 1):
                    if row[i] != "":
                        rowNames.append(row[i]);
                        rowLocs.append(locations[i]);

                if rowNames != []:
                    eventDay.append(row[0]);
                    eventType.append(row[1]);
                    eventStart.append(row[2]);
                    eventEnd.append(row[3]);
                    eventNames.append(rowNames);
                    eventLocations.append(rowLocs);
                    eventNotes.append(row[-1]);

    # for i in range(len(eventDay)):
    #     print(eventDay[i] + ", " + eventStart[i] + " - " + eventEnd[i]);
    #     for j in range(len(eventNames[i])):
    #         print("- " + eventNames[i][j] + " (" + eventLocations[i][j] + ")");


def read_keynotes(filename):
    global keynoteDetails;
    global keynoteHTMLIDs;
    global sessionIDs;

    with open(filename, mode = "r", encoding="utf8") as csvFile:
        keynoteFile = csv.DictReader(csvFile);

        numKeynotes = 0;
        
        for row in keynoteFile:
            currentKeynote = row.pop('Keynote');
            currentLinks = OrderedDict();
            sortedRow = OrderedDict(sorted(row.items(), key=lambda item: keynoteFile.fieldnames.index(item[0])))
            sortedRow['Affiliation'] = clean_affil(sortedRow['Affiliation']);
            for linkType in ['Video', 'Slides']:
                link = sortedRow.pop(linkType);
                if link != "":
                    currentLinks[linkType] = link;
            sortedRow['Links'] = currentLinks;
            keynoteDetails[currentKeynote] = sortedRow;
            keynoteHTMLIDs[currentKeynote] = sessionIDs[numKeynotes];
            numKeynotes = numKeynotes + 1;

        # print(keynoteDetails);
        # print(keynoteHTMLIDs);


def read_links(filename):
    global paperLinksByTitle;

    with open(filename, mode = "r", encoding="utf8") as csvFile:
        linkFile = csv.DictReader(csvFile);
        
        for row in linkFile:
            currentTitle = row.pop('Title');
            sortedRow = OrderedDict(sorted(row.items(), key=lambda item: linkFile.fieldnames.index(item[0])))
            paperLinksByTitle[currentTitle] = sortedRow;

        # print(paperLinksByTitle);


def html_accent_replacement(text):
    # adapted from https://code.activestate.com/recipes/546517-accent2htmlcodepy-convert-accents-and-special-char/
    htmlcodes = ['&Aacute;', '&aacute;', '&Agrave;', '&Acirc;', '&agrave;', '&Acirc;', '&acirc;', '&Auml;', '&auml;', '&Atilde;', '&atilde;', '&Aring;', '&aring;', '&Aelig;', '&aelig;', '&Ccedil;', '&ccedil;', '&Eth;', '&eth;', '&Eacute;', '&eacute;', '&Egrave;', '&egrave;', '&Ecirc;', '&ecirc;', '&Euml;', '&euml;', '&Iacute;', '&iacute;', '&Igrave;', '&igrave;', '&Icirc;', '&icirc;', '&Iuml;', '&iuml;', '&Ntilde;', '&ntilde;', '&Oacute;', '&oacute;', '&Ograve;', '&ograve;', '&Ocirc;', '&ocirc;', '&Ouml;', '&ouml;', '&Otilde;', '&otilde;', '&Oslash;', '&oslash;', '&szlig;', '&Thorn;', '&thorn;', '&Uacute;', '&uacute;', '&Ugrave;', '&ugrave;', '&Ucirc;', '&ucirc;', '&Uuml;', '&uuml;', '&Yacute;', '&yacute;', '&yuml;', '&copy;', '&reg;', '&trade;', '&euro;', '&cent;', '&pound;', '&lsquo;', '&rsquo;', '&ldquo;', '&rdquo;', '&laquo;', '&raquo;', '&mdash;', '&ndash;', '&deg;', '&plusmn;', '&frac14;', '&frac12;', '&frac34;', '&times;', '&divide;', '&alpha;', '&beta;', '&infin;', '&Cacute;', '&cacute;']
    rawcodes = ['\xc1','\xe1','\xc0','\xc2','\xe0','\xc2','\xe2','\xc4','\xe4','\xc3','\xe3','\xc5','\xe5','\xc6','\xe6','\xc7','\xe7','\xd0','\xf0','\xc9','\xe9','\xc8','\xe8','\xca','\xea','\xcb','\xeb','\xcd','\xed','\xcc','\xec','\xce','\xee','\xcf','\xef','\xd1','\xf1','\xd3','\xf3','\xd2','\xf2','\xd4','\xf4','\xd6','\xf6','\xd5','\xf5','\xd8','\xf8','\xdf','\xde','\xfe','\xda','\xfa','\xd9','\xf9','\xdb','\xfb','\xdc','\xfc','\xdd','\xfd','\xff','\xa9','\xae','\u2122','\u20ac','\xa2','\xa3','\u2018','\u2019','\u201c','\u201d','\xab','\xbb','\u2014','\u2013','\xb0','\xb1','\xbc','\xbd','\xbe','\xd7','\xf7','\u03b1','\u03b2','\u221e', '\u0106', '\u0107']
    
    newText = '';

    for char in text:
        if char not in rawcodes:
            newText = newText + char;
        else:
            newText  = newText + htmlcodes[rawcodes.index(char)];

    return newText;


def make_html_safe(text):
    return html_accent_replacement(html.escape(text)).strip();


def generate_indent(indent):
    pre = "";
    for i in range(indent):
        pre = pre + " ";

    return pre;


def get_map(location):
    global mapPaths;

    if location in mapPaths:
        return mapPaths[location];
    elif '-default-' in mapPaths:
        return mapPaths['-default-'];
    return '';


def format_media_link(label, url):
    css = 'fa-solid fa-link';
    if label == 'Paper':
        css = 'fa-solid fa-file';
    elif label == 'Video':
        css = 'fa-solid fa-video';
    elif label == 'Lightning Talk':
        css = 'fa-solid fa-video';
    elif label == 'Session Lightning Talks':
        css = 'fa-solid fa-video';
    elif label == 'Slides':
        css = 'fa-solid fa-chalkboard-user';

    return '<a href="' + url + '"><span class="' + css + '"></span> ' + make_html_safe(label) + '</a>';


def print_location(location, indent):
    global printLocations;
    global locationFloors;

    pre = generate_indent(indent);

    if printLocations and location != "" and location != "other":
        print(pre + '<h5 class="session-location">');
        print(pre + '  Location: ' + html_accent_replacement(location));
        if location in locationFloors:
            locationMap = get_map(location);
            print(pre + '  <span class="session-floor">(', end='');
            if locationMap != '':
                print('<a href="' + locationMap + '">', end='');
            print('' + html_accent_replacement(locationFloors[location]), end='');
            if locationMap != '':
                print('</a>', end='');
            print(')</span>');
        print(pre + '</h5>');


def print_session(sessionID, htmlID, location, width, indent):
    global paperTitleByID;
    global paperAuthorsByTitle;
    global paperLinksByTitle;
    global sessionInfo;
    global sessionPapers;

    pre = generate_indent(indent);

    print(pre + '<div class="schedule-session col-xs-12 col-md-' + str(width) + '">');
    print(pre + '  <div class="panel panel-default panel-session">');
    print(pre + '    <div class="panel-heading" role="tab" id="title-' + htmlID + '">');
    print(pre + '      <h4 class="panel-title">')
    print(pre + '        <a role="button" data-toggle="collapse" href="#' + htmlID + '" aria-expanded="true" aria-controls="' + htmlID + '">');
    print(pre + '          Session ' + make_html_safe(sessionID), end='');
    if sessionInfo[sessionID]['Title'] != "":
        print(': ' + make_html_safe(sessionInfo[sessionID]['Title']));
    else:
        print();
    print(pre + '        </a>');
    print(pre + '      </h4>');
    print_location(location, indent + 6);
    print(pre + '    </div>');
    print(pre);

    print(pre + '    <div id="' + htmlID + '" class="panel-collapse panel-paper collapse in" role="tabpanel" aria-labelledby="title-' + htmlID + '">');
    print(pre + '      <div class="panel-body">');

    if sessionInfo[sessionID]['Chair'] != "":
        print(pre + '        <div class="session-chair">');
        print(pre + '          Session Chair: ' + make_html_safe(sessionInfo[sessionID]['Chair']), end='');
        if sessionInfo[sessionID]['Affiliation'] != "":
            print(' <span class="affiliation">(' + make_html_safe(sessionInfo[sessionID]["Affiliation"]) + ')</span>', end='');
        print('\n' + pre + '        </div>');

    if sessionInfo[sessionID]['Lightning Talks'] != "":
        print(pre + '        <div class="session-links">');
        print(pre + '          ' + format_media_link('Session Lightning Talks', sessionInfo[sessionID]['Lightning Talks']));
        print(pre + '        </div>');

    separator = "";

    for paper in sessionPapers[sessionID]:
        print(separator + pre + '        <div class="paper">');
        # TODO: add paper times
        # TODO: add best paper flags
        print(pre + '          <div class="paper-title">');
        print(pre + '            ' + make_html_safe(paper));
        print(pre + '          </div>');
        if paper in paperAuthorsByTitle:
            print(pre + '          <div class="paper-authors">');
            print(pre + '            ' + make_html_safe(paperAuthorsByTitle[paper]));
            print(pre + '          </div>');
        else:
            print("  **ERROR**: Title '" + paper + "' in Session " + sessionID + " not found. Was the title updated?", file=sys.stderr);
        if paper in paperLinksByTitle:
            linksStarted = False;
            linkSeparator = "";
            for key, value in paperLinksByTitle[paper].items():
                if value == "":
                    continue;
                if not linksStarted:
                    linksStarted = True;
                    print(pre + '          <div class="paper-links">');
                print(linkSeparator + pre + '            ' + format_media_link(key, value));
                linkSeparator = pre + '            &bull;\n';
            if linksStarted:
                print(pre + '          </div>');
        print(pre + '        </div>');
        separator = pre + '        <hr />\n';
    
    print(pre + '      </div>');
    print(pre + '    </div>');
    print(pre + '  </div>');
    print(pre + '</div>');


def print_keynote(keynoteID, htmlID, location, indent):
    global keynoteDetails;

    pre = generate_indent(indent);

    print(pre + '<div class="schedule-session col-xs-12">');
    print(pre + '  <div class="panel panel-default panel-session panel-highlight">');
    print(pre + '    <div class="panel-heading" role="tab" id="title-k-' + htmlID + '">');
    print(pre + '      <h4 class="panel-title">')
    print(pre + '        <a role="button" data-toggle="collapse" href="#k-' + htmlID + '" aria-expanded="true" aria-controls="k-' + htmlID + '">');
    if keynoteDetails[keynoteID]["Title"] != "":
        print(pre + '          ' + make_html_safe(keynoteDetails[keynoteID]["Title"]));
    else:
        print(pre + '          Title TBA');
    print(pre + '        </a>');
    print(pre + '      </h4>');
    print_location(location, indent + 6);
    print(pre + '    </div>');
    print(pre);

    print(pre + '    <div id="k-' + htmlID + '" class="panel-collapse panel-keynote collapse" role="tabpanel" aria-labelledby="title-k-' + htmlID + '">');
    print(pre + '      <div class="panel-body">');

    print(pre + '        <p>');
    if keynoteDetails[keynoteID]["Photo URL"] != "":
        print(pre + '          <img src="' + keynoteDetails[keynoteID]["Photo URL"] + '" alt="' + keynoteDetails[keynoteID]["Speaker"] + ' headshot" class="speaker-photo" />');
    if keynoteDetails[keynoteID]["Abstract"] != "":
        print(pre + '          <b>Abstract</b><br/>');
        print(pre + '          ' + make_html_safe(keynoteDetails[keynoteID]["Abstract"]).replace('\n', '<br/>'));
    else:
        print(pre + '          Abstract TBA');
    print(pre + '        </p>');
    linksStarted = False;
    linkSeparator = "";
    for key, value in keynoteDetails[keynoteID]['Links'].items():
        if value == "":
            continue;
        if not linksStarted:
            linksStarted = True;
            print(pre + '        <div class="keynote-links">');
        print(linkSeparator + pre + '          ' + format_media_link(key, value));
        linkSeparator = pre + '          &bull;\n';
    if linksStarted:
        print(pre + '        </div>');

    if keynoteDetails[keynoteID]["Bio"] != "":
        print(pre + '        <hr />');
        print(pre + '        <p>');
        print(pre + '          <b>Bio</b><br/>');
        print(pre + '          ' + make_html_safe(keynoteDetails[keynoteID]["Bio"]).replace('\n', '<br/>'));
        print(pre + '        </p>');

    
    print(pre + '      </div>');
    print(pre + '    </div>');
    print(pre + '  </div>');
    print(pre + '</div>');


def print_jump_menu(indent):
    global workshopDaysAbbr;
    global conferenceDates;
    global conferenceSchedulePage;

    pre = generate_indent(indent);

    # TODO: add support for "Jump to Today" link

    print(pre + '<div class="row schedule">');
    print(pre + '  <div class="col-xs-12 text-center">');
    print(pre + '    Jump to');
    print(pre + '    <a href="' + conferenceSchedulePage + '#workshops">' + make_html_safe(workshopDaysAbbr) + '</a>', end = '');

    numConferenceDays = 1;
    for day, date in conferenceDates.items():
        print(' |');
        print(pre + '    <a href="' + conferenceSchedulePage + '#day' + str(numConferenceDays) + '">' + make_html_safe(day) + '</a>', end = '');
        numConferenceDays = numConferenceDays + 1;
    print();

    print(pre + '    <br/><br/>');
    print(pre + '    <a href="#" onclick="expandSessionsOnAll(); return false;">Expand All</a> / ');
    print(pre + '    <a href="#" onclick="collapseSessionsOnAll(); return false;">Collapse All</a> Sessions');
    print(pre + '  </div>');
    print(pre + '</div>');
    print(pre);
    print(pre + '<hr />');
    print(pre);


def print_workshop_link(indent):
    global workshopDates;
    global workshopSchedulePage;

    pre = generate_indent(indent);

    print(pre + '<div class="col-xs-12">');
    print(pre + '  <h2><a href="' + workshopSchedulePage + '">', end='');
    separator = '';
    for day, date in workshopDates.items():
        print(separator + make_html_safe(day) + ', ' + make_html_safe(date), end='');
        separator = ' / ';
    print(': Workshops &amp; Tutorials</a></h2>');
    print(pre + '</div>');


def print_event(day, eventType, start, end, names, locations, notes, indent):
    global timeZone;
    global sessionHTMLIDs;
    global keynoteDetails;

    pre = generate_indent(indent);

    eventIndices = [];
    sessionNames = OrderedDict();
    
    for i in range(len(names)):
        if names[i][0:8].lower() == "session ":
            sessionNames[names[i][8:]] = locations[i];
        else:
            eventIndices.append(i);

    separator = "";

    typeFormat = "";
    if eventType.lower() in ["meal", "break"]:
        typeFormat = "secondary-event ";

    if len(sessionNames) > 0:
        print(pre + '<div class="schedule-time ' + typeFormat + 'col-xs-12">');
        print(pre + '  <h3>', end='');
        if day != "":
            print(make_html_safe(day) + ', ', end='');
        print(make_html_safe(start) + ' <span class="zone-name">' + make_html_safe(timeZone) + '</span> &ndash; ' + make_html_safe(end) + ' <span class="zone-name">' + make_html_safe(timeZone) + '</span></h3>');
        if notes != "":
            print(pre + '  <ul class="h5 session-notes">');
            for note in notes.split('\n'):
                print(pre + '    <li>' + html_accent_replacement(note) + '</li>');
            print(pre + '  </ul>');
        print(pre + '</div>');
        for session, location in sessionNames.items():
            print(pre);
            print_session(session, sessionHTMLIDs[session], location, int(12 / len(sessionNames)), indent);
        separator = pre + '\n';

    for i in eventIndices:
        print(separator, end='');
        separator = pre + '\n';
        print(pre + '<div class="schedule-time ' + typeFormat + 'col-xs-12">');
        print(pre + '  <h3>', end='');
        if day != "":
            print(day + ', ', end='');
        if eventType.lower() in ["keynote"]:
            print();
            print(pre + '    ' + make_html_safe(start) + ' <span class="zone-name">' + make_html_safe(timeZone) + '</span> &ndash; ' + make_html_safe(end) + ' <span class="zone-name">' + make_html_safe(timeZone) + '</span>:');
            print(pre + '    ' + html_accent_replacement(names[i]), end='');
            if names[i] in keynoteDetails.keys():
                if keynoteDetails[names[i]]["Speaker"] != "":
                    print(' by ' + make_html_safe(keynoteDetails[names[i]]["Speaker"]));
                    if keynoteDetails[names[i]]["Affiliation"] != "":
                      print(pre + '    <span class="affiliation">(' + make_html_safe(keynoteDetails[names[i]]["Affiliation"]) + ')</span>');
                else:
                    print();
            print(pre + '  </h3>');
            if notes != "":
                print(pre + '  <ul class="h5 session-notes">');
                for note in notes.split('\n'):
                    print(pre + '    <li>' + html_accent_replacement(note) + '</li>');
                print(pre + '  </ul>');
            print(pre + '</div>');
            print_keynote(names[i], keynoteHTMLIDs[names[i]], locations[i], indent);
        else:
            print(make_html_safe(start) + ' <span class="zone-name">' + make_html_safe(timeZone) + '</span> &ndash; ' + make_html_safe(end) + ' <span class="zone-name">' + make_html_safe(timeZone) + '</span>: ' + html_accent_replacement(names[i]) + '</h3>');
            print_location(locations[i], indent + 2);
            if notes != "":
                print(pre + '  <ul class="h5 session-notes">');
                for note in notes.split('\n'):
                    print(pre + '    <li>' + html_accent_replacement(note) + '</li>');
                print(pre + '  </ul>');
            print(pre + '</div>');


def print_all_events(indent):
    global eventDay;
    global eventType;
    global eventStart;
    global eventEnd;
    global eventNames;
    global eventLocations;
    global eventNotes;

    global workshopDates;
    global conferenceDates;

    global printJSInline;

    pre = generate_indent(indent);

    event = 0;

    # start with workshop message
    print(pre + '<a class="anchor" id="workshops"></a>');
    print(pre + '<div class="row schedule container-pad-top">');
    print_workshop_link(indent + 2);
    # print any events on the workshop days
    while event < len(eventDay) and eventDay[event] in workshopDates:
        print(pre);
        print_event(eventDay[event], eventType[event], eventStart[event], eventEnd[event], eventNames[event], eventLocations[event], eventNotes[event], indent + 2);
        event = event + 1;
    print(pre + '</div>');
    print(pre);
    print(pre + '<hr />');

    # for day, date in workshopDates.items():
    currentDay = 0;
    for day, date in conferenceDates.items():
        print(pre);
        print_jump_menu(indent);
        currentDay = currentDay + 1;
        print(pre + '<a class="anchor" id="day' + str(currentDay) + '"></a>');
        print(pre + '<div class="row schedule">');
        print(pre + '  <div class="col-xs-12">');
        print(pre + '    <h2>Day ' + str(currentDay) + ': ' + make_html_safe(day) + ', ' + make_html_safe(date) + '</h2>');
        print(pre + '  </div>');
        while event < len(eventDay) and eventDay[event] == day:
            print(pre);
            # don't print days for main conference
            print_event("", eventType[event], eventStart[event], eventEnd[event], eventNames[event], eventLocations[event], eventNotes[event], indent + 2);
            event = event + 1;
        print(pre + '</div>');
        print(pre);
        print(pre + '<hr />');
    
    print_jump_menu(indent);

    if printJSInline:
        print(pre);
        print(pre + "<script>");
        print(pre + "function findBootstrapEnvironment() {");
        print(pre + "    var envs = ['xs', 'sm', 'md', 'lg'];");
        print(pre);
        print(pre + "    var $el = $('<div>');");
        print(pre + "    $el.appendTo($('body'));");
        print(pre);
        print(pre + "    for (var i = envs.length - 1; i >= 0; i--) {");
        print(pre + "	var env = envs[i];");
        print(pre)
        print(pre + "	$el.addClass('hidden-'+env);");
        print(pre + "	if ($el.is(':hidden')) {");
        print(pre + "	    $el.remove();");
        print(pre + "	    return env;");
        print(pre + "	}");
        print(pre + "    }");
        print(pre + "}");
        print(pre);
        print(pre + "function collapseSessionsOnMobile() {");
        print(pre + "  if(findBootstrapEnvironment() == 'xs') {");
        print(pre + "    jQuery('div .panel-paper').collapse('hide');");
        print(pre + "    jQuery('div .panel-keynote').collapse('hide');");
        print(pre + "  }");
        print(pre + "}");
        print(pre);
        print(pre + "function collapseSessionsOnAll() {");
        print(pre + "  jQuery('div .panel-paper').collapse('hide');");
        print(pre + "  jQuery('div .panel-keynote').collapse('hide');");
        print(pre + "}");
        print(pre);
        print(pre + "function expandSessionsOnMobile() {");
        print(pre + "  if(findBootstrapEnvironment() == 'xs') {");
        print(pre + "    jQuery('div .panel-paper').collapse('show');");
        print(pre + "    jQuery('div .panel-keynote').collapse('show');");
        print(pre + "  }");
        print(pre + "}");
        print(pre);
        print(pre + "function expandSessionsOnAll() {");
        print(pre + "  jQuery('div .panel-paper').collapse('show');");
        print(pre + "  jQuery('div .panel-keynote').collapse('show');");
        print(pre + "}");
        print(pre + "</script>");


def generate_schedule(options):
    read_authors(options.authors);
    read_session(options.info, options.papers);
    read_keynotes(options.keynotes);
    read_schedule(options.schedule);
    read_links(options.links);
    print_all_events(printIndent);


if __name__ == "__main__":
    if sys.version_info[0] < 3:
        raise Exception("This script is not compatible with Python < 3.0.");

    parser = argparse.ArgumentParser();
    parser.add_argument('-s', '--schedule', type=str, default='schedule.csv');
    parser.add_argument('-i', '--info', type=str, default='session-info.csv');
    parser.add_argument('-p', '--papers', type=str, default='session-papers.csv');
    parser.add_argument('-a', '--authors', type=str, default='authors.csv');
    parser.add_argument('-l', '--links', type=str, default='paper-links.csv');
    parser.add_argument('-k', '--keynotes', type=str, default='keynotes.csv');
    options = parser.parse_args();

    generate_schedule(options);
