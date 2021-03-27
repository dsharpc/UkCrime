FROM python:3.9-buster

RUN apt-get update
RUN apt-get -y install htop

WORKDIR /app
COPY app /app
COPY requirements.txt .

RUN pip install --upgrade pip
RUN pip install --upgrade setuptools
RUN pip install -r requirements.txt

ENV PYTHONIOENCODING=utf-8
ENV LC_ALL=C.UTF-8
ENV export LANG=C.UTF-8

CMD streamlit run app.py