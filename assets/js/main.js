/* ==========================================================================
   Хелпери
   ========================================================================== */
const html = document.documentElement;
let bodyLockStatus = true;

// Рядки, які скрипт підставляє сам. Мова береться з <html lang>
const I18N = {
	uk: {
		openMenu: 'Відкрити меню',
		closeMenu: 'Закрити меню',
		shown: (n, total) => `Показано ${n} із ${total}`,
		errName: 'Вкажіть ПІБ',
		errPhone: 'Вкажіть номер телефону повністю',
		errService: 'Оберіть документ',
		errConsent: 'Потрібна згода на обробку даних',
		errRequired: 'Заповніть це поле',
		fabOpen: 'Написати нам',
		fabClose: 'Закрити список месенджерів',
	},
	ru: {
		openMenu: 'Открыть меню',
		closeMenu: 'Закрыть меню',
		shown: (n, total) => `Показано ${n} из ${total}`,
		errName: 'Укажите ФИО',
		errPhone: 'Укажите номер телефона полностью',
		errService: 'Выберите документ',
		errConsent: 'Нужно согласие на обработку данных',
		errRequired: 'Заполните это поле',
		fabOpen: 'Написать нам',
		fabClose: 'Закрыть список мессенджеров',
	},
};
const t = I18N[html.lang] || I18N.uk;

// Блокування скролу з компенсацією ширини скролбара (body + fixed-елементи [data-lp])
function bodyLock(delay = 400) {
	if (!bodyLockStatus) return;
	const lockPaddingValue = window.innerWidth - document.body.offsetWidth + 'px';
	document.querySelectorAll('[data-lp]').forEach((el) => {
		el.style.paddingRight = lockPaddingValue;
	});
	document.body.style.paddingRight = lockPaddingValue;
	html.setAttribute('data-scroll-lock', '');
	bodyLockStatus = false;
	setTimeout(() => (bodyLockStatus = true), delay);
}

function bodyUnlock(delay = 400) {
	if (!bodyLockStatus) return;
	setTimeout(() => {
		document.querySelectorAll('[data-lp]').forEach((el) => {
			el.style.paddingRight = '';
		});
		document.body.style.paddingRight = '';
		html.removeAttribute('data-scroll-lock');
	}, delay);
	bodyLockStatus = false;
	setTimeout(() => (bodyLockStatus = true), delay);
}

/* ==========================================================================
   Шапка: висота в змінну, тінь при скролі
   ========================================================================== */
function initHeader() {
	const header = document.querySelector('[data-header]');
	if (!header) return;

	const setHeight = () => html.style.setProperty('--head-h', header.offsetHeight + 'px');
	setHeight();
	window.addEventListener('resize', setHeight);

	const onScroll = () => header.classList.toggle('header--scrolled', window.scrollY > 8);
	onScroll();
	window.addEventListener('scroll', onScroll, { passive: true });
}

/* ==========================================================================
   Мобільне меню та випадаючий список послуг
   ========================================================================== */
function initMenu() {
	const burger = document.querySelector('[data-burger]');
	const menu = document.getElementById('menu');
	if (!burger || !menu) return;

	const close = () => {
		if (!html.classList.contains('menu-open')) return;
		html.classList.remove('menu-open');
		burger.setAttribute('aria-expanded', 'false');
		burger.setAttribute('aria-label', t.openMenu);
		bodyUnlock();
	};

	burger.addEventListener('click', () => {
		if (!bodyLockStatus) return;
		if (html.classList.contains('menu-open')) {
			close();
		} else {
			html.classList.add('menu-open');
			burger.setAttribute('aria-expanded', 'true');
			burger.setAttribute('aria-label', t.closeMenu);
			bodyLock();
		}
	});

	// Перехід за посиланням закриває меню
	menu.addEventListener('click', (e) => {
		if (e.target.closest('a')) close();
	});

	// Dropdown «Послуги»
	const dropdown = document.querySelector('[data-dropdown]');
	if (dropdown) {
		const setOpen = (state) => dropdown.setAttribute('aria-expanded', String(state));
		dropdown.addEventListener('click', () => setOpen(dropdown.getAttribute('aria-expanded') !== 'true'));
		document.addEventListener('click', (e) => {
			if (!e.target.closest('.menu__item')) setOpen(false);
		});
		document.addEventListener('keydown', (e) => {
			if (e.code !== 'Escape') return;
			if (dropdown.getAttribute('aria-expanded') === 'true') {
				setOpen(false);
				dropdown.focus();
			}
			close();
		});
	}

	// При переході на десктоп меню має бути закрите
	window.matchMedia('(min-width: 62.0625em)').addEventListener('change', (e) => {
		if (e.matches) close();
	});
}

