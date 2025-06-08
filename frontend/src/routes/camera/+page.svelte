<script lang="ts">
	import jsQR from 'jsqr';
	import { PUBLIC_BACKEND_URL } from '$env/static/public';

	let videoElement: HTMLVideoElement;
	let canvasElement: HTMLCanvasElement;
	let photoCanvas: HTMLCanvasElement;
	let stream: MediaStream | null = null;

	let qrResult: string = '';
	let photoPreview: string = '';
	let scanInterval: NodeJS.Timeout;
	let firstName = '';
	let lastName = '';
	let animalName = '';
	let animalType = '';

	let animalTypes: string[] = [];
	let brokenBones = false;

	let overlayCanvas: HTMLCanvasElement;
	let isDrawing = false;
	let ctx: CanvasRenderingContext2D | null;
	let lastX = 0;
	let lastY = 0;

	fetch(`${PUBLIC_BACKEND_URL}/animal_types`, {
		method: 'GET'
	})
		.then((data) => data.json())
		.then((data) => {
			animalTypes = data.types;
		});

	async function startQRScanner() {
		try {
			stream = await navigator.mediaDevices.getUserMedia({ video: { facingMode: 'environment' } });
			videoElement.srcObject = stream;
			await videoElement.play();
			scanInterval = setInterval(scanQRCode, 500);
		} catch (err) {
			console.error('Camera error:', err);
		}
	}

	function stopQRScanner() {
		if (scanInterval) clearInterval(scanInterval);
		if (stream) {
			stream.getTracks().forEach((track) => track.stop());
			stream = null;
		}
		if (videoElement) {
			videoElement.pause();
			videoElement.srcObject = null;
		}
	}

	function scanQRCode() {
		const ctx = canvasElement.getContext('2d');
		if (!ctx || !videoElement.videoWidth) return;

		canvasElement.width = videoElement.videoWidth;
		canvasElement.height = videoElement.videoHeight;
		ctx.drawImage(videoElement, 0, 0);

		const imageData = ctx.getImageData(0, 0, canvasElement.width, canvasElement.height);
		const code = jsQR(imageData.data, canvasElement.width, canvasElement.height);

		if (code?.data) {
			qrResult = code.data;
			stopQRScanner();
		}
	}

	async function startCamera() {
		if (!stream) {
			stream = await navigator.mediaDevices.getUserMedia({ video: true });
			videoElement.srcObject = stream;
		}
		await videoElement.play();
	}

	function stopCamera() {
		if (stream) {
			stream.getTracks().forEach((t) => t.stop());
			stream = null;
		}
		if (videoElement) {
			videoElement.pause();
			videoElement.srcObject = null;
		}
	}

	function capturePhoto() {
		if (!videoElement || !photoCanvas) return;

		photoCanvas.width = videoElement.videoWidth;
		photoCanvas.height = videoElement.videoHeight;
		const ctx = photoCanvas.getContext('2d');
		ctx?.drawImage(videoElement, 0, 0);
		photoPreview = photoCanvas.toDataURL('image/png');
	}

	async function uploadPhoto() {
		if (!photoPreview || !qrResult) return;

		const finalImage = mergePhotoWithOverlay();
		const blob = await (await fetch(finalImage)).blob();
		const formData = new FormData();
		formData.append('file', blob, 'photo.png');
		formData.append('first_name', firstName);
		formData.append('last_name', lastName);
		formData.append('animal_name', animalName);
		formData.append('qr_content', qrResult);
		formData.append('animal_type', animalType);
		formData.append('broken_bone', brokenBones ? 'true' : 'false');

		const res = await fetch(`${PUBLIC_BACKEND_URL}/upload`, {
			method: 'POST',
			body: formData,
			headers: {
				Authorization: `Bearer ${localStorage.getItem('session')}`
			}
		});
		console.log(res);

		if (res.ok) {
			alert('Upload successful!');
		} else {
			alert(`Upload failed ${res.statusText}`);
		}
	}

	function startDraw(event: MouseEvent) {
		if (!overlayCanvas) return;
		ctx = overlayCanvas.getContext('2d');
		if (!ctx) return;

		isDrawing = true;
		const rect = overlayCanvas.getBoundingClientRect();
		lastX = event.clientX - rect.left;
		lastY = event.clientY - rect.top;
	}

	function draw(event: MouseEvent) {
		if (!isDrawing || !ctx) return;
		const rect = overlayCanvas.getBoundingClientRect();
		const x = event.clientX - rect.left;
		const y = event.clientY - rect.top;

		ctx.strokeStyle = 'rgba(255, 0, 0, 0.5)';
		ctx.lineWidth = 4;
		ctx.lineJoin = 'round';
		ctx.lineCap = 'round';

		ctx.beginPath();
		ctx.moveTo(lastX, lastY);
		ctx.lineTo(x, y);
		ctx.stroke();

		lastX = x;
		lastY = y;
	}

	function stopDraw() {
		isDrawing = false;
	}

	function mergePhotoWithOverlay(): string {
		const finalCanvas = document.createElement('canvas');
		finalCanvas.width = photoCanvas.width;
		finalCanvas.height = photoCanvas.height;

		const ctx = finalCanvas.getContext('2d');
		if (!ctx) return photoPreview;

		ctx.drawImage(photoCanvas, 0, 0);
		ctx.drawImage(overlayCanvas, 0, 0);

		return finalCanvas.toDataURL('image/png');
	}
