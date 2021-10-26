FROM ubuntu

RUN apt update -y

RUN apt install -y \
        python \
        python3-pip

COPY . /src

WORKDIR /src

RUN pip install -r requirements.txt

CMD ["python3", "/src/app.py"]