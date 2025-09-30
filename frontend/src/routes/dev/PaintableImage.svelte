<script lang="ts">
	import { PUBLIC_BACKEND_URL } from '$env/static/public';
	import { onMount, onDestroy } from 'svelte';

	export let imageSrc = '';
	export let cardTitle = 'Paint Over Image';
	export let maxCardWidth = 900; // px

	let imgEl: HTMLImageElement | SVGElement;
	let canvas: HTMLCanvasElement;
	let ctx: CanvasRenderingContext2D;
	let dpr = 1;

	// tools
	let tool: 'brush' | 'eraser' = 'brush';
	let brushColor = '#ff4757';
	let brushSize = 14;

	// state
	let drawing = false;
	let lastX = 0,
		lastY = 0;
	let undoStack: string[] = [];
	let redoStack: string[] = [];
	let overlayDataUrl: string | null = null;

	// convenience
	const supportsPointer = typeof window !== 'undefined' && 'PointerEvent' in window;

	function setCanvasSize() {
		if (!imgEl || !canvas) return;
		const rect = imgEl.getBoundingClientRect();
		const cssW = Math.max(1, Math.round(rect.width));
		const cssH = Math.max(1, Math.round(rect.height));

		// style size (CSS pixels)
		canvas.style.width = cssW + 'px';
		canvas.style.height = cssH + 'px';

		// backing store (device pixels) for crisp lines
		dpr = Math.max(1, window.devicePixelRatio || 1);
		canvas.width = Math.round(cssW * dpr);
		canvas.height = Math.round(cssH * dpr);

		ctx = canvas.getContext('2d');
		ctx.setTransform(dpr, 0, 0, dpr, 0, 0); // draw in CSS px coordinates

		// restore overlay if we had one
		if (overlayDataUrl) {
			const img = new Image();
			img.onload = () => {
				// draw scaled to current CSS size
				ctx.drawImage(img, 0, 0, cssW, cssH);
			};
			img.src = overlayDataUrl;
		}
	}

	function pointerPos(e: PointerEvent | MouseEvent) {
		const rect = canvas.getBoundingClientRect();
		return { x: e.clientX - rect.left, y: e.clientY - rect.top };
	}

	function pushUndo() {
		if (!canvas) return;
		try {
			undoStack.push(canvas.toDataURL('image/png'));
			if (undoStack.length > 25) undoStack.shift();
			// new action invalidates redo history
			redoStack = [];
		} catch (err) {
			// ignore memory errors from huge canvases
		}
	}

	function restoreFrom(url) {
		const img = new Image();
		img.onload = () => {
			// clear & redraw
			ctx.save();
			ctx.globalCompositeOperation = 'source-over';
			ctx.clearRect(0, 0, canvas.width, canvas.height);
			// draw in CSS coords
			ctx.setTransform(dpr, 0, 0, dpr, 0, 0);
			const rect = canvas.getBoundingClientRect();
			ctx.drawImage(img, 0, 0, rect.width, rect.height);
			ctx.restore();
			overlayDataUrl = canvas.toDataURL('image/png');
		};
		img.src = url;
	}

	function undo() {
		if (!undoStack.length) return;
		try {
			const current = canvas.toDataURL('image/png');
			redoStack.push(current);
			const last = undoStack.pop();
			restoreFrom(last);
		} catch {}
	}

	function redo() {
		if (!redoStack.length) return;
		try {
			const current = canvas.toDataURL('image/png');
			undoStack.push(current);
			const next = redoStack.pop();
			restoreFrom(next);
		} catch {}
	}

	function clearCanvas() {
		pushUndo();
		ctx.save();
		ctx.globalCompositeOperation = 'source-over';
		ctx.clearRect(0, 0, canvas.width, canvas.height);
		ctx.restore();
		overlayDataUrl = canvas.toDataURL('image/png');
	}

	function drawLine(x1: number, y1: number, x2: number, y2: number, pressure = 1) {
		ctx.save();
		ctx.globalCompositeOperation = tool === 'eraser' ? 'destination-out' : 'source-over';
		ctx.lineCap = 'round';
		ctx.lineJoin = 'round';
		ctx.strokeStyle = brushColor;
		ctx.lineWidth = Math.max(0.5, brushSize * pressure);
		ctx.beginPath();
		ctx.moveTo(x1, y1);
		ctx.lineTo(x2, y2);
		ctx.stroke();
		ctx.restore();
	}

	function drawPoint(x: number, y: number) {
		drawLine(x, y, x, y, 1);
	}

	function onPointerDown(e: PointerEvent) {
		if (e.button === 1 || e.button === 2) return; // ignore mid/right click
		e.preventDefault();
		pushUndo();
		drawing = true;
		if (canvas && e.pointerId != null) {
			try {
				canvas.setPointerCapture(e.pointerId);
			} catch {}
		}
		const p = pointerPos(e);
		lastX = p.x;
		lastY = p.y;
		drawPoint(p.x, p.y);
	}

	function onPointerMove(e) {
		if (!drawing) return;
		const p = pointerPos(e);
		const pressure = e.pressure && e.pressure > 0 ? e.pressure : 1;
		drawLine(lastX, lastY, p.x, p.y, pressure);
		lastX = p.x;
		lastY = p.y;
	}

	function onPointerUp(e: PointerEvent) {
		drawing = false;
		if (canvas && e.pointerId != null) {
			try {
				canvas.releasePointerCapture(e.pointerId);
			} catch {}
		}
		try {
			overlayDataUrl = canvas.toDataURL('image/png');
		} catch {}
	}

	function handleFileChange(e: Event) {
		const file = (e.target as HTMLInputElement).files?.[0];
		if (!file) return;
		const reader = new FileReader();
		reader.onload = () => {
			imageSrc = reader.result;
		};
		reader.readAsDataURL(file);
	}

	// Combine base image + overlay and download
	function downloadMerged() {
		if (!imgEl) return;
		const out = document.createElement('canvas');
		const outCtx = out.getContext('2d');

		// Save at displayed size to keep things snappy
		const rect = imgEl.getBoundingClientRect();
		const outW = Math.max(1, Math.round(rect.width));
		const outH = Math.max(1, Math.round(rect.height));
		out.width = outW;
		out.height = outH;

		// Draw base image (scaled to displayed size)
		outCtx.drawImage(imgEl, 0, 0, outW, outH);

		// Draw overlay (scaled)
		if (overlayDataUrl) {
			const overlay = new Image();
			overlay.onload = () => {
				outCtx.drawImage(overlay, 0, 0, outW, outH);
				const url = out.toDataURL('image/png');
				triggerDownload(url, 'painted.png');
			};
			overlay.src = overlayDataUrl;
		} else {
			const url = out.toDataURL('image/png');
			triggerDownload(url, 'painted.png');
		}
	}

	function triggerDownload(url, filename) {
		const a = document.createElement('a');
		a.href = url;
		a.download = filename;
		a.click();
	}

	function onImageLoad() {
		setCanvasSize();
		// reset overlay for new image
		undoStack = [];
		redoStack = [];
		overlayDataUrl = null;
	}

	function onWindowResize() {
		// Capture current overlay, resize, then redraw
		let snapshot = null;
		try {
			snapshot = canvas?.toDataURL('image/png');
		} catch {}
		setCanvasSize();
		if (snapshot) {
			const img = new Image();
			img.onload = () => {
				const rect = canvas.getBoundingClientRect();
				ctx.drawImage(img, 0, 0, rect.width, rect.height);
			};
			img.src = snapshot;
			overlayDataUrl = snapshot;
		}
	}

	function keyHandler(e) {
		// Keyboard shortcuts
		if ((e.ctrlKey || e.metaKey) && !e.shiftKey && e.key.toLowerCase() === 'z') {
			e.preventDefault();
			undo();
		} else if ((e.ctrlKey || e.metaKey) && e.shiftKey && e.key.toLowerCase() === 'z') {
			e.preventDefault();
			redo();
		} else if (e.key.toLowerCase() === 'b') {
			tool = 'brush';
		} else if (e.key.toLowerCase() === 'e') {
			tool = 'eraser';
		} else if (e.key.toLowerCase() === 'escape') {
			active = false;
		}
	}

	async function breakBones() {
		let formData = new FormData();
		formData.append('image_file', await fetch(imageSrc).then((res) => res.blob()), 'image.png');
		formData.append('scale', '1.0');
		formData.append('noise', '10');

		// find a bounding box around the non transparent pixels in the overlay
		const rect = canvas.getBoundingClientRect();
		const imgData = ctx.getImageData(0, 0, canvas.width, canvas.height);
		console.log(imgData);
		let minX = canvas.width,
			minY = canvas.height,
			maxX = 0,
			maxY = 0;
		let count = 0;
		for (let y = 0; y < canvas.height; y++) {
			for (let x = 0; x < canvas.width; x++) {
				const alpha = imgData.data[(y * canvas.width + x) * 4 + 3];
				if (alpha > 0) {
					if (x < minX) minX = x;
					if (y < minY) minY = y;
					if (x > maxX) maxX = x;
					if (y > maxY) maxY = y;
					count++;
				}
			}
		}
		console.log(`Found ${count} painted pixels`);
		// set color
		ctx.strokeStyle = '#0ff';
		ctx.lineWidth = 2;
		minX = (minX * rect.width) / canvas.width;
		minY = (minY * rect.height) / canvas.height;
		maxX = (maxX * rect.width) / canvas.width;
		maxY = (maxY * rect.height) / canvas.height;
		ctx.rect(minX, minY, maxX - minX, maxY - minY);
		ctx.stroke();
		console.log(`Bounding box: ${minX},${minY} - ${maxX},${maxY}`);
		let croppedCanvas = document.createElement('canvas');
		croppedCanvas.width = maxX - minX;
		croppedCanvas.height = maxY - minY;
		const croppedCtx = croppedCanvas.getContext('2d');
		croppedCtx.drawImage(
			canvas,
			minX * (canvas.width / rect.width),
			minY * (canvas.height / rect.height),
			(maxX - minX) * (canvas.width / rect.width),
			(maxY - minY) * (canvas.height / rect.height),
			0,
			0,
			(maxX - minX) * (canvas.width / rect.width),
			(maxY - minY) * (canvas.height / rect.height)
		);
		function canvasToBlobWrapper(canvas: HTMLCanvasElement): Promise<Blob> {
			return new Promise<Blob>((resolve, reject) => {
				canvas.toBlob((blob) => {
					if (blob) {
						resolve(blob);
					} else {
						reject(new Error('Canvas could not be blobbed.'));
					}
				});
			});
		}
		// this is necessary because toBlob is not awaitable, so we can't wait for the callback to run naturally.
		await canvasToBlobWrapper(croppedCanvas).then((blob) => {
			const urlblob = URL.createObjectURL(blob);
			// open in new tab for debugging
			formData.append('overlay_file', blob, 'overlay.png');
		});
		formData.append('x', Math.round(minX * (imgEl.naturalWidth / rect.width)).toString());
		formData.append('y', Math.round(minY * (imgEl.naturalHeight / rect.height)).toString());

		let res = await fetch(`${PUBLIC_BACKEND_URL}/apply_fracture`, {
			method: 'POST',
			body: formData,
			headers: {
				Authorization: `Bearer ${localStorage.getItem('session')}`
			}
		});
		if (res.ok) {
			const blob = await res.blob();
			const url = URL.createObjectURL(blob);
			imageSrc = url;
			// clear overlay
			undoStack = [];
			redoStack = [];
			overlayDataUrl = null;
			try {
				ctx.clearRect(0, 0, canvas.width, canvas.height);
			} catch {}
		}
	}

	onMount(() => {
		setCanvasSize();
		window.addEventListener('resize', onWindowResize);
		window.addEventListener('keydown', keyHandler);
		return () => {
			window.removeEventListener('resize', onWindowResize);
			window.removeEventListener('keydown', keyHandler);
		};
	});

	let active: boolean = false;
