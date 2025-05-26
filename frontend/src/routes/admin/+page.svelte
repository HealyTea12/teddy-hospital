<script lang="ts">
  let progress: number = 0;
  let generatedOnce: boolean = false;
  let generating: boolean = false;
  async function generateQR(n: number) {
    try {
      generating = true;
      progress = 0;
      const response = await fetch(`http://localhost:8000/qr?n=${n}`, {
        method: 'GET',
        headers: {
          'Accept': 'application/json',
        }
      });
      if (response.ok) {
        let interval = setInterval(() => {
          fetch('http://localhost:8000/qr/progress', {
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
    fetch('http://localhost:8000/qr/download', {
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
</script>
<svelte:head>
	<title>Admin</title>
	<meta name="description" content="Admin page" />
</svelte:head>

<div class="text-column">
    <h1>Admin</h1>

    <p>
        This is the admin page. You can manage your application settings and user accounts here.
    </p>

    <h2>Generate QR code</h2>
    <form on:submit={handleSubmit}>
        <label for="n_qrs">Number of QR codes:</label>
        <input type="number" id="n_qrs" name="n_qrs" min="1" max="1000" required>
        <input type="submit" value="Generate">
    </form>
    {#if generating}
    <progress value="{progress}" max="100"></progress><p>Generating QR codes: {progress}%</p>
    {:else if generatedOnce}
    <p>Success!</p> <button on:click={downloadQR}>Download PDF</button>
    {/if}
</div>