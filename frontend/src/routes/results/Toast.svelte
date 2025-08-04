<script lang="ts">
	import { waitFor } from '@testing-library/svelte';
	import { Toast } from 'flowbite-svelte';
	import { SalePercentOutline } from 'flowbite-svelte-icons';
	import { fade, slide } from 'svelte/transition';
	import { ssrModuleExportsKey } from 'vite/module-runner';

	let { duration, message, timeoutCallback, ...otherProps } = $props();

	let toastStatus: boolean = $state(true);
	let mDuration = $state(duration);
	const startTimeout = () => {
		if (mDuration > 0) {
			setTimeout(() => {
				mDuration--;
				startTimeout();
			}, 1000);
		} else {
			toastStatus = false;
			timeoutCallback();
		}
	};
	startTimeout();
</script>

<Toast class="w-96" {toastStatus} dismissable={true} transition={slide} {...otherProps}>
	{message} disappear in {mDuration}s
</Toast>
