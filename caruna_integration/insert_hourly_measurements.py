#!/usr/bin/python
import psycopg2
import logging
import sys

from .config import config

# Setup logging
logger = logging.getLogger('insert_hourly_measurements')
ch = logging.StreamHandler(sys.stdout)
ch.setLevel(logging.INFO)
formatter = logging.Formatter('[%(asctime)s] [%(name)s] [%(levelname)s] %(message)s')
ch.setFormatter(formatter)
logger.addHandler(ch)
logger.setLevel(logging.INFO)

# Inserts hourly measurements in to database
def insert_hourly_measurements(measurements):
    """ insert a new hourly measurement to the table """
    sql = """INSERT INTO energy_hourly(datetime, kwh_total, kwh_night, kwh_day, kwh_night_winter, tariff)
             VALUES(%s, %s, %s, %s, %s, %s)  ON CONFLICT DO NOTHING RETURNING id;"""
    conn = None
    id = None
    try:
        # read database configuration
        params = config(section='postgresql')
        # connect to the PostgreSQL database
        conn = psycopg2.connect(**params)
        # create a new cursor
        cur = conn.cursor()
        # loop through the measurements
        for measurement in measurements:
            # execute the INSERT statement
            cur.execute(sql, (measurement['datetime'], measurement['kwh_total'], measurement['kwh_night'], measurement['kwh_day'], measurement['kwh_night_winter'], measurement['tariff'],))
        # commit the changes to the database
        conn.commit()
        # close communication with the database
        cur.close()
    except (Exception, psycopg2.DatabaseError) as error:
        logger.error("psql error:")
        logger.error(error)
    finally:
        if conn is not None:
            conn.close()
