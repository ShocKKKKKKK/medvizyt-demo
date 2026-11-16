# -*- coding: utf-8 -*-
"""Збирає статичні HTML-сторінки сайту з tools/content.py.

Запуск з кореня проєкту:  python3 tools/build.py
Шапка, підвал, форма і вибір міста однакові на всіх сторінках, тому правки
робимо тут або в content.py і перезбираємо, а не редагуємо HTML вручну.
"""
import html
import json
import os
import sys
from urllib.parse import quote

sys.path.insert(0, os.path.dirname(__file__))
from content import CITIES, HOME, PAGES, SERVICES, SITE, STEP_TEXTS  # noqa: E402

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


def link(root, slug):
	return f'{root}{slug}/index.html' if slug else f'{root}index.html'


# --------------------------------------------------------------------------
# Спільні частини
# --------------------------------------------------------------------------
def head(root, slug, title, description):
	url = SITE['domain'] + (f'{slug}/' if slug else '')
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
			{'@type': 'WebSite', 'name': 'Med-assistant', 'url': SITE['domain'], 'inLanguage': 'uk'},
		],
	}
	return f'''<!DOCTYPE html>
<html lang="uk">
<head>
	<meta charset="UTF-8">
	<meta name="viewport" content="width=device-width, initial-scale=1">
	<title>{e(title)}</title>
	<meta name="description" content="{e(description)}">
	<!-- Поки сайт лежить на тестовому хостингу, він закритий від індексації. При запуску на med-assistant.net повернути index, follow -->
	<link rel="canonical" href="{url}">
	<meta name="robots" content="noindex, nofollow">
	<meta name="theme-color" content="#0a7f79">
	<link rel="icon" href="{root}assets/img/brand/logo-32.webp" type="image/webp">
	<link rel="apple-touch-icon" href="{root}assets/img/brand/logo-180.webp">
	<meta property="og:type" content="website">
	<meta property="og:locale" content="uk_UA">
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
	return f'<a class="logo" href="{link(root, "")}" aria-label="Med-assistant — на головну"><img class="logo__img" src="{root}assets/img/brand/logo.webp" width="415" height="69" alt="med-assistant"></a>'


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

			<nav class="menu" id="menu" aria-label="Головне меню" data-lp>
				<ul class="menu__list">
					<li class="menu__item"><a class="menu__link" href="{home}"{' aria-current="page"' if not current else ''}>Головна</a></li>
					<li class="menu__item">
						<button class="menu__link" type="button" aria-expanded="false" aria-controls="menu-services" data-dropdown>
							Послуги
							{icon('chevron')}
						</button>
						<ul class="menu__sub" id="menu-services">
{sub}
						</ul>
					</li>
					<li class="menu__item"><a class="menu__link" href="#how">Як це працює</a></li>
					<li class="menu__item"><a class="menu__link" href="#contacts">Контакти</a></li>
				</ul>
				<a class="button button--wide menu__cta" href="#request">Залишити заявку</a>
			</nav>

			<div class="header__actions">
				<button class="header__city" type="button" aria-haspopup="dialog" aria-controls="city" data-city-open>
					{icon('pin')}
					<span data-city-label>Уся Україна</span>
				</button>
				<a class="header__phone" href="{SITE['phone_href']}" aria-label="Зателефонувати">
					{icon('phone')}
					<span>{SITE['phone']}</span>
				</a>
				<a class="button button--small header__cta" href="#request">Залишити заявку</a>
				<button class="header__burger" type="button" aria-label="Відкрити меню" aria-expanded="false" aria-controls="menu" data-burger><span></span></button>
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
					<p class="footer__text">Оформлення медичних довідок по всій Україні: консультація, підбір форми та доставка Новою Поштою.</p>
					<div class="footer__socials">
						<a class="footer__social" href="{SITE['telegram']}" target="_blank" rel="noopener" aria-label="Telegram">{icon('telegram')}</a>
						<a class="footer__social" href="{SITE['phone_href']}" aria-label="Зателефонувати">{icon('phone')}</a>
					</div>
				</div>
				<div class="footer__col">
					<h3 class="footer__title">Послуги</h3>
					<ul class="footer__list">
{services}
					</ul>
				</div>
				<div class="footer__col">
					<h3 class="footer__title">Навігація</h3>
					<ul class="footer__list">
						<li><a class="footer__link" href="{link(root, '')}">Головна</a></li>
						<li><a class="footer__link" href="#how">Як це працює</a></li>
						<li><a class="footer__link" href="{faq}">Часті питання</a></li>
						<li><a class="footer__link" href="#request">Залишити заявку</a></li>
						<li><button class="footer__link footer__link--button" type="button" aria-haspopup="dialog" aria-controls="city" data-city-open>Обрати місто</button></li>
					</ul>
				</div>
				<div class="footer__col">
					<h3 class="footer__title">Контакти</h3>
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
		f'\t\t\t\t<li><button class="city__link" type="button" data-city-item="{e(c)}" data-city-region="{e(r)}">{e(c)}<small>{e(r)}</small></button></li>'
		for c, r in CITIES
	)
	return f'''
