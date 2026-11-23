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

sys.path.insert(0, os.path.dirname(__file__))
import content as content_uk  # noqa: E402
import content_ru  # noqa: E402
from i18n import UI  # noqa: E402
import order_form  # noqa: E402

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
	"""Чиста адреса сторінки від кореня сайту: /medknigka/, /ru/, / — як було на WordPress.
	root лишився в сигнатурі для сумісності викликів; assets і далі підключаються відносно."""
	return '/' + PREFIX[lang or LANG] + (f'{slug}/' if slug else '')


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
def head(root, slug, title, description, with_datepicker=False):
	url = page_url(slug)
	datepicker_css = ('\n\t<link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/air-datepicker@3.6.0/air-datepicker.min.css">'
	                  if with_datepicker else '')
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
	<!-- Сайт відкритий для індексації -->
	<link rel="canonical" href="{url}">
{alternates}
	<meta name="robots" content="index, follow">
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
	<link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/swiper@14/swiper-bundle.min.css">
{datepicker_css}
	<link rel="stylesheet" href="{root}assets/css/style.css?v=reviews-author-wrap-fix">
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

			<nav class="menu" id="menu" aria-label="{T['menu_label']}">
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


def tail(root, with_datepicker=False):
	datepicker_js = ('\n<script src="https://cdn.jsdelivr.net/npm/air-datepicker@3.6.0/air-datepicker.min.js" defer></script>'
	                 if with_datepicker else '')
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
<script src="https://cdn.jsdelivr.net/npm/swiper@14/swiper-bundle.min.js" defer></script>
{datepicker_js}
<script src="{root}assets/js/main.js?v=clean-urls-1" defer></script>
</body>
</html>
'''


def order_form_html(root, slug):
	"""Анкета замовлення для сторінки послуги (схема з order_form.py)."""
	forms = order_form.FORMS_RU if LANG == 'ru' else order_form.FORMS_UK
	fields = forms[slug]
	service = next((item for item in SERVICES if item['slug'] == slug), None)
	form_title = service['form_name'] if service else slug
	rows = []

	for f in fields:
		fid, ftype, label = f['id'], f['type'], f['label']
		req, opts, cond, content = f['required'], f['options'], f['cond'], f['content']
		# Телефон получателя и отделение Новой Почты обязательны во всех анкетах.
		label_lower = label.lower()
		req = req or ftype == 'phone' or 'номер відділення нової пошти' in label_lower or 'номер отделения новой почты' in label_lower
		cond_attr = hidden = ''
		if cond:
			cond_attr = ' data-cond="' + e(json.dumps(cond, ensure_ascii=False)) + '"'
			hidden = ' hidden'
		req_attr = ' data-required="1"' if req else ''
		if ftype == 'content':
			rows.append(f'<div class="form__note" data-field-id="{fid}"{cond_attr}{hidden}>{e(content)}</div>')
			continue
		if not label:
			continue
		name = 'f' + fid
		star = ' <span class="form__req">*</span>' if req else ''
		if ftype == 'select':
			gate_attr = ' data-order-gate' if slug == 'basein' and fid == '1' else ''
			opt_html = f'<option value="">{T["select_ph"]}</option>' + ''.join(
				f'<option value="{e(o)}">{e(o)}</option>' for o in opts)
			inner = (f'<span class="form__label">{e(label)}{star}</span>'
			         f'<select class="form__input form__input--select" name="{name}" data-cond-field="{fid}"{gate_attr}>{opt_html}</select>')
		elif ftype in ('radio', 'checkbox'):
			chips = ''.join(
				f'<label class="form__chip"><input type="{ftype}" name="{name}" value="{e(o)}" data-cond-field="{fid}"><span>{e(o)}</span></label>'
				for o in opts)
			inner = f'<span class="form__label">{e(label)}{star}</span><div class="form__chips">{chips}</div>'
		elif ftype == 'textarea':
			inner = (f'<span class="form__label">{e(label)}{star}</span>'
			         f'<textarea class="form__input form__input--textarea" name="{name}" rows="2" data-cond-field="{fid}"></textarea>')
		elif ftype == 'file':
			inner = (f'<span class="form__label">{e(label)}{star}</span>'
			         f'<input class="form__input form__input--file" type="file" name="{name}" accept="image/jpeg,image/png,image/webp,image/heic,image/heif,application/pdf" data-cond-field="{fid}">')
		elif ftype == 'date-time':
			birth_attr = ' data-datepicker-birth' if ('народжен' in label.lower() or 'рождени' in label.lower()) else ''
			inner = (f'<span class="form__label">{e(label)}{star}</span>'
			         f'<input class="form__input form__input--date" type="text" name="{name}" placeholder="ДД.ММ.РРРР" inputmode="numeric" autocomplete="off" data-datepicker{birth_attr} data-cond-field="{fid}">')
		else:
			it = ('tel' if ftype == 'phone' else 'number' if ftype == 'number'
			      else 'datetime-local' if ftype == 'datetime-local' else 'text')
			inner = (f'<span class="form__label">{e(label)}{star}</span>'
			         f'<input class="form__input" type="{it}" name="{name}" data-cond-field="{fid}">')
		rows.append(f'<div class="form__field" data-field-id="{fid}" data-label="{e(label)}"{req_attr}{cond_attr}{hidden}>{inner}<p class="form__error" data-error></p></div>')

	rows_html = '\n'.join(rows)
	gate_class = ' order-form--gated' if slug == 'basein' else ''
	return f'''<form class="form form--order order-form{gate_class}" action="{root}send.php" method="post" enctype="multipart/form-data" novalidate data-order data-form-title="{e(form_title)}">
						<input type="hidden" name="lang" value="{LANG}">
						<input type="hidden" name="form_started_at" value="">
						<div class="form__grid">
{rows_html}
						</div>
						<input class="form__honeypot" type="text" name="hp_note" tabindex="-1" autocomplete="new-password" aria-hidden="true">
						<div class="form__field order-form__consent">
							<label class="form__consent">
								<input class="form__checkbox" type="checkbox" name="consent" required>
								<span>{T['consent']}</span>
							</label>
							<p class="form__error" data-error></p>
						</div>
						<button class="button button--wide order-form__submit" type="submit">{T['submit']} {icon('arrow')}</button>
						<p class="form__fail" hidden role="alert" data-form-fail>{T['fail_text']} <a href="{SITE['phone_href']}">{SITE['phone']}</a></p>
						<div class="form__success" hidden role="status" data-form-success>
							{icon('check')}
							<p class="title title--h3 form__success-text">Дякуємо! Ми зв'яжемося з вами найближчим часом</p>
						</div>
					</form>'''


def simple_form_html(root, selected=None, prefix='f', comment_placeholder=None):
	"""Короткая форма с главной страницы для обычного блока или диалога."""
	comment_placeholder = comment_placeholder or T['optional_ph']
	form_title = selected or T['req_title']
	options = '\n'.join(
		f'\t\t\t\t\t\t\t\t<option{" selected" if s["form_name"] == selected else ""}>{e(s["form_name"])}</option>' for s in SERVICES
	)
	return f'''<form class="form" action="{root}send.php" method="post" novalidate data-form data-form-title="{e(form_title)}">
						<input type="hidden" name="lang" value="{LANG}">
						<input type="hidden" name="form_started_at" value="">
						<div class="form__field">
							<label class="form__label" for="{prefix}-name">{T['f_name']}</label>
							<input class="form__input" id="{prefix}-name" name="name" type="text" autocomplete="name" placeholder="{T['f_name_ph']}" required>
							<p class="form__error" data-error></p>
						</div>
						<div class="form__field">
							<label class="form__label" for="{prefix}-phone">{T['f_phone']}</label>
							<input class="form__input" id="{prefix}-phone" name="phone" type="tel" inputmode="tel" autocomplete="tel" placeholder="+38 (0__) ___ __ __" required>
							<p class="form__error" data-error></p>
						</div>
						<div class="form__field">
							<label class="form__label" for="{prefix}-service">{T['f_service']}</label>
							<select class="form__input form__input--select" id="{prefix}-service" name="service" required data-form-service>
								<option value="">{T['f_service_ph']}</option>
{options}
								<option>{T['other']}</option>
							</select>
							<p class="form__error" data-error></p>
						</div>
						<div class="form__field">
							<label class="form__label" for="{prefix}-comment">{T['f_comment']} <span class="visually-hidden">{T['optional']}</span></label>
							<textarea class="form__input form__input--textarea" id="{prefix}-comment" name="comment" rows="3" placeholder="{e(comment_placeholder)}"></textarea>
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
							<p class="title title--h3 form__success-text">Дякуємо! Ми зв'яжемося з вами найближчим часом</p>
						</div>
					</form>'''


def request_section(root, selected=None, title=None, text=None, slug=None):
	title = title or T['req_title']
	text = text or T['req_text']
	if slug and slug in (order_form.FORMS_RU if LANG == 'ru' else order_form.FORMS_UK):
		return f'''		<section class="request" id="request">
			<div class="request__container">
				<div class="request__inner request__inner--order" data-reveal>
					<div class="request__content">
						<p class="eyebrow">{T['req_eyebrow']}</p>
						<h2 class="title title--h2">{e(title)}</h2>
						<p class="request__text">{e(text)}</p>
					</div>
					{order_form_html(root, slug)}
				</div>
			</div>
		</section>
