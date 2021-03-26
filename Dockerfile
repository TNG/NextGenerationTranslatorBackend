FROM pytorch/pytorch:1.13.1-cuda11.6-cudnn8-runtime

RUN apt update
RUN apt install build-essential redis-server -y

RUN mkdir /translator
WORKDIR /translator

ADD requirements.txt requirements.txt
RUN pip install -r requirements.txt

ADD src/main .
RUN rm -rf easy_nmt_cache
ENV REDIS_HOST=localhost
ENV THREADS=5
ENV WORKERS=1
# Workers are limited to 1 so we do not have to load the model multiple times
# 5 threads are in use since concurrent translation requests are limited to 3 parallel request, so health requests still pass through
CMD [ "sh", "-c", "redis-server --daemonize yes && gunicorn --bind 0.0.0.0:80 wsgi:app -w ${WORKERS} --threads ${THREADS} --timeout 600"]
