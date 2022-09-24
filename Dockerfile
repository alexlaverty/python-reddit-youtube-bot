FROM ubuntu

ENV DEBIAN_FRONTEND=noninteractive
ENV FIREFOX_VER 87.0
ENV GECKODRIVER_VER v0.30.0

COPY assets/fonts /usr/share/fonts/truetype/ttsvibelounge

COPY assets/bin/geckodriver /usr/bin/geckodriver

RUN chmod +x /usr/bin/geckodriver

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


# Add latest FireFox
RUN set -x \
   && apt install -y \
       libx11-xcb1 \
       libdbus-glib-1-2 \
       firefox \
   && curl -sSLO https://download-installer.cdn.mozilla.net/pub/firefox/releases/${FIREFOX_VER}/linux-x86_64/en-US/firefox-${FIREFOX_VER}.tar.bz2 \
   && tar -jxf firefox-* \
   && mv firefox /opt/ \
   && chmod 755 /opt/firefox \
   && chmod 755 /opt/firefox/firefox

COPY . /app

COPY policy.xml /etc/ImageMagick-6/policy.xml

WORKDIR /app

RUN pip install -r requirements.txt

CMD ["python3", "/app/app.py"]