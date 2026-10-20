import re
def path(n): return re.search(r'd="([^"]*)"',open(f'icons/{n}.svg').read()).group(1)
crown=open('icons/crown.svg').read().replace('<svg ','<svg class="crown" ',1)
ic = {
 'shopify': f'<svg viewBox="0 0 24 24"><path fill="#7AB55C" d="{path("shopify")}"/></svg>',
 'ghl': '''<svg viewBox="0 0 100 100">
   <g stroke-linejoin="round">
   <path fill="#F9B91A" d="M21 14 L38 34 H27 V86 H15 V34 H4 Z"/>
   <path fill="#3D8BFD" d="M50 40 L67 60 H56 V86 H44 V60 H33 Z"/>
   <path fill="#3DB24A" d="M79 14 L96 34 H85 V86 H73 V34 H62 Z"/></g></svg>''',
 'n8n': f'<svg viewBox="0 0 24 24"><path fill="#EA4B71" d="{path("n8n")}"/></svg>',
 'meta': f'''<svg viewBox="0 0 24 24"><defs><linearGradient id="mg" x1="0" y1="0" x2="1" y2="0.3"><stop offset="0" stop-color="#0064E0"/><stop offset=".6" stop-color="#0082FB"/><stop offset="1" stop-color="#0064E0"/></linearGradient></defs><path fill="url(#mg)" d="{path("meta")}"/></svg>''',
 'wp': f'<svg viewBox="0 0 24 24"><path fill="#21759B" d="{path("wordpress")}"/></svg>',
 'gads': '''<svg viewBox="0 0 100 100"><g stroke-linecap="round" stroke-width="23" fill="none">
   <line x1="27" y1="76" x2="50" y2="25" stroke="#FBBC04"/>
   <line x1="50" y1="25" x2="76" y2="76" stroke="#4285F4"/></g>
   <circle cx="27" cy="76" r="11.5" fill="#34A853"/></svg>''',
 'adobe': '<span class="adobe">Adobe</span>',
 'alast': '''<svg viewBox="70 70 360 360"><path fill="#0B0B0B" d="M250 105 L398 362 L100 362 Z"/>
<path fill="#fff" d="M256 182 L322 362 L232 362 L280 252 Z"/>
<path fill="#fff" d="M190 334 L258 234 L270 243 L204 338 Z"/>
<path fill="#0B0B0B" d="M318 132 c10 -9 30 -6 33 8 c3 14 -10 26 -24 30 c6 -6 7 -14 2 -18 c-8 -4 -17 -11 -11 -20z"/></svg>''',
}
icons=''.join(f'<div class="ic {k}">{v}</div>' for k,v in ic.items())
import base64
mark='data:image/png;base64,'+base64.b64encode(open('build/mark.png','rb').read()).decode()
html=open('banner.tpl.html').read().replace('{{MARK}}',mark).replace('{{ICONS}}',icons).replace('{{CROWN}}',crown)
open('build/banner.html','w').write(html)
