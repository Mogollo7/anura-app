const puppeteer = require(process.env.PPT);
(async () => {
  const b = await puppeteer.launch({ executablePath: "C:/Program Files/Google/Chrome/Application/chrome.exe", headless: "new", userDataDir: process.env.TMPDIR_PROF });
  const p = await b.newPage();
  await p.setViewport({ width: 1142, height: 1000, deviceScaleFactor: 2 });
  await p.goto("https://anura.juanlabs.me/explorer/f3b3cc80-a011-4716-9a5f-762f9be94880", { waitUntil: "networkidle0", timeout: 60000 });
  await new Promise(r => setTimeout(r, 1000));
  await p.click('button[aria-label="Compartir observación"]');
  for (const ms of [150, 400, 1200]) { await new Promise(r => setTimeout(r, ms)); await p.screenshot({ path: `after_${ms}.png` }); }
  console.log(await p.evaluate(() => [...document.querySelectorAll('[role=dialog], .modal, [class*=share]')].map(e => e.className + " | " + e.innerText.slice(0, 200))));
  await b.close();
})();
