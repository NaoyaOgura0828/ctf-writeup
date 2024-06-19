const puppeteer = require('puppeteer');
const Redis = require('ioredis');
const crypto = require('crypto');

let processedCount = 0;

async function sleep(ms) {
  return new Promise((resolve) => setTimeout(resolve, ms));
}

function genPasscode() {
  let chars = "LINECTF";
  let emojis = [">.<", ">,<"];
  let passCode = Array.from(crypto.randomFillSync(new Uint32Array(4))).map((x) => chars[x % chars.length]).join('');
  passCode += emojis[crypto.randomInt(emojis.length)];
  return passCode;
}

async function visit(url) {
  processedCount++;
  console.log(`[${processedCount}] bot visits ${url}`);
  try {
    let browser = await puppeteer.launch({
      headless: "true",
      args: [
        "--disable-gpu",
        "--disable-dev-shm-usage",
        "--disable-setuid-sandbox",
        "--no-sandbox",
        "--ignore-certificate-errors",
        "--disable-background-networking",
        "--disk-cache-dir=/dev/null",
        "--disable-default-apps",
        "--disable-extensions",
        "--disable-desktop-notifications",
        "--disable-popup-blocking",
        "--disable-sync",
        "--disable-translate",
        "--hide-scrollbars",
        "--metrics-recording-only",
        "--mute-audio",
        "--no-first-run",
        "--safebrowsing-disable-auto-update",
        "--no-zygote",
      ],
      product: "chrome"
    });

    // write a note
    let page = await browser.newPage();
    let passCode = genPasscode();
    console.log(`[${processedCount}] passCode = ${passCode}`);
    await page.goto('http://' + process.env.BUSINESS_NAME + process.env.DOMAIN_SUFFIX);
    await page.type('[name="passCode"]', passCode);
    await page.type('[name="content"]', process.env.FLAG);
    await page.click('[type="submit"]');
    await sleep(5000);
    await page.close();
    await sleep(5000);
    
    // visit report URL
    page = await browser.newPage();
    let requestCount = 0;
    await page.setRequestInterception(true);
    page.on('request', (request) => {
      requestCount++;
      let pageURL = page.url();
      if (!request.isNavigationRequest() || (pageURL !== 'about:blank' && pageURL !== request.url()) || requestCount !== 1) {
          request.continue();
          return;
      }
      const headers = request.headers();
      headers['X-CTF-From'] = 'HeadlessChrome';
      request.continue({
          headers
      });
    });
    await page.goto(url);
    await sleep(25000);

    // close the browser
    console.log(`[${processedCount}] done visiting`);
    await browser.close();
  } catch (e) {
    console.error(e);
    try { await browser.close() } catch (e) { 
      console.log("[+] close error");
      console.error(e);
    }
  }
};

async function run() {
  let redis = new Redis({
    port: 6379,
    host: "redis",
    username: "default",
    password: process.env.REDIS_PASSWORD,
    db: 0,
  });
  while (true) {
    try {
      let [err, res] = await redis.blpop("url", 0);
      if (res) await visit(res);
    } catch {
      console.log('[+] error while getting a report URL');
    }
    await sleep(2500);
  }
}

run();