/* Служебные интерактивные варианты секции отзывов. */
document.addEventListener('DOMContentLoaded', () => {
	if (window.Swiper) {
		document.querySelectorAll('[data-concept-slider]').forEach((slider) => {
			const section = slider.closest('[data-review-concept]');
			const mode = slider.dataset.conceptSlider;
			const shared = {
				observer: true,
				observeParents: true,
				loop: true,
				watchOverflow: true,
				speed: 650,
				keyboard: {
					enabled: true,
					onlyInViewport: true,
				},
				navigation: {
					prevEl: section.querySelector('[data-concept-prev]'),
					nextEl: section.querySelector('[data-concept-next]'),
				},
				pagination: {
					el: section.querySelector('[data-concept-pagination]'),
					clickable: true,
				},
			};

			if (mode === 'stage') {
				new Swiper(slider, {
					...shared,
					centeredSlides: true,
					slidesPerView: 1.08,
					spaceBetween: 12,
					breakpoints: {
						576: { slidesPerView: 1.3, spaceBetween: 18 },
						992: { slidesPerView: 1.55, spaceBetween: 28 },
					},
				});
				return;
			}

			new Swiper(slider, {
				...shared,
				slidesPerView: 1,
				spaceBetween: 14,
				breakpoints: mode === 'split'
					? {
						640: { slidesPerView: 2, spaceBetween: 18 },
					}
					: {
						576: { slidesPerView: 2, spaceBetween: 18 },
						992: { slidesPerView: 3, spaceBetween: 24 },
					},
			});
		});
	}

	document.querySelectorAll('[data-review-focus]').forEach((block) => {
		const card = block.querySelector('.review-focus__card');
		const name = block.querySelector('[data-focus-name]');
		const text = block.querySelector('[data-focus-text]');
		const tabs = Array.from(block.querySelectorAll('[data-focus-tab]'));
		card.setAttribute('aria-live', 'polite');

		tabs.forEach((tab) => {
			tab.addEventListener('click', () => {
				if (tab.classList.contains('review-focus__tab--active')) return;
				tabs.forEach((item) => {
					const isActive = item === tab;
					item.classList.toggle('review-focus__tab--active', isActive);
					item.setAttribute('aria-pressed', String(isActive));
				});
				card.classList.add('review-focus__card--changing');
				window.setTimeout(() => {
					name.textContent = tab.dataset.name;
					text.textContent = tab.dataset.text;
					card.classList.remove('review-focus__card--changing');
				}, 160);
			});
		});
	});
});
