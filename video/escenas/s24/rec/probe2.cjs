const puppeteer = require(process.env.PPT);
const sleep = (ms) => new Promise(r => setTimeout(r, ms));
(async () => {
  const b = await puppeteer.launch({ executablePath: "C:/Program Files/Google/Chrome/Application/chrome.exe", headless: "new", userDataDir: process.env.PROF });
  const p = await b.newPage();
  p.on("response", r => { if (r.url().includes("/api/")) console.log("RESP", r.status(), r.url().replace(/\?.*/, "")); });
  await p.setViewport({ width: 1467, height: 700 });
  await p.goto("http://localhost:3010/login", { waitUntil: "networkidle0", timeout: 60000 });
  const inputs = await p.$$("input");
  await inputs[0].click({ clickCount: 3 }); await inputs[0].type(process.env.U);
  await inputs[1].type(process.env.PW);
  const btn = (await p.$$("button")).find(Boolean);
  await p.$$eval("button", bs => bs.map(b => b.innerText)).then(t => console.log("buttons", t));
  await p.evaluate(() => [...document.querySelectorAll("button")].find(b => b.innerText.trim() === "Entrar").click());
  await sleep(4000);
  console.log("URL", p.url());
  console.log((await p.evaluate(() => document.body.innerText)).replace(/\n+/g, " | ").slice(0, 400));
  await b.close();
})();
