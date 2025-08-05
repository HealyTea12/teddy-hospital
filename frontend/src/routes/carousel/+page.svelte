<script>
	import { onMount, onDestroy, tick } from 'svelte';
	import JSZip from 'jszip';

	let xrayImages = [];
	let originalImages = [];
	let visibleCount = 3;
	let autoplay = true;
	let autoplaySpeed = 3000; // in ms
	let autoplayTimer;
	let showOriginal = true;

	let internalIndex = 0;
	let transitioning = false; // Track if a transition is happening

	let fullscreen = false;

	$: totalVisible = visibleCount;
	$: clonesBefore = xrayImages.slice(-totalVisible);
	$: clonesAfter = xrayImages.slice(0, totalVisible);

	$: clonesBeforeOriginal = originalImages.slice(-totalVisible);
	$: clonesAfterOriginal = originalImages.slice(0, totalVisible);

	$: extendedImages = [...clonesBefore, ...xrayImages, ...clonesAfter];
	$: extendedImagesOriginal = [...clonesBeforeOriginal, ...originalImages, ...clonesAfterOriginal];

	$: baseIndex = totalVisible; // first real image

	$: slideOffset = fullscreen
		? -(internalIndex - baseIndex) * 100
		: -(internalIndex * (100 / visibleCount)); // change offset based on sreen mode to use the same .track logic

	onMount(() => {
		let cancelled = false;

		(async () => {
			try {
				const res = await fetch(`http://localhost:8000/carousel`);
				if (!res.ok) throw new Error('Failed to fetch carousel list');
				const carouselUrls = await res.json();

				// fetch all ZIPs
				const fetches = carouselUrls.map((url) => fetch(url));
				const zipResponses = await Promise.all(fetches);

				if (xrayImages.length > 0) {
					xrayImages.forEach((url) => URL.revokeObjectURL(url));
					originalImages.forEach((url) => URL.revokeObjectURL(url));
					xrayImages = [];
					originalImages = [];
				}

				// Check all responses are OK
				for (const r of zipResponses) {
					if (!r.ok) throw new Error('Failed to fetch one or more ZIP files');
				}

				// Get blobs from all
				const zipBlobs = await Promise.all(zipResponses.map((r) => r.blob()));

				const jszip = new JSZip();

				// Process each ZIP to extract images
				for (const zipBlob of zipBlobs) {
					if (cancelled) break;

					const zip = await jszip.loadAsync(zipBlob);
					const xrayData = await zip.file('xray.png').async('blob');
					const originalData = await zip.file('original.png').async('blob');

					const xrayUrl = URL.createObjectURL(xrayData);
					const originalUrl = URL.createObjectURL(originalData);

					xrayImages = [...xrayImages, xrayUrl];
					originalImages = [...originalImages, originalUrl];
				}

				if (!cancelled && autoplay) {
					startAutoplay();
				}
			} catch (error) {
				console.error(error);
			}
		})();

		document.addEventListener('fullscreenchange', onFullscreenChange);

		return () => {
			cancelled = true;
			document.removeEventListener('fullscreenchange', onFullscreenChange);

			xrayImages.forEach((url) => URL.revokeObjectURL(url));
			originalImages.forEach((url) => URL.revokeObjectURL(url));
		};
	});

	onDestroy(() => {
		clearInterval(autoplayTimer);
	});

	function startAutoplay() {
		clearInterval(autoplayTimer);
		autoplayTimer = setInterval(() => {
			next();
		}, autoplaySpeed);
	}

	function stopAutoplay() {
		clearInterval(autoplayTimer);
	}

	function toggleAutoplay() {
		autoplay = !autoplay;
		if (autoplay) {
			startAutoplay();
		} else {
			stopAutoplay();
		}
	}

	async function prev() {
		stopAutoplay();
		transitioning = true;
		internalIndex++;
		await tick();
		handleLoop();

		if (autoplay) startAutoplay();
	}

	async function next() {
		stopAutoplay();
		transitioning = true;
		internalIndex--;
		await tick();
		handleLoop();

		if (autoplay) startAutoplay();
	}

	async function handleLoop() {
		// Wait for CSS transition to complete
		setTimeout(async () => {
			transitioning = false;

			// Jump to real position (without animation)
			if (internalIndex >= xrayImages.length + baseIndex) {
				internalIndex = baseIndex;
				await tick(); // Wait for DOM update
			}
			if (internalIndex < baseIndex) {
				internalIndex = baseIndex + xrayImages.length - 1;
				await tick();
			}
		}, 500); // Match the CSS transition duration
	}

	function toggleFullscreen() {
		const carouselEl = document.querySelector('.carousel');
		if (!document.fullscreenElement) {
			// Enter fullscreen
			carouselEl.requestFullscreen();
		} else {
			// Exit fullscreen
			document.exitFullscreen();
		}
	}

	function onFullscreenChange() {
		fullscreen = !!document.fullscreenElement;
	}
