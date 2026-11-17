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
		errDate: 'Вкажіть коректну дату у форматі ДД.ММ.РРРР',
		orderStep: 'Крок',
		orderStepOf: 'з',
		search_ph: 'Пошук…',
		select_ph: '— оберіть —',
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
		errDate: 'Укажите корректную дату в формате ДД.ММ.ГГГГ',
		orderStep: 'Шаг',
		orderStepOf: 'из',
		search_ph: 'Поиск…',
		select_ph: '— выберите —',
		fabOpen: 'Написать нам',
		fabClose: 'Закрыть список мессенджеров',
	},
};
const t = I18N[html.lang] || I18N.uk;

const DATEPICKER_LOCALES = {
	uk: {
		days: ['Неділя', 'Понеділок', 'Вівторок', 'Середа', 'Четвер', 'Пʼятниця', 'Субота'],
		daysShort: ['Нд', 'Пн', 'Вт', 'Ср', 'Чт', 'Пт', 'Сб'],
		daysMin: ['Нд', 'Пн', 'Вт', 'Ср', 'Чт', 'Пт', 'Сб'],
		months: ['Січень', 'Лютий', 'Березень', 'Квітень', 'Травень', 'Червень', 'Липень', 'Серпень', 'Вересень', 'Жовтень', 'Листопад', 'Грудень'],
		monthsShort: ['Січ', 'Лют', 'Бер', 'Кві', 'Тра', 'Чер', 'Лип', 'Сер', 'Вер', 'Жов', 'Лис', 'Гру'],
		today: 'Сьогодні',
		clear: 'Очистити',
		dateFormat: 'dd.MM.yyyy',
		timeFormat: 'HH:mm',
		firstDay: 1,
	},
	ru: {
		days: ['Воскресенье', 'Понедельник', 'Вторник', 'Среда', 'Четверг', 'Пятница', 'Суббота'],
		daysShort: ['Вс', 'Пн', 'Вт', 'Ср', 'Чт', 'Пт', 'Сб'],
		daysMin: ['Вс', 'Пн', 'Вт', 'Ср', 'Чт', 'Пт', 'Сб'],
		months: ['Январь', 'Февраль', 'Март', 'Апрель', 'Май', 'Июнь', 'Июль', 'Август', 'Сентябрь', 'Октябрь', 'Ноябрь', 'Декабрь'],
		monthsShort: ['Янв', 'Фев', 'Мар', 'Апр', 'Май', 'Июн', 'Июл', 'Авг', 'Сен', 'Окт', 'Ноя', 'Дек'],
		today: 'Сегодня',
		clear: 'Очистить',
		dateFormat: 'dd.MM.yyyy',
		timeFormat: 'HH:mm',
		firstDay: 1,
	},
};
const datepickerInstances = new WeakMap();

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
   Небольшая форма вопроса в нативном диалоге
   ========================================================================== */
