FROM python:3-alpine
ADD requirements.txt /
RUN pip install -r requirements.txt
ADD caruna_integration/config.ini /caruna_integration/
ADD caruna_integration/*.py /caruna_integration/
ADD pycaruna/*.py /pycaruna/
ADD main.py /
ADD .env /
CMD [ "python", "./main.py" ]