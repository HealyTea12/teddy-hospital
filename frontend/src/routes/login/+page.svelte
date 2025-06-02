<script lang="ts">
	import { goto } from "$app/navigation";
    import { PUBLIC_BACKEND_URL } from '$env/static/public';

    let password: string = $state('');
    let errorMessage: string = $state('');
    const form = $props();
    async function login() {
        let data = new FormData();
        data.append('password', password);
        const response = await fetch(`${PUBLIC_BACKEND_URL}/token`, {
            method: 'POST',
            body: data,
        });
        console.log(response);
        if(response.ok){
            const json = await response.json();
            localStorage.setItem('session', json.access_token);
            await goto('/');
        } else {
            errorMessage = `Error: ${response.statusText}`;
        }
    }    
</script>

<h1>
    Login
</h1>
    <label for="password">Password:</label>
    <input type="password" id="password" name="password" bind:value={password} required>
    <button onclick={login}>Login</button>
    

    <p class="error">{errorMessage}</p>




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