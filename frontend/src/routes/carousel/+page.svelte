<script>

  import { onMount, onDestroy } from 'svelte'; 

  let images = [];
  let visibleCount = 3;
  let startIndex = 0;
  let autoplay = true;
  let autoplaySpeed = 3000; // in ms
  let autoplayTimer;

  $: visibleImages = images.slice(startIndex, startIndex + visibleCount);

  onMount(async () => {
    const res = await fetch(`http://localhost:8000/carousel`);
    if (res.ok) {
      images = await res.json();
      if (autoplay) startAutoplay();
    } else {
      console.error('Failed to fetch carousel images');
    }
  });

  onDestroy(() => {
    clearInterval(autoplayTimer);
  });

function startAutoplay() {
    clearInterval(autoplayTimer);
    autoplayTimer = setInterval(() => {
      if (startIndex + visibleCount < images.length) {
        startIndex++;
      } else {
        startIndex = 0;
      }
    }, autoplaySpeed);
  }

  function stopAutoplay() {
    clearInterval(autoplayTimer);
  }

  function toggleAutoplay() {
    autoplay = !autoplay;
    if (autoplay) {
      startAutoplay();
    } else {
      stopAutoplay();
    }
  }

  function prev() {
    stopAutoplay();
    if (startIndex > 0) {
      startIndex--;
    } else {
      startIndex = Math.max(0, images.length - visibleCount);
    }
    if (autoplay) startAutoplay();
  }

  function next() {
    stopAutoplay();
    if (startIndex + visibleCount < images.length) {
      startIndex++;
    } else {
      startIndex = 0;
    }
    if (autoplay) startAutoplay();
  }

</script>



<style>
  .carousel-container {
    display: flex;
    flex-direction: column;
    align-items: center;
  }

  .carousel {
    display: flex;
    gap: 1rem;
    overflow: hidden;
    margin: 1rem 0;
  }

  .carousel img {
    max-width: 100%;
    max-height: 200px;
    border-radius: 8px;
    box-shadow: 0 2px 6px rgba(0, 0, 0, 0.2);
  }

  .controls {
    display: flex;
    gap: 1rem;
    align-items: center;
  }

  button {
    padding: 0.5rem 1rem;
  }
</style>


<div class="carousel-container">
  <div class="controls">
    <button on:click={prev} disabled={startIndex === 0}>⬅️</button>

    <label>
      Visible:
      <input type="number" bind:value={visibleCount} min="1" max={images.length} />
    </label>

    <button on:click={next} disabled={startIndex + visibleCount >= images.length}>➡️</button>
  </div>

  <div class="controls">
    <label>
      Autoplay:
      <input type="checkbox" bind:checked={autoplay} on:change={toggleAutoplay} />
    </label>

    <label>
      Speed (ms):
      <input type="number" bind:value={autoplaySpeed} min="500" step="500" on:change={() => {
        if (autoplay) {
          startAutoplay();
        }
      }} />
    </label>
  </div>

  <div class="carousel">
    {#each visibleImages as img}
      <img src={img} alt="carousel image" />
    {/each}
  </div>
</div>
