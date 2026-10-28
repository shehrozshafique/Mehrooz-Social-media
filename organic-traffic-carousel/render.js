// Renders each .slide in carousel.html to its own 1080x1080 PNG (2x),
// then combines them into one PDF for LinkedIn document upload.
// Usage: node render.js
const { chromium } = require('playwright');
const path = require('path');
const fs = require('fs');

const outDir = path.join(__dirname, 'output');
fs.mkdirSync(outDir, { recursive: true });

(async () => {
  const browser = await chromium.launch({ args: ['--allow-file-access-from-files'] });
  const page = await browser.newPage({ viewport: { width: 1080, height: 1080 }, deviceScaleFactor: 2 });
  await page.goto('file://' + path.join(__dirname, 'carousel.html'));
  await page.evaluate(() => document.fonts.ready);
  const slides = await page.$$('.slide');
  for (let i = 0; i < slides.length; i++) {
    const file = path.join(outDir, `slide-${i + 1}.png`);
    await slides[i].screenshot({ path: file });
    console.log('wrote', file);
  }
  await browser.close();
})();
