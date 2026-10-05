import { spawn } from "node:child_process";
import { mkdtempSync } from "node:fs";
import { tmpdir } from "node:os";
import { join } from "node:path";

const chrome = process.env.CHROME_PATH ?? "C:\\Program Files\\Google\\Chrome\\Application\\chrome.exe";
const profile = mkdtempSync(join(tmpdir(), "lunara-map-smoke-"));
const port = 9241;
const browser = spawn(chrome, [
  "--headless=new", "--disable-gpu", "--no-first-run", "--disable-background-networking",
  `--remote-debugging-port=${port}`, `--user-data-dir=${profile}`,
], { stdio: "ignore", windowsHide: true });
const delay = ms => new Promise(resolve => setTimeout(resolve, ms));
const destinationName = process.env.DESTINATION ?? "LB Nagar, Hyderabad";
const expectUnavailable = process.env.EXPECT_UNAVAILABLE === "1";

async function main() {
  let page;
  for (let attempt = 0; attempt < 50; attempt++) {
    try {
      const response = await fetch(`http://127.0.0.1:${port}/json/new?${encodeURIComponent("http://localhost:3000/")}`, { method: "PUT" });
      if (response.ok) { page = await response.json(); break; }
    } catch { /* Chrome is starting. */ }
    await delay(200);
  }
  if (!page) throw new Error("Chrome did not start");
  const socket = new WebSocket(page.webSocketDebuggerUrl);
  await new Promise((resolve, reject) => { socket.addEventListener("open", resolve, { once: true }); socket.addEventListener("error", reject, { once: true }); });
  let nextId = 0;
  const pending = new Map();
  socket.addEventListener("message", event => {
    const message = JSON.parse(event.data);
    if (pending.has(message.id)) { pending.get(message.id)(message); pending.delete(message.id); }
  });
  const command = (method, params = {}) => new Promise(resolve => {
    const id = ++nextId;
    pending.set(id, resolve);
    socket.send(JSON.stringify({ id, method, params }));
  });
  const evaluate = async expression => (await command("Runtime.evaluate", { expression, returnByValue: true })).result?.result?.value;
  await command("Browser.grantPermissions", { permissions: ["geolocation"], origin: "http://localhost:3000" });
  await command("Emulation.setGeolocationOverride", { latitude: 17.411568, longitude: 78.527463, accuracy: 10 });
  for (let attempt = 0; attempt < 50; attempt++) {
    if (await evaluate("!!document.querySelector('#to')")) break;
    await delay(200);
  }
  await delay(2500);
  await evaluate(`(() => {
    const input = document.querySelector('#to');
    const setter = Object.getOwnPropertyDescriptor(HTMLInputElement.prototype, 'value').set;
    setter.call(input, ${JSON.stringify(destinationName)});
    input.dispatchEvent(new Event('input', { bubbles: true }));
    document.querySelector('form.search-card button.primary').click();
  })()`);
  let state;
  for (let attempt = 0; attempt < 90; attempt++) {
    state = await evaluate(`(() => {
      const map = document.querySelector('.map-canvas');
      const start = document.querySelector('.route-marker-start');
      const destination = document.querySelector('.route-marker-destination');
      const rect = map?.getBoundingClientRect();
      const inside = marker => {
        if (!marker || !rect) return false;
        const point = marker.getBoundingClientRect();
        return point.right >= rect.left && point.left <= rect.right && point.bottom >= rect.top && point.top <= rect.bottom;
      };
      return {
        url: location.href, demo: document.body.innerText.includes('DEMO DATA'),
        start: start?.innerText, destination: destination?.innerText,
        header: document.querySelector('.map-route-header')?.innerText,
        mapLoaded: !!document.querySelector('.maplibregl-canvas'),
        routeCards: document.querySelectorAll('.route-card').length,
        formDestination: document.querySelector('#to')?.value,
        formOrigin: document.querySelector('#from')?.value,
        alert: document.querySelector('[role=alert]')?.innerText,
        selectedCard: document.querySelector('.route-card.selected')?.innerText.slice(0, 110),
        hasInventedDistance: document.body.innerText.includes('8.1 km estimated') || document.body.innerText.includes('31 min'),
        startInside: inside(start), destinationInside: inside(destination),
        mapRect: rect && { x: rect.x, y: rect.y, width: rect.width, height: rect.height },
        startRect: start && { x: start.getBoundingClientRect().x, y: start.getBoundingClientRect().y },
        destinationRect: destination && { x: destination.getBoundingClientRect().x, y: destination.getBoundingClientRect().y },
      };
    })()`);
    if (expectUnavailable && state?.alert?.includes('Live route unavailable')) break;
    if (state?.routeCards === 3 && state?.start && state?.destination && state.startInside && state.destinationInside) break;
    await delay(1000);
  }
  if (expectUnavailable) {
    console.log(JSON.stringify(state));
    socket.close();
    if (!state?.alert?.includes("Live route unavailable") || state?.routeCards !== 0 || state?.demo || state?.hasInventedDistance) process.exitCode = 1;
    return;
  }
  await evaluate("document.querySelector('.route-marker-start')?.click()");
  await delay(200);
  const startPopup = await evaluate("document.querySelector('.route-popup')?.innerText");
  await evaluate("document.querySelector('.route-marker-destination')?.click()");
  await delay(200);
  const destinationPopup = await evaluate("document.querySelector('.route-popup')?.innerText");
  await evaluate("document.querySelector('[aria-label^=\"Balanced route\"]')?.click()");
  await delay(700);
  const switched = await evaluate("document.querySelector('.route-card.selected .badge')?.innerText");
  const switchedMarkers = await evaluate("document.querySelectorAll('.route-marker').length");
  console.log(JSON.stringify({ ...state, startPopup, destinationPopup, switched, switchedMarkers }));
  socket.close();
  if (state?.demo || !state?.url.includes("origin_label=My+Current+Location") || !state?.url.includes("travel_mode=driving") || !state?.header?.includes("My Current Location") || !state?.header?.includes(destinationName) || !state?.startInside || !state?.destinationInside || !startPopup?.includes("Start") || !destinationPopup?.includes("Destination") || switched !== "BALANCED" || switchedMarkers !== 2) process.exitCode = 1;
}

try { await main(); } finally { browser.kill(); }
