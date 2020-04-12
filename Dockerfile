FROM python:3.8.2-slim-buster

COPY requirements.txt requirements.txt
RUN pip install -r requirements.txt

WORKDIR /app/

COPY main.py .
CMD python main.py
