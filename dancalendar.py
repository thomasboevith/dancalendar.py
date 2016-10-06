#!/usr/bin/env python2
# -*- coding: utf-8 -*-
import ephem
from dateutil.relativedelta import relativedelta as rd
from dateutil.relativedelta import MO, TU, WE, TH, FR, SA, SU
from dateutil.easter import easter
import datetime
import docopt
import holidays
import logging
import os
import pytz
import sys
import time

version = '0.2'

__doc__ = """
dancalendar.py {version} --- generate comprehensive calendars for Denmark

Usage:
  {filename} [-y <year>] [--moon] [--sun] [--week] [--time] [--all]
             [--outformat <name>] [-v ...]
  {filename} (-h | --help)
  {filename} --version

Options:
  -y, --year <year>       Calendar year(s). (year, year1-year2, year1,year2,year3) (default: current year).
  -m, --moon              Include moon phases. [Default: False].
  -s, --sun               Include sun rise and sun set. [Default: False].
  -w, --week              Inlcude week numbers on Mondays. [Default: False].
  -t, --time              Include time of events. [Default: False].
  -a, --all               Include all extra information. [Default: False].
  -o, --outformat <name>  Output format (symbols, text). [Default: text].
  -h, --help              Show this screen.
  --version               Show version.
  -v                      Print info (-vv for debug info (debug)).

Examples:
  {filename}
  {filename} -a -y 1975

Copyright (C) 2016 Thomas Boevith

License: GPLv3+: GNU GPL version 3 or later <http://gnu.org/licenses/gpl.html>.
This is free software: you are free to change and redistribute it. There is NO
WARRANTY, to the extent permitted by law.
""".format(filename=os.path.basename(__file__), version=version)


def utc2localtime(utc_datetime, timezone='Europe/Copenhagen',
                  format='datetime'):
    """Convert UTC datetime to local timezone datetime"""
    tz = pytz.timezone(timezone)
    utc_dt = datetime.datetime(utc_datetime.year, utc_datetime.month,
                               utc_datetime.day, utc_datetime.hour,
                               utc_datetime.minute, utc_datetime.second,
                               utc_datetime.microsecond,
                               tzinfo=pytz.utc)
    if format == 'datetime':
        return(utc_dt.astimezone(tz))
    elif format == 'hhmm':
        return('%02i:%02i' % (utc_dt.astimezone(tz).hour,
                              utc_dt.astimezone(tz).minute))


def bright_night(ephemdate, city='Copenhagen'):
    """Determine if the upcoming night a bright night"""
    cph = ephem.city(city)
    cph.horizon = '-18'  # Astronomical twillight
    cph.date = ephemdate
    try:
        # Twillight defined by center of the sun
        cph.next_setting(ephem.Sun(), use_center=True)
        return False
    except:
        return True


def bright_nights(year, city='Copenhagen'):
    """Find beginning and end of bright nights"""
    start = ephem.Date((year, 1, 1, 0))
    brightnights_period = []
    brightnights = False
    for i in range(366):
        d = ephem.date(start + (24*ephem.hour*i))
        b = bright_night(d, city=city)
        if (b is True) and (brightnights is False):
            brightnights = True
            brightnights_period.append(d.datetime())
        if (b is False) and (brightnights is True):
            brightnights = False
            brightnights_period.append(d.datetime())

    return brightnights_period


