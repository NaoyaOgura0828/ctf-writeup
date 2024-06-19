FROM node:18-slim

ENV PUPPETEER_SKIP_DOWNLOAD true
ENV PUPPETEER_SKIP_CHROMIUM_DOWNLOAD true

RUN apt-get update && apt-get install -y chromium
RUN groupadd -r bot && useradd bot -g bot && mkdir /home/bot && chown -R bot:bot /home/bot

COPY ./src /bot
WORKDIR /bot

# RUN chown bot:bot /bot && mkdir /bot/dist && chown bot:bot /bot/dist
RUN chmod 755 /bot/entrypoint.sh
RUN npm install
RUN npx tsc --build

USER bot
WORKDIR /bot

ENTRYPOINT /bot/entrypoint.sh