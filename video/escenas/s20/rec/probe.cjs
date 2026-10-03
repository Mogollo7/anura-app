const puppeteer = require(process.env.PPT);
(async () => {
  const b = await puppeteer.launch({ executablePath: "C:/Program Files/Google/Chrome/Application/chrome.exe", headless: "new", args: ["--window-size=1920,1680"] , userDataDir: process.env.TMPDIR_PROF});
  const p = await b.newPage();
  await p.setViewport({ width: 1142, height: 1000, deviceScaleFactor: 2 });
  await p.goto("https://anura.juanlabs.me/explorer/f3b3cc80-a011-4716-9a5f-762f9be94880", { waitUntil: "networkidle0", timeout: 60000 });
  await new Promise(r => setTimeout(r, 1500));
  await p.screenshot({ path: "probe0.png" });
  const btns = await p.$$eval("button, a", els => els.map(e => ({ t: e.tagName, c: e.className, l: e.getAttribute("aria-label"), title: e.title, txt: e.innerText.trim().slice(0, 30), r: (x => [Math.round(x.x), Math.round(x.y), Math.round(x.width), Math.round(x.height)])(e.getBoundingClientRect()) })));
  console.log(JSON.stringify(btns.filter(x => /btn/.test(x.c)), null, 0));
  await b.close();
})();
