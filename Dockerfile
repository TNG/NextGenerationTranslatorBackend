FROM pytorch/pytorch:1.6.0-cuda10.1-cudnn7-runtime

RUN pip install -r requirements.txt

CMD ["python", "translator.py"]