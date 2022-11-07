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
        #git \
        ttf-mscorefonts-installer \
        vim && \
        fc-cache -f

# Install specific version of git to satisfy github workflow action requirements
run apt install -y libz-dev libssl-dev libcurl4-gnutls-dev libexpat1-dev gettext cmake gcc && \
    wget https://github.com/git/git/archive/refs/tags/v2.38.1.tar.gz && \
    tar -xvf v2.38.1.tar.gz && \
    cd git-2.38.1 && \
    make prefix=/usr/local all && \
    make prefix=/usr/local install

COPY . /app

COPY policy.xml /etc/ImageMagick-6/policy.xml

COPY config/auth-env.py /app/config/auth.py

WORKDIR /app

RUN pip install -r requirements.txt

RUN playwright install-deps && playwright install

CMD ["python3", "/app/app.py"]