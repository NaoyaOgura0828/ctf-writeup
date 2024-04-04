FROM node:latest

WORKDIR /usr/src/app

COPY package*.json ./

RUN npm install --loglevel verbose

COPY . .

HEALTHCHECK CMD (curl --fail http://127.0.0.1) || exit 1

CMD [ "node", "server.js" ]