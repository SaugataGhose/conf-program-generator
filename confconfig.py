# CONFCONFIG.PY
# Author: Saugata Ghose (ghose at illinois dot edu)
# Last Updated: September 24, 2023
#
# settings to be customized for each conference
# for use with gensched.py

from collections import OrderedDict

workshopDates = OrderedDict([
        ('Saturday'  , 'October 28'),
        ('Sunday'    , 'October 29')
        ]);

workshopDaysAbbr = 'Sat/Sun';

workshopSchedulePage = 'program/workshops.php';

conferenceDates = OrderedDict([
        ('Monday'    , 'October 30'),
        ('Tuesday'   , 'October 31'),
        ('Wednesday' , 'November 1')
        ]);

conferenceSchedulePage = 'program/';

timeZone = 'EDT';

# in minutes
paperLength = 16;

mapPaths = {
        # 'Grand AB'  : 'test.png',
        # path used for all other locations
        '-default-' : 'attend/'
        };

printLocations = False;
printJSInline = False;

printIndent = 2;