<!-- Вибір міста. Адреси сторінок регіонів задаються в CITY_URLS у main.js -->
<div class="city" id="city" role="dialog" aria-modal="true" aria-labelledby="city-title" hidden data-city>
	<div class="city__overlay" data-city-close></div>
	<div class="city__window">
		<button class="city__close" type="button" aria-label="Закрити" data-city-close>{icon('close')}</button>
		<h2 class="title title--h3" id="city-title">Виберіть своє місто</h2>
		<p class="city__text">Оберіть обласний центр, щоб перейти на сторінку вашого регіону.</p>
		<label class="city__search">
			<span class="visually-hidden">Місто або область</span>
			{icon('search')}
			<input class="city__input" type="search" placeholder="Почніть вводити назву" autocomplete="off" data-city-search>
		</label>
		<ul class="city__list" data-city-list>
{items}
		</ul>
		<p class="city__empty" hidden data-city-empty>Не знайшли? Оберіть «Уся Україна» — ми доставляємо в будь-яке місто.</p>
		<button class="button button--ghost button--wide city__all" type="button" data-city-item="Уся Україна">{icon('pin')}Уся Україна</button>
	</div>
</div>
'''


def tail(root):
	return f'''
<div class="fab" data-fab>
	<div class="fab__list" id="fab-list">
		<a class="fab__link fab__link--telegram" href="{SITE['telegram']}" target="_blank" rel="noopener" aria-label="Написати в Telegram">{icon('telegram')}</a>
		<a class="fab__link fab__link--phone" href="{SITE['phone_href']}" aria-label="Зателефонувати">{icon('phone')}</a>
	</div>
	<button class="fab__toggle" type="button" aria-expanded="false" aria-controls="fab-list" aria-label="Написати нам" data-fab-toggle>{icon('chat', 'icon fab__icon fab__icon--open')}{icon('close', 'icon fab__icon fab__icon--close')}</button>
