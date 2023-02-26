# pycaruna

Basic Python implementation for interfacing with Caruna Plus (sometimes called _Caruna+_). It supports only basic 
methods, but enough to extract electricity usage data for further processing.

Supported features:

* Get user profile information
* Get metering points ("assets")
* Get consumption data (daily/hourly)

This implementation is based on Kimmo Linna's pycaruna, which is used unmodified here. I've moved the licence and readme-files from the root to pycaruna-folder

  

# Configuration

All configuration is done on the /[caruna_integration/config.ini](/caruna_integration/config.ini). Be default most of the values are taken from environment variables, for that reason settings can be changed, either by provided a /.env -file or by directly changing the configuration on the [config.ini](/caruna_integration/config.ini)-file.

  

# Running modes

This integration can be run as python script or as dockerized container.

  

## Python script-mode

In this mode the script runs in endless single threaded loop until a key is pressed.

  

### Pre-requisites
The `assets/` directory has example Python programs illustrrating how to use the library.

The `resources/` directory has examples of API response structures.

Please note that the authentication procedure requires a lot of HTTP requests to be sent back and forth, so the 
script is relatively slow. It's best to store the token produced by it and reusing that instead of doing the 
authentication process all over again.

1. Valid Caruna+ user account

2. postgresql database with table energy_hourly (see [Database](#Database))

3. python version 3 or above

4. Configuration done in the config.ini or as .env-file

  

### Installing requirements

In order to run the script the requirements needs to be installed. This can be done with command `pip install -r requirements.txt`.

  

### Starting the script

The script can be started with command `python main.py`. Script runs with timeloop and fetches the data on the interval of seconds set in [config.ini](/caruna_integration/config.ini)->`job_interval`.

  

## Docker-mode

In this mode the script runs in an docker container.

  

### Pre-requisites

1. Valid Caruna+ user account

2. postgresql database with table energy_hourly (see [Database](#Database))

3. Docker

4. Configuration done in the config.ini or as .env-file

  

### Creating the docker image

Before the appliction is run as container, it needs the image to be created. This can be created with command `docker build -t jsdesign/caruna-integration:latest .`

  

### Running the docker image

The docker container can be run with command `docker run jsdesign/caruna-integration:latest`

  

# Database

  

This integration relies on postgresql database and it pushes the data in to the table `energy_hourly`.

  

## Create statement for energy_hourly

  

```CREATE TABLE IF NOT EXISTS public.energy_hourly

(

id bigint NOT NULL DEFAULT nextval('energy_hourly_id_seq'::regclass),

datetime timestamp with time zone,

kwh_total double precision,

kwh_night double precision,

kwh_day double precision,

kwh_night_winter double precision,

tariff character varying COLLATE pg_catalog."default",

CONSTRAINT energy_hourly_pkey PRIMARY KEY (id),

CONSTRAINT datetime UNIQUE (datetime)

)```