/* ==========================================================================
   Пошук по послугах
   ========================================================================== */
function initServices() {
	const input = document.querySelector('[data-services-search]');
	const items = Array.from(document.querySelectorAll('[data-service-item]'));
	const count = document.querySelector('[data-services-count]');
	const empty = document.querySelector('[data-services-empty]');

	if (input && items.length) {
		const update = () => {
			const query = input.value.trim().toLowerCase();
			let shown = 0;
			items.forEach((item) => {
				const match = !query || item.textContent.toLowerCase().includes(query);
				item.hidden = !match;
				if (match) shown++;
			});
			if (count) count.textContent = t.shown(shown, items.length);
			if (empty) empty.hidden = shown > 0;
			if (window.ScrollTrigger) ScrollTrigger.refresh();
		};
		input.addEventListener('input', update);
		update();
	}

}

/* ==========================================================================
   FAQ: плавне розкриття та згортання <details>, відкрите лише одне питання
   ========================================================================== */
function initFaq() {
	const items = Array.from(document.querySelectorAll('.faq__item'));
	if (!items.length) return;

	const close = (item) => {
		if (!item.classList.contains('faq__item--open')) return;
		item.classList.remove('faq__item--open');
		const answer = item.querySelector('.faq__answer');
		// Атрибут open знімаємо лише після завершення анімації, інакше відповідь зникне миттєво
		const done = (e) => {
			if (e && e.target !== answer) return;
			answer.removeEventListener('transitionend', done);
			clearTimeout(timer);
			if (!item.classList.contains('faq__item--open')) item.open = false;
		};
		const timer = setTimeout(done, 600);
		answer.addEventListener('transitionend', done);
	};

	const open = (item) => {
		item.open = true;
		// Кадр на застосування стартового стану, потім запускаємо перехід
		requestAnimationFrame(() => requestAnimationFrame(() => item.classList.add('faq__item--open')));
	};

	items.forEach((item) => {
		item.querySelector('.faq__question').addEventListener('click', (e) => {
			e.preventDefault();
			if (item.classList.contains('faq__item--open')) {
				close(item);
			} else {
				items.filter((other) => other !== item).forEach(close);
				open(item);
			}
		});
	});
}

/* ==========================================================================
   Форма заявки: перевірка полів і відправка на send.php (звідти — у Telegram)
   ========================================================================== */
function initForms() {
	const rules = {
		name: (v) => (v.trim().length >= 2 ? '' : t.errName),
		phone: (v) => (v.replace(/\D/g, '').length >= 10 ? '' : t.errPhone),
		service: (v) => (v ? '' : t.errService),
	};

	document.querySelectorAll('[data-form]').forEach((form) => {
		const setError = (control, message) => {
			const field = control.closest('.form__field');
			if (!field) return;
			field.classList.toggle('form__field--error', Boolean(message));
			const error = field.querySelector('[data-error]');
			if (error) error.textContent = message;
			control.setAttribute('aria-invalid', message ? 'true' : 'false');
		};

		const validate = (control) => {
			let message = '';
			if (control.type === 'checkbox') {
				message = control.required && !control.checked ? t.errConsent : '';
			} else if (rules[control.name] && control.type !== 'hidden') {
				message = rules[control.name](control.value);
			}
			setError(control, message);
			return !message;
		};

		form.addEventListener('input', (e) => {
			if (e.target.closest('.form__field--error')) validate(e.target);
		});
		form.addEventListener('change', (e) => {
			if (e.target.closest('.form__field--error')) validate(e.target);
		});

		const submit = form.querySelector('[type="submit"]');
		const fail = form.querySelector('[data-form-fail]');

		form.addEventListener('submit', async (e) => {
			e.preventDefault();
			const controls = Array.from(form.querySelectorAll('input:not(.form__honeypot), select, textarea'));
			const invalid = controls.filter((control) => !validate(control));
			if (invalid.length) {
				invalid[0].focus();
				return;
			}

			const data = new FormData(form);
			data.append('page', window.location.href);
			submit.disabled = true;
			form.classList.add('form--loading');
			if (fail) fail.hidden = true;

			try {
				const response = await fetch(form.action, { method: 'POST', body: data, headers: { Accept: 'application/json' } });
				const result = await response.json();
				if (!response.ok || !result.ok) throw new Error(result.error || response.status);
				form.classList.add('form--sent');
				const success = form.querySelector('[data-form-success]');
				if (success) success.hidden = false;
				form.reset();
			} catch (error) {
				// Немає PHP (сайт відкрито з диска або на GitHub Pages) чи Telegram не відповів — показуємо телефон
				if (fail) fail.hidden = false;
			} finally {
				submit.disabled = false;
				form.classList.remove('form--loading');
			}
		});
	});
}

