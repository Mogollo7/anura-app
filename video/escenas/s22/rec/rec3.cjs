const puppeteer = require(process.env.PPT);
const sleep = (ms) => new Promise(r => setTimeout(r, ms));
const SEL = '.heart-header-btn:not([aria-label="Compartir observación"])';
async function slowMove(p, a, b, ms) {
  const steps = Math.round(ms / 25);
  for (let i = 1; i <= steps; i++) {
    const k = i / steps, e = k < 0.5 ? 4 * k * k * k : 1 - Math.pow(-2 * k + 2, 3) / 2;
    await p.mouse.move(a[0] + (b[0] - a[0]) * e, a[1] + (b[1] - a[1]) * e); await sleep(20);
  }
}
const state = (p) => p.$eval(SEL, e => e.getAttribute("aria-label") + " | " + e.className);
(async () => {
  const b = await puppeteer.launch({ executablePath: "C:/Program Files (x86)/Microsoft/Edge/Application/msedge.exe", headless: "new", userDataDir: process.env.PROF, args: ["--profile-directory=Profile 1"] });
  const p = await b.newPage();
  await p.setViewport({ width: 1142, height: 1000 });
  await p.goto("https://anura.juanlabs.me/explorer/38371927-7a28-48b3-873e-0ff1cc6cad5e", { waitUntil: "networkidle0", timeout: 60000 });
  await sleep(1500);
  console.log("INICIO", await state(p));
  if ((await state(p)).includes("Quitar")) {
    await p.click(SEL);
    for (let i = 0; i < 40 && !(await state(p)).includes("Guardar en favoritos"); i++) await sleep(250);
    await p.goto(p.url(), { waitUntil: "networkidle0" }); await sleep(1500);
    console.log("QUITADO", await state(p));
  }
  const h = await p.$eval(SEL, e => { const r = e.getBoundingClientRect(); return [r.x + r.width / 2, r.y + r.height / 2]; });
  const S = [560, 620];
  await p.mouse.move(S[0], S[1]);
  await sleep(500);
  const rec = await p.screencast({ path: "s22/rec/rec3.webm" });
  await sleep(1000);
  await slowMove(p, S, h, 1000);
  await sleep(500);
  await p.mouse.down(); await sleep(90); await p.mouse.up();
  const t0 = Date.now();
  let st = "";
  for (let i = 0; i < 60; i++) { st = await state(p); if (st.includes("liked") && !(await p.$eval(SEL, e => !!e.querySelector("[class*=spin], .spinner")))) break; await sleep(100); }
  console.log("TRAS_CLIC", st, Date.now() - t0, "ms");
  p.on("console", () => {});
  const t1 = Date.now();
  for (let i = 0; i < 120; i++) { const spin = await p.$eval(SEL, e => !!e.querySelector(".icon-spin")); if (!spin && (await state(p)).includes("liked")) { const x = await p.$eval(SEL, e => e.innerHTML.length); } await sleep(100); }
  await rec.stop();
  console.log("FINAL", await state(p));
  await b.close();
})();
