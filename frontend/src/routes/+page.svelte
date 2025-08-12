<script lang="ts">
	import welcome from '$lib/images/svelte-welcome.webp';
	import welcomeFallback from '$lib/images/svelte-welcome.png';
</script>

<svelte:head>
	<title>Home</title>
	<meta name="description" content="Teddy Hospital" />
</svelte:head>

<section>
	<h1>
		<span class="welcome">
			<picture>
				<source srcset={welcome} type="image/webp" />
				<img src={welcomeFallback} alt="Welcome" />
			</picture>
		</span>

		to Teddy Hospital
	</h1>

	<!-- Explanation text -->
	<div class="mt-6 max-w-xl text-base leading-relaxed">
		<p>
			<strong>Welcome to the Teddy Hospital X-Ray App! Here's how to get started:</strong>
		</p>

		<h3 class="mt-4"><strong>Before You Begin:</strong></h3>
		<ul class="mt-2 list-inside list-disc">
			<li>Ensure your administrator has set up the cloud storage and high-performance computer.</li>
			<li>Generate QR codes in Admin pannel. (this may take some time)</li>
		</ul>

		<h3 class="mt-4"><strong>Scanning a patient:</strong></h3>
		<ol class="mt-2 list-inside list-decimal">
			<li>Head to Camera and start the camera.</li>
			<li>Scan the QR code from the patient.</li>
			<li>Fill in the form with necessary data. <span style="color: lightgrey;">especially the type of animal.</span></li>
			<li>
				Take a picture of the teddy. <span style="color: lightgrey;">Make sure that the teddy can be clearly identified in the
				picture.</span>
			</li>
			<li>Upload the picture.</li>
		</ol>

		<h3 class="mt-4"><strong>Review generated x-rays:</strong></h3>
		<ol class="mt-2 list-inside list-decimal">
			<li>Head to Results.</li>
			<li>Approve or reject the generated x-rays.<span style="color: lightgrey;">there might be a delay until all options appear</span></li>
		</ol>

		<h3 class="mt-4"><strong>Once approved:</strong></h3>
		<ul class="mt-2 list-inside list-disc">
			<li>Approved x-rays will be automaticly stored to the cloud storage</li>
			<li>Want to see recently made x-rays? You can see them in the Carousel pannel.</li>
		</ul>
	</div>
</section>

<style>
	section {
		display: flex;
		flex-direction: column;
		justify-content: center;
		align-items: center;
		flex: 0.6;
	}

	h1 {
		width: 100%;
	}

	.welcome {
		display: block;
		position: relative;
		width: 100%;
		height: 0;
		padding: 0 0 calc(100% * 495 / 2048) 0;
	}

	.welcome img {
		position: absolute;
		width: 100%;
		height: 100%;
		top: 0;
		display: block;
	}
</style>
