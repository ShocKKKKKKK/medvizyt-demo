# Перевірка: посилання, якорі, залишки кирилиці в англійській версії, мета-теги
import glob, io, json, os, re, sys

os.chdir(sys.argv[1])
bad = []
n = 0
files = ['index.html'] + sorted(glob.glob('poslugy/*/index.html')) + ['en/index.html'] + sorted(glob.glob('en/services/*/index.html'))
for f in files:
	t = io.open(f, encoding='utf-8').read()
	ids = set(re.findall(r'id="([^"]+)"', t))
	for u in re.findall(r'(?:href|src)="([^"]+)"', t):
		if u.startswith(('http', 'tel:', 'mailto:')) or u == '#':
			continue
		p, _, h = u.partition('#')
		n += 1
		if not p:
			if h not in ids:
				bad.append((f, u))
			continue
		tgt = os.path.normpath(os.path.join(os.path.dirname(f), p))
		if not os.path.isfile(tgt):
			bad.append((f, u))
			continue
		if h and 'id="%s"' % h not in io.open(tgt, encoding='utf-8').read():
			bad.append((f, u))
	json.loads(re.search(r'<script type="application/ld\+json">(.*?)</script>', t, re.S).group(1))
	if f.startswith('en'):
		body = re.sub(r'<svg class="sprite".*?</svg>|<script.*?</script>', '', t, flags=re.S)
		cyr = [x for x in re.findall(r'[^<>"]*[А-Яа-яЇїЄєҐґ][^<>"]*', body) if 'Українська версія' not in x]
		if cyr:
			bad.append((f, 'CYR', len(cyr)))
	if t.count('hreflang="x-default"') != 1 or t.count('class="lang"') != 1 or t.count('<h1') != 1:
		bad.append((f, 'structure'))
print(len(files), 'pages,', n, 'links, bad:', len(bad))
for b in bad[:20]:
	print('  ', ascii(b))
