# weather.py
This command-line tool retrieves weather forecasts for the US from the National Weather Service. Regular and hourly weather forecasts are supported. Alerts are displayed if there are any. A forecast location can be specified; it defaults to a location obtained from the IP address.

## Usage

This is a command-line utility. It is usually called with no command-line arguments. This is the command for Linux and macOS:

```
./weather.py
```

On Windows the command is:

```
python .\weather.py
```

This call results in weather alerts (if any) and a forecast:
```
Heat Advisory issued September 12 at 2:10AM PDT until September 12 at 9:00PM PDT by NWS San Diego CA
====================================================================================================
* WHAT...Temperatures 97 to 103. * WHERE...San Bernardino and Riverside County Valleys-The Inland Empire.
* WHEN...Until 9 PM PDT Sunday. * IMPACTS...Hot conditions may cause heat illness.
Drink plenty of fluids, stay in an air-conditioned room, stay out of the sun, and check up on relatives and neighbors.
Young children and pets should never be left unattended in vehicles under any circumstances. When possible reschedule
strenuous activities to early morning or evening.

Forecast for Jurupa Valley, CA
==============================

Today
=====
Sunny, with a high near 99. West wind 0 to 15 mph, with gusts as high as 25 mph.

Tonight
=======
Clear, with a low around 65. West wind 0 to 15 mph, with gusts as high as 25 mph.

Monday
======
Sunny, with a high near 94. Southwest wind 0 to 15 mph, with gusts as high as 25 mph.

Monday Night
============
Clear, with a low around 62. Southwest wind 0 to 15 mph, with gusts as high as 25 mph.

Tuesday
=======
Sunny, with a high near 90. Southwest wind 0 to 15 mph, with gusts as high as 25 mph.

Tuesday Night
=============
Mostly clear, with a low around 61.

Wednesday
=========
Sunny, with a high near 88.

Wednesday Night
===============
Mostly clear, with a low around 59.

Thursday
========
Sunny, with a high near 86.

Thursday Night
==============
Mostly clear, with a low around 59.

Friday
======
Sunny, with a high near 86.

Friday Night
============
Mostly clear, with a low around 60.

Saturday
========
Sunny, with a high near 86.

Saturday Night
==============
Mostly clear, with a low around 60.
```
Several command line options are available:

```
usage: weather.py [-h] [--latitude LATITUDE] [--longitude LONGITUDE] [--hourly]

optional arguments:
  -h, --help            show this help message and exit
  --latitude LATITUDE   Latitude for forecast.
  --longitude LONGITUDE
                        Longitude for forecast.
  --hourly              Request hourly forecast.
```
The `--hourly` option requests an hourly forecast for the next 6 days or so. The `--latitude` and `--longitude` options can be used to specify a forecast location.

## Dependencies

This package requires Phyton 3 and only one additional package `requests` is needed. This package can be installed on Debian distributions like Ubuntu with the command `sudo apt install python3-requests` and on other platforms with the command

```
pip install requests
```

If necessary, `pip3` should be called instead of `pip` to avoid accidentally installing the Python 2 package.

## Errors

An error is expected for a forecast location outside the USA. This is an example:

```
./weather.py --lat 89.99999 --lon 0
*** Error #404. ***
{
    "correlationId": "1976c6",
    "title": "Data Unavailable For Requested Point",
    "type": "https://api.weather.gov/problems/InvalidPoint",
    "status": 404,
    "detail": "Unable to provide data for requested point 90,0",
    "instance": "https://api.weather.gov/requests/1976c6"
}
```

The location given is the North Pole for which the National Weather Service does not provide forecasts.
