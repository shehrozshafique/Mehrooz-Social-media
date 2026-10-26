// Renders post.html to a 1080x1350 PNG (2x for a crisp upload).
// Usage: node render.js [output.png]
const { chromium } = require('playwright');
const path = require('path');

const out = path.resolve(process.argv[2] || path.join(__dirname, 'output', 'brand-discovery-ecosystem.png'));

(async () => {
  const browser = await chromium.launch({ args: ['--allow-file-access-from-files'] });
  const page = await browser.newPage({ viewport: { width: 1080, height: 1350 }, deviceScaleFactor: 2 });
  await page.goto('file://' + path.join(__dirname, 'post.html'));
  await page.evaluate(() => document.fonts.ready);
  await page.screenshot({ path: out });
  await browser.close();
  console.log('wrote', out);
})();
