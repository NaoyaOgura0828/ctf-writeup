const express = require('express');
const morgan = require('morgan');
const svgCaptcha = require('svg-captcha');
const session = require('express-session');
const crypto = require('crypto');
const Redis = require("ioredis");
const fs = require("fs");

const PORT = 80;
const HOST = '0.0.0.0';
const redis = new Redis({
  port: 6379,
  host: "redis",
  username: "default",
  password: process.env.REDIS_PASSWORD,
  db: 0,
});

function genCaptcha() {
  return svgCaptcha.create({
    size: 8,
    noise: 8,
    width: 300,
    height: 100
  });
}

const app = express();
app.use(session({
  secret: crypto.randomBytes(20).toString("hex"),
  cookie: {}
}));
app.use(morgan('combined'));
app.use(express.urlencoded({extended: false}));

app.get('/', (req, res) => {
  return res.sendFile(__dirname + '/index.html' , { root : '/' });
});

app.post('/', async (req, res) => {
    let { url, captcha } = req.body;
    
    try {
      fs.appendFileSync("/logs/bot/payload_logs.txt", `[${new Date()}] [${req.ip}] - [${url}]\n\n`);
    } catch (e) {
      console.log(e);
    }

    if (!req.session.captcha || typeof captcha !== "string" || req.session.captcha !== captcha) {
      req.session.captcha = genCaptcha().text;
      return res.redirect(`/?error=${encodeURIComponent('Wrong Captcha')}`);
    }
    if (typeof url !== "string") return res.redirect(`/?error=${encodeURIComponent('Invalid URL')}`);

    if (!url.startsWith("http://") && !url.startsWith("https://")) {
        return res.redirect(`/?error=${encodeURIComponent('Only http and https scheme are allowed')}`);
    }

    let schemeLength = url.startsWith('http://') ? "http://".length : "https://".length;
    let strippedURL = url.substring(schemeLength);
    strippedURL += '/';
    let nextSlashPos = strippedURL.indexOf('/');
    let host = strippedURL.substring(0, nextSlashPos);

    if (host.search(/[^(a-zA-Z.)]/) > 0) {
        return res.redirect(`/?error=${encodeURIComponent('Malformed host')}`);
    }

    let regex = new RegExp(`^.*${process.env.BUSINESS_NAME.substring(1)}.*$`, "gi");
    if (!host.endsWith(process.env.DOMAIN_SUFFIX) || host.match(regex)) {
        return res.redirect(`/?error=${encodeURIComponent('Forbidden host')}`);
    }
    
    try {
      await redis.rpush('url', url);
      return res.redirect(`/?success=${encodeURIComponent("URL has been reported")}`);
    } catch {
      return res.redirect(`/?error=${encodeURIComponent('Error! Please try again!')}`);
    }
});

app.get('/captcha', function (req, res) {
  let captcha = genCaptcha();
  req.session.captcha = captcha.text;
  res.type('svg');
  return res.status(200).send(captcha.data);
});

app.listen(PORT, HOST, () => {
  console.log(`Running on http://${HOST}:${PORT}`);
});