</div>
{city_modal()}
<script src="https://cdnjs.cloudflare.com/ajax/libs/gsap/3.13.0/gsap.min.js" defer></script>
<script src="https://cdnjs.cloudflare.com/ajax/libs/gsap/3.13.0/ScrollTrigger.min.js" defer></script>
<script src="{root}assets/js/main.js" defer></script>
</body>
</html>
'''


def request_section(selected=None, title='Залишіть заявку', text='ми зв’яжемося з вами протягом 5 хвилин!'):
	options = '\n'.join(
		f'\t\t\t\t\t\t\t\t<option{" selected" if s["form_name"] == selected else ""}>{e(s["form_name"])}</option>' for s in SERVICES
	)
	return f'''		<section class="request" id="request">
			<div class="request__container">
				<div class="request__inner" data-reveal>
					<div class="request__content">
						<p class="eyebrow">Заявка</p>
						<h2 class="title title--h2">{e(title)}</h2>
						<p class="request__text">{e(text)}</p>
						<ul class="request__list">
							<li>{icon('check')}Підкажемо, яка форма довідки вам потрібна</li>
							<li>{icon('check')}Пояснимо вимоги та порядок оформлення</li>
							<li>{icon('check')}Доставимо документ Новою Поштою</li>
						</ul>
					</div>

					<!-- Обробник відправки ще не підключено: форма перевіряє поля і показує підтвердження -->
					<form class="form" novalidate data-form>
						<div class="form__field">
							<label class="form__label" for="f-name">ПІБ (українською мовою)</label>
							<input class="form__input" id="f-name" name="name" type="text" autocomplete="name" placeholder="Прізвище, ім’я, по батькові" required>
							<p class="form__error" data-error></p>
						</div>
						<div class="form__field">
							<label class="form__label" for="f-phone">Контактний телефон</label>
							<input class="form__input" id="f-phone" name="phone" type="tel" inputmode="tel" autocomplete="tel" placeholder="+38 (0__) ___ __ __" required>
							<p class="form__error" data-error></p>
						</div>
						<div class="form__field">
							<label class="form__label" for="f-service">Який документ цікавить</label>
							<select class="form__input form__input--select" id="f-service" name="service" required data-form-service>
								<option value="">Оберіть документ</option>
{options}
								<option>Інша довідка</option>
							</select>
							<p class="form__error" data-error></p>
						</div>
						<div class="form__field">
							<label class="form__label" for="f-comment">Додаткова інформація <span class="visually-hidden">(необов’язково)</span></label>
							<textarea class="form__input form__input--textarea" id="f-comment" name="comment" rows="3" placeholder="Необов’язково"></textarea>
						</div>
						<input class="form__honeypot" type="text" name="hp_note" tabindex="-1" autocomplete="new-password" aria-hidden="true">
						<div class="form__field">
							<label class="form__consent">
								<input class="form__checkbox" type="checkbox" name="consent" required>
								<span>Погоджуюся на обробку персональних даних</span>
							</label>
							<p class="form__error" data-error></p>
						</div>
						<button class="button button--wide" type="submit">Відправити {icon('arrow')}</button>
						<div class="form__success" hidden role="status" data-form-success>
							{icon('check')}
							<h3 class="title title--h3">Заявку прийнято</h3>
							<p class="form__success-text">Менеджер зв’яжеться з вами найближчим часом.</p>
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
					<p class="eyebrow">Як це працює</p>
					<h2 class="title title--h2">Від заявки до отримання — <span class="title__accent">чотири кроки</span></h2>
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
						<p class="service-card__footer"><span class="service-card__price">Перейти до послуги</span><span class="service-card__arrow">{icon('arrow')}</span></p>
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
					<p class="eyebrow">Питання та відповіді</p>
					<h2 class="title title--h2">{title}</h2>
					<a class="button button--ghost" href="#request">Поставити своє запитання</a>
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
	root = '../'

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

		<nav class="breadcrumbs" aria-label="Хлібні крихти">
			<div class="breadcrumbs__container">
				<ol class="breadcrumbs__list">
					<li class="breadcrumbs__item"><a class="breadcrumbs__link" href="{link(root, '')}">Головна</a></li>
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
						<a class="button" href="#request">Залишити заявку {icon('arrow')}</a>
						<a class="button button--ghost" href="#price">Переглянути ціни</a>
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
						<span class="sheet__stamp">Офіційний<br>бланк</span>
					</div>
				</div>
			</div>
		</section>

		<section class="intro">
			<div class="intro__container">
				<div class="intro__inner" data-reveal>
					<div class="intro__content">
						<p class="eyebrow">Про документ</p>
						<h2 class="title title--h2">{nb(e(p['intro_title']))}</h2>
{intro}
					</div>
					<div class="intro__aside">
						<a class="button button--light button--wide" href="#request">Залишити заявку {icon('arrow')}</a>
						<a class="intro__phone" href="{SITE['phone_href']}">{icon('phone')}{SITE['phone']}</a>
					</div>
				</div>
			</div>
		</section>

		<!-- БЛОК ЦІНИ: ціни з живого сайту, редагуються в tools/content.py -->
		<section class="prices" id="price">
			<div class="prices__container">
				<div class="section-head" data-reveal>
					<p class="eyebrow">Ціни</p>
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
{request_section(selected=s['form_name'], title='Для замовлення залишайте заявку')}
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

