const puppeteer = require(process.env.PPT);
const sleep = (ms) => new Promise(r => setTimeout(r, ms));
(async () => {
  const b = await puppeteer.launch({ executablePath: "C:/Program Files (x86)/Microsoft/Edge/Application/msedge.exe", headless: "new", userDataDir: process.env.PROF, args: ["--profile-directory=Profile 1"] });
  const p = await b.newPage();
  await p.setViewport({ width: 1142, height: 1000 });
  for (const u of ["https://anura.juanlabs.me/explorer/38371927-7a28-48b3-873e-0ff1cc6cad5e", "http://localhost:3010/observaciones"]) {
    await p.goto(u, { waitUntil: "networkidle0", timeout: 60000 }); await sleep(4000);
    console.log(u, "->", p.url(), "|", (await p.evaluate(() => document.body.innerText)).replace(/\n+/g, " | ").slice(0, 200));
  }
  await b.close();
})();
