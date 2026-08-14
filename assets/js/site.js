document.querySelectorAll(".agent-set").forEach((agentSet) => {
	const carousel = agentSet.querySelector(".agent-carousel");
	const previous = agentSet.querySelector("[data-carousel-prev]");
	const next = agentSet.querySelector("[data-carousel-next]");

	if (!carousel || !previous || !next) return;

	const updateControls = () => {
		const maxScroll = carousel.scrollWidth - carousel.clientWidth;
		previous.disabled = carousel.scrollLeft <= 2;
		next.disabled = carousel.scrollLeft >= maxScroll - 2;
	};

	const move = (direction) => {
		carousel.scrollBy({
			left: direction * carousel.clientWidth,
			behavior: window.matchMedia("(prefers-reduced-motion: reduce)").matches ? "auto" : "smooth",
		});
	};

	previous.addEventListener("click", () => move(-1));
	next.addEventListener("click", () => move(1));
	carousel.addEventListener("scroll", updateControls, { passive: true });
	window.addEventListener("resize", updateControls);
	updateControls();
});

function enhanceMobileNavigation() {
	const toggle = document.querySelector("[data-mobile-menu-toggle]");
	const shell = document.querySelector("[data-mobile-menu-shell]");
	const drawer = document.querySelector("[data-mobile-navigation]");
	const scrim = document.querySelector("[data-mobile-menu-scrim]");
	if (!toggle || !shell || !drawer) return;

	const isOpen = () => !drawer.hidden;

	const setOpen = (open, restoreFocus = false) => {
		drawer.hidden = !open;
		drawer.setAttribute("aria-hidden", String(!open));
		if (scrim) scrim.hidden = !open;
		shell.classList.toggle("is-open", open);
		document.body.classList.toggle("mobile-menu-open", open);
		toggle.setAttribute("aria-expanded", String(open));
		toggle.setAttribute("aria-label", open ? "Close navigation" : "Open navigation");

		if (open) {
			const firstLink = drawer.querySelector("a[href]");
			if (firstLink) window.requestAnimationFrame(() => firstLink.focus());
		} else if (restoreFocus) {
			toggle.focus();
		}
	};

	toggle.addEventListener("click", () => setOpen(!isOpen()));
	drawer.querySelectorAll("a[href]").forEach((link) => link.addEventListener("click", () => setOpen(false)));
	if (scrim) scrim.addEventListener("click", () => setOpen(false, true));

	document.addEventListener("keydown", (event) => {
		if (!isOpen()) return;
		if (event.key === "Escape") {
			event.preventDefault();
			setOpen(false, true);
			return;
		}
		if (event.key !== "Tab") return;

		const focusable = [toggle, ...drawer.querySelectorAll("a[href], button:not([disabled]), [tabindex]:not([tabindex=\"-1\"])")];
		const first = focusable[0];
		const last = focusable[focusable.length - 1];
		if (event.shiftKey && document.activeElement === first) {
			event.preventDefault();
			last.focus();
		} else if (!event.shiftKey && document.activeElement === last) {
			event.preventDefault();
			first.focus();
		}
	});
}

enhanceMobileNavigation();

document.addEventListener("click", (event) => {
	document.querySelectorAll(".site-nav-dropdown[open]").forEach((dropdown) => {
		if (!dropdown.contains(event.target)) dropdown.removeAttribute("open");
	});
});
