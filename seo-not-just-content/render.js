// Renders post.html to a 1080x1350 (4:5) PNG at 2x pixel density, plus a 1x copy.
// Usage: node render.js
const { chromium } = require('playwright');
const path = require('path');

(async () => {
  const browser = await chromium.launch({ args: ['--allow-file-access-from-files'] });
  for (const scale of [2, 1]) {
    const page = await browser.newPage({ viewport: { width: 1080, height: 1350 }, deviceScaleFactor: scale });
    await page.goto('file://' + path.join(__dirname, 'post.html'));
    await page.evaluate(() => Promise.all([document.fonts.ready, ...[...document.images].map(i => i.decode().catch(() => {}))]));
    const out = path.join(__dirname, 'output', `seo-not-just-content${scale === 2 ? '@2x' : ''}.png`);
    await page.screenshot({ path: out });
    console.log('wrote', out);
    await page.close();
  }
  await browser.close();
})();
