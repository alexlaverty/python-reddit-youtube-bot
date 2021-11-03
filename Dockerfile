FROM ubuntu

ENV DEBIAN_FRONTEND=noninteractive

RUN apt update -y

RUN apt install -y \
        python3.8 \
        python3-pip \
        libmagick++-dev \
        imagemagick \
        vim \
        ttf-mscorefonts-installer && \
        fc-cache -f

COPY . /app

COPY policy.xml /etc/ImageMagick-6/policy.xml

WORKDIR /app

RUN pip install -r requirements.txt

# RUN poetry config virtualenvs.create false
# RUN poetry install 


CMD ["python3", "/app/app.py"]