function initDialogs() {
	const dialogs = Array.from(document.querySelectorAll('[data-dialog]'));
	if (!dialogs.length) return;

	const syncScrollLock = () => {
		const hasOpenDialog = dialogs.some((dialog) => dialog.open);
		const cityIsOpen = Boolean(document.querySelector('[data-city]:not([hidden])'));
		if (hasOpenDialog && !html.hasAttribute('data-scroll-lock') && bodyLockStatus) {
			bodyLock(0);
		} else if (!hasOpenDialog && !cityIsOpen && !html.classList.contains('menu-open') && html.hasAttribute('data-scroll-lock')) {
			if (bodyLockStatus) bodyUnlock(0);
			else setTimeout(syncScrollLock, 50);
		}
	};

	document.addEventListener('click', (event) => {
		const openButton = event.target.closest('[data-dialog-open]');
		if (openButton) {
			const dialog = document.getElementById(openButton.dataset.dialogOpen);
			if (dialog && !dialog.open) {
				dialog.showModal();
				syncScrollLock();
			}
			return;
		}

		const closeButton = event.target.closest('[data-dialog-close]');
		if (closeButton) {
			const dialog = closeButton.closest('dialog');
			if (dialog) dialog.close();
		}
	});

	dialogs.forEach((dialog) => {
		dialog.addEventListener('click', (event) => {
			if (event.target === dialog) dialog.close();
		});
		new MutationObserver(syncScrollLock).observe(dialog, { attributes: true, attributeFilter: ['open'] });
	});
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
/* ==========================================================================
   Кастомний селект для анкети (у стилі сайту, з пошуком)
   ========================================================================== */
function initCustomSelects() {
	document.querySelectorAll('[data-order] select.form__input--select').forEach((select) => {
		if (select.dataset.cselect) return;
		select.dataset.cselect = '1';

		const wrap = document.createElement('div');
		wrap.className = 'cselect';
		select.parentNode.insertBefore(wrap, select);
		wrap.appendChild(select);
		select.classList.add('cselect__native');

		const trigger = document.createElement('button');
		trigger.type = 'button';
		trigger.className = 'cselect__trigger';
		trigger.setAttribute('aria-haspopup', 'listbox');
		trigger.setAttribute('aria-expanded', 'false');
		const triggerValue = document.createElement('span');
		triggerValue.className = 'cselect__value';
		trigger.appendChild(triggerValue);
		wrap.appendChild(trigger);

		const panel = document.createElement('div');
		panel.className = 'cselect__panel';
		panel.hidden = true;
		const search = document.createElement('input');
		search.type = 'search';
		search.className = 'cselect__search';
		search.placeholder = t.search_ph;
		search.autocomplete = 'off';
		const list = document.createElement('ul');
		list.className = 'cselect__list';
		list.setAttribute('role', 'listbox');
		panel.appendChild(search);
		panel.appendChild(list);
		wrap.appendChild(panel);

		const placeholder = select.options[0] && !select.options[0].value ? select.options[0].textContent : t.select_ph;
		const items = [];
		Array.from(select.options).forEach((opt) => {
			if (!opt.value) return;
			const li = document.createElement('li');
			li.className = 'cselect__option';
			li.setAttribute('role', 'option');
			li.textContent = opt.textContent;
			li.dataset.value = opt.value;
			list.appendChild(li);
			items.push(li);
		});

		const filter = (q) => {
			q = q.trim().toLowerCase();
			items.forEach((li) => {
				li.hidden = Boolean(q) && !li.textContent.toLowerCase().includes(q);
			});
		};
		const sync = () => {
			const sel = select.options[select.selectedIndex];
			const isPlaceholder = !select.value;
			const text = isPlaceholder ? placeholder : sel.textContent;
			triggerValue.textContent = text;
			trigger.title = isPlaceholder ? '' : text;
			trigger.classList.toggle('cselect__trigger--placeholder', isPlaceholder);
			items.forEach((li) => li.setAttribute('aria-selected', li.dataset.value === select.value ? 'true' : 'false'));
		};
		const close = () => {
			panel.hidden = true;
			trigger.setAttribute('aria-expanded', 'false');
		};
		const open = () => {
			panel.hidden = false;
			trigger.setAttribute('aria-expanded', 'true');
			search.value = '';
			filter('');
			search.focus();
		};
		const choose = (value) => {
			select.value = value;
			select.dispatchEvent(new Event('change', { bubbles: true }));
			sync();
			close();
			trigger.focus();
		};

		items.forEach((li) => li.addEventListener('click', () => choose(li.dataset.value)));
		trigger.addEventListener('click', () => (panel.hidden ? open() : close()));
		select.addEventListener('change', sync);
		search.addEventListener('input', () => filter(search.value));
		search.addEventListener('keydown', (e) => {
			if (e.key === 'Enter') {
				e.preventDefault();
				const first = items.find((li) => !li.hidden);
				if (first) choose(first.dataset.value);
			}
		});
		document.addEventListener('click', (e) => {
			if (!wrap.contains(e.target)) close();
		});
		document.addEventListener('keydown', (e) => {
			if (e.key === 'Escape') close();
		});
		const form = select.closest('form');
		if (form) form.addEventListener('reset', () => setTimeout(sync, 0));

		sync();
	});
}


function parseDateValue(value) {
	const normalized = String(value || '').trim();
	let parts = normalized.match(/^(\d{2})\.(\d{2})\.(\d{4})$/);
	if (!parts) {
		const iso = normalized.match(/^(\d{4})-(\d{2})-(\d{2})$/);
		if (!iso) return null;
		parts = [iso[0], iso[3], iso[2], iso[1]];
	}

	const day = Number(parts[1]);
	const month = Number(parts[2]);
	const year = Number(parts[3]);
	const date = new Date(year, month - 1, day);
	if (date.getFullYear() !== year || date.getMonth() !== month - 1 || date.getDate() !== day) return null;
	return date;
}

function formatDateValue(date) {
	const pad = (value) => String(value).padStart(2, '0');
	return `${pad(date.getDate())}.${pad(date.getMonth() + 1)}.${date.getFullYear()}`;
}

function isValidDateInput(input) {
	const date = parseDateValue(input.value);
	if (!date) return false;
	if (!input.hasAttribute('data-datepicker-birth')) return true;
	const today = new Date();
	today.setHours(23, 59, 59, 999);
	return date <= today;
}

function initDatepickers() {
	const fields = document.querySelectorAll('[data-datepicker]');
	if (!fields.length) return;

	if (typeof window.AirDatepicker !== 'function') {
		const now = new Date();
		const pad = (value) => String(value).padStart(2, '0');
		const today = `${now.getFullYear()}-${pad(now.getMonth() + 1)}-${pad(now.getDate())}`;
		fields.forEach((input) => {
			input.type = 'date';
			input.placeholder = '';
			if (input.hasAttribute('data-datepicker-birth')) input.max = today;
		});
		return;
	}

	const locale = DATEPICKER_LOCALES[html.lang] || DATEPICKER_LOCALES.uk;
	const mobile = window.matchMedia('(max-width: 48em)').matches;
	fields.forEach((input) => {
		const isBirthDate = input.hasAttribute('data-datepicker-birth');
		const initialDate = parseDateValue(input.value);
		const validInitialDate = initialDate && (!isBirthDate || isValidDateInput(input));
		const options = {
			locale,
			autoClose: true,
			dateFormat: 'dd.MM.yyyy',
			view: isBirthDate ? 'years' : 'days',
			keyboardNav: true,
			toggleSelected: false,
			isMobile: mobile,
		};
		if (isBirthDate) {
			options.maxDate = new Date();
			options.startDate = validInitialDate ? initialDate : new Date(1990, 0, 1);
		}
		if (validInitialDate) options.selectedDates = [initialDate];
		else if (input.value) input.value = '';

		const picker = new window.AirDatepicker(input, options);
		datepickerInstances.set(input, picker);
		if (initialDate && (!isBirthDate || initialDate <= new Date())) input.value = formatDateValue(initialDate);
		input.addEventListener('blur', () => {
			const date = parseDateValue(input.value);
			if (!date || (isBirthDate && !isValidDateInput(input))) return;
			picker.selectDate(date, { silent: true });
			input.value = formatDateValue(date);
		});

		const form = input.closest('form');
		if (form) form.addEventListener('reset', () => setTimeout(() => picker.clear({ silent: true }), 0));
	});
}


function initOrderForms() {
	document.querySelectorAll('[data-order]').forEach((form) => {
		const wrappers = Array.from(form.querySelectorAll('[data-cond]'));
		const gate = form.querySelector('[data-order-gate]');
		const syncGate = () => {
			if (gate) form.classList.toggle('order-form--expanded', gate.value !== '');
		};

		const focusControl = (control) => {
			const customTrigger = control.closest('.cselect') && control.closest('.cselect').querySelector('.cselect__trigger');
			(customTrigger || control).focus();
		};

		const validateVisibleFields = () => {
			let firstInvalid = null;
			form.querySelectorAll('.form__field').forEach((wrapper) => {
				if (wrapper.hidden) return;
				const control = wrapper.querySelector('input,select,textarea');
				const isRequired = wrapper.hasAttribute('data-required');
				const isDate = control && control.matches('[data-datepicker]');
				if (!isRequired && !isDate) return;
				let valid = false;
				if (!control) valid = true;
				else if (control.type === 'radio' || control.type === 'checkbox') {
					valid = Boolean(form.querySelector('[name="' + control.name + '"]:checked'));
				} else if (isDate) {
					valid = control.value.trim() === '' ? !isRequired : isValidDateInput(control);
				} else valid = control.value.trim() !== '';
				wrapper.classList.toggle('form__field--error', !valid);
				const error = wrapper.querySelector('[data-error]');
				if (error) {
					const empty = !control || control.value.trim() === '';
					error.textContent = valid ? '' : isDate && !empty ? t.errDate : t.errRequired;
				}
				if (!valid && !firstInvalid) firstInvalid = control;
			});
			return firstInvalid;
		};

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
						else {
							const datepicker = datepickerInstances.get(x);
							if (datepicker) datepicker.clear({ silent: true });
							x.value = '';
							if (x.tagName === 'SELECT') x.dispatchEvent(new Event('change'));
						}
					});
					w.classList.remove('form__field--error');
					const e = w.querySelector('[data-error]');
					if (e) e.textContent = '';
				}
			});
		};
		const fail = form.querySelector('[data-form-fail]');
		const clearFail = () => {
			if (fail) fail.hidden = true;
		};
		form.addEventListener('change', () => {
			clearFail();
			evaluate();
			syncGate();
		});
		form.addEventListener('input', () => {
			clearFail();
			evaluate();
		});
		form.addEventListener('reset', () => setTimeout(() => {
			evaluate();
			syncGate();
		}, 0));
		evaluate();
		syncGate();

		const submit = form.querySelector('[type="submit"]');
		form.addEventListener('submit', async (ev) => {
			ev.preventDefault();
			let firstInvalid = validateVisibleFields();
			const consent = form.querySelector('input[name="consent"]');
			if (consent && !consent.checked) {
				const f = consent.closest('.form__field');
				f.classList.add('form__field--error');
				const e = f.querySelector('[data-error]');
				if (e) e.textContent = t.errConsent;
				if (!firstInvalid) firstInvalid = consent;
			}
			if (firstInvalid) {
				focusControl(firstInvalid);
				firstInvalid.closest('.form__field').scrollIntoView({
					behavior: window.matchMedia('(prefers-reduced-motion: reduce)').matches ? 'auto' : 'smooth',
					block: 'center',
				});
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
					if (c && c.type === 'file') v = c.files && c.files[0] ? c.files[0].name : '';
					else if (c) v = c.value.trim();
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
	initDatepickers();
	initOrderForms();
	initCustomSelects();
	initContacts();
	initDialogs();
	initCity();
	initStepsLine();
	initAnimations();
});
