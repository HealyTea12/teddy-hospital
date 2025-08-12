<script lang="ts">
	import jsQR from 'jsqr';
    import { PUBLIC_BACKEND_URL } from '$env/static/public';
	import { Alert, Input, Label, Helper, Select, ButtonGroup, Button, type SelectOptionType, Card } from "flowbite-svelte";
	import { BackwardStepOutline } from "flowbite-svelte-icons";

	let videoElement: HTMLVideoElement;
	let canvasElement: HTMLCanvasElement;
	let photoCanvas: HTMLCanvasElement;
	let stream: MediaStream | null = null;

	let qrResult: string = $state('');
	let isScanning = $state(false);
	let cameraOn = $state(false);
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
				animalTypes.push({value: type, name: type});
			}
			animalTypes = animalTypes;
		});

	async function startQRScanner() {
		try {
			isScanning = true;
			stream = await navigator.mediaDevices.getUserMedia({ video: { facingMode: 'environment' } });
			videoElement.srcObject = stream;
			await videoElement.play();
			scanInterval = setInterval(scanQRCode, 500);
		} catch (err) {
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
			cameraOn = true;
		}
		await videoElement.play();
	}

	function stopCamera() {
		if (stream) {
			stream.getTracks().forEach((t) => t.stop());
			stream = null;
			cameraOn = false;
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


	<div class="flex gap-1 flex-col h-full mb-2">
	{#if import.meta.env.DEV}
	<button on:click={() => qrResult = qrResult ? "" : "a"}>toglle</button>
	{/if} 
{#if !qrResult }
	<h1>Step 1: Scan QR Code</h1>
	<!-- svelte-ignore a11y_media_has_caption -->
		<div class="flex-auto flex items-center justify-center relative">
	<video class="" bind:this={videoElement} autoplay></video>
	<canvas class="" bind:this={canvasElement} style="display: none;"></canvas>
	</div>
	<button
		on:click={startQRScanner}
		class="rounded-xl cursor-pointer flex-initial w-1/2  mx-auto position-center bg-blue-600 px-2 py-1 text-sm font-medium text-white shadow transition-all hover:bg-blue-700 active:scale-95" disabled={isScanning} style="opacity: {isScanning ? 0.2 : 1};"
		>Start QR Scanner</button
	>
{:else}
	{#if alert_message !== ""}
	<Alert color={alert_color} class="mb-2">
		{alert_message}
	</Alert>
	{/if}
	<div>
	<Button 
		onclick={() => qrResult=""} outline color="blue" class="w-20 float-start"><BackwardStepOutline class="shrink-0 h-6 w-6" />Back</Button>
	<h1 class="place-self-center">
		Step 2: Take picture of Patient.
	</h1>
	</div>	
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

		<Card class="flex flex-col items-center p-2 mb-2 gap-4 md:flex-row min-w-full min-h-96">
		<!-- svelte-ignore a11y_media_has_caption -->
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
		</Card>

		<!-- Canvas (hidden) -->
		<canvas bind:this={photoCanvas} style="display: none;"></canvas>

			<ButtonGroup class="*:ring-primary-700! flex flex-row gap-1 w-2/3 place-self-center">
			<Button outline
				onclick={startCamera}
				class="rounded bg-blue-600 px-2 grow py-1 text-sm font-medium text-white shadow transition-all hover:bg-blue-600 active:scale-95 disabled:cursor-not-allowed disabled:opacity-30" disabled={cameraOn}
				>Start Camera</Button
			>
			<Button outline
				onclick={stopCamera}
				class="rounded grow bg-blue-500 px-2 py-1 text-sm font-medium text-white shadow transition-all hover:bg-red-400 active:scale-95 disabled:cursor-not-allowed disabled:opacity-30" disabled={!cameraOn}
				>Stop Camera</Button
			>
			<Button outline
				onclick={capturePhoto}
				class="rounded grow bg-green-600 px-2 py-1 text-sm font-medium text-white shadow transition-all hover:bg-green-700 active:scale-95 disabled:cursor-not-allowed" style="opacity: {photoPreview || !cameraOn ? 0.5 : 1};" disabled={!cameraOn}
				>{photoPreview ? "Recapture Photo" : "Capture Photo"}</Button
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
