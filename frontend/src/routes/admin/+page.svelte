<script lang="ts">

  import { BACKEND_URL } from '$env/static/private';
  let progress: number = 0;
  let generatedOnce: boolean = false;
  let generating: boolean = false;
  async function generateQR(n: number) {
    try {
      generating = true;
      progress = 0;
      const response = await fetch(`${BACKEND_URL}/qr?n=${n}`, {
        method: 'GET',
        headers: {
          'Accept': 'application/json',
        }
      });
      if (response.ok) {
        let interval = setInterval(() => {
          fetch(`${BACKEND_URL}/qr/progress`, {
            method: 'GET',
            headers: {
              'Accept': 'application/json',
            }
          }).then(res => res.json()).then(data => {
            console.log('Progress data:', data);
            progress = data.progress;
            if (progress >= 100) {
              generating = false;
              generatedOnce = true;
              clearInterval(interval);
            }
          });
        }, 2000);
      } else {
        alert('Error generating QR codes: ' + response.statusText);
      }
    } catch (error) {
      alert('Failed to generate QR codes. ' + error );
    }
  }

  function downloadQR() {
    fetch(`${BACKEND_URL}/qr/download`, {
      method: 'GET',
      headers: {
        'Accept': 'application/pdf',
      }
    }).then(response => {
      if (!response.ok) {
        alert('Failed to download PDF');
      }
      response.blob().then(blob => URL.createObjectURL(blob)).then(pdfBlob => {
        window.open(pdfBlob, '_blank');
      });
    });
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
	let resultMessage = '';
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
        <input type="number" id="n_qrs" name="n_qrs" min="1" max="1000" required>
        <div class="group relative w-fit">
			<button
				type="submit"
				class="rounded bg-blue-600 px-4 py-2 font-semibold text-white shadow transition-all hover:bg-blue-700 active:scale-95 disabled:cursor-not-allowed disabled:opacity-50"
				disabled={generating}
			>
				{generating ? 'Generating...' : 'Generate'}
			</button>
			<button
				type="button"
				on:click={downloadQR}
				class="ml-2 rounded bg-green-600 px-4 py-2 font-semibold text-white shadow transition-all hover:bg-green-700 active:scale-95 disabled:cursor-not-allowed disabled:opacity-50"
				disabled={!generatedOnce || generating}
			>Download PDF</button>

			<!-- Tooltip (appears on hover) -->
			<span
				class="absolute bottom-full left-1/2 mb-2 -translate-x-1/2 scale-0 whitespace-nowrap rounded bg-gray-800 px-2 py-1 text-xs text-white transition-transform group-hover:scale-100"
			>
				Large numbers may take a few minutes
			</span>

			<!-- Feedback message -->
			{#if generating}
			    <progress value="{progress}" max="100"></progress><p>Generating QR codes: {progress}%</p>
				<p class="text-sm text-gray-500">Generating QR codes, please wait...</p>
			{:else if generatedOnce}
				<p class="font-medium text-green-600">Success!</p>
			{/if}
		</div>
    </form>
</div>
