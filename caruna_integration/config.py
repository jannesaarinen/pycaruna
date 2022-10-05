#!/usr/bin/python
import configparser
import os
from dotenv import load_dotenv

# Load from .env file the environment variables
load_dotenv()

# Substitute env variables
class EnvInterpolation(configparser.BasicInterpolation):
    """Interpolation which expands environment variables in values."""

    def before_get(self, parser, section, option, value, defaults):
        value = super().before_get(parser, section, option, value, defaults)
        return os.path.expandvars(value)

def config(filename='./caruna_integration/config.ini', section='postgresql'):

    # create a parser
    parser = configparser.ConfigParser(interpolation=EnvInterpolation())
    # read config file
    parser.read(filename)

    # get section, default to postgresql
    db = {}
    if parser.has_section(section):
        params = parser.items(section)
        for param in params:
            db[param[0]] = param[1]
    else:
        raise Exception('Section {0} not found in the {1} file'.format(section, filename))

    return db