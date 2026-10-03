const puppeteer = require(process.env.PPT);
const sleep = (ms) => new Promise(r => setTimeout(r, ms));
(async () => {
  const b = await puppeteer.launch({ executablePath: "C:/Program Files/Google/Chrome/Application/chrome.exe", headless: "new", userDataDir: process.env.PROF });
  const p = await b.newPage();
  await p.setViewport({ width: 1467, height: 700, deviceScaleFactor: 1 });
  await p.goto("http://localhost:3010/observaciones", { waitUntil: "networkidle0", timeout: 60000 });
  if (p.url().includes("/login")) {
    const inputs = await p.$$("input");
    await inputs[0].type(process.env.U); await inputs[1].type(process.env.PW);
    await Promise.all([p.waitForNavigation({ waitUntil: "networkidle0", timeout: 30000 }).catch(() => {}), p.keyboard.press("Enter")]);
    await sleep(1500);
    console.log("after login", p.url());
    await p.goto("http://localhost:3010/observaciones", { waitUntil: "networkidle0", timeout: 60000 });
  }
  await sleep(1500);
  console.log("URL", p.url());
  const info = await p.evaluate(() => {
    const t = document.querySelector("div.overflow-x-auto.rounded-lg.border.border-border.bg-surface");
    if (!t) return { found: false, txt: document.body.innerText.slice(0, 300) };
    const r = t.getBoundingClientRect();
    return { found: true, r: [r.x, r.y, r.width, r.height].map(Math.round), rows: t.querySelectorAll("tbody tr").length, txt: t.innerText.slice(0, 300) };
  });
  console.log(JSON.stringify(info));
  await p.screenshot({ path: "probe.png" });
  await b.close();
})();
