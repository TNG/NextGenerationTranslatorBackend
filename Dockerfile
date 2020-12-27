FROM pytorch/pytorch:1.7.0-cuda11.0-cudnn8-runtime

RUN apt update
RUN apt install build-essential -y

RUN mkdir /translator
WORKDIR /translator

ADD requirements.txt requirements.txt
RUN pip install -r requirements.txt

ADD src/main/translator.py translator.py
ADD src/main/detector.py detector.py
ADD src/main/translator_service.py translator_service.py
ADD src/main/request_limitation.py request_limitation.py
ADD src/main/wsgi.py wsgi.py

# Workers are limited to 1 so we do not have to load the model multiple times
# 5 threads are in use since concurrent translation requests are limited to 3 parallel request, so health requests still pass through
CMD ["gunicorn", "--bind", "0.0.0.0:80", "wsgi:app", "-w", "1", "--threads", "5"]