class MoonPhases:
    """Moon phase date times"""
    def moon_phase_names(self, moon_phase, outformat=None):
        if outformat == 'text':
            text_names = {'new_moon': 'Nymåne',
                          'first_quarter': 'Første kvarter',
                          'full_moon': 'Fuldmåne',
                          'last_quarter': 'Sidste kvarter'
                          }
            return text_names[moon_phase]
        elif outformat == 'symbols':
            symbols = {'new_moon': '🌑',
                       'first_quarter': '🌓',
                       'full_moon': '🌕',
                       'last_quarter': '🌗'
                       }
            return symbols[moon_phase]

    def __init__(self, year, timezone='Europe/Copenhagen',
                 outformat='text'):
        """Compute moon phases for a whole year"""
        # Backtrack and look ahead to be sure to catch moons around newyear
        start_date = ephem.Date((year-1, 9, 1))
        end_date = ephem.Date((year+1, 3, 1))
        self.moon_phases = {}
        new_moon = ephem.next_new_moon(start_date)
        first_quarter = ephem.next_first_quarter_moon(start_date)
        full_moon = ephem.next_full_moon(start_date)
        last_quarter = ephem.next_last_quarter_moon(start_date)
        while True:
            local_new_moon = utc2localtime(new_moon.datetime())
            local_first_quarter = utc2localtime(first_quarter.datetime())
            local_full_moon = utc2localtime(full_moon.datetime())
            local_last_quarter = utc2localtime(last_quarter.datetime())
            if local_new_moon.year == year:
                self.moon_phases[local_new_moon] = \
                    self.moon_phase_names('new_moon', outformat)
            if local_first_quarter.year == year:
                self.moon_phases[local_first_quarter] = \
                    self.moon_phase_names('first_quarter', outformat)
            if local_full_moon.year == year:
                self.moon_phases[local_full_moon] = \
                    self.moon_phase_names('full_moon', outformat)
            if local_last_quarter.year == year:
                self.moon_phases[local_last_quarter] = \
                    self.moon_phase_names('last_quarter', outformat)

            new_moon = ephem.next_new_moon(new_moon)
            first_quarter = ephem.next_first_quarter_moon(first_quarter)
            full_moon = ephem.next_full_moon(full_moon)
            last_quarter = ephem.next_last_quarter_moon(last_quarter)
            if (new_moon > end_date) and (first_quarter > end_date) and \
               (full_moon > end_date) and (last_quarter > end_date):
                break


class SunRiseSunSet:
    """Sun rise and sun set datetimes for every week"""
    def __init__(self, year, observer, sun=False, week=False):
        self.sun = sun
        self.week = week
        self.sun_rise_sun_set = {}
        start = ephem.Date((year, 1, 1, 0))
        for i in range(367):
            d = ephem.date(start + (24*ephem.hour*i))
            if d.datetime().weekday() == 0:  # If monday
                observer.date = d
                sunrise = observer.next_rising(ephem.Sun())
                sunset = observer.next_setting(ephem.Sun())
                weeknumber = d.datetime().strftime("%U")
                if d.datetime().year == year:
                    if self.week and self.sun:
                        self.sun_rise_sun_set[d.datetime()] \
                            = 'Uge %s, sol %s-%s' % (weeknumber,
                              utc2localtime(sunrise.datetime(), format='hhmm'),
                               utc2localtime(sunset.datetime(), format='hhmm'))
                    elif self.week and not self.sun:
                        self.sun_rise_sun_set[d.datetime()] = 'Uge %s' \
                                                              % (weeknumber)
                    elif not self.week and self.sun:
                        self.sun_rise_sun_set[d.datetime()] = 'Sol %s-%s' \
                           % (utc2localtime(sunrise.datetime(), format='hhmm'),
                               utc2localtime(sunset.datetime(), format='hhmm'))


