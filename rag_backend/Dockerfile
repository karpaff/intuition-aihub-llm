FROM python:3.12

WORKDIR /app

COPY . /app

RUN apt-get update && \
    pip install --upgrade pip && \ 
    pip install -r /app/requirements.txt

ENV PYTHONPATH=/app

CMD python3 src/common/qdrant/init_qdrant.py && python3 run.py