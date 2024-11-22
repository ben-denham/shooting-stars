FROM node:23-bookworm

ENV NPM_CONFIG_PREFIX=/home/node/.npm-global
ENV PATH=$PATH:/home/node/.npm-global/bin

USER node

RUN npm install --global meteor@3.0.4

RUN mkdir /home/node/src
WORKDIR /home/node/src
