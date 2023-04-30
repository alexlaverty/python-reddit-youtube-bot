FROM python:3.11-bullseye

ENV DEBIAN_FRONTEND=noninteractive
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1
ENV PATH="/home/vscode/.local/bin:/scripts:$PATH"

ARG USERNAME=vscode
ARG USER_UID=1000
ARG USER_GID=$USER_UID

#RUN mkdir -p /scripts
COPY ./dependencies /
RUN chmod -R +x /scripts

RUN groupadd --gid $USER_GID $USERNAME && \
    useradd --uid $USER_UID --gid $USER_GID -m $USERNAME && \
    apt-get update && \
    apt-get install -y sudo vim ghostscript && \
    echo $USERNAME ALL=\(root\) NOPASSWD:ALL > /etc/sudoers.d/$USERNAME && \
    chmod 0440 /etc/sudoers.d/$USERNAME && \
    chmod -R +x /scripts

RUN apt-get update -y && \
    apt-get install -y --no-install-recommends build-essential

RUN mkdir -p /home/vscode/.local/bin && \
    curl -s https://github.com/yt-dlp/yt-dlp/releases/latest/download/yt-dlp -o /home/vscode/.local/bin/yt-dlp && \    
    chmod +x /home/vscode/.local/bin/yt-dlp && \
    chown -R vscode /home/vscode/.local

USER $USERNAME

ENTRYPOINT ["/bin/bash"]