'''
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
					</div>

					<!-- Заявка надсилається через SMTP-обробник send.php. -->
					<form class="form" action="{root}send.php" method="post" novalidate data-form data-form-title="{e(title)}">
						<input type="hidden" name="lang" value="{LANG}">
						<input type="hidden" name="form_started_at" value="">
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
							<p class="title title--h3 form__success-text">Дякуємо! Ми зв'яжемося з вами найближчим часом</p>
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
		cards.append(f'''					<article class="service-card swiper-slide" data-reveal data-service-item>
						<div class="service-card__top"><span class="service-card__icon">{icon(s['icon'])}</span><span class="service-card__code">{nb(e(s['code']))}</span></div>
						<h3 class="title title--h3"><a class="service-card__link" href="{link(root, s['slug'])}">{e(s['card_title'])}</a></h3>
						<p class="service-card__text">{nb(e(s['card_text']))}</p>
						<p class="service-card__footer"><span class="service-card__price">{T['card_more']}</span><span class="service-card__arrow">{icon('arrow')}</span></p>
					</article>''')
	return '\n'.join(cards)


def services_slider(root, exclude=None, searchable=False):
	grid_attr = ' data-services-grid' if searchable else ''
	return f'''				<div class="services__slider swiper" data-services-slider>
					<div class="services__grid swiper-wrapper"{grid_attr}>
{services_cards(root, exclude=exclude)}
					</div>
				</div>
				<div class="services__controls">
					<button class="services__arrow services__arrow--prev" type="button" aria-label="{T['slider_prev']}" data-services-prev>{icon('arrow')}</button>
					<div class="services__pagination" data-services-pagination></div>
					<button class="services__arrow services__arrow--next" type="button" aria-label="{T['slider_next']}" data-services-next>{icon('arrow')}</button>
				</div>'''


REVIEWS = (
	('Іван', '18 листопада 2026', '2026-11-18', 'ivan.jpg', 'Дякую, довідка оригінальна, на роботі забрали без питань.'),
	('Роман', '15 листопада 2026', '2026-11-15', 'roman.jpg', 'В универе справка 095 прошла. Доставили как и обещали за день.'),
	('Марина', '12 листопада 2026', '2026-11-12', 'marina.jpg', 'Зробили довідку за день, ціна маленька, на роботі прийняли.'),
	('Ольга', '10 листопада 2026', '2026-11-10', 'olga.jpg', 'Роблю книжку в цьому мед центрі не перший рік. Всім задоволений.'),
	('Денис', '8 листопада 2026', '2026-11-08', 'denis.jpg', 'Рекомендували вас, колеги с роботи. Зробили все чітко та на наступний день забрав сан книжку.'),
)
GOOGLE_REVIEWS_URL = 'https://maps.app.goo.gl/7otPuzSgCWm7yBvWA'


def reviews_section(root):
	"""Единый блок отзывов для главной и всех страниц услуг."""
	stars = ''.join(icon('star-fill') for _ in range(5))
	cards = '\n'.join(
		f'''\t\t\t\t\t<article class="reviews__card swiper-slide">
