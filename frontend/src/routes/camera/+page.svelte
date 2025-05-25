<script lang="ts">
	import jsQR from 'jsqr';

	let videoElement: HTMLVideoElement;
	let canvasElement: HTMLCanvasElement;
	let photoCanvas: HTMLCanvasElement;
	let stream: MediaStream | null = null;

	let qrResult: string = '';
	let scanInterval: number | undefined;
	let photoPreview: string = '';

	let firstName = '';
	let lastName = '';
	let animalName = '';

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
		if (!photoPreview || !firstName || !lastName || !animalName || !qrResult) return;

		const blob = await (await fetch(photoPreview)).blob();
		const formData = new FormData();
		formData.append('file', blob, 'photo.png');
		formData.append('firstName', firstName);
		formData.append('lastName', lastName);
		formData.append('animalName', animalName);
		formData.append('qrContent', qrResult);

		const res = await fetch('http://localhost:8000/upload', {
			method: 'POST',
			body: formData
		});

		if (res.ok) {
			alert('Upload successful!');
		} else {
			alert('Upload failed');
		}
	}

	$: allFieldsFilled = firstName && lastName && animalName && qrResult;
</script>

<h1>Step 1: Scan QR Code</h1>

{#if !qrResult}
	<video bind:this={videoElement} autoplay></video>
	<canvas bind:this={canvasElement} style="display: none;"></canvas>
	<button on:click={startQRScanner}>Start QR Scanner</button>
{:else}
	<h2>QR Result: {qrResult}</h2>

	<div class="fields">
		<input placeholder="First Name" bind:value={firstName} />
		<input placeholder="Last Name" bind:value={lastName} />
		<input placeholder="Animal Name" bind:value={animalName} />
	</div>

	{#if allFieldsFilled}
		<video bind:this={videoElement} autoplay></video>
		<canvas bind:this={photoCanvas} style="display: none;"></canvas>

		<div class="controls">
			<button on:click={startCamera}>Start Camera</button>
			<button on:click={stopCamera}>Stop Camera</button>
			<button on:click={capturePhoto}>Capture Photo</button>
		</div>

		{#if photoPreview}
			<img src={photoPreview} alt="Captured Image" />
		{/if}

		<button on:click={uploadPhoto} disabled={!photoPreview}> Upload Photo with Data </button>
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
