const puppeteer = require(process.env.PPT);
const fs = require("fs");
const sleep = (ms) => new Promise(r => setTimeout(r, ms));
const SEL = '.heart-header-btn:not([aria-label="Compartir observación"])';
const state = (p) => p.$eval(SEL, e => e.getAttribute("aria-label") + " | " + e.className + " | spin=" + !!e.querySelector(".icon-spin"));
(async () => {
  const b = await puppeteer.launch({ executablePath: "C:/Program Files (x86)/Microsoft/Edge/Application/msedge.exe", headless: "new", userDataDir: process.env.PROF, args: ["--profile-directory=Profile 1"] });
  const p = await b.newPage();
  await p.setViewport({ width: 1142, height: 1000 });
  await p.goto("https://anura.juanlabs.me/explorer/38371927-7a28-48b3-873e-0ff1cc6cad5e", { waitUntil: "networkidle0", timeout: 60000 });
  await sleep(1500);
  if ((await state(p)).includes("Quitar")) {
    await p.click(SEL);
    for (let i = 0; i < 60 && !(await state(p)).startsWith("Guardar en favoritos | btn-secondary btn-icon heart-header-btn  | spin=false"); i++) await sleep(250);
    await p.goto(p.url(), { waitUntil: "networkidle0" }); await sleep(1500);
  }
  console.log("ANTES", await state(p));
  const h = await p.$eval(SEL, e => { const r = e.getBoundingClientRect(); return [r.x + r.width / 2, r.y + r.height / 2]; });
  const S = [560, 620];
  await p.mouse.move(S[0], S[1]); await sleep(300);
  const shots = []; const T0 = Date.now(); let n = 0;
  const snap = async (tag) => { const f = `shots/${String(n++).padStart(4, "0")}.png`; await p.screenshot({ path: f }); shots.push([f, (Date.now() - T0) / 1000, tag]); };
  // 1 s quieto
  while ((Date.now() - T0) < 1000) await snap("");
  // movimiento lento 1.0 s, un paso del ratón por captura
  const tm = Date.now();
  while (Date.now() - tm < 1000) {
    const k = Math.min(1, (Date.now() - tm) / 1000), e = k < 0.5 ? 4 * k * k * k : 1 - Math.pow(-2 * k + 2, 3) / 2;
    await p.mouse.move(S[0] + (h[0] - S[0]) * e, S[1] + (h[1] - S[1]) * e); await snap("");
  }
  await p.mouse.move(h[0], h[1]);
  const tw = Date.now(); while (Date.now() - tw < 400) await snap("");
  await p.mouse.down(); await sleep(60); await p.mouse.up();
  const tclick = (Date.now() - T0) / 1000;
  const ta = Date.now(); while (Date.now() - ta < 3000) await snap(await state(p));
  fs.writeFileSync("shots/index.json", JSON.stringify({ tclick, shots, heart: h }));
  console.log("CLICK", tclick, "N", shots.length, "FINAL", await state(p));
  await b.close();
})();