\t\t\t\t\t\t<a class="reviews__link" href="{GOOGLE_REVIEWS_URL}" target="_blank" rel="noopener">
\t\t\t\t\t\t\t<div class="reviews__meta">
\t\t\t\t\t\t\t\t<img class="reviews__avatar" src="{root}assets/img/reviews/{avatar}" alt="" width="320" height="320" loading="lazy" decoding="async">
\t\t\t\t\t\t\t\t<div class="reviews__details">
\t\t\t\t\t\t\t\t\t<div class="reviews__author-line">
\t\t\t\t\t\t\t\t\t\t<div class="reviews__author">
\t\t\t\t\t\t\t\t\t\t\t{icon('google', 'reviews__google')}
\t\t\t\t\t\t\t\t\t\t\t<h3 class="reviews__name">{e(name)}</h3>
\t\t\t\t\t\t\t\t\t\t</div>
\t\t\t\t\t\t\t\t\t\t<span class="reviews__stars" aria-label="5 з 5 зірок">{stars}</span>
\t\t\t\t\t\t\t\t\t</div>
\t\t\t\t\t\t\t\t\t<div class="reviews__date">{icon('calendar')}<time datetime="{date_iso}">{e(date_label)}</time></div>
\t\t\t\t\t\t\t\t</div>
\t\t\t\t\t\t\t</div>
\t\t\t\t\t\t\t<p class="reviews__text">{e(text)}</p>
\t\t\t\t\t\t</a>
\t\t\t\t\t</article>'''
		for name, date_label, date_iso, avatar, text in REVIEWS
	)
	return f'''\t\t<section class="reviews" aria-labelledby="reviews-title">
