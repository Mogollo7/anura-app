const puppeteer = require(process.env.PPT);
(async () => {
  const b = await puppeteer.launch({ executablePath: "C:/Program Files/Google/Chrome/Application/chrome.exe", headless: "new", userDataDir: process.env.TMPDIR_PROF });
  const p = await b.newPage();
  await p.setViewport({ width: 1142, height: 920, deviceScaleFactor: 1 });
  await p.goto("http://localhost:3010/observaciones", { waitUntil: "networkidle0", timeout: 60000 });
  await new Promise(r => setTimeout(r, 1200));
  console.log("URL", p.url());
  console.log((await p.evaluate(() => document.body.innerText)).slice(0, 300).replace(/\n+/g, " | "));
  await p.screenshot({ path: "s24probe.png" });
  await b.close();
})();
