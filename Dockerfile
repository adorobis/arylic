FROM python:slim

ARG VERSION

WORKDIR /usr/src/app

COPY requirements.txt ./

RUN pip install --no-cache-dir -r requirements.txt

# WORKDIR /usr/src/config

COPY config.ini ./

# WORKDIR /usr/src/app

COPY arylic.py ./

CMD [ "python", "./arylic.py" ]