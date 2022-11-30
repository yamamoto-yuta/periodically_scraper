# Base image
FROM python:3.8.2

# Environment
ENV HOME /home
WORKDIR $HOME
COPY requirements.txt $HOME/

# Installl commands
RUN apt-get update && apt-get upgrade -y \
    && apt-get install -y \
    vim \
    git

# Install Python libraries
RUN pip install --upgrade pip \
    && pip install -r $HOME/requirements.txt
