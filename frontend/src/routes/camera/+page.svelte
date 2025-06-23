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

		const width = videoElement.videoWidth;
		const height = videoElement.videoHeight;

		const size = Math.min(width, height);

		photoCanvas.width = size;
		photoCanvas.height = size; // set size to a square of min(width,height) of camera output

		const ctx = photoCanvas.getContext('2d');
		ctx?.drawImage(
			videoElement,
			(width - size) / 2,
			(height - size) / 2,
			size,
			size,
			0,
			0,
			size,
			size
		); // center videofeed
		photoPreview = photoCanvas.toDataURL('image/png');
	}

	async function uploadPhoto() {
		if (!photoPreview || !firstName || !lastName || !animalName || !qrResult || !animalType) return;

		// logic to scale upload image to 1024x1024
		// Create a new canvas to scale the image
		const scaleCanvas = document.createElement('canvas');
		scaleCanvas.width = 1024;
		scaleCanvas.height = 1024;
		const ctx = scaleCanvas.getContext('2d');

		// Create an image element to load the photoPreview
		const img = new Image();
		img.src = photoPreview;

		// Wait for the image to load
		await new Promise((resolve) => {
			img.onload = resolve;
		});

		// Draw the image onto the canvas, scaling it to 1024x1024
		ctx?.drawImage(img, 0, 0, 1024, 1024);

		// Convert the canvas to a blob
		const blob = await new Promise((resolve) => {
			scaleCanvas.toBlob(resolve, 'image/png');
		});

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

	$: allFieldsFilled = firstName && lastName && animalName && qrResult;
</script>

<div class="container">
	<h1>Step 1: Scan QR Code</h1>

	{#if !qrResult}
		<button
			on:click={startQRScanner}
			class="rounded bg-blue-600 px-2 py-1 text-sm font-medium text-white shadow transition-all hover:bg-blue-700 active:scale-95"
			>Start QR Scanner</button
		>
		<!-- svelte-ignore a11y_media_has_caption -->
		<video bind:this={videoElement} autoplay></video>
		<canvas bind:this={canvasElement} style="display: none;"></canvas>

	{:else}
		<h2>QR Result: {qrResult}</h2>
		<div class="content">

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

		{#if allFieldsFilled}
			<!-- svelte-ignore a11y_media_has_caption -->
			<div class="flex flex-col items-start gap-4 md:flex-row">
				<!-- Live Video Feed -->
				<div class="flex-1">
					<video bind:this={videoElement} autoplay class="w-full max-w-md rounded shadow" />
				</div>

				<!-- Captured Image Preview (only shown if available) -->
				{#if photoPreview}
					<div class="flex-1">
						<img
							src={photoPreview}
							alt="Photo captured from camera"
							class="w-full max-w-md rounded shadow"
						/>
					</div>
				{/if}
			</div>

			<!-- Canvas (hidden) -->
			<canvas bind:this={photoCanvas} style="display: none;"></canvas>

			<div class="vertcontent">
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
			</div>
		{/if}
		</div>
	{/if}
</div>

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

	.container {
		display: flex;
		flex-direction: column;
		align-items: center;
		justify-content: center;
		height: 100vh; /* Full viewport height */
		overflow: hidden; /* Prevent scrolling */
		padding: 5px; /* Add some padding */
	}

	.content {
		display: flex; /* Use flexbox for horizontal layout */
		flex-direction: row; /* Arrange items in a row */
		align-items: flex-start; /* Align items at the start */
		width: 100%; /* Full width */
		max-height: 80vh; /* Limit height to prevent overflow */
		overflow: auto; /* Allow scrolling if content overflows */
	}

	.vertcontent {
		display: flex; /* Use flexbox for horizontal layout */
		flex-direction: column; /* Arrange items in a column */
		align-items: flex-start; /* Align items at the start */
		height: 100%; /* Full width */
		overflow: auto; /* Allow scrolling if content overflows */
	}

	video {
		width: 100%; /* Responsive width */
		max-height: 75vh; /* Limit height to half the viewport */
		object-fit: cover; /* Maintain aspect ratio */
	}

	button {
		margin-top: 10px; /* Space between video and button */
		padding: 0.5rem 1rem; /* Smaller padding */
		font-size: 0.8rem; /* Smaller font size */
	}
</style>