def extended_denmark(years=False, sun=False, moon=False, week=False,
                     time=False, outformat='text'):
    """Extends the official public holidays of Denmark"""

    # Populate the holiday list with the default DK holidays
    holidays_dk = holidays.Denmark(years=years)

    # Extend with other dates
    for year in years:
        if sun or week:
            # Sun rise and sunsets
            cph = ephem.city('Copenhagen')
            sun_rise_sun_set = SunRiseSunSet(year, cph)
            for key in sorted(sun_rise_sun_set.sun_rise_sun_set):
                holidays_dk.append({key:
                                       sun_rise_sun_set.sun_rise_sun_set[key]})

        if moon:
            # Moon phases
            moon_phases = MoonPhases(year, outformat=outformat)
            for key in sorted(moon_phases.moon_phases):
                holidays_dk.append({key: moon_phases.moon_phases[key]})

        # Equinoxes and solstices
        spring_equinox = ephem.next_equinox(str(year))
        summer_solstice = ephem.next_solstice(spring_equinox)
        fall_equinox = ephem.next_equinox(summer_solstice)
        winter_solstice = ephem.next_solstice(fall_equinox)
        # Bright nights, nights when sun is not under 18 deg below horizon
        brightnights = bright_nights(year)
        holidays_dk.append({brightnights[0]: 'Lyse nætter begynder'})
        holidays_dk.append({brightnights[1]: 'Lyse nætter slutter'})

        if time:
            holidays_dk.append({utc2localtime(spring_equinox.datetime()):
                           'Forårsjævndøgn %s' %
                       utc2localtime(spring_equinox.datetime(),
                                     format='hhmm')})
            holidays_dk.append({utc2localtime(summer_solstice.datetime()):
                           'Sommersolhverv %s' %
                       utc2localtime(summer_solstice.datetime(),
                                     format='hhmm')})
            holidays_dk.append({utc2localtime(fall_equinox.datetime()):
                           'Efterårsjævndøgn %s' %
                       utc2localtime(fall_equinox.datetime(),
                                     format='hhmm')})
            holidays_dk.append({utc2localtime(winter_solstice.datetime()):
                           'Vintersolhverv %s' %
                       utc2localtime(winter_solstice.datetime(),
                                     format='hhmm')})
        else:
            holidays_dk.append({utc2localtime(spring_equinox.datetime()): 'Forårsjævndøgn'})
            holidays_dk.append({utc2localtime(summer_solstice.datetime()): 'Sommersolhverv'})
            holidays_dk.append({utc2localtime(fall_equinox.datetime()): 'Efterårsjævndøgn'})
            holidays_dk.append({utc2localtime(winter_solstice.datetime()): 'Vintersolhverv'})

        # Add other Danish holidays and events
        holidays_dk.append({datetime.date(year, 1, 6): 'Helligtrekonger'})
        holidays_dk.append({datetime.date(year, 2, 14): 'Valentinsdag'})
        holidays_dk.append({datetime.date(year, 3, 8): 'Kvindernes internationale kampdag'})
        holidays_dk.append({easter(year) + rd(weekday=SU(-8)): 'Fastelavn'})
        holidays_dk.append({easter(year) + rd(weekday=SU(-2)): 'Palmesøndag'})
        holidays_dk.append({datetime.date(year, 4, 1) + rd(weekday=SU(-1)): 'Sommertid begynder'})
        holidays_dk.append({datetime.date(year, 5, 1) + rd(weekday=SU(+2)): 'Mors dag'})
        holidays_dk.append({datetime.date(year, 5, 1): 'Arbejdernes internationale kampdag'})
        holidays_dk.append({datetime.date(year, 5, 23): 'Sankthansaften'})
        holidays_dk.append({datetime.date(year, 5, 24): 'Sankthansdag'})
        holidays_dk.append({datetime.date(year, 5, 4): 'Danmarks befrielsesaften'})
        holidays_dk.append({datetime.date(year, 5, 5): 'Danmarks befrielse'})
        holidays_dk.append({datetime.date(year, 6, 5): 'Fars dag'})
        holidays_dk.append({datetime.date(year, 6, 5): 'Grundlovsdag'})
        holidays_dk.append({datetime.date(year, 10, 31): 'Mortensaften'})
        holidays_dk.append({datetime.date(year, 11, 11): 'Mortensdag'})
        holidays_dk.append({datetime.date(year, 11, 1) + rd(weekday=SU(-1)): 'Sommertid slutter'})
        holidays_dk.append({datetime.date(year, 12, 13): 'Sankta Lucia'})
        for i in range(4):
            holidays_dk.append({datetime.date(year, 12, 24) +
                                rd(weekday=SU(-(i+1))):
                                    '%s. søndag i advent' % abs(4-i)})

        holidays_dk.append({datetime.date(year, 12, 24): 'Juleaftensdag'})
        holidays_dk.append({datetime.date(year, 12, 31): 'Nytårsaftensdag'})

    return holidays_dk

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

    # Parse years
    if args['--year'] is None:
        years = [datetime.datetime.now().year]
    elif '-' in args['--year']:
        yearlist = map(int, args['--year'].strip().split('-'))
        years = range(yearlist[0], yearlist[1]+1)
    elif ',' in args['--year']:
        years = map(int, args['--year'].strip().split(','))
    else:
        years = int(args['--year'])

    if args['--all']:
        args['--moon'] = args['--sun'] = args['--week'] = args['--time'] = True

    for year in years:
        if (year < 1) or (year > 9999):
            message = 'Specify specify years between year 1 and 9999'
            log.debug(message)
            print(message)
            sys.exit(1)

    dk_holidays = extended_denmark(years=years, sun=args['--sun'],
                                   week=args['--week'], moon=args['--moon'],
                                   time=args['--time'],
                                   outformat=args['--outformat'])

    for date, name in sorted(dk_holidays.items()):
        print('%s %s' % (date, name))

    log.debug('Processing time={0:.2f} s'.format(time.time() - start_time))
    log.debug('%s ended' % os.path.basename(__file__))
