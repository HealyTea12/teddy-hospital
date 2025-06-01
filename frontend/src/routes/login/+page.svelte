<script lang="ts">
        
    import { enhance } from '$app/forms';
    const form = $props();
    
</script>

<h1>
    Login
</h1>
<form method="POST" use:enhance>
    <label for="password">Password:</label>
    <input type="password" id="password" name="password" required>
    <button type="submit">Login</button>
    
{#if form?.error}
    <p class="error">{form.error}</p>
{/if}
</form>



<style>
    .error {
        color: red;
        margin-top: 10px;
    }
    
    form {
        display: flex;
        flex-direction: column;
        gap: 10px;
        max-width: 300px;
        margin: 0 auto;
    }
    
    button {
        margin-top: 10px;
    }
</style>