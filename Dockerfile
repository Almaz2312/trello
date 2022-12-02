FROM python:3.10.6
ENV PYTHONBUFFERED=1

WORKDIR /trello

COPY ./requirements.txt ./requirements.txt
RUN pip3 install -r requirements.txt


COPY . .