\t\t\t<div class="reviews__container">
\t\t\t\t<div class="section-head section-head--center" data-reveal>
\t\t\t\t\t<p class="eyebrow">Відгуки</p>
\t\t\t\t\t<h2 class="title title--h2" id="reviews-title">Відгуки клієнтів</h2>
\t\t\t\t</div>
\t\t\t\t<div class="reviews__slider swiper" data-reviews-slider>
\t\t\t\t\t<div class="reviews__wrapper swiper-wrapper">
{cards}
\t\t\t\t\t</div>
\t\t\t\t</div>
\t\t\t\t<div class="reviews__controls">
\t\t\t\t\t<button class="reviews__arrow reviews__arrow--prev" type="button" aria-label="Попередній відгук" data-reviews-prev>{icon('arrow')}</button>
\t\t\t\t\t<div class="reviews__pagination" data-reviews-pagination></div>
\t\t\t\t\t<button class="reviews__arrow reviews__arrow--next" type="button" aria-label="Наступний відгук" data-reviews-next>{icon('arrow')}</button>
\t\t\t\t</div>
\t\t\t\t<div class="reviews__footer">
\t\t\t\t\t<a class="button button--ghost" href="{GOOGLE_REVIEWS_URL}" target="_blank" rel="noopener">Дивитися всі відгуки в Google {icon('arrow')}</a>
\t\t\t\t</div>
\t\t\t</div>
\t\t</section>
'''


def question_dialog(root, selected):
	"""Небольшая форма вопроса, которая открывается из блока FAQ."""
	return f'''<dialog class="form-dialog" id="question-dialog" aria-labelledby="question-dialog-title" data-dialog>
	<div class="form-dialog__window">
		<button class="form-dialog__close" type="button" aria-label="{T['close']}" data-dialog-close>{icon('close')}</button>
		<div class="form-dialog__head">
			<p class="eyebrow">{T['faq_eyebrow']}</p>
			<h2 class="title title--h2" id="question-dialog-title">{T['question_title']}</h2>
			<p class="form-dialog__text">{T['question_text']}</p>
		</div>
		<div class="form-dialog__body">
			{simple_form_html(root, selected=selected, prefix='question', comment_placeholder=T['question_ph'])}
		</div>
	</div>