/* ==========================================================================
   Кнопка зв'язку, швидкий вибір послуги, посилання-заглушки
   ========================================================================== */
function initContacts() {
	// Кругла кнопка розгортає список месенджерів
	const fab = document.querySelector('[data-fab]');
	const toggle = document.querySelector('[data-fab-toggle]');
	if (fab && toggle) {
		const setOpen = (state) => {
			fab.classList.toggle('fab--open', state);
			toggle.setAttribute('aria-expanded', String(state));
			toggle.setAttribute('aria-label', state ? t.fabClose : t.fabOpen);
		};
		toggle.addEventListener('click', () => setOpen(!fab.classList.contains('fab--open')));
		document.addEventListener('click', (e) => {
			if (!e.target.closest('[data-fab]')) setOpen(false);
		});
		document.addEventListener('keydown', (e) => {
			if (e.code === 'Escape') setOpen(false);
		});
	}

	// Швидкий вибір у першому екрані підставляє послугу у форму заявки
	const quick = document.querySelector('[data-quick]');
	if (quick) {
		quick.addEventListener('submit', (e) => {
			e.preventDefault();
			const select = document.querySelector('[data-form-service]');
			const target = document.getElementById('request');
			if (select) select.value = quick.querySelector('[data-quick-select]').value;
			if (target) target.scrollIntoView();
			const name = target && target.querySelector('input[name="name"]');
			if (name) name.focus({ preventScroll: true });
		});
	}

}

/* ==========================================================================
   Вибір міста: вікно з пошуком по обласних центрах
   ========================================================================== */
// Сторінки регіонів ще не створені. Коли замовник погодить адреси, вписати їх сюди
// (ключ — українська назва міста, однакова для обох мов):
// { 'Київ': '/kyiv/', 'Харків': '/kharkiv/', ... } — тоді вибір міста переводитиме на сторінку.
const CITY_URLS = {};
const CITY_KEY = 'ma-city';

