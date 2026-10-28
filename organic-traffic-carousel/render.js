// Renders each .slide in carousel.html as its own separate post:
// output/post-N/post.png (2160x2160) and output/post-N/post.pdf (one page).
// Usage: node render.js
const { chromium } = require('playwright');
const path = require('path');
const fs = require('fs');

const outDir = path.join(__dirname, 'output');

(async () => {
  const browser = await chromium.launch({ args: ['--allow-file-access-from-files'] });
  const page = await browser.newPage({ viewport: { width: 1080, height: 1080 }, deviceScaleFactor: 2 });
  await page.goto('file://' + path.join(__dirname, 'carousel.html'));
  await page.evaluate(() => document.fonts.ready);
  const slides = await page.$$('.slide');
  for (let i = 0; i < slides.length; i++) {
    const dir = path.join(outDir, `post-${i + 1}`);
    fs.mkdirSync(dir, { recursive: true });
    await slides[i].screenshot({ path: path.join(dir, 'post.png') });
    console.log('wrote', dir);
  }
  await browser.close();
})();
