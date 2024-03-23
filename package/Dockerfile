FROM nvidia/cuda:12.3.2-devel-ubuntu22.04

COPY . /south-park

WORKDIR /south-park

RUN apt-get update --allow-insecure-repositories \
    && apt-get install -y python3 python3-pip

ENV CMAKE_ARGS="-DLLAMA_CUBLAS=ON"

RUN pip install --upgrade pip && \
    pip install -r requirements.txt

CMD uvicorn api:app --reload --host 0.0.0.0 --port $PORT
