FROM pytorch/pytorch:1.6.0-cuda10.1-cudnn7-runtime

RUN apt update
RUN apt install build-essential -y

RUN mkdir /translator
WORKDIR /translator

ADD requirements.txt requirements.txt
RUN pip install -r requirements.txt

ADD translator.py translator.py
ADD detector.py detector.py
ADD translator_service.py translator_service.py
ADD wsgi.py wsgi.py

CMD ["gunicorn", "--bind", "0.0.0.0:80", "wsgi:app"]
