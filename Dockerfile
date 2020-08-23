FROM pytorch/pytorch:1.6.0-cuda10.1-cudnn7-runtime

RUN mkdir /translator
ADD requirements.txt /translator/requirements.txt
ADD initialize_cache.py /translator/initialize_cache.py
ADD translator.py /translator/translator.py

WORKDIR /translator

RUN apt update
RUN apt install build-essential -y

RUN pip install -r requirements.txt
#RUN python initialize_cache.py

CMD ["python", "translator.py"]