#!/usr/bin/env node
// KEEP IN SYNC: this file is duplicated in skills/threejs-gameplay-systems/assets/threejs-vite-game/scripts/.
// Single source of truth is the threejs-qa-release copy; edit there first, then mirror byte-for-byte.
import { chromium, devices } from '@playwright/test';
import { mkdir, writeFile } from 'node:fs/promises';
import path from 'node:path';
import { PNG } from 'pngjs';

function parseArgs(argv) {
  const args = {
    url: 'http://127.0.0.1:5188',
    out: 'artifacts/canvas-inspection',
    mobile: false,
    wait: 750,
  };

  for (let i = 0; i < argv.length; i += 1) {
    const value = argv[i];
    if (value === '--url') args.url = argv[++i];
    else if (value === '--out') args.out = argv[++i];
    else if (value === '--mobile') args.mobile = true;
    else if (value === '--wait') {
      args.wait = Number(argv[++i]);
      if (!Number.isFinite(args.wait) || args.wait < 0) {
        throw new Error('--wait requires a finite value >= 0 (milliseconds)');
      }
    }
    else if (value === '-h' || value === '--help') {
      console.log('Usage: inspect-threejs-canvas.mjs [--url URL] [--out DIR] [--mobile] [--wait MS]');
      process.exit(0);
    } else {
      throw new Error(`Unknown argument: ${value}`);
    }
  }

  return args;
}

async function sampleCanvas(page) {
  const locator = page.locator('canvas').first();
  const rect = await locator.boundingBox();
  if (!rect || rect.width < 32 || rect.height < 32) {
    return { ok: false, reason: 'canvas-too-small', rect };
  }

  const buffer = await locator.screenshot();
  const png = PNG.sync.read(buffer);
  let min = 255;
  let max = 0;
  const colors = new Set();
  const stride = Math.max(1, Math.floor((png.width * png.height) / 4096));

  for (let pixel = 0; pixel < png.width * png.height; pixel += stride) {
    const offset = pixel * 4;
    const r = png.data[offset];
    const g = png.data[offset + 1];
    const b = png.data[offset + 2];
    min = Math.min(min, r, g, b);
    max = Math.max(max, r, g, b);
    colors.add(`${r >> 4},${g >> 4},${b >> 4}`);
  }

  const variance = max - min;
  const diagnostics = await page.evaluate(() => {
    const canvas = document.querySelector('canvas');
    return {
      drawingBuffer: canvas
        ? { width: canvas.width, height: canvas.height }
        : null,
      game: window.__THREE_GAME_DIAGNOSTICS__ ?? null,
    };
  });

  // A uniform/blank render has near-zero luminance variance and only a handful
  // of color buckets; require both real variance and color diversity to pass.
  const ok = variance > 8 && colors.size > 3;
  return {
    ok,
    reason: ok ? 'nonblank' : 'low-variance',
    rect,
    drawingBuffer: diagnostics.drawingBuffer,
    variance,
    colorBuckets: colors.size,
    diagnostics: diagnostics.game,
  };
}

async function main() {
  const args = parseArgs(process.argv.slice(2));
  await mkdir(args.out, { recursive: true });

  const browser = await chromium.launch();
  const context = await browser.newContext(args.mobile
    ? { ...devices['iPhone 13'] }
    : { viewport: { width: 1280, height: 720 }, deviceScaleFactor: 1 });
  const page = await context.newPage();
  const consoleErrors = [];
  const pageErrors = [];

  page.on('console', (message) => {
    if (message.type() === 'error') consoleErrors.push(message.text());
  });
  page.on('pageerror', (error) => pageErrors.push(error.message));

  const reportPath = path.join(args.out, args.mobile ? 'mobile.json' : 'desktop.json');
  const screenshotPath = path.join(args.out, args.mobile ? 'mobile.png' : 'desktop.png');

  let result;
  try {
    // Rely on the canvas waitForSelector + warmup wait rather than 'networkidle',
    // which is flaky for games with continuous rAF/streaming.
    await page.goto(args.url, { waitUntil: 'load' });
    await page.waitForSelector('canvas', { state: 'visible', timeout: 10_000 });
    await page.waitForTimeout(args.wait);
    result = await sampleCanvas(page);
    await page.screenshot({ path: screenshotPath, fullPage: false });
  } catch (error) {
    // The most common real failures happen before sampling (nav timeout, no
    // canvas). Always emit a structured report so callers get diagnostics.
    const message = String(error && error.message ? error.message : error);
    const reason = /waiting for selector|canvas/i.test(message) ? 'no-canvas' : 'nav-timeout';
    result = { ok: false, reason, error: message };
    const report = {
      url: args.url,
      mode: args.mobile ? 'mobile' : 'desktop',
      screenshotPath: null,
      result,
      consoleErrors,
      pageErrors,
    };
    await writeFile(reportPath, `${JSON.stringify(report, null, 2)}\n`);
    await browser.close();
    console.log(JSON.stringify(report, null, 2));
    process.exit(1);
  }

  const report = {
    url: args.url,
    mode: args.mobile ? 'mobile' : 'desktop',
    screenshotPath,
    result,
    consoleErrors,
    pageErrors,
  };

  await writeFile(reportPath, `${JSON.stringify(report, null, 2)}\n`);
  await browser.close();

  console.log(JSON.stringify(report, null, 2));

  if (!result.ok || consoleErrors.length > 0 || pageErrors.length > 0) {
    process.exit(1);
  }
}

main().catch((error) => {
  console.error(error);
  process.exit(1);
});
