// Renders animation.html frame-by-frame into an MP4 with ffmpeg.
// Usage: node render.js [output.mp4] [--fps 30] [--stills 2,8,15]
const { chromium } = require('playwright');
const { spawn } = require('child_process');
const fs = require('fs');
const path = require('path');

const args = process.argv.slice(2);
const opt = (name, def) => { const i = args.indexOf(name); return i >= 0 ? args[i + 1] : def; };
const fps = Number(opt('--fps', 30));
const stills = opt('--stills', null);
const out = path.resolve(args.find(a => a.endsWith('.mp4')) || path.join(__dirname, 'output', 'google-spider-crawl.mp4'));

(async () => {
  const browser = await chromium.launch({ args: ['--allow-file-access-from-files'] });
  const page = await browser.newPage({ viewport: { width: 1080, height: 1920 } });
  await page.goto('file://' + path.join(__dirname, 'animation.html'));
  await page.evaluate(() => window.ready);
  const grab = t => page.evaluate(t => { window.draw(t); return document.getElementById('c').toDataURL('image/png'); }, t);

  if (stills) {
    const dir = path.join(__dirname, 'output', 'stills');
    fs.mkdirSync(dir, { recursive: true });
    for (const t of stills.split(',').map(Number)) {
      const data = await grab(t);
      fs.writeFileSync(path.join(dir, `t${t}.png`), Buffer.from(data.split(',')[1], 'base64'));
    }
    await browser.close();
    return;
  }

  fs.mkdirSync(path.dirname(out), { recursive: true });
  const duration = await page.evaluate(() => window.DURATION);
  const total = Math.round(duration * fps);
  const ff = spawn('ffmpeg', ['-y', '-f', 'image2pipe', '-framerate', String(fps), '-i', '-',
    '-f', 'lavfi', '-i', 'anullsrc=channel_layout=stereo:sample_rate=44100',
    '-c:v', 'libx264', '-preset', 'slow', '-crf', '18', '-pix_fmt', 'yuv420p',
    '-c:a', 'aac', '-shortest', '-movflags', '+faststart', out], { stdio: ['pipe', 'ignore', 'inherit'] });
  for (let f = 0; f < total; f++) {
    const data = await grab(f / fps);
    if (!ff.stdin.write(Buffer.from(data.split(',')[1], 'base64'))) await new Promise(r => ff.stdin.once('drain', r));
    if (f % 150 === 0) console.log(`frame ${f}/${total}`);
  }
  ff.stdin.end();
  await new Promise(r => ff.on('close', r));
  await browser.close();
  console.log('wrote', out);
})();