function initCity() {
	const modal = document.querySelector('[data-city]');
	if (!modal) return;
	const input = modal.querySelector('[data-city-search]');
	const items = Array.from(modal.querySelectorAll('[data-city-list] li'));
	const empty = modal.querySelector('[data-city-empty]');
	const labels = document.querySelectorAll('[data-city-label]');
	let opener = null;

	const read = () => {
		try {
			return localStorage.getItem(CITY_KEY);
		} catch (e) {
			return null;
		}
	};
	const save = (city) => {
		try {
			localStorage.setItem(CITY_KEY, city);
		} catch (e) {
			/* приватний режим — просто не запам'ятовуємо */
		}
	};
	// Зберігаємо id міста (українська назва), а показуємо назву мовою сторінки
	const show = (id) => {
		const current = Array.from(modal.querySelectorAll('[data-city-id]')).find((btn) => btn.dataset.cityId === id);
		if (!current) return;
		labels.forEach((label) => (label.textContent = current.dataset.cityItem));
		modal.querySelectorAll('[data-city-id]').forEach((btn) => {
			btn.classList.toggle('city__link--active', btn === current);
		});
	};

	const filter = () => {
		const query = input.value.trim().toLowerCase();
		let shown = 0;
		items.forEach((li) => {
			const btn = li.querySelector('[data-city-item]');
			const text = (btn.dataset.cityItem + ' ' + btn.dataset.cityRegion).toLowerCase();
			// Без запиту — лише популярні міста, з запитом — пошук по всіх обласних центрах і областях
			li.hidden = query ? !text.includes(query) : !('cityPopular' in li.dataset);
			if (!li.hidden) shown++;
		});
		empty.hidden = !query || shown > 0;
	};

	const open = (trigger) => {
		opener = trigger;
		modal.hidden = false;
		bodyLock(0);
		input.value = '';
		filter();
		input.focus();
	};
	const close = () => {
		if (modal.hidden) return;
		modal.hidden = true;
		bodyUnlock(0);
		if (opener) opener.focus();
	};

	document.querySelectorAll('[data-city-open]').forEach((btn) => {
		btn.addEventListener('click', () => {
			// На мобільному відкрите меню треба закрити, інакше вікно з'явиться під ним
			if (html.classList.contains('menu-open')) document.querySelector('[data-burger]').click();
			open(btn);
		});
	});
	modal.querySelectorAll('[data-city-close]').forEach((btn) => btn.addEventListener('click', close));
	document.addEventListener('keydown', (e) => {
		if (e.code === 'Escape') close();
	});
	input.addEventListener('input', filter);
	// Enter у пошуку обирає перше знайдене місто
	input.addEventListener('keydown', (e) => {
		if (e.key !== 'Enter') return;
		e.preventDefault();
		const first = items.find((li) => !li.hidden);
		if (first) first.querySelector('[data-city-id]').click();
	});

	modal.addEventListener('click', (e) => {
		const btn = e.target.closest('[data-city-id]');
		if (!btn) return;
		const id = btn.dataset.cityId;
		save(id);
		show(id);
		close();
		if (CITY_URLS[id]) window.location.href = CITY_URLS[id];
	});

	const stored = read();
	if (stored) show(stored);
}

/* ==========================================================================
   Анімації GSAP. Стартові стани задані в CSS під класом .js-anim
   ========================================================================== */
function initStepsLine() {
	const lists = Array.from(document.querySelectorAll('[data-steps]'));
	if (!lists.length) return;
	const update = () => {
		const vh = window.innerHeight;
		const vertical = window.matchMedia('(max-width: 48em)').matches;
		lists.forEach((list) => {
			const fill = list.querySelector('[data-steps-fill]');
			if (!fill) return;
			const rect = list.getBoundingClientRect();
			const startTop = vh * 0.75;
			const endTop = vh * 0.6 - rect.height;
			const span = startTop - endTop;
			let p = span > 0 ? (startTop - rect.top) / span : 0;
			p = Math.max(0, Math.min(1, p));
			fill.style.transform = vertical ? 'scaleY(' + p + ')' : 'scaleX(' + p + ')';
		});
	};
	update();
	window.addEventListener('scroll', update, { passive: true });
	window.addEventListener('resize', update);
}


function initAnimations() {
	const reduced = window.matchMedia('(prefers-reduced-motion: reduce)').matches;
	if (reduced || !window.gsap || !window.ScrollTrigger) {
		html.classList.remove('js-anim');
		return;
	}

	gsap.registerPlugin(ScrollTrigger);
	gsap.defaults({ ease: 'power2.out', duration: 0.6 });

	/* Лінія кроків рахується окремо в initStepsLine (без GSAP) */

	/* Легкий паралакс плаваючих карток першого екрана, лише десктоп */
	gsap.matchMedia().add('(min-width: 62.0625em)', () => {
		gsap.utils.toArray('.hero__float').forEach((chip, i) => {
			gsap.to(chip, {
				yPercent: i % 2 ? -40 : 40,
				ease: 'none',
				scrollTrigger: { trigger: '.hero', start: 'top top', end: 'bottom top', scrub: true },
			});
		});
	});
}

/* ==========================================================================
   Старт
   ========================================================================== */
/* ==========================================================================
   Анкета замовлення (сторінки послуг): умовні поля + відправка на send.php
   ========================================================================== */