</dialog>'''


def faq_section(items, title, root, selected):
	rows = []
	for i, (q, a) in enumerate(items):
		opened = ' faq__item--open" open' if i == 0 else '"'
		rows.append(f'''					<details class="faq__item{opened} data-reveal>
						<summary class="faq__question"><span class="faq__question-text">{nb(e(q))}</span>{icon('plus')}</summary>
						<div class="faq__answer"><div class="faq__answer-inner"><p class="faq__text">{nb(e(a))}</p></div></div>
					</details>''')
	rows = '\n'.join(rows)
	return f'''		<section class="faq faq--plain" id="faq">
			<div class="faq__container">
				<div class="faq__aside" data-reveal>
					<p class="eyebrow">{T['faq_eyebrow']}</p>
					<h2 class="title title--h2">{title}</h2>
					<button class="button button--ghost" type="button" aria-haspopup="dialog" aria-controls="question-dialog" data-dialog-open="question-dialog">{T['faq_btn']}</button>
				</div>
				<div class="faq__list">
{rows}
				</div>
			</div>
		</section>
{question_dialog(root, selected)}
'''


# --------------------------------------------------------------------------
# Сторінка послуги
# --------------------------------------------------------------------------
def service_page(slug):
	p = PAGES[slug]
	s = next(x for x in SERVICES if x['slug'] == slug)
	root = '../' + ('../' if LANG == 'ru' else '')

	sheet_label, sheet_code, _ = p['sheet']
	sheet_rows = '\n'.join(
		f'\t\t\t\t\t\t<p class="sheet__row">{icon("check")}{nb(e(text))}</p>' for text in p['perks']
	)
	hero_visual = f'''\t\t\t\t<div class="service-hero__visual" aria-hidden="true">
\t\t\t\t\t<div class="sheet" data-hero-chip>
\t\t\t\t\t\t<div class="sheet__head">
\t\t\t\t\t\t\t<div>
\t\t\t\t\t\t\t\t<p class="sheet__label">{e(sheet_label)}</p>
\t\t\t\t\t\t\t\t<p class="sheet__code">{nb(e(sheet_code))}</p>
\t\t\t\t\t\t\t</div>
\t\t\t\t\t\t\t<span class="sheet__mark">{icon(s['icon'])}</span>
\t\t\t\t\t\t</div>
{sheet_rows}
\t\t\t\t\t\t<div class="sheet__line"></div>
\t\t\t\t\t\t<div class="sheet__line sheet__line--short"></div>
\t\t\t\t\t\t<span class="sheet__stamp">{T['stamp']}</span>
\t\t\t\t\t</div>
\t\t\t\t</div>'''

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
			else f'\t\t\t\t\t\t\t\t<td class="prices__cell" data-label="{e(table["head"][i])}"><span class="prices__value">{nb(e(c))}</span></td>'
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
				</div>

{hero_visual}
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
						<a class="button button--telegram button--wide" href="{SITE['telegram']}" target="_blank" rel="noopener">{icon('telegram')}{T['telegram_action']}</a>
						<a class="button button--light button--wide" href="{SITE['phone_href']}">{icon('phone')}{T['call_action']}</a>
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
{request_section(root, selected=s['form_name'], title=T['order_title'], slug=slug)}
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

{reviews_section(root)}
{faq_section(p['faq'], T['faq_title'], root, s['form_name'])}
		<section class="services services--related">
			<div class="services__container">
				<div class="section-head" data-reveal>
					<p class="eyebrow">{T['other_eyebrow']}</p>
					<h2 class="title title--h2">{T['our_services']}</h2>
				</div>
{services_slider(root, exclude=slug)}
			</div>
		</section>

	</main>

'''
	return head(root, slug, p['title'], p['description'], with_datepicker=True) + header(root, slug) + body + footer(root) + tail(root, with_datepicker=True)


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
	map_src = SITE['map_embed']
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
						<span>{T['questions']} <a class="hero__telegram" href="{SITE['telegram']}" target="_blank" rel="noopener">{icon('telegram')}{T['questions_telegram']}</a></span>
					</p>
				</div>

				<div class="hero__visual" aria-hidden="true">
					<img class="hero__illustration" src="{root}assets/img/hero-medical-docs-v2.webp" width="900" height="675" alt="" data-hero-chip>
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

{services_slider(root, searchable=True)}
				<p class="services__empty" hidden data-services-empty>{T['svc_empty']}</p>
			</div>
		</section>

{steps_section(T['home_step2'], soft=False)}
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
							<li class="docs__item">{icon('pin')}<span>{T['work_country']}</span></li>
						</ul>
					</aside>
				</div>
			</div>
		</section>

{request_section(root)}
{reviews_section(root)}
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


