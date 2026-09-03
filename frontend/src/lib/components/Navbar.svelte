<script>
	/**
	 * Navbar.svelte — Barra de navegación principal.
	 * Aparece en TODAS las páginas gracias al layout.
	 *
	 * Links públicos (siempre visibles):
	 *  /        → Inicio
	 *  /publico → Vista Pública (fixture + posiciones para hinchas)
	 *
	 * Links de administrador (solo visibles si isAdmin === true):
	 *  /equipos      → Equipos registrados
	 *  /mesa-control → Panel de arbitraje
	 */
	import { page } from '$app/stores';
	import { auth } from '$lib/stores/auth';

	const publicLinks = [
		{ href: '/',        label: 'Inicio',       icon: '🏠' },
		{ href: '/publico', label: 'Vista Pública', icon: '🌐' }
	];

	const adminLinks = [
		{ href: '/equipos',      label: 'Equipos',         icon: '👕' },
		{ href: '/mesa-control', label: 'Mesa de Control', icon: '🎮' }
	];

	let isAdmin = $state(false);

	// Suscripción al store de autenticación
	const unsub = auth.subscribe((val) => (isAdmin = val));
	import { onDestroy } from 'svelte';
	onDestroy(unsub);

	// Estado para el menú mobile (hamburguesa) en Svelte 5
	let mobileMenuOpen = $state(false);
	const toggleMenu = () => (mobileMenuOpen = !mobileMenuOpen);

	function handleLogout() {
		auth.logout();
		mobileMenuOpen = false;
	}
</script>

<header class="sticky top-0 z-40 w-full border-b" style="background: #0b0f19; border-color: var(--border-color);">
	<nav class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 flex items-center justify-between h-16">

		<!-- Logo -->
		<a href="/" class="flex items-center gap-2 shrink-0">
			<span class="text-2xl">⚽</span>
			<span class="font-bold text-lg tracking-tight text-emerald-400">
				Nombre<span class="text-white">-Creativo</span>
			</span>
		</a>

		<!-- Links escritorio -->
		<div class="hidden md:flex items-center gap-1">
			<!-- Links públicos -->
			{#each publicLinks as link}
				<a
					href={link.href}
					class="flex items-center gap-1.5 px-4 py-2 rounded-lg text-sm font-medium transition-colors duration-150 {$page.url.pathname === link.href
						? 'text-emerald-400 bg-emerald-500/10 font-semibold'
						: 'text-slate-300 hover:text-white hover:bg-slate-800/60'}"
				>
					<span>{link.icon}</span>
					<span>{link.label}</span>
				</a>
			{/each}

			<!-- Separador visual admin -->
			{#if isAdmin}
				<span class="w-px h-5 bg-slate-700 mx-1"></span>
				{#each adminLinks as link}
					<a
						href={link.href}
						class="flex items-center gap-1.5 px-4 py-2 rounded-lg text-sm font-medium transition-colors duration-150 {$page.url.pathname === link.href
							? 'text-amber-400 bg-amber-500/10 font-semibold'
							: 'text-slate-300 hover:text-white hover:bg-slate-800/60'}"
					>
						<span>{link.icon}</span>
						<span>{link.label}</span>
					</a>
				{/each}

				<button
					onclick={handleLogout}
					class="ml-2 flex items-center gap-1.5 px-3 py-1.5 rounded-lg text-xs font-medium text-slate-500 hover:text-red-400 hover:bg-red-500/10 transition-colors duration-150"
					title="Cerrar sesión de administrador"
				>
					🔓 Salir
				</button>
			{:else}
				<a
					href="/mesa-control"
					class="ml-1 flex items-center gap-1 px-3 py-1.5 rounded-lg text-xs font-medium text-slate-500 hover:text-slate-300 transition-colors"
					title="Acceso de administrador"
				>
					🔐 Admin
				</a>
			{/if}
		</div>

		<!-- Indicador de estado -->
		<div class="hidden md:flex items-center gap-2 text-xs text-slate-500">
			<span class="w-1.5 h-1.5 rounded-full bg-emerald-500"></span>
			API Live
		</div>

		<!-- Botón hamburguesa mobile -->
		<button
			class="md:hidden p-2 rounded-lg text-slate-300 hover:text-white hover:bg-white/5 transition"
			onclick={toggleMenu}
			aria-label="Abrir menú"
		>
			{#if mobileMenuOpen}✕{:else}☰{/if}
		</button>
	</nav>

	<!-- Menú mobile desplegable -->
	{#if mobileMenuOpen}
		<div class="md:hidden border-t px-4 py-3 flex flex-col gap-1" style="border-color: var(--border-color); background: var(--bg-primary);">
			{#each publicLinks as link}
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

			{#if isAdmin}
				<div class="border-t border-slate-800 my-2 pt-2 flex flex-col gap-1">
					<p class="text-xs text-amber-500/70 px-3 pb-1 font-semibold uppercase tracking-wider">Admin</p>
					{#each adminLinks as link}
						<a
							href={link.href}
							class="flex items-center gap-2 px-3 py-2 rounded-lg text-sm font-medium transition {$page.url.pathname === link.href
								? 'text-amber-400 bg-amber-500/10'
								: 'text-slate-300 hover:text-white hover:bg-white/5'}"
							onclick={() => (mobileMenuOpen = false)}
						>
							<span>{link.icon}</span>
							<span>{link.label}</span>
						</a>
					{/each}
					<button
						onclick={handleLogout}
						class="flex items-center gap-2 px-3 py-2 rounded-lg text-sm font-medium text-red-400 hover:bg-red-500/10 transition mt-1"
					>
						🔓 Cerrar sesión de admin
					</button>
				</div>
			{:else}
				<a
					href="/mesa-control"
					class="flex items-center gap-2 px-3 py-2 rounded-lg text-sm text-slate-500 hover:text-slate-300 transition mt-1"
					onclick={() => (mobileMenuOpen = false)}
				>
					🔐 Acceso Admin
				</a>
			{/if}
		</div>
	{/if}
</header>
