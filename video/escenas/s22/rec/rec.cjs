const puppeteer = require(process.env.PPT);
const sleep = (ms) => new Promise(r => setTimeout(r, ms));
async function slowMove(p, a, b, ms) {
  const steps = Math.round(ms / 25);
  for (let i = 1; i <= steps; i++) {
    const k = i / steps, e = k < 0.5 ? 4 * k * k * k : 1 - Math.pow(-2 * k + 2, 3) / 2;
    await p.mouse.move(a[0] + (b[0] - a[0]) * e, a[1] + (b[1] - a[1]) * e); await sleep(20);
  }
}
(async () => {
  const b = await puppeteer.launch({ executablePath: "C:/Program Files (x86)/Microsoft/Edge/Application/msedge.exe", headless: "new", userDataDir: process.env.PROF, args: ["--profile-directory=Profile 1"] });
  // ---------- S22: me gusta ----------
  const p = await b.newPage();
  await p.setViewport({ width: 1142, height: 1000 });
  await p.goto("https://anura.juanlabs.me/explorer/38371927-7a28-48b3-873e-0ff1cc6cad5e", { waitUntil: "networkidle0", timeout: 60000 });
  await sleep(1500);
  const heart = await p.$eval('.heart-header-btn:not([aria-label="Compartir observación"])', e => { const r = e.getBoundingClientRect(); return { x: r.x + r.width / 2, y: r.y + r.height / 2, label: e.getAttribute("aria-label"), cls: e.className, pressed: e.getAttribute("aria-pressed") }; });
  console.log("HEART_BEFORE", JSON.stringify(heart));
  const S = [560, 620];
  await p.mouse.move(S[0], S[1]);
  const rec = await p.screencast({ path: "s22/rec/rec.webm" });
  await sleep(1000);
  await slowMove(p, S, [heart.x, heart.y], 1000);
  await sleep(500);
  await p.mouse.down(); await sleep(90); await p.mouse.up();
  await sleep(2500);
  await rec.stop();
  console.log("HEART_AFTER", JSON.stringify(await p.$eval('.heart-header-btn:not([aria-label="Compartir observación"])', e => ({ label: e.getAttribute("aria-label"), cls: e.className, pressed: e.getAttribute("aria-pressed") }))));
  await p.screenshot({ path: "s22/rec/after.png" });

  // ---------- S24: admin por "Modo administrativo" ----------
  const newTab = new Promise(res => b.once("targetcreated", t => res(t.page())));
  await p.evaluate(() => [...document.querySelectorAll("button")].find(x => /Modo administrativo/.test(x.innerText)).click());
  const a = await newTab;
  await a.setViewport({ width: 1467, height: 700 });
  await sleep(6000);
  console.log("ADMIN_AFTER_HANDOFF", a.url());
  await a.goto("http://localhost:3010/observaciones", { waitUntil: "networkidle0", timeout: 60000 });
  await sleep(2500);
  console.log("ADMIN_URL", a.url());
  const t = await a.evaluate(() => {
    const el = document.querySelector("div.overflow-x-auto.rounded-lg.border.border-border.bg-surface");
    if (!el) return null; const r = el.getBoundingClientRect();
    return { r: [r.x, r.y, r.width, r.height].map(Math.round), rows: el.querySelectorAll("tbody tr").length, head: el.innerText.slice(0, 200) };
  });
  console.log("TABLE", JSON.stringify(t));
  await a.mouse.move(1300, 120);
  const rec2 = await a.screencast({ path: "s24/rec/rec.webm" });
  await sleep(1000);
  if (t) await slowMove(a, [1300, 120], [t.r[0] + t.r[2] * 0.35, t.r[1] + 60], 1400);
  await sleep(3000);
  await rec2.stop();
  await a.screenshot({ path: "s24/rec/after.png" });
  await b.close();
})();