def reviews_concepts_page():
	"""Служебная страница для сравнения пяти вариантов секции отзывов."""
	root = '../'
	google_url = GOOGLE_REVIEWS_URL

	def section_head(number, name, description):
		return f'''\t\t\t<div class="review-concept__head">
\t\t\t\t<p class="review-concept__label">Варіант {number}</p>
\t\t\t\t<h2 class="review-concept__title">{e(name)}</h2>
\t\t\t\t<p class="review-concept__description">{e(description)}</p>
\t\t\t</div>'''

	def controls():
		return f'''\t\t\t<div class="review-concept__controls">
\t\t\t\t<button class="review-concept__arrow review-concept__arrow--prev" type="button" aria-label="Попередній відгук" data-concept-prev>{icon('arrow')}</button>
\t\t\t\t<div class="review-concept__pagination" data-concept-pagination></div>
\t\t\t\t<button class="review-concept__arrow review-concept__arrow--next" type="button" aria-label="Наступний відгук" data-concept-next>{icon('arrow')}</button>
\t\t\t</div>'''

	def google_link():
		return f'''\t\t\t<div class="review-concept__footer">
\t\t\t\t<a class="button button--ghost review-concept__google" href="{google_url}" target="_blank" rel="noopener">Дивитися всі відгуки в Google {icon('arrow')}</a>
\t\t\t</div>'''

	document_cards = '\n'.join(
		f'''\t\t\t\t\t<article class="review-document__card swiper-slide">
\t\t\t\t\t\t<div class="review-document__meta"><span>Відгук клієнта</span><span class="review-document__check">{icon('check')}</span></div>
\t\t\t\t\t\t<p class="review-document__text">{e(text)}</p>
\t\t\t\t\t\t<div class="review-document__signature"><span class="review-document__name">{e(name)}</span><span class="review-document__line"></span></div>
\t\t\t\t\t</article>'''
		for name, _date_label, _date_iso, _avatar, text in REVIEWS
	)

	focus_tabs = '\n'.join(
		f'''\t\t\t\t\t<button class="review-focus__tab{' review-focus__tab--active' if index == 0 else ''}" type="button" data-focus-tab data-name="{e(name, quote=True)}" data-text="{e(text, quote=True)}" aria-pressed="{'true' if index == 0 else 'false'}"><span class="review-focus__initial">{e(name[0])}</span><span>{e(name)}</span></button>'''
		for index, (name, _date_label, _date_iso, _avatar, text) in enumerate(REVIEWS)
	)

	stack_cards = '\n'.join(
		f'''\t\t\t\t<article class="review-stack__card">
\t\t\t\t\t<span class="review-stack__quote" aria-hidden="true">“</span>
\t\t\t\t\t<p class="review-stack__text">{e(text)}</p>
\t\t\t\t\t<div class="review-stack__person"><span class="review-stack__initial">{e(name[0])}</span><strong>{e(name)}</strong></div>
\t\t\t\t</article>'''
		for name, _date_label, _date_iso, _avatar, text in REVIEWS
	)

	split_cards = '\n'.join(
		f'''\t\t\t\t\t\t<article class="review-split__card swiper-slide">
\t\t\t\t\t\t\t<p class="review-split__text">{e(text)}</p>
\t\t\t\t\t\t\t<div class="review-split__person"><span>{e(name[0])}</span><strong>{e(name)}</strong></div>
\t\t\t\t\t\t</article>'''
		for name, _date_label, _date_iso, _avatar, text in REVIEWS
	)

	stage_cards = '\n'.join(
		f'''\t\t\t\t\t<article class="review-stage__card swiper-slide">
\t\t\t\t\t\t<span class="review-stage__quote" aria-hidden="true">“</span>
\t\t\t\t\t\t<p class="review-stage__text">{e(text)}</p>
\t\t\t\t\t\t<div class="review-stage__person"><span>{e(name[0])}</span><strong>{e(name)}</strong></div>
\t\t\t\t\t</article>'''
		for name, _date_label, _date_iso, _avatar, text in REVIEWS
	)

	first_name, _first_date_label, _first_date_iso, _first_avatar, first_text = REVIEWS[0]
	page_head = head(
		root,
		'reviews-concepts',
		'П’ять варіантів секції відгуків — Med-assistant',
		'Службова сторінка для вибору дизайну секції відгуків.',
	).replace(
		'<meta name="robots" content="index, follow">',
		'<meta name="robots" content="noindex, nofollow">',
	).replace(
		'</head>',
		f'\t<link rel="stylesheet" href="{root}assets/css/reviews-concepts.css">\n</head>',
	)

	body = f'''<div class="wrapper review-lab">
	<header class="review-lab__header">
		<div class="review-lab__header-container">
			{logo(root)}
			<a class="button button--ghost button--small" href="{link(root, 'basein')}">{icon('arrow', 'icon review-lab__back-icon')} Повернутися до сайту</a>
		</div>
	</header>

	<main class="review-lab__main">
		<section class="review-lab__intro">
			<div class="review-lab__container">
				<p class="eyebrow">Дизайн-лабораторія</p>
				<h1 class="review-lab__title">П’ять варіантів секції відгуків</h1>
				<p class="review-lab__lead">У кожному варіанті використані ті самі імена, тексти та кольори сайту. Відрізняється лише композиція.</p>
				<nav class="review-lab__nav" aria-label="Варіанти секції">
					<a href="#variant-1">01 · Бланки</a><a href="#variant-2">02 · Акцент</a><a href="#variant-3">03 · Стос карток</a><a href="#variant-4">04 · Поділ</a><a href="#variant-5">05 · Центр уваги</a>
				</nav>
			</div>
		</section>

		<section class="review-concept review-concept--document" id="variant-1" data-review-concept>
			<div class="review-concept__container">
{section_head('01', 'Відгуки як медичні бланки', 'Фірмовий мотив документа: службова позначка, відмітка та підпис клієнта.')}
				<div class="review-document__slider swiper" data-concept-slider="documents">
					<div class="review-document__wrapper swiper-wrapper">
{document_cards}
					</div>
				</div>
{controls()}
{google_link()}
			</div>
		</section>

		<section class="review-concept review-concept--focus" id="variant-2" data-review-concept>
			<div class="review-concept__container">
{section_head('02', 'Один головний відгук', 'Один текст отримує максимум уваги, а імена працюють як компактне перемикання.')}
				<div class="review-focus" data-review-focus>
					<article class="review-focus__card">
						<span class="review-focus__quote" aria-hidden="true">“</span>
						<p class="review-focus__text" data-focus-text>{e(first_text)}</p>
						<strong class="review-focus__name" data-focus-name>{e(first_name)}</strong>
					</article>
					<div class="review-focus__tabs" aria-label="Оберіть відгук">
{focus_tabs}
					</div>
				</div>
{google_link()}
			</div>
		</section>

		<section class="review-concept review-concept--stack" id="variant-3" data-review-concept>
			<div class="review-concept__container">
{section_head('03', 'Стос живих карток', 'Картки трохи зміщені одна відносно одної, ніби окремі нотатки клієнтів.')}
				<div class="review-stack">
{stack_cards}
				</div>
{google_link()}
			</div>
		</section>

		<section class="review-concept review-concept--split" id="variant-4" data-review-concept>
			<div class="review-concept__container">
{section_head('04', 'Розділена композиція', 'Заголовок і дія утворюють окрему панель, а відгуки рухаються поруч.')}
				<div class="review-split">
					<aside class="review-split__aside">
						<p class="review-split__eyebrow">Нам довіряють</p>
						<h3 class="review-split__title">Реальний досвід наших клієнтів</h3>
						<p class="review-split__description">Коротко про оформлення, доставку та прийняття документів.</p>
						<a class="button button--light review-split__google" href="{google_url}" target="_blank" rel="noopener">Відгуки в Google {icon('arrow')}</a>
					</aside>
					<div class="review-split__content">
						<div class="review-split__slider swiper" data-concept-slider="split">
							<div class="review-split__wrapper swiper-wrapper">
{split_cards}
							</div>
						</div>
{controls()}
					</div>
				</div>
			</div>
		</section>

		<section class="review-concept review-concept--stage" id="variant-5" data-review-concept>
			<div class="review-concept__container">
{section_head('05', 'Відгук у центрі уваги', 'Активний відгук великий, сусідні картки залишаються частково видимими.')}
				<div class="review-stage__slider swiper" data-concept-slider="stage">
					<div class="review-stage__wrapper swiper-wrapper">
{stage_cards}
					</div>
				</div>
{controls()}
{google_link()}
			</div>
		</section>
	</main>
</div>

<script src="https://cdn.jsdelivr.net/npm/swiper@14/swiper-bundle.min.js" defer></script>
<script src="{root}assets/js/reviews-concepts.js" defer></script>
</body>
</html>
'''
	return page_head + body


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
	use('uk')
	write('reviews-concepts/index.html', reviews_concepts_page())
	write('sitemap.xml', sitemap())