</script>

<div class="carousel-container">
	<div class="controls">
		<button on:click={prev}>⬅️</button>

		<label>
			Visible:
			<input type="number" bind:value={visibleCount} min="1" max={xrayImages.length} />
		</label>

		<button on:click={next}>➡️</button>
	</div>

	<div class="controls">
		<label>
			Autoplay:
			<input type="checkbox" checked={autoplay} on:change={toggleAutoplay} />
		</label>

		<label>
			Speed (ms):
			<input
				type="number"
				bind:value={autoplaySpeed}
				min="500"
				step="500"
				on:change={() => {
					if (autoplay) {
						startAutoplay();
					}
				}}
			/>
		</label>

		<label>
			Show Original:
			<input type="checkbox" bind:checked={showOriginal} />
		</label>

		<button on:click={toggleFullscreen}>
			{fullscreen ? 'Exit Fullscreen' : 'Enter Fullscreen'}
		</button>
	</div>

	<div
		class="carousel"
		class:fullscreen
		style={`--visible-count: ${fullscreen ? 1 : showOriginal ? visibleCount : visibleCount}`}
	>
		<div
			class="track"
			class:no-transition={!transitioning}
			style="transform: {`translateX(${slideOffset}%)`};"
		>
			{#each extendedImages as img, i}
				<div class="image-wrapper">
					<img src={img} alt="Xray Image" />
					{#if showOriginal}
						<img src={extendedImagesOriginal[i]} alt="Original Image" />
					{/if}
				</div>
			{/each}
		</div>
	</div>
</div>

<style>
	.fullscreen {
		position: fixed;
		inset: 0;
		background-color: #000;
		z-index: 9999;
		display: flex;
		justify-content: center;
		align-items: center;
		padding: 1rem;
	}
	.carousel-container {
		display: flex;
		flex-direction: column;
		align-items: center;
		width: 100%;
	}
	.carousel.fullscreen {
		position: fixed;
		inset: 0;
		background-color: #000;
		z-index: 9999;
		display: flex;
		justify-content: center;
		align-items: center;
		width: 100vw;
		height: 100vh;
		margin: 0;
	}
	.carousel.fullscreen img {
		height: 90vh;
		width: auto;
		object-fit: contain;
		box-shadow: none;
		border-radius: 0;
	}

	.carousel {
		display: flex;
		overflow: hidden;
		margin: 1rem 0;
		width: 100%;
		position: relative;
	}

	.carousel img {
		height: auto; /* Allow height to adjust based on width */
		width: calc(100% / var(--visible-count));
		max-width: 100%;
		max-height: 60vh;
		object-fit: contain;
		border-radius: 8px;
		box-shadow: 0 2px 6px rgba(0, 0, 0, 0.2);
	}

	.track {
		display: flex;
		transition: transform 0.5s ease;
		will-change: transform;
		width: max-content;
	}

	.track.no-transition {
		transition: none;
	}

	.image-wrapper {
		flex: 0 0 calc(100% / var(--visible-count));
		display: flex;
		gap: 0.5rem;
		align-items: center;
		justify-content: center;
		box-sizing: border-box;
		padding: 0 0.5rem;
	}

	.controls {
		display: flex;
		gap: 1rem;
		align-items: center;
	}

	button {
		padding: 0.5rem 1rem;
	}
</style>
