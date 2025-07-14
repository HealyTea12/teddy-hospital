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

	let canvasEl: HTMLCanvasElement;
	let ctx: CanvasRenderingContext2D;
	let drawing = false;

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
		tick().then(() => setupCanvas());
	}

	function setupCanvas() {
		const img = new Image();
		img.src = buildUrl(modalImageUrl);
		img.onload = () => {
			canvasEl.width = img.width;
			canvasEl.height = img.height;
			ctx = canvasEl.getContext('2d');
			ctx.clearRect(0, 0, canvasEl.width, canvasEl.height);
			ctx.strokeStyle = 'rgba(128,128,128,0.5)';
			ctx.lineWidth = 10;
			ctx.lineCap = 'round';
		};
	}

	function startDraw(event: MouseEvent) {
		event.preventDefault();
		drawing = true;
		ctx.beginPath();
		ctx.moveTo(event.offsetX, event.offsetY);
	}

	function draw(event: MouseEvent) {
		if (!drawing) return;
		event.preventDefault();
		ctx.lineTo(event.offsetX, event.offsetY);
		ctx.stroke();
	}

	function endDraw() {
		drawing = false;
		ctx.closePath();
	}

	async function uploadOverlay() {
		const img = new Image();
		img.src = buildUrl(modalImageUrl);
		img.crossOrigin = 'anonymous';
		img.onload = async () => {
			const off = document.createElement('canvas');
			off.width = img.width;
			off.height = img.height;
			const offCtx = off.getContext('2d');
			offCtx.drawImage(img, 0, 0);
			offCtx.drawImage(canvasEl, 0, 0);
			off.toBlob(async (blob) => {
				await sendConfirmation(modalIndex, modalChoice, true, blob);
				showModal = false;
			});
		};
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
					src={buildUrl(modalImageUrl)}
					alt="selected"
					draggable="false"
					on:dragstart|preventDefault
				/>
				<canvas
					bind:this={canvasEl}
					on:mousedown={startDraw}
					on:mousemove={draw}
					on:mouseup={endDraw}
					on:mouseleave={endDraw}
				/>
			</div>
			<button on:click={uploadOverlay}>Upload</button>
			<button on:click={() => (showModal = false)}>Cancel</button>
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
	.image-container {
		position: relative;
	}
	.image-container img,
	.image-container canvas {
		display: block;
	}
	.image-container canvas {
		position: absolute;
		top: 0;
		left: 0;
	}
</style>
