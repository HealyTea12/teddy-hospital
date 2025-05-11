<script lang="ts">
  // Fix: Changed Number to lowercase number (correct TypeScript primitive type)
  // Fix: Updated form submission handling
  async function generateQR(n: number) {
    try {
      // Use an absolute URL with http protocol (not https)
      const response = await fetch(`http://localhost:8000/qr?n=${n}`, {
        method: 'GET',
        // Add proper headers for binary data
        headers: {
          'Accept': 'application/pdf',
        }
      });
      
      if (response.ok) {
        // Get the PDF as a blob and create an object URL
        const pdfBlob = await response.blob();
        const pdfUrl = URL.createObjectURL(pdfBlob);
        
        // Open PDF in a new tab
        window.open(pdfUrl, '_blank');
      } else {
        alert('Error generating QR codes: ' + response.statusText);
      }
    } catch (error) {
      console.error('Error generating QR codes:', error);
      alert('Failed to generate QR codes. See console for details.');
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

    <p>
        This is the admin page. You can manage your application settings and user accounts here.
    </p>

    <h2>Generate QR code</h2>
    <form on:submit={handleSubmit}>
        <label for="n_qrs">Number of QR codes:</label>
        <input type="number" id="n_qrs" name="n_qrs" min="1" max="1000" required>
        <input type="submit" value="Generate">
    </form>
</div>