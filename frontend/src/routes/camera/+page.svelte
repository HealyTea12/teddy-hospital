<script lang="ts">
	let videoElement: HTMLVideoElement;
	let canvasElement: HTMLCanvasElement;
	let photoPreview: string = '';
	let stream: MediaStream | null = null;

	async function startCamera() {
		try {
			stream = await navigator.mediaDevices.getUserMedia({ video: true });
			if (videoElement) {
				videoElement.srcObject = stream;
				await videoElement.play();
			}
		} catch (err) {
			console.error('Error accessing camera:', err);
		}
	}

	function stopCamera() {
		if (stream) {
			stream.getTracks().forEach((track) => track.stop());
			stream = null;
		}
		if (videoElement) {
			videoElement.pause();
			videoElement.srcObject = null;
		}
	}

	function capturePhoto() {
		if (videoElement && canvasElement) {
			const context = canvasElement.getContext('2d');
			canvasElement.width = videoElement.videoWidth;
			canvasElement.height = videoElement.videoHeight;
			context?.drawImage(videoElement, 0, 0);
			photoPreview = canvasElement.toDataURL('image/png');
		}
	}

	async function uploadPhoto() {
		if (!photoPreview) return;

		try {
			const response = await fetch(photoPreview);
			const blob = await response.blob();

			const formData = new FormData();
			formData.append('file', blob, 'photo.png');

			const uploadResponse = await fetch('http://localhost:8000/upload', {
				method: 'POST',
				body: formData
			});

			if (uploadResponse.ok) {
				console.log('Upload successful!');
			} else {
				console.error('Upload failed with status:', uploadResponse.status);
			}
		} catch (error) {
			console.error('Error during upload:', error);
		}
	}
</script>

<svelte:head>
	<title>Admin</title>
	<meta name="description" content="Admin page" />
</svelte:head>

<h1>Camera Interface</h1>

<video bind:this={videoElement} autoplay></video>
<canvas bind:this={canvasElement} style="display: none;"></canvas>

<div class="controls">
	<button on:click={startCamera}>Start Camera</button>
	<button on:click={stopCamera}>Stop Camera</button>
	<button on:click={capturePhoto}>Capture Photo</button>
	<button on:click={uploadPhoto} disabled={!photoPreview}>Upload Photo</button>
</div>

{#if photoPreview}
	<h2>Preview:</h2>
	<img src={photoPreview} alt="Captured Photo" />
{/if}

<!-- <div class="text-column">
    <h1>Admin</h1>

    <p>
        This is the admin page. You can manage your application settings and user accounts here.
    </p>

    <h2>Upload a Photo from Your Camera</h2>
    <form id="photoForm" action="/upload" method="post" enctype="multipart/form-data">
        <label for="photoInput">Take or select a photo:</label><br>
        <input type="file" id="photoInput" name="photo" accept="image/*" capture="environment" required><br>
        <img id="preview" src="#" alt="Image preview" style="display:none;"><br>
        <button type="submit">Upload Photo</button>
    </form>
</div> -->

<style>
	video,
	canvas,
	img {
		max-width: 100%;
		margin-bottom: 1rem;
		border-radius: 8px;
	}
	.controls {
		display: flex;
		gap: 1rem;
		margin-bottom: 1rem;
	}
</style>
