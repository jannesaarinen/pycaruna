import sys
import logging
import json
from datetime import timedelta, date

from caruna_integration import get_hourly_measurements
from caruna_integration.config import config

# Get configuration
params = config(section='main')

# Setup logging
logger = logging.getLogger('main')
ch = logging.StreamHandler(sys.stdout)
ch.setLevel(logging.DEBUG)
formatter = logging.Formatter('[%(asctime)s] [%(name)s] [%(levelname)s] %(message)s')
ch.setFormatter(formatter)
logger.addHandler(ch)
logger.setLevel(logging.DEBUG)

# load days to process from file
with open('dates.csv') as f:
    dates = f.read().splitlines()

try:
    get_hourly_measurements.get_hourly_measurements(int(params['days_to_load']), dates)
except (Exception) as error:
    logger.error("caruna_integration.get_hourly_measurements() returned an error:")
    logger.error(error)
    pass