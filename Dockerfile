FROM pytorch/pytorch:1.7.0-cuda11.0-cudnn8-runtime

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
ADD test.py test.py

CMD ["/bin/bash"]
