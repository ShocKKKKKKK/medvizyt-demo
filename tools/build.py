# -*- coding: utf-8 -*-
"""Збирає статичні HTML-сторінки сайту двома мовами.

Запуск з кореня проєкту:  python3 tools/build.py
Українська — у корені сайту, російська — у папці ru/.
Тексти сторінок: content.py (UA) і content_ru.py (RU), рядки інтерфейсу: i18n.py.
Шапка, підвал, форма і вибір міста однакові на всіх сторінках, тому правки
робимо в цих файлах і перезбираємо, а не редагуємо HTML вручну.
"""
import html
import json
import os
import sys
from urllib.parse import quote

sys.path.insert(0, os.path.dirname(__file__))
import content as content_uk  # noqa: E402
import content_ru  # noqa: E402
from i18n import UI  # noqa: E402

LANGS = {'uk': content_uk, 'ru': content_ru}
PREFIX = {'uk': '', 'ru': 'ru/'}

# Поточна мова збірки: встановлюється у use()
LANG = 'uk'
T = UI['uk']
SITE = HOME = PAGES = SERVICES = CITIES = STEP_TEXTS = None


def use(lang):
	global LANG, T, SITE, HOME, PAGES, SERVICES, CITIES, STEP_TEXTS
	c = LANGS[lang]
	LANG, T = lang, UI[lang]
	SITE, HOME, PAGES, SERVICES, CITIES, STEP_TEXTS = c.SITE, c.HOME, c.PAGES, c.SERVICES, c.CITIES, c.STEP_TEXTS

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SPRITE = open(os.path.join(os.path.dirname(__file__), 'partials', 'sprite.svg'), encoding='utf-8').read().strip()

e = html.escape


def icon(name, cls='icon'):
	return f'<svg class="{cls}" aria-hidden="true"><use href="#{name}"></use></svg>'


def nb(text):
	"""Номери форм не розриваємо на два рядки."""
	for code in ('083/о', '086/о', '063/о', '063/o', '100-2/о', '1-ОМК', '140/о', '122-2/о', '086-1/о'):
		text = text.replace(code, f'<span class="nowrap">{code}</span>')
	return text


def link(root, slug, lang=None):
	"""Шлях до сторінки. root — шлях до кореня сайту (там лежать assets)."""
	base = root + PREFIX[lang or LANG]
	return f'{base}{slug}/index.html' if slug else f'{base}index.html'


def page_url(slug, lang=None):
	return SITE['domain'] + PREFIX[lang or LANG] + (f'{slug}/' if slug else '')


def lang_switch(root, slug):
	items = []
	for code, label in (('uk', 'UA'), ('ru', 'RU')):
		if code == LANG:
			items.append(f'<span class="lang__link lang__link--active" aria-current="true">{label}</span>')
		else:
			items.append(f'<a class="lang__link" href="{link(root, slug, code)}" hreflang="{UI[code]["html_lang"]}" lang="{UI[code]["html_lang"]}">{label}</a>')
	return f'<nav class="lang" aria-label="{T["lang_label"]}">{"".join(items)}</nav>'


