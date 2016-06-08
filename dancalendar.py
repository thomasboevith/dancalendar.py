#!/usr/bin/env python2
# -*- coding: utf-8 -*-
import ephem
from dateutil.relativedelta import relativedelta as rd
from dateutil.relativedelta import MO, TU, WE, TH, FR, SA, SU
from datetime import date, datetime
import docopt
import holidays
import logging
import os
import sys
import time

version = '0.1'

__doc__ = """
dancalendar.py {version} --- generate comprehensive calendars for Denmark

Usage:
  {filename} [-y <year>] [-v ...]
  {filename} (-h | --help)
  {filename} --version

Options:
  -y, --year <year>       Calendar year. (default: current year).
  -h, --help              Show this screen.
  --version               Show version.
  -v                      Print info (-vv for debug info (debug)).

Examples:
  {filename}

Copyright (C) 2016 Thomas Boevith

License: GPLv3+: GNU GPL version 3 or later <http://gnu.org/licenses/gpl.html>.
This is free software: you are free to change and redistribute it. There is NO
WARRANTY, to the extent permitted by law.
""".format(filename=os.path.basename(__file__), version=version)


if __name__ == '__main__':
    start_time = time.time()
    args = docopt.docopt(__doc__, version=str(version))

    log = logging.getLogger(os.path.basename(__file__))
    formatstr = '%(asctime)-15s %(name)-17s %(levelname)-5s %(message)s'
    if args['-v'] >= 2:
        logging.basicConfig(level=logging.DEBUG, format=formatstr)
    elif args['-v'] == 1:
        logging.basicConfig(level=logging.INFO, format=formatstr)
    else:
        logging.basicConfig(level=logging.WARNING, format=formatstr)

    log.debug('%s started' % os.path.basename(__file__))
    log.debug('docopt args=%s' % str(args).replace('\n', ''))

    if args['--year'] is None:
        year = datetime.now().year
    else:
        year = int(args['--year'])

    class ExtendedDenmark(holidays.Denmark):
        def _populate(self, year):
            # Populate the holiday list with the default DK holidays
            holidays.Denmark._populate(self, year)
            # Add other Danish holidays and events
            self[date(year, 5, 1) + rd(weekday=SU(+2))] = 'Mors dag'
            self[date(year, 6, 5)] = 'Fars dag'
            self[date(year, 6, 5)] = 'Grundlovsdag'
            self[date(year, 12, 24)] = 'Juleaftensdag'
            self[date(year, 12, 31)] = 'Nytårsaftensdag'

            observer = ephem.city('Copenhagen')
            spring_equinox = ephem.next_equinox(str(year))
            summer_solstice = ephem.next_solstice(spring_equinox)
            fall_equinox = ephem.next_equinox(summer_solstice)
            winter_solstice = ephem.next_solstice(fall_equinox)
            self[spring_equinox.datetime()] = 'Forårsjævndøgn'
            self[summer_solstice.datetime()] = 'Sommersolhverv'
            self[fall_equinox.datetime()] = 'Efterårsjævndøgn'
            self[winter_solstice.datetime()] = 'Vintersolhverv'

    dk_holidays = ExtendedDenmark(years=year)
    for date, name in sorted(dk_holidays.items()):
        print('%s %s' % (date, name))

    log.debug('Processing time={0:.2f} s'.format(time.time() - start_time))
    log.debug('%s ended' % os.path.basename(__file__))