function initOrderForms() {
	document.querySelectorAll('[data-order]').forEach((form) => {
		const wrappers = Array.from(form.querySelectorAll('[data-cond]'));

		const value = (id) => {
			const el = form.querySelector('[name="f' + id + '"]');
			if (!el) return null;
			if (el.type === 'checkbox' || el.type === 'radio') {
				const checked = form.querySelector('[name="f' + id + '"]:checked');
				return checked ? checked.value : null;
			}
			return el.value;
		};
		const matches = (c) => {
			const v = value(c.f);
			if (c.op === '==') return v === c.v;
			if (c.op === '!=') return v !== c.v;
			return false;
		};
		const evaluate = () => {
			wrappers.forEach((w) => {
				let groups;
				try {
					groups = JSON.parse(w.getAttribute('data-cond'));
				} catch (err) {
					return;
				}
				const show = groups.some((g) => g.every(matches));
				w.hidden = !show;
				if (!show) {
					w.querySelectorAll('input,select,textarea').forEach((x) => {
						if (x.type === 'checkbox' || x.type === 'radio') x.checked = false;
						else x.value = '';
					});
					w.classList.remove('form__field--error');
					const e = w.querySelector('[data-error]');
					if (e) e.textContent = '';
				}
			});
		};
		form.addEventListener('change', evaluate);
		form.addEventListener('input', evaluate);
		evaluate();

		const submit = form.querySelector('[type="submit"]');
		const fail = form.querySelector('[data-form-fail]');
		form.addEventListener('submit', async (ev) => {
			ev.preventDefault();
			let firstInvalid = null;
			form.querySelectorAll('.form__field[data-required]').forEach((w) => {
				if (w.hidden) return;
				const control = w.querySelector('input,select,textarea');
				let ok = false;
				if (!control) ok = true;
				else if (control.type === 'radio' || control.type === 'checkbox') {
					ok = Boolean(form.querySelector('[name="' + control.name + '"]:checked'));
				} else ok = control.value.trim() !== '';
				w.classList.toggle('form__field--error', !ok);
				const e = w.querySelector('[data-error]');
				if (e) e.textContent = ok ? '' : t.errRequired;
				if (!ok && !firstInvalid) firstInvalid = control;
			});
			const consent = form.querySelector('input[name="consent"]');
			if (consent && !consent.checked) {
				const f = consent.closest('.form__field');
				f.classList.add('form__field--error');
				const e = f.querySelector('[data-error]');
				if (e) e.textContent = t.errConsent;
				if (!firstInvalid) firstInvalid = consent;
			}
			if (firstInvalid) {
				firstInvalid.focus();
				return;
			}

			const details = [];
			form.querySelectorAll('.form__field[data-label]').forEach((w) => {
				if (w.hidden) return;
				const label = w.getAttribute('data-label');
				let v = '';
				const radio = w.querySelector('input[type="radio"]:checked');
				const checks = Array.from(w.querySelectorAll('input[type="checkbox"]:checked'));
				if (radio) v = radio.value;
				else if (checks.length) v = checks.map((c) => c.value).join(', ');
				else {
					const c = w.querySelector('input:not([type="radio"]):not([type="checkbox"]), select, textarea');
					if (c) v = c.value.trim();
				}
				if (v) details.push({ label: label, value: v });
			});

			const data = new FormData(form);
			data.set('details', JSON.stringify(details));
			const phoneEl = form.querySelector('input[type="tel"]');
			if (phoneEl && phoneEl.value.trim()) data.set('phone', phoneEl.value.trim());
			const nameWrap = Array.from(form.querySelectorAll('.form__field[data-label]')).find((w) => /ПІБ|ФИО/i.test(w.getAttribute('data-label')));
			if (nameWrap) {
				const c = nameWrap.querySelector('input,select,textarea');
				if (c && c.value.trim()) data.set('name', c.value.trim());
			}

			submit.disabled = true;
			form.classList.add('form--loading');
			if (fail) fail.hidden = true;
			try {
				const response = await fetch(form.action, { method: 'POST', body: data, headers: { Accept: 'application/json' } });
				const result = await response.json();
				if (!response.ok || !result.ok) throw new Error(result.error || response.status);
				form.classList.add('form--sent');
				const success = form.querySelector('[data-form-success]');
				if (success) success.hidden = false;
				form.reset();
				evaluate();
			} catch (err) {
				if (fail) fail.hidden = false;
			} finally {
				submit.disabled = false;
				form.classList.remove('form--loading');
			}
		});
	});
}

document.addEventListener('DOMContentLoaded', () => {
	initHeader();
	initMenu();
	initServices();
	initFaq();
	initForms();
	initOrderForms();
	initContacts();
	initCity();
	initStepsLine();
	initAnimations();
});
