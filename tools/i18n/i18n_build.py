# Збирання англійської версії з української: en/ + перемикач мов + hreflang
import glob, io, json, os, re, sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from en_map import M

ROOT = sys.argv[1]
SITE = 'https://shockkkkkkk.github.io/medvizyt-demo'
SLUGS = {
	'dovidka-083': 'drivers-medical-083', 'ogliad-086': 'medical-checkup-086', 'karta-shcheplen-063': 'vaccination-record-063',
	'medychna-knyzhka': 'medical-book', 'dovidka-100-2': 'psychiatric-certificate-100-2', 'dovidka-u-basein': 'swimming-pool-certificate',
	'fliuorohrafiia': 'chest-x-ray',
}
M['Мова сайту'] = 'Site language'
CYR = re.compile('[А-Яа-яІіЇїЄєҐґ]')
CODES_EN = re.compile(r'(?<![\w>])(100-2/o|083/o|086/o|063/o|1-OMK)(?!</span>)')
missing = []


def read(p):
	return io.open(p, encoding='utf-8').read()


def write(p, t):
	os.makedirs(os.path.dirname(p), exist_ok=True)
	io.open(p, 'w', encoding='utf-8', newline='\n').write(t)


def tr(s, where):
	key = s.strip()
	if not key or not CYR.search(key):
		return s
	if key not in M:
		missing.append((where, key))
		return s
	return s.replace(key, M[key])


def tr_json(o, where):
	if isinstance(o, str):
		return tr(o, where)
	if isinstance(o, dict):
		return {k: tr_json(v, where) for k, v in o.items()}
	if isinstance(o, list):
		return [tr_json(v, where) for v in o]
	return o


def lang_block(active, href, indent):
	uk = '<span class="lang__item lang__item--active" aria-current="true">UA</span>' if active == 'uk' else \
		'<a class="lang__item" href="%s" hreflang="uk" lang="uk" aria-label="Українська версія">UA</a>' % href
	en = '<span class="lang__item lang__item--active" aria-current="true">EN</span>' if active == 'en' else \
		'<a class="lang__item" href="%s" hreflang="en" lang="en" aria-label="English version">EN</a>' % href
	label = 'Мова сайту' if active == 'uk' else 'Site language'
	return '<div class="lang" role="group" aria-label="%s">\n%s\t%s\n%s\t%s\n%s</div>' % (label, indent, uk, indent, en, indent)


def hreflang(uk_path, en_path):
	return ('\t<link rel="alternate" hreflang="uk" href="%s%s">\n\t<link rel="alternate" hreflang="en" href="%s%s">\n'
		'\t<link rel="alternate" hreflang="x-default" href="%s%s">\n') % (SITE, uk_path, SITE, en_path, SITE, uk_path)


