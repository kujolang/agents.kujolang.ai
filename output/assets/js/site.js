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

function enhanceHeroDither() {
	const canvas = document.querySelector("[data-hero-dither]");
	const media = canvas && canvas.closest(".chain-hero__media");
	if (!media || window.matchMedia("(prefers-reduced-motion: reduce)").matches) return;

	const image = media.querySelector("[data-dither-source]") || media.querySelector("img");
	const context = canvas && canvas.getContext("2d");
	if (!image || !canvas || !context) return;
	if (image.dataset.src && !image.getAttribute("src")) image.setAttribute("src", image.dataset.src);

	const bayer8 = [
		0, 48, 12, 60, 3, 51, 15, 63,
		32, 16, 44, 28, 35, 19, 47, 31,
		8, 56, 4, 52, 11, 59, 7, 55,
		40, 24, 36, 20, 43, 27, 39, 23,
		2, 50, 14, 62, 1, 49, 13, 61,
		34, 18, 46, 30, 33, 17, 45, 29,
		10, 58, 6, 54, 9, 57, 5, 53,
		42, 26, 38, 22, 41, 25, 37, 21,
	];

	let frames = [];
	let frameIndex = 0;
	let lastTick = 0;
	let resizeTimer = 0;
	let isVisible = true;

	const buildFrames = () => {
		const width = Math.max(1, Math.min(720, Math.ceil(media.clientWidth / 2.5)));
		const height = Math.max(1, Math.round(width * media.clientHeight / media.clientWidth));
		const sourceCanvas = document.createElement("canvas");
		const sourceContext = sourceCanvas.getContext("2d", { willReadFrequently: true });
		if (!sourceContext) return;

		canvas.width = width;
		canvas.height = height;
		sourceCanvas.width = width;
		sourceCanvas.height = height;

		const scale = Math.max(width / image.naturalWidth, height / image.naturalHeight);
		const drawWidth = image.naturalWidth * scale;
		const drawHeight = image.naturalHeight * scale;
		sourceContext.drawImage(image, width - drawWidth, (height - drawHeight) / 2, drawWidth, drawHeight);
		const source = sourceContext.getImageData(0, 0, width, height).data;

		frames = Array.from({ length: 8 }, (_, frame) => {
			const output = context.createImageData(width, height);
			const target = output.data;
			const driftX = frame % 8;
			const driftY = (frame * 3) % 8;
			const thresholdShift = Math.sin(frame * Math.PI / 4) * 12;

			for (let y = 0; y < height; y += 1) {
				for (let x = 0; x < width; x += 1) {
					const index = (y * width + x) * 4;
					let luminance = 0.299 * source[index] + 0.587 * source[index + 1] + 0.114 * source[index + 2];
					luminance = (luminance - 128) * 1.12 + 128;
					const matrix = bayer8[((y + driftY) % 8) * 8 + ((x + driftX) % 8)];
					const value = luminance > 94 + matrix * 1.88 + thresholdShift ? 255 : 0;
					target[index] = value;
					target[index + 1] = value;
					target[index + 2] = value;
					target[index + 3] = 255;
				}
			}

			return output;
		});

		frameIndex = 0;
		context.putImageData(frames[0], 0, 0);
		canvas.dataset.ditherReady = "true";
	};

	const animate = (now) => {
		if (isVisible && !document.hidden && frames.length && now - lastTick >= 100) {
			lastTick = now;
			frameIndex = (frameIndex + 1) % frames.length;
			context.putImageData(frames[frameIndex], 0, 0);
		}
		window.requestAnimationFrame(animate);
	};

	const setup = () => {
		buildFrames();
		window.requestAnimationFrame(animate);
	};

	if ("IntersectionObserver" in window) {
		new IntersectionObserver(([entry]) => { isVisible = entry.isIntersecting; }).observe(media);
	}

	window.addEventListener("resize", () => {
		window.clearTimeout(resizeTimer);
		resizeTimer = window.setTimeout(buildFrames, 140);
	});

	if (image.complete && image.naturalWidth) setup();
	else image.addEventListener("load", setup, { once: true });
}

enhanceHeroDither();

function enhanceCommandCopy() {
	const copyIcon = '<svg class="command-copy-icon" viewBox="0 0 24 24" aria-hidden="true"><rect x="8" y="8" width="11" height="11" rx="1"></rect><path d="M16 8V5H5v11h3"></path></svg>';
	const checkIcon = '<svg class="command-copy-check" viewBox="0 0 24 24" aria-hidden="true"><path d="m5 12 4 4L19 6"></path></svg>';

	const copyText = async (text) => {
		if (navigator.clipboard && window.isSecureContext) {
			await navigator.clipboard.writeText(text);
			return;
		}

		const textarea = document.createElement("textarea");
		textarea.value = text;
		textarea.setAttribute("readonly", "");
		textarea.style.position = "fixed";
		textarea.style.opacity = "0";
		document.body.appendChild(textarea);
		textarea.select();
		document.execCommand("copy");
		textarea.remove();
	};

	const addCopyButton = (container, code) => {
		if (!container || !code || container.querySelector("[data-copy-command]")) return;
		const button = document.createElement("button");
		button.type = "button";
		button.className = "command-copy-button";
		button.dataset.copyCommand = "";
		button.setAttribute("aria-label", "Copy command");
		button.title = "Copy command";
		button.innerHTML = copyIcon + checkIcon;
		button.addEventListener("click", async () => {
			try {
				await copyText(code.textContent.trim());
				button.dataset.copied = "true";
				button.setAttribute("aria-label", "Command copied");
				button.title = "Copied";
				window.setTimeout(() => {
					delete button.dataset.copied;
					button.setAttribute("aria-label", "Copy command");
					button.title = "Copy command";
				}, 1600);
			} catch {
				button.setAttribute("aria-label", "Copy failed");
				button.title = "Copy failed";
			}
		});
		container.appendChild(button);
	};

	document.querySelectorAll(".agent-platform-promo__commands p").forEach((command) => {
		addCopyButton(command, command.querySelector("code"));
	});

	document.querySelectorAll(".agent-platform-body pre").forEach((pre) => {
		const wrapper = document.createElement("div");
		wrapper.className = "command-block";
		pre.parentNode.insertBefore(wrapper, pre);
		wrapper.appendChild(pre);
		addCopyButton(wrapper, pre.querySelector("code"));
	});
}

enhanceCommandCopy();

document.addEventListener("click", (event) => {
	document.querySelectorAll(".site-nav-dropdown[open]").forEach((dropdown) => {
		if (!dropdown.contains(event.target)) dropdown.removeAttribute("open");
	});
});
