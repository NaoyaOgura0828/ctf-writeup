import * as Puppeteer from "puppeteer";
import Redis from "ioredis";

const redis: Redis = new Redis(6379, "172.30.0.30");

const sleep = async (ms: number) => {
    new Promise((resolve) => setTimeout(resolve, ms));
};

(async (): Promise<void> => {
    while (true) {
        try {
            const [error, data]: any = await redis.blpop("query", 0);
            if (data) {
                console.log("> Start to process - " + data);
                await (async (url: string): Promise<void> => {
                    const bot: Puppeteer.Browser = await Puppeteer.launch({
                        executablePath: "/usr/bin/chromium",
                        product: "chrome",
                        headless: true,
                        ignoreHTTPSErrors: true,
                        args: [
                            "--no-sandbox",
                            "--disable-default-apps",
                            "--disk-cache-dir=/dev/null",
                            "--disable-extensions",
                            "--disable-gpu",
                        ],
                    });
                    const page: Puppeteer.Page = await bot.newPage();
                    await page.setExtraHTTPHeaders({ "X-Internal": "true" });
                    await page.goto(
                        `${process.env.AUTH_HOST}/api/v1/authorize.oauth2?client_id=internal&redirect_uri=&response_type=code&scope=all`
                    );
                    await page.type(
                        "input[name=username]",
                        process.env.ADMIN_USERNAME
                    );
                    await page.type(
                        "input[name=password]",
                        process.env.ADMIN_PASSWORD
                    );
                    await page.click("button[type=submit]");
                    await page.waitForNavigation();
                    await page.goto(`${process.env.AUTH_HOST}/api/v1/logout`);
                    await page
                        .goto(url, {
                            timeout: 10000,
                        })
                        .catch((error: Error): void => {
                            console.error(error);
                        });
                    await sleep(3000);
                    setTimeout(() => {
                        bot.close();
                    }, 30000);
                })(data);
                console.log("> Job Done.");
            }
        } catch (error) {
            console.log("> " + error);
        }
    }
})();
