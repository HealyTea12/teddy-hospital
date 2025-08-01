<script lang="ts">
	import jsQR from 'jsqr';
    import { PUBLIC_BACKEND_URL } from '$env/static/public';
	import { Alert, Input, Label, Helper, Select, ButtonGroup, Button, type SelectOptionType } from "flowbite-svelte";
	
	let videoElement: HTMLVideoElement;
	let canvasElement: HTMLCanvasElement;
	let photoCanvas: HTMLCanvasElement;
	let stream: MediaStream | null = null;

	let qrResult: string = $state('');
	let photoPreview: string = $state('');
	let scanInterval: NodeJS.Timeout;
	let firstName = $state('');
	let lastName = $state('');
	let animalName = $state('');
	let animalType = $state('');

	let animalTypes: Array<SelectOptionType<any>> = [];
	let brokenBones = false;

	let alert_message: string = $state("");
	let alert_color: string = $state("red");
	fetch(`${PUBLIC_BACKEND_URL}/animal_types`, {
		method: 'GET'
	})
		.then((data) => data.json())
		.then((data) => {
			for(let type of data.types){
				console.log(animalTypes);
				animalTypes.push({value: type, name: type});
			}
			animalTypes = animalTypes;
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
		if (!photoPreview || !firstName || !lastName || !animalName || !qrResult || !animalType) {
			alert_message = "Please fill all fields and take a photo before uploading.";
			alert_color = "red";
			return;
		}

		const blob = await (await fetch(photoPreview)).blob();
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
				'Authorization': `Bearer ${localStorage.getItem('session')}`
			}
		});
		console.log(res);

		if (res.ok) {
			alert_message = 'Upload successful!';
			alert_color = "green";
		} else {
			alert_message = `Upload failed ${res.statusText}`;
			alert_color = "red";
		}
	}

	let allFieldsFilled = $derived(firstName && lastName && animalName);
</script>

<h1>Step 1: Scan QR Code</h1>

	<div class="flex gap-1 flex-col h-full mb-2">
{#if !qrResult }
	<!-- svelte-ignore a11y_media_has_caption -->
		<div class="flex-auto flex items-center justify-center relative">
	<video class="" bind:this={videoElement} autoplay></video>
	<canvas class="" bind:this={canvasElement} style="display: none;"></canvas>
	</div>
	<button
		on:click={startQRScanner}
		class="rounded-xl cursor-pointer flex-initial w-1/2  mx-auto position-center bg-blue-600 px-2 py-1 text-sm font-medium text-white shadow transition-all hover:bg-blue-700 active:scale-95"
		>Start QR Scanner</button
	>
{:else}
	{#if alert_message !== ""}
	<Alert color={alert_color} class="mb-2">
		{alert_message}
	</Alert>
	{/if}
	<h2>QR Result: {qrResult}</h2>

	<div class="mb-2 grid gap-2 md:grid-cols-2">
		<div>
			<Label for="first_name" class="mb-2">First Name</Label>
			<Input id="first_name" placeholder="First Name" bind:value={firstName} />
		</div>
		<div>
			<Label for="last_name" class="mb-2">Last Name</Label>
			<Input id="last_name" placeholder="Last Name" bind:value={lastName} />
		</div>
		<div>
			<Label for="animal_name" class="mb-2">Animal Name</Label>
			<Input id="animal_name" placeholder="Animal Name" bind:value={animalName} />
		</div>
		<div>
			<Label for="animal_type" class="mb-2">Animal Type</Label>
			<Select class="mt-2" items={animalTypes} bind:value={animalType}></Select>
		</div>
	</div>

		<!-- svelte-ignore a11y_media_has_caption -->
		<div class="flex flex-col items-start gap-4 md:flex-row">
			<!-- Live Video Feed -->
			<div class="flex-1">
				<video bind:this={videoElement} autoplay class="w-full max-w-md rounded shadow"></video>
			</div>

			<!-- Captured Image Preview (only shown if available) -->
			<div class="flex-1">
					{#if photoPreview}
					<img
						src={photoPreview}
						alt="Photo captured from camera"
						class="w-full max-w-md rounded shadow"
					/>
					{/if}
				</div>
		</div>

		<!-- Canvas (hidden) -->
		<canvas bind:this={photoCanvas} style="display: none;"></canvas>

			<ButtonGroup class="*:ring-primary-700! flex flex-row gap-1 w-2/3 place-self-center">
			<Button outline
				onclick={startCamera}
				class="rounded bg-blue-600 px-2 grow py-1 text-sm font-medium text-white shadow transition-all hover:bg-blue-700 active:scale-95"
				>Start Camera</Button
			>
			<Button outline
				onclick={stopCamera}
				class="rounded grow bg-red-600 px-2 py-1 text-sm font-medium text-white shadow transition-all hover:bg-red-700 active:scale-95"
				>Stop Camera</Button
			>
			<Button outline
				onclick={capturePhoto}
				class="rounded grow bg-green-600 px-2 py-1 text-sm font-medium text-white shadow transition-all hover:bg-green-700 active:scale-95"
				>Capture Photo</Button
			>

			<Button outline
				onclick={uploadPhoto}
				class="rounded bg-yellow-600 px-4 py-2 font-semibold text-white shadow transition-all hover:bg-yellow-700 active:scale-95 disabled:cursor-not-allowed disabled:opacity-50"
				disabled={!photoPreview}
			>
				Upload Photo with Data
			</Button>

			</ButtonGroup>
			{#if !photoPreview}
				<span
					class="absolute bottom-full left-1/2 z-10 mb-2 -translate-x-1/2 scale-0 whitespace-nowrap rounded bg-gray-800 px-2 py-1 text-xs text-white transition-transform group-hover:scale-100"
				>
					Please take a photo before uploading
				</span>
			{/if}
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
</style>
