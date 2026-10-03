const puppeteer = require(process.env.PPT);
const sleep = (ms) => new Promise(r => setTimeout(r, ms));
(async () => {
  const b = await puppeteer.launch({ executablePath: "C:/Program Files/Google/Chrome/Application/chrome.exe", headless: "new", userDataDir: process.env.TMPDIR_PROF });
  const URL = "https://anura.juanlabs.me/explorer/f3b3cc80-a011-4716-9a5f-762f9be94880";
  await b.defaultBrowserContext().overridePermissions("https://anura.juanlabs.me", ["clipboard-read", "clipboard-write", "clipboard-sanitized-write"]);
  const p = await b.newPage();
  await p.setViewport({ width: 1142, height: 1000, deviceScaleFactor: 2 });
  await p.goto(URL, { waitUntil: "networkidle0", timeout: 60000 });
  await sleep(1500);
  const r = await p.$eval('button[aria-label="Compartir observación"]', e => { const x = e.getBoundingClientRect(); return [x.x + x.width / 2, x.y + x.height / 2]; });
  console.log("BTN", JSON.stringify(r));
  await p.mouse.move(560, 620);
  const rec = await p.screencast({ path: "rec.webm" });
  const t0 = Date.now();
  await sleep(1000);
  // movimiento lento hacia el botón: 1.0 s
  const steps = 40;
  for (let i = 1; i <= steps; i++) {
    const k = i / steps, e = k < 0.5 ? 4 * k * k * k : 1 - Math.pow(-2 * k + 2, 3) / 2;
    await p.mouse.move(560 + (r[0] - 560) * e, 620 + (r[1] - 620) * e);
    await sleep(25);
  }
  await sleep(450);
  const tc = Date.now() - t0;
  await p.mouse.down(); await sleep(90); await p.mouse.up();
  console.log("CLICK_MS", tc);
  await sleep(2600);
  await rec.stop();
  console.log("CLIP", await p.evaluate(() => navigator.clipboard.readText().catch(e => "ERR " + e)));
  await b.close();
})();
