<script lang="ts">
	import { onMount, tick } from 'svelte';
	import { writable } from 'svelte/store';
	import { PUBLIC_BACKEND_URL } from '$env/static/public';

	interface Results {
		[key: string]: string[];
	}

	const results = writable<Results>({});
	const pollingInterval = 5000; // 5 seconds

	let token: string | null = null;

	// Modal state
	let showModal = false;
	let modalImageUrl = '';
	let modalIndex = '';
	let modalChoice = -1;

	let bgCanvasEl: HTMLCanvasElement;
	let overlayCanvasEl: HTMLCanvasElement;

	let canvasEl: HTMLCanvasElement;
	let ctx: CanvasRenderingContext2D;
	let drawing = false;

	let overlayScale = 1;
	let overlayRotation = 0; // in degrees

	let overlayX = 0;
	let overlayY = 0;
	let overlayPlaced = false;

	let useDrawMode = false;

	// Image dimensions and offset for correct positioning
	let modalImgEl: HTMLImageElement;
	let modalImgRect: DOMRect;

	function handleImageClick(event: MouseEvent) {
		modalImgRect = modalImgEl.getBoundingClientRect();

		const scaleX = modalImgEl.naturalWidth / modalImgRect.width;
		const scaleY = modalImgEl.naturalHeight / modalImgRect.height;

		const x = (event.clientX - modalImgRect.left) * scaleX;
		const y = (event.clientY - modalImgRect.top) * scaleY;

		overlayX = x;
		overlayY = y;
		overlayPlaced = true;

		if (useDrawMode && overlayPlaced) {
			tick().then(() => {
				setupCanvas();
			});
		}
	}

	function buildUrl(path: string) {
		return path.startsWith('http') ? path : `${PUBLIC_BACKEND_URL}${path}`;
	}

	onMount(() => {
		token = localStorage.getItem('session');
		fetchResults();
		const interval = setInterval(fetchResults, pollingInterval);
		return () => clearInterval(interval);
	});

	async function fetchResults() {
		const res = await fetch(buildUrl('/results'), {
			headers: { Authorization: `Bearer ${token}` }
		});
		if (res.ok) {
			const data: Results = await res.json();
			results.set(data);
		}
	}

	async function rejectRow(index: string) {
		await sendConfirmation(index, -1, false, null);
	}

	function openModal(index: string, choice: number, url: string) {
		modalIndex = index;
		modalChoice = choice;
		modalImageUrl = url;
		showModal = true;
		overlayPlaced = false;
	}

	function setupCanvas() {
		const rect = modalImgEl.getBoundingClientRect();
		canvasEl.width = rect.width;
		canvasEl.height = rect.height;

		ctx = canvasEl.getContext('2d');
		ctx.clearRect(0, 0, canvasEl.width, canvasEl.height);
		ctx.strokeStyle = 'rgba(128,128,128,0.5)';
		ctx.lineWidth = 4;
		ctx.lineCap = 'round';
	}

	function startDraw(event: MouseEvent) {
		if (!ctx) return;

		event.preventDefault();
		drawing = true;
		ctx.beginPath();
		ctx.moveTo(event.offsetX, event.offsetY);
	}

	function draw(event: MouseEvent) {
		if (!ctx) return;

		if (!drawing) return;
		event.preventDefault();
		ctx.lineTo(event.offsetX, event.offsetY);
		ctx.stroke();
	}

	function endDraw() {
		if (!ctx) return;

		drawing = false;
		ctx.closePath();
	}

	function sampleAverageColor(
		ctx: CanvasRenderingContext2D,
		x: number,
		y: number,
		size = 5
	): [number, number, number] {
		const offset = Math.floor(size / 2);
		const imgData = ctx.getImageData(x - offset, y - offset, size, size);
		const data = imgData.data;

		let r = 0,
			g = 0,
			b = 0;
		for (let i = 0; i < data.length; i += 4) {
			r += data[i];
			g += data[i + 1];
			b += data[i + 2];
		}
		const count = data.length / 4;
		return [r / count, g / count, b / count];
	}

	function createGradient(
		width: number,
		height: number,
		leftColor: [number, number, number],
		rightColor: [number, number, number]
	): ImageData {
		const gradient = new Uint8ClampedArray(width * height * 4);
		for (let y = 0; y < height; y++) {
			for (let x = 0; x < width; x++) {
				const t = x / width;
				let r = (1 - t) * leftColor[0] + t * rightColor[0] + (Math.random() - 0.5) * 20;
				let g = (1 - t) * leftColor[1] + t * rightColor[1] + (Math.random() - 0.5) * 20;
				let b = (1 - t) * leftColor[2] + t * rightColor[2] + (Math.random() - 0.5) * 20;

				const i = (y * width + x) * 4;
				gradient[i] = Math.min(Math.max(r, 0), 255);
				gradient[i + 1] = Math.min(Math.max(g, 0), 255);
				gradient[i + 2] = Math.min(Math.max(b, 0), 255);
				gradient[i + 3] = 255;
			}
		}
		console.log(
			`Gradient size: ${width}x${height}, expected: ${width * height * 4}, actual: ${gradient.length}`
		);

		return new ImageData(gradient, width, height);
	}

	async function uploadOverlay() {
		if (!overlayPlaced) {
			alert('Please click on the image to place the overlay.');
			return;
		}

		const originalImage = new Image();
		originalImage.src = buildUrl(modalImageUrl);
		originalImage.crossOrigin = 'anonymous';
		await new Promise<void>((resolve) => (originalImage.onload = () => resolve()));

		bgCanvasEl.width = originalImage.width;
		bgCanvasEl.height = originalImage.height;
		const bgCtx = bgCanvasEl.getContext('2d');
		bgCtx.drawImage(originalImage, 0, 0);

		let overlayWidth: number, overlayHeight: number;
		let ovCtx: CanvasRenderingContext2D;
		let gradient: ImageData;

		if (useDrawMode) {
			// Use user's drawing as overlay
			// When copying from draw canvas to overlay canvas
			// We scale from the visible canvas size to the natural size
			overlayWidth = modalImgEl.naturalWidth;
			overlayHeight = modalImgEl.naturalHeight;
			overlayCanvasEl.width = overlayWidth;
			overlayCanvasEl.height = overlayHeight;

			ovCtx = overlayCanvasEl.getContext('2d');
			ovCtx.clearRect(0, 0, overlayWidth, overlayHeight);

			// Draw scaled from display size to natural resolution
			ovCtx.drawImage(
				canvasEl,
				0,
				0,
				canvasEl.width,
				canvasEl.height,
				0,
				0,
				overlayWidth,
				overlayHeight
			);

			// Use solid overlay color
			const solidOverlayColor: [number, number, number] = [30, 30, 30];
			gradient = createSolidOverlay(overlayWidth, overlayHeight, solidOverlayColor);
		} else {
			const fractureOverlay = new Image();
			fractureOverlay.src = '/fracture.png';
			fractureOverlay.crossOrigin = 'anonymous';
			await new Promise<void>((resolve) => (fractureOverlay.onload = () => resolve()));

			overlayWidth = fractureOverlay.width * overlayScale;
			overlayHeight = fractureOverlay.height * overlayScale;

			overlayCanvasEl.width = overlayWidth;
			overlayCanvasEl.height = overlayHeight;

			ovCtx = overlayCanvasEl.getContext('2d');
			ovCtx.clearRect(0, 0, overlayWidth, overlayHeight);

			ovCtx.save();
			ovCtx.translate(overlayWidth / 2, overlayHeight / 2);
			ovCtx.rotate((overlayRotation * Math.PI) / 180);
			ovCtx.translate(-fractureOverlay.width / 2, -fractureOverlay.height / 2);
			ovCtx.drawImage(fractureOverlay, 0, 0);
			ovCtx.restore();

			const centerX = Math.floor(overlayX + overlayWidth / 2);
			const centerY = Math.floor(overlayY + overlayHeight / 2);
			const colorLeft = sampleAverageColor(bgCtx, centerX - 30, centerY);
			const colorRight = sampleAverageColor(bgCtx, centerX + 30, centerY);
			gradient = createGradient(overlayWidth, overlayHeight, colorLeft, colorRight);
		}

		// Always extract alpha and blend — for both modes
		const alphaData = ovCtx.getImageData(0, 0, overlayWidth, overlayHeight);
		const finalX = overlayX - overlayWidth / 2;
		const finalY = overlayY - overlayHeight / 2;

		blendOverlayWithBoneMask(bgCtx, gradient, alphaData, Math.floor(finalX), Math.floor(finalY));

		bgCanvasEl.toBlob(async (blob) => {
			if (!blob) {
				alert('Failed to generate overlay image.');
				return;
			}
			await sendConfirmation(modalIndex, modalChoice, true, blob);
			showModal = false;
			overlayPlaced = false;
		});
	}

	function blendOverlayWithBoneMask(
		bgCtx: CanvasRenderingContext2D,
		gradient: ImageData,
		alphaMask: ImageData,
		x: number,
		y: number,
		grayLow = 90,
		grayHigh = 255
	) {
		const w = gradient.width;
		const h = gradient.height;
		const bgData = bgCtx.getImageData(x, y, w, h);

		for (let i = 0; i < bgData.data.length; i += 4) {
			const gray = 0.299 * bgData.data[i] + 0.587 * bgData.data[i + 1] + 0.114 * bgData.data[i + 2];
			const a = alphaMask.data[i + 3] / 255;
			const boneMask = gray >= grayLow && gray <= grayHigh ? 1 : 0;
			const blend = a * boneMask;

			bgData.data[i] = (1 - blend) * bgData.data[i] + blend * gradient.data[i];
			bgData.data[i + 1] = (1 - blend) * bgData.data[i + 1] + blend * gradient.data[i + 1];
			bgData.data[i + 2] = (1 - blend) * bgData.data[i + 2] + blend * gradient.data[i + 2];
			// alpha stays at 255
		}

		bgCtx.putImageData(bgData, x, y);
	}

	// Create noisy horizontal gradient
	function createSolidOverlay(
		width: number,
		height: number,
		rgb: [number, number, number]
	): ImageData {
		const data = new Uint8ClampedArray(width * height * 4);
		for (let i = 0; i < data.length; i += 4) {
			data[i] = rgb[0]; // R
			data[i + 1] = rgb[1]; // G
			data[i + 2] = rgb[2]; // B
			data[i + 3] = 255; // Alpha
		}
		return new ImageData(data, width, height);
	}

	async function sendConfirmation(
		index: string,
		choice: number,
		confirm: boolean,
		imageBlob: Blob | null
	) {
		const form = new FormData();
		form.append('image_id', index);
		form.append('choice', choice.toString());
		form.append('confirm', String(confirm));
		if (imageBlob) form.append('image', imageBlob, 'overlay.png');

		console.log('Sending confirmation:');
		await fetch(buildUrl('/confirm'), {
			method: 'POST',
			headers: { Authorization: `Bearer ${token}` },
			body: form
		});
		console.log('Confirmation sent successfully');
	}
