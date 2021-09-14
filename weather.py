#!/usr/bin/env python3
import os, requests, shelve, sys, time

#
# Simple command-line tool that obtains forecast from National Weather Service.
#
# API used: https://www.weather.gov/documentation/services-web-api
#

if sys.platform == 'win32':
    CACHE_DIRECTORY = os.path.join(os.path.expanduser('~'),
                                   'AppData', 'Local', 'Weather')
else:
    CACHE_DIRECTORY = os.path.join(os.path.expanduser('~'),
                                   '.cache', 'weather')

# create CACHE_DIRECTORY if needed

if not os.path.exists(CACHE_DIRECTORY):
    os.makedirs(CACHE_DIRECTORY)

cache = shelve.open(os.path.join(CACHE_DIRECTORY, 'nws_api.cache'))

CACHE_GRID_EXPIRATION     = 24 * 3600  #  1 day
CACHE_ALERT_EXPIRATION    = 5  * 60    #  5 minutes
CACHE_FORECAST_EXPIRATION = 15 * 60    # 15 minutes
CACHE_LOCATION_EXPIRATION = 3600       #  1 hour
TOO_MANY_API_CALLS_DELAY  = 60         #  1 minute

AGENT  = '(weather.py, your_email_here@hotmail.com)'
ACCEPT = 'application/geo+json'

#
# Get our location estimate based on IP address; returns None on error.
#
def getLocation():
    url = 'http://ip-api.com/json/?fields=1097945'
    result = getUrlWithCache(url, CACHE_LOCATION_EXPIRATION,
                             {'Content-type':'application/json'})
    if result is not None and result['status'] == 'success':
        return result

#
# Get the NWS grid for a particular location; returns None on error.
#
def getGrid(latitude, longitude):
    url = f'https://api.weather.gov/points/{latitude},{longitude}'
    return getUrlWithCache(url, CACHE_GRID_EXPIRATION)

#
# Get a forecast; the urls for forecasts are obtained with getGrid().
#
def getUrlWithCache(url, cache_expiration=CACHE_FORECAST_EXPIRATION,
                    headers={'User-Agent':AGENT, 'Accept':ACCEPT}):
    tim = time.time()
    if not url in cache or cache[url][0] < tim - cache_expiration:
        delay = TOO_MANY_API_CALLS_DELAY
        while True:
            response = requests.get(url, headers=headers)
            if response.status_code == requests.codes.too_many:
                time.sleep(delay)
                delay *= 2
                tim = time.time()
            else:
                break
        if response.status_code == requests.codes.ok:
            cache[url] = (tim, response.json())
        else:
            print (f"*** Error #{response.status_code} for url '{url}'. ***")
            print (response.text)
            return None
    return cache[url][1]


#
# Main Program, downloads and prints forecast for our location or a location
# specified with latitude/longitude on command-line.
#
if __name__ == '__main__':
    import argparse

    # Command-line parameter checks.
    def latitude(lat):
        try:
            lat = float(lat)
            if lat > -90 and lat < 90:
                return lat
        except:
            pass
        raise ValueError('Latitude must be between -90 and 90 degrees.')
    def longitude(lon):
        try:
            lon = float(lon)
            if lon >= -180.0 and lon < 180:
                return lon
        except:
            pass
        raise ValueError('Longitude must be between -180 and 180 degrees.')

    # Print a title, an underlined line of text.
    def printTitle(title, newLine=True):
        print(title)
        print('=' * len(title))
        if newLine:
            print()    
    #
    # Parse command-line.
    #
    parser = argparse.ArgumentParser()
    parser.add_argument("--latitude", type=latitude,
                        help="Latitude for forecast.")
    parser.add_argument("--longitude", type=longitude,
                        help="Longitude for forecast.")
    parser.add_argument("--hourly", action="store_true",
                        help="Request hourly forecast.")
    args = parser.parse_args()

    #
    # Get forecast location if not given in command-line.
    #
    if args.longitude is None or args.latitude is None:
        location = getLocation() # get location estimate based on IP address
        args.latitude = float(location['lat']) if location else 37.7491191
        args.longitude = float(location['lon']) if location else -119.588735

    #
    # Get NWS grid. It contains urls for alerts and forecasts
    #
    grid = getGrid(args.latitude, args.longitude)

    if not grid:
        # Usually fails due to a location outside the US
        sys.exit(1)

    #
    # Get city and state the forecast is for.
    #
    city = grid['properties']['relativeLocation']['properties']['city']
    state = grid['properties']['relativeLocation']['properties']['state']

    #
    # Get urls for alerts and the forecast and hourly forecast.
    #
    forecastUrl = grid['properties']['forecast']
    hourlyForecastUrl = grid['properties']['forecastHourly']
    zoneId = grid['properties']['forecastZone'].split('/')[-1]
    alertUrl = f"https://api.weather.gov/alerts/active/zone/{zoneId}"

    #
    # First of all, download and report alerts if there are any.
    #
    alerts = getUrlWithCache(alertUrl, CACHE_ALERT_EXPIRATION)
    for alert in alerts['features']:
        properties = alert['properties']
        printTitle(' '.join(properties['headline'].split()),
                   newLine=False)
        if 'description' in properties and properties['description'] is not None:
            print(properties['description'].strip())
        if 'instruction' in properties and properties['instruction'] is not None:
            print(properties['instruction'].strip())
        print()

    #
    # Download and print forecast.
    #
    if not args.hourly:
        forecast = getUrlWithCache(forecastUrl)
        if forecast is None: sys.exit(1)
        printTitle(f'Forecast for {city}, {state}')
        for dayNight in forecast['properties']['periods']:
            printTitle(dayNight['name'], newLine=False)
            print(dayNight['detailedForecast'])
            print()
    else:
        hourlyForecast = getUrlWithCache(hourlyForecastUrl)
        if hourlyForecast is None: sys.exit(1)
        printTitle(f'Hourly Forecast for {city}, {state}')
        for hour in hourlyForecast['properties']['periods']:
            startTime = hour['startTime']
            day = f'{int(startTime[5:7])}/{int(startTime[8:10])}'
            time = int(startTime[11:13])
            time = 'midnight' if time == 0 else f'{time} AM' if time < 12 else \
                   'noon' if time == 12  else f'{time-12} PM'
            printTitle(f'{day}, {time}', newLine=False)
            print(f"{hour['shortForecast']}, "
                  f"{hour['temperature']}°{hour['temperatureUnit']}, "
                  f"Wind {hour['windSpeed']} {hour['windDirection']}.")
            print()
