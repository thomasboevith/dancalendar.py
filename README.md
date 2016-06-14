# dancalendar.py
Generate comprehensive calendars for Denmark.

Included are precisely computed astronomical events.

    dancalendar.py 0.1 --- generate comprehensive calendars for Denmark

    Usage:
      dancalendar.py [-y <year>] [--moons] [--sun] [--week] [--times] [-v ...]
      dancalendar.py (-h | --help)
      dancalendar.py --version

    Options:
      -y, --year <year>       Calendar year. (default: current year).
      -m, --moons             Include moon phases. [Default: False].
      -s, --sun               Include sun rise and sun set. [Default: False].
      -w, --week              Inlcude week numbers on Mondays. [Default: False].
      -t, --times             Include times of events. [Default: False].
      -h, --help              Show this screen.
      --version               Show version.
      -v                      Print info (-vv for debug info (debug)).

    Examples:
      dancalendar.py
      dancalendar.py -m -y 1975

    Copyright (C) 2016 Thomas Boevith

    License: GPLv3+: GNU GPL version 3 or later <http://gnu.org/licenses/gpl.html>.
    This is free software: you are free to change and redistribute it. There is NO
    WARRANTY, to the extent permitted by law.

## Example:

    >./dancalendar.py
    2016-01-01 Nytårsdag
    2016-01-06 Helligtrekonger
    2016-02-07 Fastelavn
    2016-02-14 Valentinsdag
    2016-03-08 Kvindernes internationale kampdag
    2016-03-20 Palmesøndag, Forårsjævndøgn
    2016-03-24 Skærtorsdag
    2016-03-25 Langfredag
    2016-03-27 Sommertid begynder, Påskedag
    2016-03-28 Anden påskedag
    2016-04-22 Store bededag
    2016-05-01 Arbejdernes internationale kampdag
    2016-05-04 Danmarks befrielsesaften
    2016-05-05 Danmarks befrielse, Lyse nætter begynder, Kristi himmelfartsdag
    2016-05-08 Mors dag
    2016-05-15 Pinsedag
    2016-05-16 Anden pinsedag
    2016-05-23 Sankthansaften
    2016-05-24 Sankthansdag
    2016-06-05 Grundlovsdag, Fars dag
    2016-06-21 Sommersolhverv
    2016-08-07 Lyse nætter slutter
    2016-09-22 Efterårsjævndøgn
    2016-10-30 Sommertid slutter
    2016-10-31 Mortensaften
    2016-11-11 Mortensdag
    2016-11-27 1. søndag i advent
    2016-12-04 2. søndag i advent
    2016-12-11 3. søndag i advent
    2016-12-13 Sankta Lucia
    2016-12-18 4. søndag i advent
    2016-12-21 Vintersolhverv
    2016-12-24 Juleaftensdag
    2016-12-25 Juledag
    2016-12-26 Anden juledag
    2016-12-31 Nytårsaftensdag