pages = [('index.html', None)] + [('poslugy/%s/index.html' % s, s) for s in SLUGS]
report = []
for rel, slug in pages:
	path = os.path.join(ROOT, rel)
	t = read(path)
	uk_path = '/' if slug is None else '/poslugy/%s/' % slug
	en_path = '/en/' if slug is None else '/en/services/%s/' % SLUGS[slug]
	to_en = 'en/index.html' if slug is None else '../../en/services/%s/index.html' % SLUGS[slug]
	to_uk = '../index.html' if slug is None else '../../../poslugy/%s/index.html' % slug

	# ---------- українська сторінка: перемикач і hreflang ----------
	if 'class="lang"' not in t:
		t = t.replace('\t\t\t\t<a class="header__phone"', '\t\t\t\t' + lang_block('uk', to_en, '\t\t\t\t') + '\n\t\t\t\t<a class="header__phone"', 1)
		assert 'class="lang"' in t
	if 'hreflang="x-default"' not in t:
		t, n = re.subn(r'(\t<link rel="canonical"[^\n]*\n)', lambda m: m.group(1) + hreflang(uk_path, en_path), t, count=1)
		assert n == 1, rel
	write(path, t)

	# ---------- англійська сторінка ----------
	e = re.sub(r'<span class="nowrap">(.*?)</span>', r'\1', t)
	e = re.sub(r'[ \t]*<!--(.*?)-->\n?', lambda m: m.group(0) if 'БЛОК ЦІНИ' in m.group(1) else '', e, flags=re.S)
	e = e.replace('<!-- БЛОК ЦІНИ: єдиний блок, що змінюється між сторінками послуг -->', '<!-- PRICE BLOCK: the only block that differs between service pages -->')

	# JSON-LD
	def ld(m):
		return '<script type="application/ld+json">%s</script>' % json.dumps(tr_json(json.loads(m.group(1)), rel), ensure_ascii=False)
	e = re.sub(r'<script type="application/ld\+json">(.*?)</script>', ld, e, flags=re.S)

	# службові фрагменти не перекладаємо
	stash = []
	def keep(m):
		stash.append(m.group(0))
		return '\x00%d\x00' % (len(stash) - 1)
	e = re.sub(r'<svg class="sprite".*?</svg>|<script.*?</script>', keep, e, flags=re.S)

	e = re.sub(r'<title>(.*?)</title>', lambda m: '<title>%s</title>' % tr(m.group(1), rel), e)
	e = re.sub(r'((?:aria-label|placeholder|content|value|alt)=")([^"]*)(")', lambda m: m.group(1) + tr(m.group(2), rel) + m.group(3), e)
	e = re.sub(r'(?<=>)[^<\x00]+(?=<)', lambda m: tr(m.group(0), rel), e)
	e = re.sub(r'\x00(\d+)\x00', lambda m: stash[int(m.group(1))], e)

	# номери форм не розриваються
	head, sep, body = e.partition('<body>')
	body = re.sub(r'(?<=>)[^<]+(?=<)', lambda m: CODES_EN.sub(r'<span class="nowrap">\1</span>', m.group(0)), body)
	body = re.sub(r'<option[^>]*>.*?</option>', lambda m: re.sub(r'<span class="nowrap">(.*?)</span>', r'\1', m.group(0)), body, flags=re.S)
	body = re.sub(r'(<svg class="sprite".*?</svg>)', lambda m: re.sub(r'<span class="nowrap">(.*?)</span>', r'\1', m.group(1)), body, flags=re.S)
	e = head + sep + body

	# мова, адреси, шляхи
	e = e.replace('<html lang="uk">', '<html lang="en">').replace('content="uk_UA"', 'content="en_US"')
	for uk_slug, en_slug in SLUGS.items():
		e = e.replace('%s/poslugy/%s/' % (SITE, uk_slug), '%s/en/services/%s/' % (SITE, en_slug))
	e = e.replace('"%s/"' % SITE, '"%s/en/"' % SITE).replace('%s/#services' % SITE, '%s/en/#services' % SITE)
	# hreflang мають вказувати на обидві версії: відновлюємо українські адреси
	e = re.sub(r'\t<link rel="alternate"[^\n]*\n', '', e)
	e, n = re.subn(r'(\t<link rel="canonical"[^\n]*\n)', lambda m: m.group(1) + hreflang(uk_path, en_path), e, count=1)
	assert n == 1
	if slug is None:
		e = re.sub(r'(href|src)="assets/', r'\1="../assets/', e)
		e = re.sub(r'href="poslugy/([a-z0-9-]+)/index\.html"', lambda m: 'href="services/%s/index.html"' % SLUGS[m.group(1)], e)
	else:
		e = e.replace('"../../assets/', '"../../../assets/')
		e = re.sub(r'href="\.\./\.\./poslugy/([a-z0-9-]+)/index\.html"', lambda m: 'href="../../services/%s/index.html"' % SLUGS[m.group(1)], e)
	e = re.sub(r'<div class="lang".*?</div>', lambda m: lang_block('en', to_uk, '\t\t\t\t'), e, count=1, flags=re.S)
	e = e.replace('Website by <a', 'Website by <a')

	out = os.path.join(ROOT, 'en', 'index.html') if slug is None else os.path.join(ROOT, 'en', 'services', SLUGS[slug], 'index.html')
	write(out, e)
	title = re.search(r'<title>(.*?)</title>', e).group(1)
	desc = re.search(r'name="description" content="([^"]*)"', e).group(1)
	left = sorted(set(x for x in re.findall(r'>([^<]*[А-Яа-яІіЇїЄєҐґ][^<]*)<', re.sub(r'<script.*?</script>', '', e, flags=re.S))))
	report.append('%-34s title %2d desc %3d cyr-left %d' % (en_path, len(title), len(desc), len(left)))

print('\n'.join(report))
uniq = []
for w, k in missing:
	if k not in uniq:
		uniq.append(k)
print('MISSING', len(uniq))
for k in uniq:
	print('  ' + k)

urls = ['/'] + ['/poslugy/%s/' % s for s in SLUGS] + ['/en/'] + ['/en/services/%s/' % s for s in SLUGS.values()]
write(os.path.join(ROOT, 'sitemap.xml'), '<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n%s\n</urlset>\n'
	% '\n'.join('\t<url><loc>%s%s</loc></url>' % (SITE, u) for u in urls))
