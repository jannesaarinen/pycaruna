import os
import sys
import inspect
import json
import logging
from datetime import timedelta, date

from caruna_integration.config import config

currentdir = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))
parentdir = os.path.dirname(currentdir)
sys.path.insert(0, parentdir)

from datetime import date, timedelta
from pycaruna import Authenticator, CarunaPlus, TimeSpan
from .insert_hourly_measurements import carunaplus_insert_hourly_measurements

saveToFile = False

# Setup logging
logger = logging.getLogger('get_hourly_measurements')
ch = logging.StreamHandler(sys.stdout)
ch.setLevel(logging.INFO)
formatter = logging.Formatter('[%(asctime)s] [%(name)s] [%(levelname)s] %(message)s')
ch.setFormatter(formatter)
logger.addHandler(ch)
logger.setLevel(logging.INFO)


def get_metering_point(client, username): 
    metering_points = client.get_metering_points(username)
    return metering_points[0]['meteringPoint']['meteringPointNumber']

def get_hourly_measurements(days_to_load, fixed_dates=None):
    # User and Password
    params = config(section='caruna')
    username = params['username']
    password = params['password']

    # Check if user and password provided
    if username is None or password is None:
        raise Exception('CARUNA_USERNAME and CARUNA_PASSWORD must be defined')


    # Authenticate using your e-mail and password. This will ultimately return an object containing a token (used for
    # Caruna Plus API interaction) and a user object which among other things contain your customer IDs (needed when
    # interacting with the Caruna Plus API). See resources/login_result.json for an example of the JSON structure.
    #
    # The token is valid for 60 minutes (as of this writing), so it should be enough to authenticate once and then
    # reuse the token for all further requests you may want to make.
    authenticator = Authenticator(username, password)
    logger.info('Logging in')
    login_result = authenticator.login()

    token = login_result['token']
    customer_id = login_result['user']['ownCustomerNumbers'][0]

    if token is None or customer_id is None:
        raise Exception('Caruna plus authentication failed.')

    logger.debug('login_result=' + json.dumps(login_result))

    # Create client
    logger.info('Creating client')
    client = CarunaPlus(token)

    # Get metering points, also known as "assets". Each asset has an "assetId" which is needed e.g. to
    # retrieve energy consumption information for a metering point type asset.
    logger.info('Getting metering points')
    metering_points = client.get_assets(customer_id)
    logger.debug('metering_points=' + json.dumps(metering_points))

    # Get daily usage for the month of January 2023 for the first metering point. Yes, this means TimeSpan.MONTHLY. If
    # you want hourly usage, use TimeSpan.DAILY.
    asset_id = metering_points[1]['assetId']
    logger.debug('asset_id=' + str(asset_id))

    # d = date.fromisoformat('2015-12-31')
    # while d < date.today() - timedelta(days=1):

    
    if fixed_dates == None:
        # Loop through all dates to load the hourly consumption, default operation mode
        for x in range(days_to_load):
            d = date.today() - timedelta(days=x+1) # date which consumption is queried, starting from yesterday
            logger.info('Proccesing date '+ d.isoformat() + ', getting consumption from Caruna+')
            measurements = client.get_energy(customer_id, asset_id, TimeSpan.DAILY, d.year, d.month, d.day)
            logger.debug('energy=' + json.dumps(measurements))
            logger.info('Inserting to database')
            carunaplus_insert_hourly_measurements(measurements)
            logger.info('Done processing date '+ d.isoformat())
            d = d + timedelta(days=1) # increment one day
        return 1
    else:
        for fixed_date in fixed_dates:
            # process a fixed date
            d = date.fromisoformat(fixed_date) # date which consumption is queried, starting from yesterday
            logger.info('Proccesing date '+ d.isoformat() + ', getting consumption from Caruna+')
            measurements = client.get_energy(customer_id, asset_id, TimeSpan.DAILY, d.year, d.month, d.day)
            logger.debug('energy=' + json.dumps(measurements))
            logger.info('Inserting to database')
            carunaplus_insert_hourly_measurements(measurements)
            logger.info('Done processing date '+ d.isoformat())
        return 1
