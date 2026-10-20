const { chromium } = require('playwright');
(async()=>{const [,,inp,out,w,h,s]=process.argv;const b=await chromium.launch();const p=await b.newPage({viewport:{width:+w,height:+h},deviceScaleFactor:+s});
await p.goto('file://'+inp,{waitUntil:'networkidle'});await p.evaluate(()=>document.fonts.ready);await p.waitForTimeout(500);await p.screenshot({path:out});await b.close();})();
