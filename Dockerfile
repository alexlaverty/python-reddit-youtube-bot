FROM ubuntu

ENV DEBIAN_FRONTEND=noninteractive
# ENV FIREFOX_VER 87.0
# ENV GECKODRIVER_VER v0.30.0

COPY assets/fonts /usr/share/fonts/truetype/ttsvibelounge

#COPY assets/bin/geckodriver /usr/bin/geckodriver

RUN apt update -y && \
    apt install -y \
        curl \
        imagemagick \
        libmagick++-dev \
        python3-pip \
        python3 \
        ttf-mscorefonts-installer \
        vim && \
        fc-cache -f

COPY . /app

COPY policy.xml /etc/ImageMagick-6/policy.xml

COPY config/auth-env.py /app/config/auth.py

WORKDIR /app

RUN pip install -r requirements.txt

RUN playwright install-deps && playwright install



CMD ["python3", "/app/app.py"]