FROM python:3.7-slim-buster as builder

RUN apt update -y \
    && apt-get install -y python3.7-venv

ENV PATH=/opt/venv/bin:$PATH
RUN python3 -m venv /opt/venv

COPY requirements.txt requirements.txt
RUN pip install -r requirements.txt

FROM python:3.7-alpine as runner

COPY --from=builder /opt/venv /opt/venv
ENV PATH=/opt/venv/bin:$PATH

WORKDIR /app/

COPY main.py .
CMD python main.py
