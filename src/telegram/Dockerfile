FROM ubuntu:18.04

RUN apt-get update && apt install -y python3-pip

COPY requirements.txt /src/requirements.txt
RUN pip3 install --upgrade pip
RUN pip3 install -r /src/requirements.txt

COPY main.py /src/main.py

CMD ["python3", "/src/main.py"]