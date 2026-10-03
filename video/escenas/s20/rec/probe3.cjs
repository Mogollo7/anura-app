const puppeteer = require(process.env.PPT);
(async () => {
  const b = await puppeteer.launch({ executablePath: "C:/Program Files/Google/Chrome/Application/chrome.exe", headless: "new", userDataDir: process.env.TMPDIR_PROF });
  const p = await b.newPage();
  p.on("console", m => console.log("console:", m.text()));
  await p.setViewport({ width: 1142, height: 1000, deviceScaleFactor: 1 });
  await p.evaluateOnNewDocument(() => {
    window.__log = [];
    Object.defineProperty(navigator, "share", { configurable: true, value: (d) => { window.__log.push(["share", JSON.stringify(d)]); return Promise.resolve(); } });
    Object.defineProperty(navigator, "canShare", { configurable: true, value: () => true });
    const cw = navigator.clipboard && navigator.clipboard.writeText;
    if (navigator.clipboard) navigator.clipboard.writeText = (t) => { window.__log.push(["clip", t]); return Promise.resolve(); };
  });
  await p.goto("https://anura.juanlabs.me/explorer/f3b3cc80-a011-4716-9a5f-762f9be94880", { waitUntil: "networkidle0", timeout: 60000 });
  await p.click('button[aria-label="Compartir observación"]');
  await new Promise(r => setTimeout(r, 800));
  console.log(JSON.stringify(await p.evaluate(() => window.__log)));
  await p.screenshot({ path: "after_share_stub.png" });
  await b.close();
})();