# --------------------------------------------------------------------------
# Спільні частини
# --------------------------------------------------------------------------
def head(root, slug, title, description):
	url = page_url(slug)
	alternates = '\n'.join(
		f'\t<link rel="alternate" hreflang="{UI[c]["html_lang"]}" href="{page_url(slug, c)}">' for c in LANGS
	) + f'\n\t<link rel="alternate" hreflang="x-default" href="{page_url(slug, "uk")}">'
	ld = {
		'@context': 'https://schema.org',
		'@graph': [
			{
				'@type': 'MedicalBusiness',
				'@id': SITE['domain'] + '#org',
				'name': 'ПРОФ МЕД ДОКС',
				'alternateName': 'Med-assistant',
				'url': SITE['domain'],
				'telephone': SITE['phone_href'].replace('tel:', ''),
				'address': {'@type': 'PostalAddress', 'addressLocality': 'Київ', 'streetAddress': 'провулок Бехтерівський, 8', 'addressCountry': 'UA'},
				'areaServed': 'UA',
				'openingHoursSpecification': [
					{'@type': 'OpeningHoursSpecification', 'dayOfWeek': ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday'], 'opens': '08:00', 'closes': '22:00'},
					{'@type': 'OpeningHoursSpecification', 'dayOfWeek': ['Saturday', 'Sunday'], 'opens': '09:00', 'closes': '18:00'},
				],
			},
			{'@type': 'WebSite', 'name': 'Med-assistant', 'url': SITE['domain'], 'inLanguage': T['html_lang']},
		],
	}
	return f'''<!DOCTYPE html>
<html lang="{T['html_lang']}">
<head>
	<meta charset="UTF-8">
	<meta name="viewport" content="width=device-width, initial-scale=1">
	<title>{e(title)}</title>
	<meta name="description" content="{e(description)}">
	<!-- Поки сайт лежить на тестовому хостингу, він закритий від індексації. При запуску на med-assistant.net повернути index, follow -->
	<link rel="canonical" href="{url}">
{alternates}
	<meta name="robots" content="noindex, nofollow">
	<meta name="theme-color" content="#0a7f79">
	<link rel="icon" href="{root}assets/img/brand/logo-32.webp" type="image/webp">
	<link rel="apple-touch-icon" href="{root}assets/img/brand/logo-180.webp">
	<meta property="og:type" content="website">
	<meta property="og:locale" content="{T['og_locale']}">
	<meta property="og:site_name" content="Med-assistant">
	<meta property="og:title" content="{e(title)}">
	<meta property="og:description" content="{e(description)}">
	<meta property="og:url" content="{url}">
	<meta name="twitter:card" content="summary">
	<script type="application/ld+json">{json.dumps(ld, ensure_ascii=False)}</script>
	<!-- Стартові стани анімацій: клас ставиться синхронно, до стилів -->
	<script>
		if (!window.matchMedia('(prefers-reduced-motion: reduce)').matches) {{
			document.documentElement.classList.add('js-anim');
		}}
	</script>
	<link rel="preconnect" href="https://fonts.googleapis.com">
	<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
	<link href="https://fonts.googleapis.com/css2?family=Manrope:wght@400;500;600;700;800&display=swap" rel="stylesheet">
	<link rel="stylesheet" href="{root}assets/css/style.css">
</head>
<body>
<!-- Спрайт іконок вбудовано: зовнішній <use> не працює при відкритті з диска. Іконки: Lucide (ISC), Simple Icons (CC0) -->
<svg class="sprite" xmlns="http://www.w3.org/2000/svg" aria-hidden="true">
	{SPRITE.replace(chr(10), chr(10) + chr(9))}
</svg>
'''


def logo(root):
	return f'<a class="logo" href="{link(root, "")}" aria-label="{T['to_home']}"><img class="logo__img" src="{root}assets/img/brand/logo.webp" width="415" height="69" alt="med-assistant"></a>'


def header(root, current):
	sub = '\n'.join(
		f'\t\t\t\t\t\t\t<li><a class="menu__sub-link{" menu__sub-link--active" if s["slug"] == current else ""}" href="{link(root, s["slug"])}"'
		f'{" aria-current=\"page\"" if s["slug"] == current else ""}>{e(s["menu"])} <span class="menu__sub-code">{nb(e(s["code"]))}</span></a></li>'
		for s in SERVICES
	)
	home = link(root, '')
	return f'''<div class="wrapper">

	<header class="header" data-header>
		<div class="header__container">
			{logo(root)}

			<nav class="menu" id="menu" aria-label="{T['menu_label']}" data-lp>
				<ul class="menu__list">
					<li class="menu__item"><a class="menu__link" href="{home}"{' aria-current="page"' if not current else ''}>{T['nav_home']}</a></li>
					<li class="menu__item">
						<button class="menu__link" type="button" aria-expanded="false" aria-controls="menu-services" data-dropdown>
							{T['nav_services']}
							{icon('chevron')}
						</button>
						<ul class="menu__sub" id="menu-services">
{sub}
						</ul>
					</li>
					<li class="menu__item"><a class="menu__link" href="#how">{T['nav_how']}</a></li>
					<li class="menu__item"><a class="menu__link" href="#contacts">{T['nav_contacts']}</a></li>
				</ul>
				<a class="button button--wide menu__cta" href="#request">{T['cta']}</a>
				<div class="menu__lang">{lang_switch(root, current)}</div>
			</nav>

			<div class="header__actions">
				{lang_switch(root, current)}
				<button class="header__city" type="button" aria-haspopup="dialog" aria-controls="city" data-city-open>
					{icon('pin')}
					<span data-city-label>{T['all_country']}</span>
					{icon('chevron', 'icon header__city-arrow')}
				</button>
				<a class="header__phone" href="{SITE['phone_href']}" aria-label="{T['call']}">
					{icon('phone')}
					<span>{SITE['phone']}</span>
				</a>
				<button class="header__burger" type="button" aria-label="{T['open_menu']}" aria-expanded="false" aria-controls="menu" data-burger><span></span></button>
			</div>
		</div>
	</header>
'''


def footer(root, faq='#faq'):
	services = '\n'.join(
		f'\t\t\t\t\t\t<li><a class="footer__link" href="{link(root, s["slug"])}">{nb(e(s["menu"]))}</a></li>' for s in SERVICES
	)
	hours = '<br>'.join(f'{d} — {t}' for d, t in SITE['hours'])
	return f'''	<footer class="footer" id="contacts">
		<div class="footer__container">
			<div class="footer__top">
				<div class="footer__about">
					{logo(root)}
					<p class="footer__text">{T['footer_text']}</p>
					<div class="footer__socials">
						<a class="footer__social" href="{SITE['telegram']}" target="_blank" rel="noopener" aria-label="Telegram">{icon('telegram')}</a>
						<a class="footer__social" href="{SITE['phone_href']}" aria-label="{T['call']}">{icon('phone')}</a>
					</div>
				</div>
				<div class="footer__col">
					<h3 class="footer__title">{T['footer_services']}</h3>
					<ul class="footer__list">
{services}
					</ul>
				</div>
				<div class="footer__col">
					<h3 class="footer__title">{T['footer_nav']}</h3>
					<ul class="footer__list">
						<li><a class="footer__link" href="{link(root, '')}">{T['nav_home']}</a></li>
						<li><a class="footer__link" href="#how">{T['nav_how']}</a></li>
						<li><a class="footer__link" href="{faq}">{T['faq_link']}</a></li>
						<li><a class="footer__link" href="#request">{T['cta']}</a></li>
						<li><button class="footer__link footer__link--button" type="button" aria-haspopup="dialog" aria-controls="city" data-city-open>{T['choose_city']}</button></li>
					</ul>
				</div>
				<div class="footer__col">
					<h3 class="footer__title">{T['footer_contacts']}</h3>
					<ul class="footer__list">
						<li><a class="footer__phone" href="{SITE['phone_href']}"><span>{SITE['phone']}</span></a></li>
						<li><a class="footer__link" href="{SITE['telegram']}" target="_blank" rel="noopener">{SITE['telegram_label']}</a></li>
						<li><address>{e(SITE['address'])}</address></li>
						<li>{hours}</li>
					</ul>
				</div>
			</div>
			<div class="footer__bottom">
				<p class="footer__copy">{e(SITE['company'])} © {SITE['year']}</p>
			</div>
		</div>
	</footer>

</div>
'''


def city_modal():
	items = '\n'.join(
		# Перші 6 міст видно одразу, як на скриншоті замовника; решта обласних центрів — через пошук
		f'\t\t\t\t<li{" data-city-popular" if i < 6 else " hidden"}><button class="city__link" type="button" data-city-id="{e(cid)}" data-city-item="{e(c)}" data-city-region="{e(r)}">{e(c)}</button></li>'
		for i, ((cid, _), (c, r)) in enumerate(zip(content_uk.CITIES, CITIES))
	)
	return f'''
<!-- Вибір міста. Адреси сторінок регіонів задаються в CITY_URLS у main.js -->
<div class="city" id="city" role="dialog" aria-modal="true" aria-labelledby="city-title" hidden data-city>
	<div class="city__overlay" data-city-close></div>
	<div class="city__window">
		<button class="city__close" type="button" aria-label="{T['close']}" data-city-close>{icon('close')}</button>
		<h2 class="title title--h3" id="city-title">{T['city_title']}</h2>
		<p class="city__text">{T['city_text']}</p>
		<label class="city__label" for="city-search">{T['city_label']}</label>
		<div class="city__search">
			{icon('search')}
			<input class="city__input" id="city-search" type="search" placeholder="{T['city_ph']}" autocomplete="off" data-city-search>
		</div>
		<ul class="city__list" data-city-list>
{items}
		</ul>
		<p class="city__empty" hidden data-city-empty>{T['city_empty']}</p>
		<button class="city__all" type="button" data-city-id="Уся Україна" data-city-item="{T['all_country']}">{T['all_country']}</button>
		<button class="button button--ghost button--wide city__done" type="button" data-city-close>{T['close']}</button>
	</div>
</div>
'''


def tail(root):
	return f'''
<!-- Нижня панель на телефоні: дзвінок і Telegram, як на скриншоті замовника -->
<nav class="callbar" aria-label="{T['bar_label']}">
	<a class="callbar__link" href="{SITE['phone_href']}">{icon('phone')}{T['bar_call']}</a>
	<a class="callbar__link callbar__link--accent" href="{SITE['telegram']}" target="_blank" rel="noopener">{icon('telegram')}Telegram</a>
</nav>
<div class="fab" data-fab>
	<div class="fab__list" id="fab-list">
		<a class="fab__link fab__link--telegram" href="{SITE['telegram']}" target="_blank" rel="noopener" aria-label="{T['fab_tg']}">{icon('telegram')}</a>
		<a class="fab__link fab__link--phone" href="{SITE['phone_href']}" aria-label="{T['call']}">{icon('phone')}</a>
	</div>
	<button class="fab__toggle" type="button" aria-expanded="false" aria-controls="fab-list" aria-label="{T['fab_toggle']}" data-fab-toggle>{icon('chat', 'icon fab__icon fab__icon--open')}{icon('close', 'icon fab__icon fab__icon--close')}</button>
</div>
{city_modal()}
<script src="https://cdnjs.cloudflare.com/ajax/libs/gsap/3.13.0/gsap.min.js" defer></script>
<script src="https://cdnjs.cloudflare.com/ajax/libs/gsap/3.13.0/ScrollTrigger.min.js" defer></script>
<script src="{root}assets/js/main.js" defer></script>
</body>
</html>
'''


def request_section(root, selected=None, title=None, text=None):
	title = title or T['req_title']
	text = text or T['req_text']
	req_list = '\n'.join(f'\t\t\t\t\t\t\t<li>{icon("check")}{e(t)}</li>' for t in T['req_list'])
	options = '\n'.join(
		f'\t\t\t\t\t\t\t\t<option{" selected" if s["form_name"] == selected else ""}>{e(s["form_name"])}</option>' for s in SERVICES
	)
	return f'''		<section class="request" id="request">
			<div class="request__container">
				<div class="request__inner" data-reveal>
					<div class="request__content">
						<p class="eyebrow">{T['req_eyebrow']}</p>
						<h2 class="title title--h2">{e(title)}</h2>
						<p class="request__text">{e(text)}</p>
						<ul class="request__list">
{req_list}
						</ul>
					</div>

					<!-- Заявка йде на send.php, звідти в Telegram. Налаштування бота: tg-config.php (див. tg-config.example.php) -->
					<form class="form" action="{root}send.php" method="post" novalidate data-form>
						<input type="hidden" name="lang" value="{LANG}">
						<div class="form__field">
							<label class="form__label" for="f-name">{T['f_name']}</label>
							<input class="form__input" id="f-name" name="name" type="text" autocomplete="name" placeholder="{T['f_name_ph']}" required>
							<p class="form__error" data-error></p>
						</div>
						<div class="form__field">
							<label class="form__label" for="f-phone">{T['f_phone']}</label>
							<input class="form__input" id="f-phone" name="phone" type="tel" inputmode="tel" autocomplete="tel" placeholder="+38 (0__) ___ __ __" required>
							<p class="form__error" data-error></p>
						</div>
						<div class="form__field">
							<label class="form__label" for="f-service">{T['f_service']}</label>
							<select class="form__input form__input--select" id="f-service" name="service" required data-form-service>
								<option value="">{T['f_service_ph']}</option>
{options}
								<option>{T['other']}</option>
							</select>
							<p class="form__error" data-error></p>
						</div>
						<div class="form__field">
							<label class="form__label" for="f-comment">{T['f_comment']} <span class="visually-hidden">{T['optional']}</span></label>
							<textarea class="form__input form__input--textarea" id="f-comment" name="comment" rows="3" placeholder="{T['optional_ph']}"></textarea>
						</div>
						<input class="form__honeypot" type="text" name="hp_note" tabindex="-1" autocomplete="new-password" aria-hidden="true">
						<div class="form__field">
							<label class="form__consent">
								<input class="form__checkbox" type="checkbox" name="consent" required>
								<span>{T['consent']}</span>
							</label>
							<p class="form__error" data-error></p>
						</div>
						<button class="button button--wide" type="submit">{T['submit']} {icon('arrow')}</button>
						<p class="form__fail" hidden role="alert" data-form-fail>{T['fail_text']} <a href="{SITE['phone_href']}">{SITE['phone']}</a></p>
						<div class="form__success" hidden role="status" data-form-success>
							{icon('check')}
							<h3 class="title title--h3">{T['ok_title']}</h3>
							<p class="form__success-text">{T['ok_text']}</p>
						</div>
					</form>
				</div>
			</div>
		</section>
'''


def steps_section(step2, soft=True):
	items = []
	for i, (title, text) in enumerate(STEP_TEXTS):
		items.append(f'''					<li class="steps__item" data-reveal>
						<h3 class="title title--h3">{e(title or step2)}</h3>
						<p class="steps__text">{e(text)}</p>
					</li>''')
	items = '\n'.join(items)
	return f'''		<section class="steps{' steps--soft' if soft else ''}" id="how">
			<div class="steps__container">
				<div class="section-head section-head--center" data-reveal>
					<p class="eyebrow">{T['steps_eyebrow']}</p>
					<h2 class="title title--h2">{T['steps_title']}</h2>
				</div>
				<ol class="steps__list steps__list--four" data-steps>
					<li class="steps__line" aria-hidden="true"><span class="steps__line-fill" data-steps-fill></span></li>
{items}
				</ol>
			</div>
		</section>
'''


def services_cards(root, exclude=None):
	cards = []
	for s in SERVICES:
		if s['slug'] == exclude:
			continue
		cards.append(f'''					<article class="service-card" data-reveal data-service-item>
						<div class="service-card__top"><span class="service-card__icon">{icon(s['icon'])}</span><span class="service-card__code">{nb(e(s['code']))}</span></div>
						<h3 class="title title--h3"><a class="service-card__link" href="{link(root, s['slug'])}">{e(s['card_title'])}</a></h3>
						<p class="service-card__text">{nb(e(s['card_text']))}</p>
						<p class="service-card__footer"><span class="service-card__price">{T['card_more']}</span><span class="service-card__arrow">{icon('arrow')}</span></p>
					</article>''')
	return '\n'.join(cards)


def faq_section(items, title):
	rows = []
	for i, (q, a) in enumerate(items):
		opened = ' faq__item--open" open' if i == 0 else '"'
		rows.append(f'''					<details class="faq__item{opened} data-reveal>
						<summary class="faq__question">{nb(e(q))}{icon('plus')}</summary>
						<div class="faq__answer"><div class="faq__answer-inner"><p class="faq__text">{nb(e(a))}</p></div></div>
					</details>''')
	rows = '\n'.join(rows)
	return f'''		<section class="faq faq--plain" id="faq">
			<div class="faq__container">
				<div class="faq__aside" data-reveal>
					<p class="eyebrow">{T['faq_eyebrow']}</p>
					<h2 class="title title--h2">{title}</h2>
					<a class="button button--ghost" href="#request">{T['faq_btn']}</a>
				</div>
				<div class="faq__list">
{rows}
				</div>
			</div>
		</section>
'''


# --------------------------------------------------------------------------
# Сторінка послуги
# --------------------------------------------------------------------------
def service_page(slug):
	p = PAGES[slug]
	s = next(x for x in SERVICES if x['slug'] == slug)
	root = '../' + ('../' if LANG == 'ru' else '')

	perks = '\n'.join(
		f'\t\t\t\t\t\t<li class="service-hero__stat"><span class="service-hero__stat-value">{nb(e(v))}</span><span class="service-hero__stat-label">{e(l)}</span></li>'
		for v, l in p['perks']
	)
	sheet_label, sheet_code, sheet_rows = p['sheet']
	sheet_rows = '\n'.join(f'\t\t\t\t\t\t<p class="sheet__row">{icon("check")}{e(r)}</p>' for r in sheet_rows)

	intro = '\n'.join(f'\t\t\t\t\t\t<p class="intro__text">{nb(e(t))}</p>' for t in p['intro'])

	table = p['prices']
	price_head = '\n'.join(
		f'\t\t\t\t\t\t\t\t<th class="prices__cell{" prices__cell--name" if i == 0 else ""}" scope="col">{e(h)}</th>'
		for i, h in enumerate(table['head'])
	)
	price_rows = '\n'.join(
		'\t\t\t\t\t\t\t<tr class="prices__row">\n'
		+ '\n'.join(
			f'\t\t\t\t\t\t\t\t<th class="prices__cell prices__cell--name" scope="row">{nb(e(c))}</th>' if i == 0
			else f'\t\t\t\t\t\t\t\t<td class="prices__cell" data-label="{e(table["head"][i])}">{nb(e(c))}</td>'
			for i, c in enumerate(row)
		)
		+ '\n\t\t\t\t\t\t\t</tr>'
		for row in table['rows']
	)

	features = []
	for i, f in enumerate(p['features']):
		items = '\n'.join(f'\t\t\t\t\t\t\t<li class="features__item">{icon("check")}<span>{nb(e(t))}</span></li>' for t in f['items'])
		outro = f'\n\t\t\t\t\t\t<p class="features__outro">{nb(e(f["outro"]))}</p>' if f['outro'] else ''
		features.append(f'''					<article class="features__card{' features__card--dark' if i else ''}" data-reveal>
						<h2 class="title title--h3">{nb(e(f['title']))}</h2>
						<p class="features__text">{nb(e(f['intro']))}</p>
						<ul class="features__list">
{items}
						</ul>{outro}
					</article>''')
	features = '\n'.join(features)

	article = '\n'.join(f'\t\t\t\t\t<p class="about__text">{nb(e(t))}</p>' for t in p['article'])

	body = f'''
	<main class="page">

		<nav class="breadcrumbs" aria-label="{T['crumbs']}">
			<div class="breadcrumbs__container">
				<ol class="breadcrumbs__list">
					<li class="breadcrumbs__item"><a class="breadcrumbs__link" href="{link(root, '')}">{T['nav_home']}</a></li>
					<li class="breadcrumbs__item" aria-current="page">{e(p['crumb'])}</li>
				</ol>
			</div>
		</nav>

		<section class="service-hero">
			<div class="service-hero__container">
				<div class="service-hero__content">
					<p class="hero__badge" data-hero>{icon('doc')}{nb(e(p['badge']))}</p>
					<h1 class="title title--h1" data-hero>{nb(e(p['h1']))}</h1>
					<div class="service-hero__actions" data-hero>
						<a class="button" href="#request">{T['cta']} {icon('arrow')}</a>
						<a class="button button--ghost" href="#price">{T['see_prices']}</a>
					</div>
					<ul class="service-hero__stats service-hero__stats--four" data-hero>
{perks}
					</ul>
				</div>

				<div class="service-hero__visual" aria-hidden="true">
					<div class="sheet" data-hero-chip>
						<div class="sheet__head">
							<div>
								<p class="sheet__label">{e(sheet_label)}</p>
								<p class="sheet__code">{nb(e(sheet_code))}</p>
							</div>
							<span class="sheet__mark">{icon(s['icon'])}</span>
						</div>
{sheet_rows}
						<div class="sheet__line"></div>
						<div class="sheet__line sheet__line--short"></div>
						<span class="sheet__stamp">{T['stamp']}</span>
					</div>
				</div>
			</div>
		</section>

		<section class="intro">
			<div class="intro__container">
				<div class="intro__inner" data-reveal>
					<div class="intro__content">
						<p class="eyebrow">{T['intro_eyebrow']}</p>
						<h2 class="title title--h2">{nb(e(p['intro_title']))}</h2>
{intro}
					</div>
					<div class="intro__aside">
						<a class="button button--light button--wide" href="#request">{T['cta']} {icon('arrow')}</a>
						<a class="intro__phone" href="{SITE['phone_href']}">{icon('phone')}{SITE['phone']}</a>
					</div>
				</div>
			</div>
		</section>

		<!-- БЛОК ЦІНИ: ціни з живого сайту, редагуються в tools/content.py і tools/content_ru.py -->
		<section class="prices" id="price">
			<div class="prices__container">
				<div class="section-head" data-reveal>
					<p class="eyebrow">{T['prices_eyebrow']}</p>
					<h2 class="title title--h2">{nb(e(p['prices_title']))}</h2>
				</div>
				<div class="prices__card" data-reveal>
					<table class="prices__table">
						<thead>
							<tr class="prices__row prices__row--head">
{price_head}
							</tr>
						</thead>
						<tbody>
{price_rows}
						</tbody>
					</table>
				</div>
			</div>
		</section>

{steps_section(p['step2'])}
{request_section(root, selected=s['form_name'], title=T['order_title'])}
		<section class="features">
			<div class="features__container">
				<div class="features__grid">
{features}
				</div>
			</div>
		</section>

		<section class="about">
			<div class="about__container about__container--single">
				<div class="about__content" data-reveal>
					<h2 class="title title--h2">{nb(e(p['article_title']))}</h2>
{article}
				</div>
			</div>
		</section>

{faq_section(p['faq'], T['faq_title'])}
		<section class="services services--related">
			<div class="services__container">
				<div class="section-head" data-reveal>
					<p class="eyebrow">{T['other_eyebrow']}</p>
					<h2 class="title title--h2">{T['our_services']}</h2>
				</div>
				<div class="services__grid">
{services_cards(root, exclude=slug)}
				</div>
			</div>
		</section>

	</main>

'''
	return head(root, slug, p['title'], p['description']) + header(root, slug) + body + footer(root) + tail(root)


# --------------------------------------------------------------------------
# Головна
# --------------------------------------------------------------------------
def home_page():
	root = '../' if LANG == 'ru' else ''
	options = '\n'.join(f'<option>{e(s["form_name"])}</option>' for s in SERVICES)
	perks = '\n'.join(
		f'\t\t\t\t\t<li class="perks__item" data-reveal><span class="perks__icon">{icon(i)}</span><span class="perks__text">{e(t)}</span></li>'
		for i, t in HOME['perks']
	)
	about = '\n'.join(f'\t\t\t\t\t<p class="about__text">{e(t)}</p>' for t in HOME['about'])
	hours = '<br>'.join(f'{d} — {t}' for d, t in SITE['hours'])
	map_src = 'https://maps.google.com/maps?q=' + quote(SITE['map_query']) + '&hl=' + LANG + '&output=embed'
	docs_items = '\n\t\t\t\t\t\t'.join(f'<span class="hero__float-item">{icon("check")}{e(t)}</span>' for t in T['fl_docs_items'])
	days = ''.join(
		f'<span class="booking__day{" booking__day--active" if i == 1 else ""}">{d}<b>{14 + i}</b></span>' for i, d in enumerate(T['bk_days'])
	)

	body = f'''
	<main class="page">

		<section class="hero">
			<div class="hero__container">
				<div class="hero__content">
					<p class="hero__badge" data-hero>{icon('cross')}"ПРОФ МЕД ДОКС"</p>
					<h1 class="title title--h1" data-hero>{e(HOME['h1'])}</h1>
					<p class="lead hero__lead" data-hero>{e(HOME['lead'])}</p>
					<form class="quick" data-quick data-hero>
						<label class="quick__label" for="q-service">{T['quick_label']}</label>
						<div class="quick__row">
							<select class="quick__select" id="q-service" data-quick-select>{options}<option>{T['other']}</option></select>
							<button class="button" type="submit">{T['quick_btn']} {icon('arrow')}</button>
						</div>
					</form>
					<p class="hero__note" data-hero>
						<button class="hero__city" type="button" aria-haspopup="dialog" aria-controls="city" data-city-open>{icon('pin')}<span>{T['your_city']} <b data-city-label>{T['all_country']}</b></span></button>
						<span>{T['questions']} <a class="hero__phone" href="{SITE['phone_href']}">{SITE['phone']}</a></span>
					</p>
				</div>

				<div class="hero__visual" aria-hidden="true">
					<div class="booking" data-hero-chip>
						<div class="booking__head">
							<span class="booking__icon">{icon('car')}</span>
							<div>
								<p class="booking__label">{T['bk_label']}</p>
								<p class="booking__title">{T['bk_title']} <span class="nowrap">083/о</span></p>
							</div>
							<span class="booking__badge">{T['bk_badge']}</span>
						</div>
						<p class="booking__row">{icon('truck')}{T['bk_row']}</p>
						<div class="booking__days">{days}</div>
						<div class="booking__slots">
							<span class="booking__slot">09:30</span>
							<span class="booking__slot booking__slot--active">11:00</span>
							<span class="booking__slot">13:30</span>
							<span class="booking__slot">16:00</span>
						</div>
						<span class="booking__button">{T['bk_button']}</span>
					</div>
					<div class="hero__float hero__float--status" data-hero-chip>
						<span class="hero__float-icon">{icon('check')}</span>
						<span>{T['fl_status']}<small>{T['fl_status_small']}</small></span>
					</div>
					<div class="hero__float hero__float--docs" data-hero-chip>
						<span>{T['fl_docs']}</span>
						{docs_items}
					</div>
				</div>
			</div>
		</section>

		<section class="perks" aria-label="{T['perks_label']}">
			<div class="perks__container">
				<ul class="perks__list">
{perks}
				</ul>
			</div>
		</section>

		<section class="services" id="services">
			<div class="services__container">
				<div class="section-head" data-reveal>
					<p class="eyebrow">{T['svc_eyebrow']}</p>
					<h2 class="title title--h2">{T['svc_title']}</h2>
					<p class="lead">{T['svc_lead']}</p>
				</div>

				<label class="services__search" data-reveal>
					<span class="visually-hidden">{T['svc_search']}</span>
					{icon('search')}
					<input class="services__input" type="search" placeholder="{T['svc_search_ph']}" autocomplete="off" data-services-search>
				</label>
				<p class="services__count" data-reveal aria-live="polite" data-services-count></p>

				<div class="services__grid" data-services-grid>
{services_cards(root)}
				</div>
				<p class="services__empty" hidden data-services-empty>{T['svc_empty']}</p>
			</div>
		</section>

{steps_section(T['home_step2'], soft=False)}
		<section class="help">
			<div class="help__container">
				<div class="help__inner" data-reveal>
					<div class="help__content">
						<h2 class="title title--h3">{T['help_title']}</h2>
						<p class="help__text">{T['help_text']}</p>
					</div>
					<a class="button button--dark" href="#request">{T['help_btn']} {icon('arrow')}</a>
				</div>
			</div>
		</section>

		<section class="about about--home">
			<div class="about__container">
				<div class="about__content" data-reveal>
					<p class="eyebrow">Med-assistant</p>
					<h2 class="title title--h2">{e(HOME['about_title'])}</h2>
{about}
				</div>
				<div class="about__aside">
					<aside class="docs" data-reveal>
						<h3 class="title title--h3">{T['contacts_title']}</h3>
						<ul class="docs__list">
							<li class="docs__item">{icon('phone')}<a href="{SITE['phone_href']}">{SITE['phone']}</a></li>
							<li class="docs__item">{icon('telegram')}<a href="{SITE['telegram']}" target="_blank" rel="noopener">{SITE['telegram_label']}</a></li>
							<li class="docs__item">{icon('clock')}<span>{hours}</span></li>
							<li class="docs__item">{icon('pin')}<span>{e(SITE['address'])}</span></li>
						</ul>
					</aside>
				</div>
			</div>
		</section>

{request_section(root)}
		<section class="map" aria-label="{T['map_label']}">
			<div class="map__container">
				<div class="map__frame" data-reveal>
					<iframe class="map__iframe" src="{map_src}" title="{T['map_title']}: {e(SITE['map_query'])}" loading="lazy" referrerpolicy="no-referrer-when-downgrade"></iframe>
				</div>
			</div>
		</section>

	</main>

'''
	return head(root, '', HOME['title'], HOME['description']) + header(root, '') + body + footer(root, faq=link(root, 'meddovidky') + '#faq') + tail(root)


def write(path, content):
	full = os.path.join(ROOT, path)
	os.makedirs(os.path.dirname(full), exist_ok=True)
	with open(full, 'w', encoding='utf-8') as f:
		f.write(content)
	print('  ', path)


def sitemap():
	rows = []
	for slug in [''] + [x['slug'] for x in SERVICES]:
		alt = ''.join(
			f'<xhtml:link rel="alternate" hreflang="{UI[c]["html_lang"]}" href="{page_url(slug, c)}"/>' for c in LANGS
		)
		for c in LANGS:
			rows.append(f'\t<url><loc>{page_url(slug, c)}</loc>{alt}</url>')
	rows = '\n'.join(rows)
	return (
		'<?xml version="1.0" encoding="UTF-8"?>\n'
		'<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9" xmlns:xhtml="http://www.w3.org/1999/xhtml">\n'
		f'{rows}\n</urlset>\n'
	)


if __name__ == '__main__':
	print('Збірка сторінок:')
	for lang in LANGS:
		use(lang)
		write(f'{PREFIX[lang]}index.html', home_page())
		for item in SERVICES:
			write(f'{PREFIX[lang]}{item["slug"]}/index.html', service_page(item['slug']))
	write('sitemap.xml', sitemap())
