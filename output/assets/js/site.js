document.querySelectorAll(".agent-carousel-shell").forEach((shell) => {
	const carousel = shell.querySelector(".agent-carousel");
	const previous = shell.querySelector("[data-carousel-prev]");
	const next = shell.querySelector("[data-carousel-next]");

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

function enhanceHeroDither() {
	const bayer8 = [
		[0, 48, 12, 60, 3, 51, 15, 63],
		[32, 16, 44, 28, 35, 19, 47, 31],
		[8, 56, 4, 52, 11, 59, 7, 55],
		[40, 24, 36, 20, 43, 27, 39, 23],
		[2, 50, 14, 62, 1, 49, 13, 61],
		[34, 18, 46, 30, 33, 17, 45, 29],
		[10, 58, 6, 54, 9, 57, 5, 53],
		[42, 26, 38, 22, 41, 25, 37, 21],
	];

	document.querySelectorAll(".chain-hero__media").forEach((media) => {
		const image = media.querySelector("img");
		const canvas = media.querySelector("[data-hero-dither]");
		if (!image || !canvas) return;

		const context = canvas.getContext("2d", { willReadFrequently: true });
		const sourceCanvas = document.createElement("canvas");
		const sourceContext = sourceCanvas.getContext("2d", { willReadFrequently: true });
		let sourcePixels = null;
		let resizeFrame = 0;

		if (!context || !sourceContext) return;

		const sizeCanvas = () => {
			// A low-resolution static pass keeps the ordered-dither treatment while
			// avoiding a full-screen per-pixel animation on the main thread.
			const width = Math.max(1, Math.ceil(media.clientWidth / 6));
			const height = Math.max(1, Math.ceil(media.clientHeight / 6));
			canvas.width = width;
			canvas.height = height;
			sourceCanvas.width = width;
			sourceCanvas.height = height;

			const scale = Math.max(width / image.naturalWidth, height / image.naturalHeight);
			const drawWidth = image.naturalWidth * scale;
			const drawHeight = image.naturalHeight * scale;
			sourceContext.clearRect(0, 0, width, height);
			sourceContext.drawImage(image, width - drawWidth, (height - drawHeight) / 2, drawWidth, drawHeight);
			sourcePixels = sourceContext.getImageData(0, 0, width, height);
		};

		const drawFrame = () => {
			if (!sourcePixels) return;
			const width = canvas.width;
			const height = canvas.height;
			const output = context.createImageData(width, height);
			const source = sourcePixels.data;
			const target = output.data;

			for (let y = 0; y < height; y += 1) {
				for (let x = 0; x < width; x += 1) {
					const index = (y * width + x) * 4;
					let luminance = 0.299 * source[index] + 0.587 * source[index + 1] + 0.114 * source[index + 2];
					luminance = (luminance - 128) * 1.12 + 128;
					const matrix = bayer8[y % 8][x % 8];
					const threshold = 94 + matrix * 1.88;
					const value = luminance > threshold ? 244 : 14;
					target[index] = value;
					target[index + 1] = value;
					target[index + 2] = value;
					target[index + 3] = 255;
				}
			}

			context.putImageData(output, 0, 0);
			canvas.dataset.ditherReady = "true";
		};

		const setup = () => {
			sizeCanvas();
			drawFrame();
		};

		const handleResize = () => {
			window.cancelAnimationFrame(resizeFrame);
			resizeFrame = window.requestAnimationFrame(() => {
				sizeCanvas();
				drawFrame();
			});
		};

		if (image.complete && image.naturalWidth) setup();
		else image.addEventListener("load", setup, { once: true });
		window.addEventListener("resize", handleResize);
	});
}

enhanceHeroDither();

document.addEventListener("click", (event) => {
	document.querySelectorAll(".site-nav-dropdown[open]").forEach((dropdown) => {
		if (!dropdown.contains(event.target)) dropdown.removeAttribute("open");
	});
});

document.querySelectorAll("[data-agent-directory-grid]").forEach((grid) => {
	const categoryFilter = document.querySelector("[data-agent-category-filter]");
	const sortControl = document.querySelector("[data-agent-sort]");
	const results = document.querySelector("[data-agent-results]");
	const cards = Array.from(grid.querySelectorAll(".listing-card"));

	if (!categoryFilter || !sortControl || cards.length === 0) return;

	const compareText = (a, b) => a.localeCompare(b, undefined, { sensitivity: "base" });
	const cardValue = (card, key) => card.dataset[key] || "";

	const refresh = () => {
		const category = categoryFilter.value;
		const sort = sortControl.value;
		const sorted = [...cards].sort((a, b) => {
			const aTitle = cardValue(a, "agentTitle");
			const bTitle = cardValue(b, "agentTitle");
			if (sort === "az") return compareText(aTitle, bTitle);
			if (sort === "za") return compareText(bTitle, aTitle);
			if (sort === "updated-desc") {
				return compareText(cardValue(b, "agentUpdated"), cardValue(a, "agentUpdated")) || compareText(aTitle, bTitle);
			}
			if (sort === "updated-asc") {
				return compareText(cardValue(a, "agentUpdated"), cardValue(b, "agentUpdated")) || compareText(aTitle, bTitle);
			}
			return Number(cardValue(a, "agentOrder")) - Number(cardValue(b, "agentOrder"));
		});

		let visible = 0;
		sorted.forEach((card) => {
			const matches = category === "all" || cardValue(card, "agentCategory") === category;
			card.hidden = !matches;
			if (matches) visible += 1;
			grid.append(card);
		});

		if (results) results.textContent = `${visible} ${visible === 1 ? "agent" : "agents"}`;
	};

	categoryFilter.addEventListener("change", refresh);
	sortControl.addEventListener("change", refresh);
	refresh();
});