{faq_section(p['faq'], 'Часті <span class="title__accent">питання</span>')}
		<section class="services services--related">
			<div class="services__container">
				<div class="section-head" data-reveal>
					<p class="eyebrow">Інші послуги</p>
					<h2 class="title title--h2">Наші послуги</h2>
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
	root = ''
	options = '\n'.join(f'<option>{e(s["form_name"])}</option>' for s in SERVICES)
	perks = '\n'.join(
		f'\t\t\t\t\t<li class="perks__item" data-reveal><span class="perks__icon">{icon(i)}</span><span class="perks__text">{e(t)}</span></li>'
		for i, t in HOME['perks']
	)
	about = '\n'.join(f'\t\t\t\t\t<p class="about__text">{e(t)}</p>' for t in HOME['about'])
	hours = '<br>'.join(f'{d} — {t}' for d, t in SITE['hours'])
	map_src = 'https://maps.google.com/maps?q=' + quote(SITE['map_query']) + '&output=embed'

	body = f'''
	<main class="page">

		<section class="hero">
			<div class="hero__container">
				<div class="hero__content">
					<p class="hero__badge" data-hero>{icon('cross')}"ПРОФ МЕД ДОКС"</p>
					<h1 class="title title--h1" data-hero>{e(HOME['h1'])}</h1>
					<p class="lead hero__lead" data-hero>{e(HOME['lead'])}</p>
					<form class="quick" data-quick data-hero>
						<label class="quick__label" for="q-service">Яка довідка вам потрібна?</label>
						<div class="quick__row">
							<select class="quick__select" id="q-service" data-quick-select>{options}<option>Інша довідка</option></select>
							<button class="button" type="submit">Обрати довідку {icon('arrow')}</button>
						</div>
					</form>
					<p class="hero__note" data-hero>
						<button class="hero__city" type="button" aria-haspopup="dialog" aria-controls="city" data-city-open>{icon('pin')}<span>Ваше місто: <b data-city-label>Уся Україна</b></span></button>
						<span>Є запитання? <a class="hero__phone" href="{SITE['phone_href']}">{SITE['phone']}</a></span>
					</p>
				</div>

				<div class="hero__visual" aria-hidden="true">
					<div class="booking" data-hero-chip>
						<div class="booking__head">
							<span class="booking__icon">{icon('car')}</span>
							<div>
								<p class="booking__label">Ваша заявка</p>
								<p class="booking__title">Довідка водія <span class="nowrap">083/о</span></p>
							</div>
							<span class="booking__badge">Офіційно</span>
						</div>
						<p class="booking__row">{icon('truck')}Доставка Новою Поштою · Київ</p>
						<div class="booking__days">
							<span class="booking__day">Пн<b>14</b></span>
							<span class="booking__day booking__day--active">Вт<b>15</b></span>
							<span class="booking__day">Ср<b>16</b></span>
							<span class="booking__day">Чт<b>17</b></span>
							<span class="booking__day">Пт<b>18</b></span>
						</div>
						<div class="booking__slots">
							<span class="booking__slot">09:30</span>
							<span class="booking__slot booking__slot--active">11:00</span>
							<span class="booking__slot">13:30</span>
							<span class="booking__slot">16:00</span>
						</div>
						<span class="booking__button">Підтвердити заявку</span>
					</div>
					<div class="hero__float hero__float--status" data-hero-chip>
						<span class="hero__float-icon">{icon('check')}</span>
						<span>Заявку прийнято<small>Зв’яжемося за 5 хвилин</small></span>
					</div>
					<div class="hero__float hero__float--docs" data-hero-chip>
						<span>Що знадобиться</span>
						<span class="hero__float-item">{icon('check')}Паспорт</span>
						<span class="hero__float-item">{icon('check')}Ідентифікаційний код</span>
						<span class="hero__float-item">{icon('check')}Мета довідки</span>
					</div>
				</div>
			</div>
		</section>

		<section class="perks" aria-label="Наші переваги">
			<div class="perks__container">
				<ul class="perks__list">
{perks}
				</ul>
			</div>
		</section>

		<section class="services" id="services">
			<div class="services__container">
				<div class="section-head" data-reveal>
					<p class="eyebrow">Послуги</p>
					<h2 class="title title--h2">Яка довідка вам потрібна?</h2>
					<p class="lead">Оберіть послугу — підкажемо вимоги та порядок оформлення.</p>
				</div>

				<label class="services__search" data-reveal>
					<span class="visually-hidden">Пошук послуги</span>
					{icon('search')}
					<input class="services__input" type="search" placeholder="Назва довідки або номер форми, наприклад 083" autocomplete="off" data-services-search>
				</label>
				<p class="services__count" data-reveal aria-live="polite" data-services-count></p>

				<div class="services__grid" data-services-grid>
{services_cards(root)}
				</div>
				<p class="services__empty" hidden data-services-empty>Нічого не знайшли. Спробуйте інший запит або <a class="service-card__more" href="#request">залиште заявку</a> — підкажемо.</p>
			</div>
		</section>

{steps_section('Підготовка довідки', soft=False)}
		<section class="help">
			<div class="help__container">
				<div class="help__inner" data-reveal>
					<div class="help__content">
						<h2 class="title title--h3">Не знаєте, яку довідку обрати?</h2>
						<p class="help__text">Розкажіть, для чого вона потрібна — допоможемо розібратися з вимогами.</p>
					</div>
					<a class="button button--dark" href="#request">Отримати консультацію {icon('arrow')}</a>
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
						<h3 class="title title--h3">Ми на зв’язку</h3>
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

{request_section()}
		<section class="map" aria-label="Ми на карті">
			<div class="map__container">
				<div class="map__frame" data-reveal>
					<iframe class="map__iframe" src="{map_src}" title="Карта: {e(SITE['map_query'])}" loading="lazy" referrerpolicy="no-referrer-when-downgrade"></iframe>
				</div>
			</div>
		</section>

	</main>

'''
	return head(root, '', HOME['title'], HOME['description']) + header(root, '') + body + footer(root, faq='meddovidky/index.html#faq') + tail(root)


def write(path, content):
	full = os.path.join(ROOT, path)
	os.makedirs(os.path.dirname(full), exist_ok=True)
	with open(full, 'w', encoding='utf-8') as f:
		f.write(content)
	print('  ', path)


def sitemap():
	urls = [SITE['domain']] + [SITE['domain'] + s['slug'] + '/' for s in SERVICES]
	rows = '\n'.join(f'\t<url><loc>{u}</loc></url>' for u in urls)
	return f'<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n{rows}\n</urlset>\n'


if __name__ == '__main__':
	print('Збірка сторінок:')
	write('index.html', home_page())
	for s in SERVICES:
		write(f'{s["slug"]}/index.html', service_page(s['slug']))
	write('sitemap.xml', sitemap())
