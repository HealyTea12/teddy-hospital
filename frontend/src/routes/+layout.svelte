<script lang="ts">
	import Header from './Header.svelte';
	import '../app.css';
	import { goto } from '$app/navigation';
	import { browser } from '$app/environment';
	
	let { children } = $props();

	import { onMount } from 'svelte';
	
	onMount(() => {
		if (!localStorage.getItem('session')) {
			goto('/login');
		}
	});
</script>

<div class="app">
	<Header />

	<main>
		{@render children()}
	</main>

	<footer>
		<p>
			visit our <a href="https://teddy-hospital-xray.readthedocs.io/en/latest/">readthedocs page</a> to learn more about our project!
		</p>
	</footer>
</div>

<style>
	.app {
		display: flex;
		flex-direction: column;
		min-height: 100vh;
	}

	main {
		flex: 1;
		display: flex;
		flex-direction: column;
		padding: 1rem;
		width: 100%;
		max-width: 100rem;
		margin: 0 auto;
		box-sizing: border-box;
	}

	footer {
		display: flex;
		flex-direction: column;
		justify-content: center;
		align-items: center;
		padding: 12px;
	}

	footer a {
		font-weight: bold;
	}

	@media (min-width: 480px) {
		footer {
			padding: 12px 0;
		}
	}
</style>