</script>

<div class="grid">
	{#each Object.entries($results) as [index, variants]}
		<div class="row">
			{#each variants as url, i}
				<div class="cell">
					<img src={buildUrl(url)} alt="variant" draggable="false" on:dragstart|preventDefault />
					<button on:click={() => openModal(index, i, url)}>Confirm</button>
				</div>
			{/each}
			<button class="row-reject" on:click={() => rejectRow(index)}>Reject</button>
		</div>
	{/each}
</div>

{#if showModal}
	<div class="modal">
		<div class="modal-content">
			<div class="image-container">
				<img
					bind:this={modalImgEl}
					src={buildUrl(modalImageUrl)}
					alt="selected"
					draggable="false"
					on:dragstart|preventDefault
					on:click={handleImageClick}
				/>
				<div class="controls">
					<label>
						Scale:
						<input type="range" min="0.2" max="2.5" step="0.05" bind:value={overlayScale} />
						{overlayScale.toFixed(2)}
					</label>
					<label>
						Rotation:
						<input type="range" min="-180" max="180" step="1" bind:value={overlayRotation} />
						{overlayRotation}°
					</label>
					<label>
						<input type="checkbox" bind:checked={useDrawMode} />
						Draw mode
					</label>
				</div>
				{#if overlayPlaced}
					{#if useDrawMode}
						<canvas
							class="draw-canvas"
							bind:this={canvasEl}
							on:mousedown={startDraw}
							on:mousemove={draw}
							on:mouseup={endDraw}
						/>
					{/if}
				{/if}

				{#if overlayPlaced && !useDrawMode}
					<img
						src="/fracture.png"
						alt="overlay"
						class="overlay-preview"
						style="
			left: {overlayX}px;
			top: {overlayY}px;
			transform: translate(-50%, -50%) scale({overlayScale}) rotate({overlayRotation}deg);
		"
					/>
				{/if}
			</div>

			<button on:click={uploadOverlay}>Upload</button>
			<button on:click={() => (showModal = false)}>Cancel</button>
		</div>

		<!-- ✅ Add this block here -->
		<div style="display: none;">
			<canvas bind:this={bgCanvasEl}></canvas>
			<canvas bind:this={overlayCanvasEl}></canvas>
		</div>
	</div>
{/if}

<style>
	.grid {
		display: flex;
		flex-direction: column;
		gap: 1rem;
	}
	.row {
		display: flex;
		align-items: center;
		gap: 1rem;
	}
	.cell {
		position: relative;
	}
	.cell img {
		height: 150px;
		width: auto;
		object-fit: contain;
		border: 1px solid #ccc;
		user-drag: none;
		user-select: none;
	}
	.cell img::-webkit-drag {
		display: none;
	}
	.cell button {
		position: absolute;
		bottom: 5px;
		left: 5px;
	}
	.row-reject {
		margin-left: auto;
	}
	.modal {
		position: fixed;
		top: 0;
		left: 0;
		width: 100%;
		height: 100%;
		background: rgba(0, 0, 0, 0.5);
		display: flex;
		justify-content: center;
		align-items: center;
	}
	.modal-content {
		background: #fff;
		padding: 1rem;
		position: relative;
	}
	.overlay-preview {
		position: absolute;
		pointer-events: none;
		z-index: 2;
	}
	.image-container {
		position: relative;
	}
	.image-container img {
		display: block;
	}

	.image-container canvas {
		display: block;
	}
	.image-container canvas {
		position: absolute;
		top: 0;
		left: 0;
	}
	.draw-canvas {
		position: absolute;
		top: 0;
		left: 0;
		z-index: 3;
		cursor: crosshair;
	}
</style>
