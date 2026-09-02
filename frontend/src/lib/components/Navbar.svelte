<script>
	/**
	 * Navbar.svelte — Barra de navegación principal.
	 * Aparece en TODAS las páginas gracias al layout.
	 *
	 * Links:
	 *  /             → Inicio
	 *  /equipos      → Equipos registrados
	 *  /fixture      → Calendario de partidos
	 *  /posiciones   → Tabla de posiciones
	 */
	import { page } from '$app/stores';

	// Lista de páginas del sitio
	const navLinks = [
		{ href: '/',           label: 'Inicio',      icon: '🏠' },
		{ href: '/equipos',    label: 'Equipos',     icon: '👕' },
		{ href: '/fixture',    label: 'Fixture',     icon: '📅' },
		{ href: '/posiciones', label: 'Posiciones',  icon: '📊' }
	];

	// Estado para el menú mobile (hamburguesa) en Svelte 5
	let mobileMenuOpen = $state(false);
	const toggleMenu = () => (mobileMenuOpen = !mobileMenuOpen);
</script>

<header class="sticky top-0 z-40 w-full border-b" style="background: rgba(15,23,42,0.85); backdrop-filter: blur(16px); border-color: var(--border-color);">
	<nav class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 flex items-center justify-between h-16">

		<!-- Logo / Nombre del proyecto -->
		<a href="/" class="flex items-center gap-2 group">
			<span class="text-2xl">⚽</span>
			<span class="font-bold text-lg tracking-tight" style="color: var(--accent-green);">
				Nombre<span class="text-white">-Creativo</span>
			</span>
		</a>

		<!-- Links escritorio -->
		<div class="hidden md:flex items-center gap-1">
			{#each navLinks as link}
				<a
					href={link.href}
					class="flex items-center gap-1.5 px-4 py-2 rounded-lg text-sm font-medium transition-all duration-200 {$page.url.pathname === link.href
						? 'text-emerald-400 bg-emerald-500/10'
						: 'text-slate-300 hover:text-white hover:bg-white/5'}"
				>
					<span>{link.icon}</span>
					<span>{link.label}</span>
				</a>
			{/each}
		</div>

		<!-- Indicador de estado (API live) -->
		<div class="hidden md:flex items-center gap-2 text-xs text-slate-400">
			<span class="w-2 h-2 rounded-full bg-emerald-500 animate-pulse"></span>
			API Live
		</div>

		<!-- Botón hamburguesa mobile -->
		<button
			class="md:hidden p-2 rounded-lg text-slate-300 hover:text-white hover:bg-white/5 transition"
			onclick={toggleMenu}
			aria-label="Abrir menú"
		>
			{#if mobileMenuOpen}
				✕
			{:else}
				☰
			{/if}
		</button>
	</nav>

	<!-- Menú mobile desplegable -->
	{#if mobileMenuOpen}
		<div class="md:hidden border-t px-4 py-3 flex flex-col gap-1" style="border-color: var(--border-color); background: var(--bg-primary);">
			{#each navLinks as link}
				<a
					href={link.href}
					class="flex items-center gap-2 px-3 py-2 rounded-lg text-sm font-medium transition {$page.url.pathname === link.href
						? 'text-emerald-400 bg-emerald-500/10'
						: 'text-slate-300 hover:text-white hover:bg-white/5'}"
					onclick={() => (mobileMenuOpen = false)}
				>
					<span>{link.icon}</span>
					<span>{link.label}</span>
				</a>
			{/each}
		</div>
	{/if}
</header>
