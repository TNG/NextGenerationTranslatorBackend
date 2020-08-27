FROM pytorch/pytorch:1.6.0-cuda10.1-cudnn7-runtime

RUN apt update
RUN apt install build-essential -y

RUN mkdir /translator
WORKDIR /translator

ADD requirements.txt requirements.txt
RUN pip install -r requirements.txt

ADD initialize_cache.py initialize_cache.py
#RUN python initialize_cache.py

ADD translator.py translator.py

CMD ["python", "translator.py"]
