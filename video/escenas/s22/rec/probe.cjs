const puppeteer = require(process.env.PPT);
const sleep = (ms) => new Promise(r => setTimeout(r, ms));
(async () => {
  const b = await puppeteer.launch({ executablePath: "C:/Program Files/Google/Chrome/Application/chrome.exe", headless: "new", userDataDir: process.env.TMPDIR_PROF });
  const p = await b.newPage();
  await p.setViewport({ width: 1142, height: 1000, deviceScaleFactor: 1 });
  await p.goto("https://anura.juanlabs.me/explorer/38371927-7a28-48b3-873e-0ff1cc6cad5e", { waitUntil: "networkidle0", timeout: 60000 });
  await sleep(1200);
  await p.screenshot({ path: "before.png" });
  const btn = await p.$$eval(".heart-header-btn", els => els.map(e => ({ l: e.getAttribute("aria-label"), c: e.className, r: (x => [x.x + x.width / 2, x.y + x.height / 2])(e.getBoundingClientRect()) })));
  console.log(JSON.stringify(btn));
  await p.click('button[aria-label="Guardar en favoritos"]');
  await sleep(1200);
  console.log("URL", p.url());
  await p.screenshot({ path: "after.png" });
  await b.close();
})();
