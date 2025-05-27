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
	<div class="mt-6 text-base leading-relaxed max-w-xl">
		<p>
			<strong>Welcome to the Teddy Hospital X-Ray App! Here's how to get started:</strong> 
		</p>
		<ol class="list-decimal list-inside mt-2">
			<li>Make sure that your administrator has setup the cloud storage and the high perforamnce computer.</li>
			<li>Start by generating QR codes under Admin.(this may take some time)</li>
			<li>Head to Camera and start the camera.</li>
			<li>Start by scanning the QR code of the patient</li>
			<li>Input neccesary data in to the form, especially the type of animal</li>
			<li>Take a picture of the teddy. Make sure that the teddy can be clearly identified in the picture.</li>
			<li>Once the upload is succesful, head to Results to see the generated x-rays.</li>
			<li>You can approve one or reject the generated x-rays.</li>
			<li>If approved, the x-rays will be stored on the cloud storage.</li>
		</ol>
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
