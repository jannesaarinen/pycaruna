#!/usr/bin/python
import psycopg2
import logging
import sys
import json

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
def carunaplus_insert_hourly_measurements(measurements):
    sql = """INSERT INTO carunaplus_energy_hourly(%s) VALUES(%s)  ON CONFLICT DO NOTHING RETURNING timestamp;"""
    logger.debug('insert sql=' + sql)
    conn = None
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
            if (len(measurement)< 4):
                logger.warn('measurement has less than 4 fields: ' + json.dumps(measurement))
            # elif (len(measurement) == 4): 
            #     cur.execute(sql_short, (measurement['timestamp'], measurement['totalConsumption'], measurement['invoicedConsumption'], measurement['temperature'],))
            # #     logger.debug('Executing sql_short')
            # else:
            #     cur.execute(sql_long, (measurement['timestamp'], measurement['totalConsumption'], measurement['invoicedConsumption'], measurement['totalFee'], measurement['distributionFee'], measurement['distributionBaseFee'],                        measurement['electricityTax'],                        measurement['valueAddedTax'],                       measurement['temperature']))
            #     logger.debug('Executing sql_long')
            else:
                fields = '"' + ('","'.join(map(str, measurement.keys()))) + '"'
                values = "'" + ("','".join(map(lambda s: s.replace("'",'"'), map(str, measurement.values())))) + "'"
                logger.debug('sql=' + sql % (fields, values))
                cur.execute(sql % (fields, values))
        # commit the changes to the database
        conn.commit()
        # close communication with the database
        cur.close()
    except (Exception, psycopg2.DatabaseError) as error:
        logger.error("psql error:" + str(error))
    finally:
        if conn is not None:
            conn.close()
