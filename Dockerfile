FROM python:3.8

# RUN useradd -m SQRYRDS

ENV PYTHONUNBUFFERED 0

ENV ERROR_LOGFILE /home/app/logs/gunicorn-error.log

ENV ACCESS_LOGFILE /home/app/logs/gunicorn-access.log

WORKDIR /home/app

ADD requirements.txt /home/app

RUN pip install --upgrade pip && \
    pip install --trusted-host pypi.python.org -r requirements.txt

RUN apt-get clean && apt-get update && apt-get install -y locales locales-all

ADD . /home/app

EXPOSE 8080

ENV PORT="${PORT:-8080}"

CMD gunicorn main:app \
    --bind 0.0.0.0:$PORT \
    --workers=4 \
    --timeout 60 \
    -k uvicorn.workers.UvicornWorker \
    --log-level=info \
    --error-logfile=$ERROR_LOGFILE \
    --access-logfile=$ACCESS_LOGFILE \
    --capture-output

