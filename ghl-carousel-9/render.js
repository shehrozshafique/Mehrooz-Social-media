// Renders carousel.html (one 9720x1350 strip) and slices it into nine 1080x1350 PNG slides.
// Usage: node render.js
const { chromium } = require('playwright');
const fs = require('fs');
const path = require('path');

(async () => {
  const browser = await chromium.launch({ args: ['--allow-file-access-from-files'] });
  const page = await browser.newPage({ viewport: { width: 9720, height: 1350 } });
  await page.goto('file://' + path.join(__dirname, 'carousel.html'));
  await page.evaluate(() => Promise.all([document.fonts.ready, ...[...document.images].map(i => i.decode().catch(() => {}))]));
  const out = path.join(__dirname, 'output');
  fs.mkdirSync(out, { recursive: true });
  await page.screenshot({ path: path.join(out, 'ghl-carousel-strip.png') });
  for (let i = 0; i < 9; i++) {
    await page.screenshot({ path: path.join(out, `ghl-slide-${i + 1}.png`), clip: { x: i * 1080, y: 0, width: 1080, height: 1350 } });
  }
  await browser.close();
  console.log('wrote', out);
})();
