/* ==========================================================================
   Хелпери
   ========================================================================== */
const html = document.documentElement;

// Тексти інтерфейсу для двох мовних версій; мова береться з <html lang>
const I18N = {
	uk: {
		menuOpen: 'Відкрити меню',
		menuClose: 'Закрити меню',
		shown: (shown, total) => `Показано ${shown} із ${total}`,
		errName: "Вкажіть ім'я",
		errPhone: 'Вкажіть номер телефону повністю',
		errService: 'Оберіть послугу',
		errConsent: 'Потрібна згода на обробку даних',
		fabOpen: 'Написати нам',
		fabClose: 'Закрити список месенджерів',
	},
	en: {
		menuOpen: 'Open menu',
		menuClose: 'Close menu',
		shown: (shown, total) => `Showing ${shown} of ${total}`,
		errName: 'Enter your name',
		errPhone: 'Enter your full phone number',
		errService: 'Choose a service',
		errConsent: 'Consent to data processing is required',
		fabOpen: 'Message us',
		fabClose: 'Close messenger list',
	},
};
const T = I18N[html.lang === 'en' ? 'en' : 'uk'];
let bodyLockStatus = true;

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
		burger.setAttribute('aria-label', T.menuOpen);
		bodyUnlock();
	};

	burger.addEventListener('click', () => {
		if (!bodyLockStatus) return;
		if (html.classList.contains('menu-open')) {
			close();
		} else {
			html.classList.add('menu-open');
			burger.setAttribute('aria-expanded', 'true');
			burger.setAttribute('aria-label', T.menuClose);
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
			if (count) count.textContent = T.shown(shown, items.length);
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
   Форма заявки: перевірка полів. Обробник відправки ще не підключено.
   ========================================================================== */
function initForms() {
	const rules = {
		name: (v) => (v.trim().length >= 2 ? '' : T.errName),
		phone: (v) => (v.replace(/\D/g, '').length >= 10 ? '' : T.errPhone),
		service: (v) => (v ? '' : T.errService),
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
				message = control.required && !control.checked ? T.errConsent : '';
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

		form.addEventListener('submit', (e) => {
			e.preventDefault();
			const controls = Array.from(form.querySelectorAll('input:not(.form__honeypot), select'));
			const invalid = controls.filter((control) => !validate(control));
			if (invalid.length) {
				invalid[0].focus();
				return;
			}

			const data = Object.fromEntries(new FormData(form));
			delete data.hp_note;
			// TODO: підключити відправку (Telegram / пошта) — зараз дані нікуди не надсилаються
			form.classList.add('form--sent');
			const success = form.querySelector('[data-form-success]');
			if (success) success.hidden = false;
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
			toggle.setAttribute('aria-label', state ? T.fabClose : T.fabOpen);
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

	// Посилання на месенджери ще не надані замовником
	document.querySelectorAll('[data-todo-link]').forEach((link) => {
		link.addEventListener('click', (e) => e.preventDefault());
	});
}

/* ==========================================================================
   Анімації GSAP. Стартові стани задані в CSS під класом .js-anim
   ========================================================================== */
function initAnimations() {
	const reduced = window.matchMedia('(prefers-reduced-motion: reduce)').matches;
	if (reduced || !window.gsap || !window.ScrollTrigger) {
		html.classList.remove('js-anim');
		return;
	}

	gsap.registerPlugin(ScrollTrigger);
	gsap.defaults({ ease: 'expo.out', duration: 1 });

	/* --- Перший екран --- */
	const heroItems = gsap.utils.toArray('[data-hero]');
	const heroVisual = document.querySelector('.service-hero__visual');
	const pins = gsap.utils.toArray('.map__pin');
	const chips = gsap.utils.toArray('[data-hero-chip]');
	const counters = gsap.utils.toArray('[data-count]');

	// Лічильники обнуляємо одразу, поки елемент ще прихований
	counters.forEach((el) => (el.textContent = '0'));
	gsap.set(chips, { autoAlpha: 0 });

	const tl = gsap.timeline({ delay: 0.1 });
	tl.fromTo(heroItems, { y: 28, autoAlpha: 0 }, { y: 0, autoAlpha: 1, stagger: 0.09 }, 0);
	if (heroVisual) {
		tl.to(heroVisual, { clipPath: 'inset(0 0 0% 0 round 28px)', duration: 1.5 }, 0.15);
	}
	if (pins.length) {
		tl.fromTo(
			pins,
			{ y: -26, scale: 0.4, opacity: 0, transformOrigin: '50% 100%' },
			{ y: 0, scale: 1, opacity: 1, duration: 0.9, stagger: 0.14, ease: 'back.out(2)' },
			0.8
		);
	}
	tl.fromTo(chips, { y: 24, autoAlpha: 0 }, { y: 0, autoAlpha: 1, stagger: 0.15 }, 0.9);
	counters.forEach((el) => {
		const state = { value: 0 };
		tl.to(
			state,
			{
				value: Number(el.dataset.count),
				duration: 1.4,
				ease: 'power2.out',
				onUpdate: () => (el.textContent = Math.round(state.value)),
			},
			0.5
		);
	});

	/* --- Поява блоків при скролі, каскад по ряду --- */
	const revealItems = gsap.utils.toArray('[data-reveal]');
	gsap.set(revealItems, { y: 36 });
	ScrollTrigger.batch(revealItems, {
		start: 'top 88%',
		once: true,
		batchMax: () => (window.innerWidth >= 1200 ? 4 : window.innerWidth >= 992 ? 3 : window.innerWidth >= 576 ? 2 : 1),
		onEnter: (batch) => gsap.to(batch, { y: 0, autoAlpha: 1, stagger: 0.1, overwrite: true }),
	});

	/* --- Лінія кроків заповнюється разом зі скролом --- */
	document.querySelectorAll('[data-steps]').forEach((list) => {
		const fill = list.querySelector('[data-steps-fill]');
		if (!fill) return;
		const mm = gsap.matchMedia();
		const scrollTrigger = { trigger: list, start: 'top 75%', end: 'bottom 60%', scrub: 0.6 };
		mm.add('(min-width: 48.0625em)', () => {
			gsap.fromTo(fill, { scaleX: 0, scaleY: 1 }, { scaleX: 1, ease: 'none', scrollTrigger });
		});
		mm.add('(max-width: 48em)', () => {
			gsap.fromTo(fill, { scaleY: 0, scaleX: 1 }, { scaleY: 1, ease: 'none', scrollTrigger });
		});
	});

	/* --- Легкий паралакс плаваючих карток першого екрана, лише десктоп --- */
	gsap.matchMedia().add('(min-width: 62.0625em)', () => {
		gsap.utils.toArray('.hero__float').forEach((chip, i) => {
			gsap.to(chip, {
				yPercent: i % 2 ? -40 : 40,
				ease: 'none',
				scrollTrigger: { trigger: '.hero', start: 'top top', end: 'bottom top', scrub: true },
			});
		});
	});

	/* --- Страховка: якщо спостерігач не спрацював, показуємо все, що в зоні видимості --- */
	setTimeout(() => {
		document.querySelectorAll('[data-reveal], [data-hero], [data-hero-chip]').forEach((el) => {
			const rect = el.getBoundingClientRect();
			const style = getComputedStyle(el);
			const hidden = style.opacity === '0' || style.visibility === 'hidden';
			if (hidden && rect.top < window.innerHeight && rect.bottom > 0 && !gsap.isTweening(el)) {
				gsap.set(el, { autoAlpha: 1, y: 0 });
			}
		});
		if (heroVisual && !gsap.isTweening(heroVisual)) gsap.set(heroVisual, { clipPath: 'none' });
		pins.forEach((pin) => {
			if (!gsap.isTweening(pin)) gsap.set(pin, { opacity: 1 });
		});
	}, 4000);
}

/* ==========================================================================
   Старт
   ========================================================================== */
document.addEventListener('DOMContentLoaded', () => {
	initHeader();
	initMenu();
	initServices();
	initFaq();
	initForms();
	initContacts();
	initAnimations();
});
