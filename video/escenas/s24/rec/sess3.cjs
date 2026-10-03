const puppeteer = require(process.env.PPT);
const sleep = (ms) => new Promise(r => setTimeout(r, ms));
(async () => {
  const b = await puppeteer.launch({ executablePath: "C:/Program Files (x86)/Microsoft/Edge/Application/msedge.exe", headless: "new", userDataDir: process.env.PROF, args: ["--profile-directory=Profile 1"] });
  const p = await b.newPage();
  await p.setViewport({ width: 1467, height: 700 });
  await p.goto("https://anura.juanlabs.me/ajustes", { waitUntil: "networkidle0", timeout: 60000 }); await sleep(1500);
  const links = await p.$$eval("a", as => as.filter(a => /administrativo/i.test(a.innerText)).map(a => [a.innerText, a.href, a.target]));
  console.log(JSON.stringify(links));
  const btns = await p.$$eval("button", bs => bs.filter(b => /administrativo/i.test(b.innerText)).map(b => b.innerText));
  console.log(JSON.stringify(btns));
  await b.close();
})();
