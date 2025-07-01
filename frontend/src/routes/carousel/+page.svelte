<script>
	import { onMount, onDestroy, tick } from 'svelte';

	let images = [];
	let visibleCount = 3;
	let startIndex = 0;
	let autoplay = true;
	let autoplaySpeed = 3000; // in ms
	let autoplayTimer;

	let internalIndex = 0;
	let transitioning = false; // Track if a transition is happening

	let fullscreen = false;

	$: totalVisible = visibleCount;
	$: clonesBefore = images.slice(-totalVisible);
	$: clonesAfter = images.slice(0, totalVisible);

	$: extendedImages = [...clonesBefore, ...images, ...clonesAfter];

	$: baseIndex = totalVisible; // first real image

	$: slideOffset = -(internalIndex * (100 / visibleCount));

	onMount(async () => {
		const res = await fetch(`http://localhost:8000/carousel`);
		if (res.ok) {
			images = await res.json();
			internalIndex = baseIndex;
			if (autoplay) startAutoplay();
		} else {
			console.error('Failed to fetch carousel images');
		}

    
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
			if (internalIndex >= images.length + baseIndex) {
				internalIndex = baseIndex;
				await tick(); // Wait for DOM update
			}
			if (internalIndex < baseIndex) {
				internalIndex = baseIndex + images.length - 1;
				await tick();
			}
		}, 500); // Match the CSS transition duration
	}

function toggleFullscreen() {
  fullscreen = !fullscreen;
}
</script>

<div class="carousel-container">
	<div class="controls">
		<button on:click={prev} disabled={startIndex === 0}>⬅️</button>

		<label>
			Visible:
			<input type="number" bind:value={visibleCount} min="1" max={images.length} />
		</label>

		<button on:click={next} disabled={startIndex + visibleCount >= images.length}>➡️</button>
	</div>

	<div class="controls">
		<label>
			Autoplay:
			<input type="checkbox" bind:checked={autoplay} on:change={toggleAutoplay} />
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

		<button on:click={toggleFullscreen}>
			{fullscreen ? 'Exit Fullscreen' : 'Enter Fullscreen'}
		</button>
	</div>

  
	<div class="carousel" class:fullscreen={fullscreen} style={`--visible-count: ${fullscreen ? 1 : visibleCount}`}>
		<div
			class="track"
			class:no-transition={!transitioning}
			style="transform: translateX({slideOffset}%);"
		>
			{#each extendedImages as img, i}
				<div class="image-wrapper">
					<img src={img} alt="carousel image" />
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
	padding: 1rem;
	width: 100vw;
	height: 100vh;
}

.carousel.fullscreen img {
	height: 100%;
	width: auto;
	object-fit: contain;
	box-shadow: none;
	border-radius: 0;
}

	.carousel {
		display: flex;
		gap: 1rem;
		overflow: hidden;
		margin: 1rem 0;
		width: 100%;
		position: relative;
	}

	.carousel img {
		height: 60vh;
		width: auto;
		max-width: 100%;
		object-fit: cover;
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
