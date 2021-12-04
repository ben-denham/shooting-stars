FROM node:16-bullseye

ENV NPM_CONFIG_PREFIX=/home/node/.npm-global
ENV PATH=$PATH:/home/node/.npm-global/bin

USER node

RUN npm install --global meteor@2.5.1

RUN mkdir /home/node/src
WORKDIR /home/node/src
