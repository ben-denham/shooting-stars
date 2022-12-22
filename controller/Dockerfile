FROM python:3.9-bullseye

RUN groupadd --gid 1000 coder
RUN useradd --uid 1000 --gid coder --shell /bin/bash --create-home coder
USER coder

RUN mkdir /home/coder/src
WORKDIR /home/coder/src

# Pip packages will be installed in a directory we can mount from the
# host as a volume.
ENV PYTHONUSERBASE=/home/coder/src/.pip-packages
ENV PATH=$PATH:/home/coder/src/.pip-packages/bin
