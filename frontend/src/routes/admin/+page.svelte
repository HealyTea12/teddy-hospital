<script lang="ts">
	// boolean to dis/enable generate button
	let isLoading = false;
	let resultMessage = '';
	// Fix: Changed Number to lowercase number (correct TypeScript primitive type)
	// Fix: Updated form submission handling
	async function generateQR(n: number) {
		try {
			// disable generate button
			isLoading = true;
			resultMessage = '';
			// Use an absolute URL with http protocol (not https)
			const response = await fetch(`http://localhost:8000/qr?n=${n}`, {
				method: 'GET',
				// Add proper headers for binary data
				headers: {
					Accept: 'application/pdf'
				}
			});

			if (response.ok) {
				// Get the PDF as a blob and create an object URL
				const pdfBlob = await response.blob();
				const pdfUrl = URL.createObjectURL(pdfBlob);

				// Open PDF in a new tab
				window.open(pdfUrl, '_blank');
				resultMessage = 'QR code(s) generated successfully!';
			} else {
				alert('Error generating QR codes: ' + response.statusText);
			}
		} catch (error) {
			console.error('Error generating QR codes:', error);
			alert('Failed to generate QR codes. See console for details.');
		} finally {
			isLoading = false;
		}
	}

	// Handle form submission
	function handleSubmit(event: Event) {
		event.preventDefault();
		const form = event.target as HTMLFormElement;
		const formData = new FormData(form);
		const n = Number(formData.get('n_qrs'));
		if (n > 0) {
			generateQR(n);
		}
	}
</script>

<svelte:head>
	<title>Admin</title>
	<meta name="description" content="Admin page" />
</svelte:head>

<div class="text-column">
	<h1>Admin</h1>

	<p>This is the admin page. You can manage your application settings and user accounts here.</p>

	<h2>Generate QR code</h2>
	<form on:submit={handleSubmit}>
		<label for="n_qrs">Number of QR codes:</label>
		<input type="number" id="n_qrs" name="n_qrs" min="1" max="1000" required />
		<div class="group relative w-fit">
			<button
				type="submit"
				class="rounded bg-blue-600 px-4 py-2 font-semibold text-white shadow transition-all hover:bg-blue-700 active:scale-95 disabled:cursor-not-allowed disabled:opacity-50"
				disabled={isLoading}
			>
				{isLoading ? 'Generating...' : 'Generate'}
			</button>

			<!-- Tooltip (appears on hover) -->
			<span
				class="absolute bottom-full left-1/2 mb-2 -translate-x-1/2 scale-0 whitespace-nowrap rounded bg-gray-800 px-2 py-1 text-xs text-white transition-transform group-hover:scale-100"
			>
				Large numbers may take a few minutes
			</span>

			<!-- Feedback message -->
			{#if isLoading}
				<p class="text-sm text-gray-500">Generating QR codes, please wait...</p>
			{:else if resultMessage}
				<p class="font-medium text-green-600">{resultMessage}</p>
			{/if}
		</div>
	</form>
</div>