</script>

<svelte:head>
	<style>
    :root { --card-max: {maxCardWidth}px; }
	</style>
</svelte:head>

<div class="page relative">
	<button on:click={() => (active = !active)} class="top-right-btn">
		{active ? 'Close' : 'Open'}</button
	>
	{#if !active}
		<img src={imageSrc} alt="Paintable" />
	{:else}
		<div class="overlay" on:click={() => (active = false)}>
			<div class="card" style="--card-max: {maxCardWidth}px" on:click|stopPropagation>
				<div class="card-header">
					<div class="title">{cardTitle}</div>
					<div class="spacer" />
					<div class="toolbar">
						<button
							class="btn"
							data-active={tool === 'brush'}
							on:click={() => (tool = 'brush')}
							title="Brush (B)">🖌️ Brush</button
						>
						<button
							class="btn"
							data-active={tool === 'eraser'}
							on:click={() => (tool = 'eraser')}
							title="Eraser (E)">🧽 Eraser</button
						>

						<div class="swatch" title="Color">
							<input type="color" bind:value={brushColor} />
						</div>

						<div class="slider">
							<label for="size">Size</label>
							<input id="size" type="range" min="1" max="64" bind:value={brushSize} />
							<span>{brushSize}px</span>
						</div>

						<button class="btn" on:click={undo} title="Undo (Ctrl/Cmd+Z)">↶ Undo</button>
						<button class="btn" on:click={redo} title="Redo (Ctrl/Cmd+Shift+Z)">↷ Redo</button>
						<button class="btn" on:click={clearCanvas} title="Clear overlay">🗑️ Clear</button>
						<button class="btn" on:click={breakBones} title="Break!">🦴⚡ Break!</button>
					</div>
				</div>

				<div class="canvas-wrap">
					<img
						bind:this={imgEl}
						class="img-stage"
						{imageSrc}
						src={imageSrc}
						alt="Base"
						on:load={onImageLoad}
					/>

					<canvas
						bind:this={canvas}
						class="draw"
						on:pointerdown={supportsPointer ? onPointerDown : null}
						on:pointermove={supportsPointer ? onPointerMove : null}
						on:pointerup={supportsPointer ? onPointerUp : null}
						on:pointerleave={supportsPointer ? onPointerUp : null}
						on:mousedown={!supportsPointer ? onPointerDown : null}
						on:mousemove={!supportsPointer ? onPointerMove : null}
						on:mouseup={!supportsPointer ? onPointerUp : null}
						aria-label="Drawing canvas"
					></canvas>
				</div>

				<div class="card-footer">
					<div class="footer-left">
						<span class="hint"
							>Shortcuts: <b>B</b>=Brush, <b>E</b>=Eraser, <b>Ctrl/Cmd+Z</b>=Undo,
							<b>Esc</b>=Back</span
						>
					</div>
				</div>
			</div>
		</div>
	{/if}
</div>

<style>
	.page {
		display: grid;
		place-items: center;
		padding: 0.5rem;
	}
	.overlay {
		position: fixed;
		inset: 0; /* tblr = 0 */
		background: rgba(0, 0, 0, 0.7);
		display: flex;
		justify-content: center;
		align-items: center;
		z-index: 1000; /* above all else */
		padding: 2rem;
	}

	.card {
		display: flex;
		flex-direction: column;
		max-width: 900px;
		max-height: 90vh;
		width: min(90vw, var(--card-max));
		background: #111214;
		border: 1px solid #2a2b2f;
		border-radius: 18px;
		box-shadow: 0 20px 50px rgba(0, 0, 0, 0.35);
		overflow: hidden;
	}
	.card-header,
	.card-footer {
		display: flex;
		align-items: center;
		gap: 0.75rem;
		padding: 0.9rem 1rem;
		background: #15171a;
		border-bottom: 1px solid #22242a;
	}
	.card-footer {
		border-top: 1px solid #22242a;
		border-bottom: none;
		justify-content: space-between;
		gap: 1rem;
	}
	.title {
		font:
			600 0.95rem/1.2 system-ui,
			-apple-system,
			Segoe UI,
			Roboto,
			Ubuntu,
			'Helvetica Neue',
			Arial,
			'Noto Sans',
			'Apple Color Emoji',
			'Segoe UI Emoji';
		color: #e8e9ec;
		letter-spacing: 0.2px;
	}
	.spacer {
		flex: 1;
	}

	.toolbar {
		display: flex;
		align-items: center;
		gap: 0.5rem;
	}
	.btn {
		background: #1e2025;
		border: 1px solid #2a2d33;
		color: #e5e7eb;
		padding: 0.45rem 0.65rem;
		border-radius: 10px;
		cursor: pointer;
		font-size: 0.9rem;
	}
	.btn[data-active='true'] {
		outline: 2px solid #3b82f6;
	}
	.btn:disabled {
		opacity: 0.5;
		cursor: not-allowed;
	}

	.swatch {
		width: 28px;
		height: 28px;
		border-radius: 8px;
		border: 1px solid #2a2d33;
		overflow: hidden;
		position: relative;
	}
	.swatch input[type='color'] {
		position: absolute;
		inset: 0;
		border: none;
		padding: 0;
		margin: 0;
		background: none;
		width: 100%;
		height: 100%;
		cursor: pointer;
	}
	.slider {
		display: flex;
		align-items: center;
		gap: 0.5rem;
		color: #cdd1d6;
		font-size: 0.85rem;
	}
	.slider input {
		width: 140px;
	}
	.hint {
		color: #98a0aa;
		font-size: 0.8rem;
	}

	.canvas-wrap {
		position: relative;
		display: grid;
		place-items: center;
		background: #0c0d0f;
		padding: 1rem;
	}
	.img-stage {
		max-width: 100%;
		height: auto;
		display: block;
		border-radius: 10px;
		box-shadow: 0 10px 25px rgba(0, 0, 0, 0.25);
		user-select: none;
		-webkit-user-drag: none;
		pointer-events: none; /* ensure drawing is on canvas only */
	}
	canvas.draw {
		position: absolute;
		inset: 1rem; /* match padding around the image area */
		width: calc(100% - 2rem);
		height: calc(100% - 2rem);
		touch-action: none; /* better pointer behavior on touch */
	}

	.footer-left,
	.footer-right {
		display: flex;
		align-items: center;
		gap: 0.75rem;
		flex-wrap: wrap;
	}
	.file {
		font-size: 0.85rem;
		color: #cdd1d6;
	}

	@media (min-width: 700px) {
		.card {
			border-radius: 20px;
		}
	}
	.top-right-btn {
		position: absolute;
		top: 0.5rem; /* adjust spacing */
		right: 0.5rem; /* adjust spacing */
		z-index: 10;
		background: rgba(0, 0, 0, 0.6); /* translucent */
		color: white;
		border: none;
		border-radius: 9999px; /* round */
		padding: 0.25rem 0.5rem;
		cursor: pointer;
		transition: background 0.2s ease;
	}

	.top-right-btn:hover {
		background: rgba(0, 0, 0, 0.8);
	}
</style>