</script>

<h1>Step 1: Scan QR Code</h1>

{#if !qrResult}
	<!-- svelte-ignore a11y_media_has_caption -->
	<video bind:this={videoElement} autoplay></video>
	<canvas bind:this={canvasElement} style="display: none;"></canvas>
	<button
		on:click={startQRScanner}
		class="rounded bg-blue-600 px-2 py-1 text-sm font-medium text-white shadow transition-all hover:bg-blue-700 active:scale-95"
		>Start QR Scanner</button
	>
{:else}
	<h2>QR Result: {qrResult}</h2>

	<div class="fields">
		<input placeholder="First Name" bind:value={firstName} />
		<input placeholder="Last Name" bind:value={lastName} />
		<input placeholder="Animal Name" bind:value={animalName} />
		<select bind:value={animalType}>
			{#each animalTypes as at}
				<option value={at}>{at}</option>
			{/each}
		</select>
		<label>
			<input type="checkbox" bind:checked={brokenBones} />
			Broken Bones
		</label>
	</div>

	{#if qrResult}
		<!-- svelte-ignore a11y_media_has_caption -->
		<div class="flex flex-col items-start gap-4 md:flex-row">
			<!-- Live Video Feed -->
			<div class="flex-1">
				<video bind:this={videoElement} autoplay class="w-full max-w-md rounded shadow" />
			</div>

			<!-- Captured Image Preview (only shown if available) -->
			{#if photoPreview}
				<div style="position: relative; display: inline-block;">
					<img src={photoPreview} alt="Captured" style="display: block; max-width: 100%;" />
					<canvas
						bind:this={overlayCanvas}
						width={videoElement?.videoWidth}
						height={videoElement?.videoHeight}
						style="position: absolute; top: 0; left: 0; width: 100%; height: 100%;"
						on:mousedown={startDraw}
						on:mousemove={draw}
						on:mouseup={stopDraw}
						on:mouseleave={stopDraw}
					></canvas>
				</div>
			{/if}
		</div>

		<!-- Canvas (hidden) -->
		<canvas bind:this={photoCanvas} style="display: none;"></canvas>

		<div class="controls">
			<button
				on:click={startCamera}
				class="rounded bg-blue-600 px-2 py-1 text-sm font-medium text-white shadow transition-all hover:bg-blue-700 active:scale-95"
				>Start Camera</button
			>
			<button
				on:click={stopCamera}
				class="rounded bg-red-600 px-2 py-1 text-sm font-medium text-white shadow transition-all hover:bg-red-700 active:scale-95"
				>Stop Camera</button
			>
			<button
				on:click={capturePhoto}
				class="rounded bg-green-600 px-2 py-1 text-sm font-medium text-white shadow transition-all hover:bg-green-700 active:scale-95"
				>Capture Photo</button
			>
		</div>

		<div class="controls">
			<button
				on:click={uploadPhoto}
				class="rounded bg-yellow-600 px-4 py-2 font-semibold text-white shadow transition-all hover:bg-yellow-700 active:scale-95 disabled:cursor-not-allowed disabled:opacity-50"
				disabled={!photoPreview}
			>
				Upload Photo with Data
			</button>

			{#if !photoPreview}
				<span
					class="absolute bottom-full left-1/2 z-10 mb-2 -translate-x-1/2 scale-0 whitespace-nowrap rounded bg-gray-800 px-2 py-1 text-xs text-white transition-transform group-hover:scale-100"
				>
					Please take a photo before uploading
				</span>
			{/if}
		</div>
	{/if}
{/if}

<style>
	video,
	canvas,
	img {
		max-width: 100%;
		border-radius: 8px;
		margin-bottom: 1rem;
	}

	.controls,
	.fields {
		display: flex;
		flex-direction: column;
		gap: 1rem;
		margin-bottom: 1rem;
	}

	input,
	button {
		padding: 0.75rem;
		font-size: 1rem;
	}
</style>
