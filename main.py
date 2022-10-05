import time
import sys
import logging

from caruna_integration import get_hourly_measurements
from caruna_integration.config import config

from timeloop import Timeloop
from datetime import timedelta

# Get configuration
params = config(section='main')

# Initialize new timeloop object
tl = Timeloop()

# Setup logging
logger = logging.getLogger('main')
ch = logging.StreamHandler(sys.stdout)
ch.setLevel(logging.INFO)
formatter = logging.Formatter('[%(asctime)s] [%(name)s] [%(levelname)s] %(message)s')
ch.setFormatter(formatter)
logger.addHandler(ch)
logger.setLevel(logging.INFO)

# Timeloop function
@tl.job(interval=timedelta(seconds=int(params['job_interval'])))
def periodic_job():
    logger.info("{}: starting caruna_integration.get_hourly_measurements()".format(time.ctime()))
    try:
        get_hourly_measurements.get_hourly_measurements(int(params['job_interval']))
    except (Exception) as error:
        logger.error("caruna_integration.get_hourly_measurements() returned an error:")
        logger.error(error)
        pass

tl.start(block=True)