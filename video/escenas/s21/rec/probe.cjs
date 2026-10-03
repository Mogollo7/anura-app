const puppeteer = require(process.env.PPT);
(async () => {
  const b = await puppeteer.launch({ executablePath: "C:/Program Files/Google/Chrome/Application/chrome.exe", headless: "new", userDataDir: process.env.TMPDIR_PROF });
  const p = await b.newPage();
  await p.setViewport({ width: 1142, height: 1000, deviceScaleFactor: 1 });
  await p.goto("https://anura.juanlabs.me/observaciones?view=observers", { waitUntil: "networkidle0", timeout: 60000 });
  await new Promise(r => setTimeout(r, 1500));
  console.log("URL", p.url());
  await p.screenshot({ path: "probe0.png" });
  console.log(JSON.stringify(await p.evaluate(() => {
    const c = document.querySelector(".observers-list.card");
    if (!c) return { found: false, body: document.body.innerText.slice(0, 400) };
    const r = c.getBoundingClientRect();
    const rows = [...c.children].map(e => { const x = e.getBoundingClientRect(); return { cls: e.className, txt: e.innerText.replace(/\s+/g, " ").slice(0, 80), r: [x.x, x.y, x.width, x.height].map(Math.round) }; });
    return { found: true, r: [r.x, r.y, r.width, r.height].map(Math.round), rows: rows.slice(0, 6), n: rows.length };
  })));
  await b.close();
})();
