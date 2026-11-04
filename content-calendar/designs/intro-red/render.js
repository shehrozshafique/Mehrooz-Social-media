const { chromium } = require('playwright');
(async () => {
  const b = await chromium.launch({args:['--allow-file-access-from-files']});
  const p = await b.newPage({ viewport: { width: 1080, height: 1350 }, deviceScaleFactor: 1 });
  await p.goto('file://' + process.argv[2] + '/index.html');
  await p.evaluate(() => document.fonts.ready);
  await p.waitForTimeout(500);
  await p.screenshot({ path: process.argv[3] });
  console.log(await p.evaluate(()=>[...document.fonts].filter(f=>f.status==='loaded').length));
  await b.close();
})();
