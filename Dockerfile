FROM python:3.9.5-slim
RUN apt-get update \
    && apt-get -y install libpq-dev gcc \
    && pip install psycopg2
#RUN apt-get -y install libxml2 libxslt 
RUN apt-get -y install libxml2 
RUN apt-get -y install python3-lxml
RUN apt-get -y install libxml2-dev libxslt-dev python3-dev
RUN apt-get -y install libz-dev
ADD requirements.txt /
RUN pip install lxml
RUN pip install -r requirements.txt
ADD caruna_integration/*.py /caruna_integration/
ADD pycaruna/*.py /pycaruna/
ADD main.py /
ADD caruna_integration/config.ini /caruna_integration/
ADD .env /
ADD start.sh /
# CMD [ "python", "./main.py" ]
ENTRYPOINT [ "/start.sh" ]
