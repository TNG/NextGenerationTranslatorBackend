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
ADD src/main/wsgi.py wsgi.py

CMD ["gunicorn", "--bind", "0.0.0.0:80", "wsgi:app"]