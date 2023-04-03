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
@tl.job(interval=timedelta(seconds=int(params['job_interval'])), initial_delay=timedelta(seconds=1))
def periodic_job():
    logger.info("Starting caruna_integration.get_hourly_measurements()")
    try:
        get_hourly_measurements.get_hourly_measurements(int(params['days_to_load']))
    except (Exception) as error:
        logger.error("caruna_integration.get_hourly_measurements() returned an error:")
        logger.error(error)
        pass
    logger.info("All done caruna_integration.get_hourly_measurements()")

tl.start(block=True)

# Run once in the beginning
tl.jobs[0].run()