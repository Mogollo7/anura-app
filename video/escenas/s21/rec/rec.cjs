const puppeteer = require(process.env.PPT);
const sleep = (ms) => new Promise(r => setTimeout(r, ms));
(async () => {
  const b = await puppeteer.launch({ executablePath: "C:/Program Files/Google/Chrome/Application/chrome.exe", headless: "new", userDataDir: process.env.TMPDIR_PROF });
  const p = await b.newPage();
  await p.setViewport({ width: 1142, height: 1000, deviceScaleFactor: 1 });
  await p.goto("https://anura.juanlabs.me/observaciones?view=observers", { waitUntil: "networkidle0", timeout: 60000 });
  await sleep(1500);
  const S = [931, 184], E = [330, 300];
  await p.mouse.move(S[0], S[1]);
  const rec = await p.screencast({ path: "rec.webm" });
  await sleep(1200);
  const steps = 50;
  for (let i = 1; i <= steps; i++) {
    const k = i / steps, e = k < 0.5 ? 4 * k * k * k : 1 - Math.pow(-2 * k + 2, 3) / 2;
    await p.mouse.move(S[0] + (E[0] - S[0]) * e, S[1] + (E[1] - S[1]) * e);
    await sleep(20);
  }
  await sleep(4000);
  await rec.stop();
  await b.close();
})();
