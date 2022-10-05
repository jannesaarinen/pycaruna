import os
import sys
import inspect
import json
import logging

from caruna_integration.config import config

currentdir = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))
parentdir = os.path.dirname(currentdir)
sys.path.insert(0, parentdir)

from datetime import date, datetime, timedelta
from pycaruna import Caruna, Resolution
from .insert_hourly_measurements import insert_hourly_measurements

debug = True
saveToFile = False

# Setup logging
logger = logging.getLogger('get_hourly_measurements')
ch = logging.StreamHandler(sys.stdout)
ch.setLevel(logging.INFO)
formatter = logging.Formatter('[%(asctime)s] [%(name)s] [%(levelname)s] %(message)s')
ch.setFormatter(formatter)
logger.addHandler(ch)
logger.setLevel(logging.INFO)

def make_min_hour_datetime(date):
    return datetime.combine(date, datetime.min.time())

def make_max_hour_datetime(date):
    return datetime.combine(date, datetime.max.time()).replace(microsecond=0)

def get_metering_point(client, username): 
    metering_points = client.get_metering_points(username)
    return metering_points[0]['meteringPoint']['meteringPointNumber']

def get_hourly_consumption(client, username, metering_point, start_time, end_time):
    if debug: logger.info('Getting hourly consumption: ' + start_time + ' - ' + end_time)

    consumption_hourly = client.get_consumption(username,
                                          metering_point,
                                         Resolution.HOURS, True,
                                         start_time, end_time)

    # Extract the relevant data, filter out days without values (usually the most recent datapoint)
    filtered_consumption_hourly = [item for item in consumption_hourly if item['values']]

    if debug: logger.info('Done.')
    if debug: logger.info('Mapping consumption next.')
    mapped_consumption_hourly = list(map(lambda item: {
        #'date': make_max_hour_datetime(
        #    date.today().replace(year=item['year'], month=item['month'], day=item['day'])).isoformat(),
        'datetime': item['timestamp'],
        'kwh_total':        item['values']['EL_ENERGY_CONSUMPTION#0']['value'] if 'EL_ENERGY_CONSUMPTION#0' in item['values'] else None,
        'kwh_night':        item['values']['EL_ENERGY_CONSUMPTION#2']['value'] if 'EL_ENERGY_CONSUMPTION#2' in item['values'] else None,
        'kwh_day':          item['values']['EL_ENERGY_CONSUMPTION#4']['value'] if 'EL_ENERGY_CONSUMPTION#4' in item['values'] else None,
        'kwh_night_winter': item['values']['EL_ENERGY_CONSUMPTION#5']['value'] if 'EL_ENERGY_CONSUMPTION#5' in item['values'] else None,
        'tariff':           'night_winter'                                     if 'EL_ENERGY_CONSUMPTION#5' in item['values'] else 'other_times'
    }, filtered_consumption_hourly))
    if debug: logger.info('Done.')
    if debug: logger.info('Inserting results to database.')
    insert_hourly_measurements(mapped_consumption_hourly)

    # Save to file
    if saveToFile:
        if debug: logger.info('Done.')
        if debug: logger.info('Writing json output to file.')
        with open(start_time.rpartition('T')[0] + '.' + end_time.rpartition('T')[0]  + "-hourly-output.json", "w", encoding="utf-8") as fh:
            fh.write(json.dumps(mapped_consumption_hourly))

    if debug: logger.info('All tasks done.')
    return 1

def get_hourly_measurements(days_to_load):
    # User and Password
    params = config(section='caruna')
    username = params['username']
    password = params['password']

    # Check if user and password provided
    if username is None or password is None:
        raise Exception('CARUNA_USERNAME and CARUNA_PASSWORD must be defined')

    # Create client & login
    if debug: logger.info('Creating client')
    client = Caruna(username, password)
    if debug: logger.info('Done.')
    if debug: logger.info('Logging in')
    client.login()
    if debug: logger.info('Done')

    # Get customer details and metering points so we can get the required identifiers
    customer = client.get_user_profile()
    username = customer['username']

    # Get metering point
    if debug: logger.info('Getting metering points.')
    metering_point = get_metering_point(client, username)
    if debug: logger.info('Metering_point: ' + metering_point)
    if debug: logger.info('Done')

    # Fetch data from midnight 00:00 7 days ago to 23:59 today
    start_time = make_min_hour_datetime(date.today() - timedelta(days=days_to_load)).astimezone().isoformat()
    end_time = make_max_hour_datetime(date.today() - timedelta(days=0)).astimezone().isoformat()

    get_hourly_consumption(client, username, metering_point, start_time, end_time)

    client.logout()