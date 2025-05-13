
<svelte:head>
	<title>Admin</title>
	<meta name="description" content="Admin page" />
</svelte:head>

<div class="text-column">
    <h1>Admin</h1>

    <p>
        This is the admin page. You can manage your application settings and user accounts here.
    </p>

    <h2>Upload the Photo of the Teddy!</h2>
    <form id="photoForm" action="/upload" method="post" enctype="multipart/form-data">
        <label for="photoInput">Take or select a photo:</label><br>
        <input type="file" id="photoInput" name="photo" accept="image/*" capture="environment" required><br>
        <img id="preview" src="#" alt="Image preview" style="display:none;"><br>
        <button type="submit">Upload Photo</button>
    </form>
</div>