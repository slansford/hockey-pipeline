FROM apache/airflow:3.2.2

USER root

RUN apt-get update && apt-get install -y git

USER airflow

COPY requirements.txt /requirements.txt
RUN pip install -r /requirements.txt