<script>
	/**
	 * +layout.svelte — Layout raíz de la aplicación.
	 *
	 * ¿Qué hace?
	 * Envuelve TODAS las páginas con:
	 *   - La Navbar (siempre visible arriba)
	 *   - El contenedor principal donde se renderizan las páginas
	 *   - El componente Toast (notificaciones globales)
	 *
	 * SvelteKit renderiza el contenido de cada página donde dice {#snippet children()}
	 */
	import './layout.css';
	import Navbar from '$lib/components/Navbar.svelte';
	import Toast from '$lib/components/Toast.svelte';

	let { children } = $props();
</script>

<svelte:head>
	<title>Nombre-Creativo — Torneos Deportivos</title>
</svelte:head>

<!-- Navbar siempre visible -->
<Navbar />

<!-- Contenido de cada página -->
<main class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
	{@render children()}
</main>

<!-- Notificaciones tipo toast (visibles en toda la app) -->
<Toast />
