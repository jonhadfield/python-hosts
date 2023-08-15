FROM python:latest

WORKDIR /usr/src/app

COPY test-requirements.txt ./

RUN python3 -m pip install --no-cache-dir -r test-requirements.txt

COPY . .

ENTRYPOINT /usr/local/bin/python