import { spawn } from "node:child_process";
import { mkdtempSync } from "node:fs";
import { tmpdir } from "node:os";
import { join } from "node:path";

const chrome = process.env.CHROME_PATH ?? "C:\\Program Files\\Google\\Chrome\\Application\\chrome.exe";
const profile = mkdtempSync(join(tmpdir(), "lunara-route-smoke-"));
const debuggingPort = 9238;
const browser = spawn(chrome, [
  "--headless=new", "--disable-gpu", "--no-first-run", "--disable-background-networking",
  `--remote-debugging-port=${debuggingPort}`, `--user-data-dir=${profile}`,
], { stdio: "ignore", windowsHide: true });

const delay = ms => new Promise(resolve => setTimeout(resolve, ms));
const routeUrl = new URL("http://localhost:3000/routes");
routeUrl.search = new URLSearchParams({
  origin: "Osmania University, Hyderabad",
  destination: "Secunderabad Railway Station, Hyderabad",
  departure_time: "2026-10-05T19:15:00+05:30",
  preference: "30",
}).toString();

async function target() {
  for (let attempt = 0; attempt < 50; attempt++) {
    try {
      const response = await fetch(`http://127.0.0.1:${debuggingPort}/json/new?${encodeURIComponent(routeUrl.href)}`, { method: "PUT" });
      if (response.ok) return response.json();
    } catch { /* Browser is still starting. */ }
    await delay(200);
  }
  throw new Error("Headless Chrome did not start");
}

async function main() {
  const page = await target();
  const socket = new WebSocket(page.webSocketDebuggerUrl);
  await new Promise((resolve, reject) => { socket.addEventListener("open", resolve, { once: true }); socket.addEventListener("error", reject, { once: true }); });
  let nextId = 0;
  const pending = new Map();
  socket.addEventListener("message", event => {
    const message = JSON.parse(event.data);
    if (pending.has(message.id)) { pending.get(message.id)(message); pending.delete(message.id); }
  });
  const evaluate = expression => new Promise(resolve => {
    const id = ++nextId;
    pending.set(id, message => resolve(message.result?.result?.value));
    socket.send(JSON.stringify({ id, method: "Runtime.evaluate", params: { expression, returnByValue: true } }));
  });
  let rendered = "";
  for (let attempt = 0; attempt < 70; attempt++) {
    rendered = await evaluate("document.body?.innerText || ''");
    if (rendered.includes("OpenStreetMap pedestrian routing")) break;
    await delay(1000);
  }
  const live = rendered.includes("OpenStreetMap pedestrian routing");
  const demo = rendered.includes("DEMO DATA");
  const three = ["SAFEST", "BALANCED", "FASTEST"].every(label => rendered.toUpperCase().includes(label));
  console.log(JSON.stringify({ live, demo, three, url: routeUrl.href, browserUrl: await evaluate("location.href"), readyState: await evaluate("document.readyState"), excerpt: rendered.slice(0, 500) }));
  socket.close();
  if (!live || demo || !three) process.exitCode = 1;
}

try { await main(); } finally { browser.kill(); }
