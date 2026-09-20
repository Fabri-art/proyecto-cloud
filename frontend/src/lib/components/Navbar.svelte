<script>
	/**
	 * Navbar.svelte — Barra de navegación principal rediseñada.
	 *
	 * Links públicos:   /  |  /publico
	 * Links de admin:   /equipos  |  /mesa-control  (solo con sesión PIN)
	 */
	import { page } from '$app/stores';
	import { auth } from '$lib/stores/auth';
	import { onDestroy } from 'svelte';

	const publicLinks = [
		{ href: '/',        label: 'Inicio',       icon: 'home' },
		{ href: '/publico', label: 'Vista Pública', icon: 'globe' }
	];

	const adminLinks = [
		{ href: '/equipos',      label: 'Equipos',         icon: 'users' },
		{ href: '/mesa-control', label: 'Mesa de Control', icon: 'monitor' }
	];

	let isAdmin = $state(false);
	const unsub = auth.subscribe((val) => (isAdmin = val));
	onDestroy(unsub);

	let mobileMenuOpen = $state(false);
	const toggleMenu = () => (mobileMenuOpen = !mobileMenuOpen);

	function handleLogout() { auth.logout(); mobileMenuOpen = false; }

	// SVG inline helpers
	const icons = {
		home:    `<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 20 20" fill="currentColor" class="w-4 h-4"><path fill-rule="evenodd" d="M9.293 2.293a1 1 0 0 1 1.414 0l7 7A1 1 0 0 1 17 11h-1v6a1 1 0 0 1-1 1h-2a1 1 0 0 1-1-1v-3a1 1 0 0 0-1-1H9a1 1 0 0 0-1 1v3a1 1 0 0 1-1 1H5a1 1 0 0 1-1-1v-6H3a1 1 0 0 1-.707-1.707l7-7Z" clip-rule="evenodd"/></svg>`,
		globe:   `<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 20 20" fill="currentColor" class="w-4 h-4"><path fill-rule="evenodd" d="M18 10a8 8 0 1 1-16 0 8 8 0 0 1 16 0Zm-1.503.204A6.5 6.5 0 1 0 4.45 12.69a.5.5 0 0 1 .032-.287l.53-1.27a.5.5 0 0 0-.258-.632L4 10.1v-.6a.5.5 0 0 1 .5-.5h1a.5.5 0 0 1 .5.5v.74a.5.5 0 0 0 .326.469l.994.363a.5.5 0 0 1 .334.526.5.5 0 0 0 .5.502h.5a.5.5 0 0 1 .5.5v.14a.5.5 0 0 0 .5.5h.5a.5.5 0 0 1 .5.5V15a6.472 6.472 0 0 0 3.398-4.797ZM13.5 8.5a.5.5 0 0 1-.5.5h-.5a.5.5 0 0 1-.5-.5V8a.5.5 0 0 0-.5-.5h-.5a.5.5 0 0 1-.5-.5v-.5a.5.5 0 0 1 .5-.5H12a.5.5 0 0 0 .5-.5V5a.5.5 0 0 1 .5-.5.5.5 0 0 1 .5.5v.5A1.5 1.5 0 0 1 15 7v.5a1 1 0 0 1-1 1h-.5Z" clip-rule="evenodd"/></svg>`,
		users:   `<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 20 20" fill="currentColor" class="w-4 h-4"><path d="M10 9a3 3 0 1 0 0-6 3 3 0 0 0 0 6ZM6 8a2 2 0 1 1-4 0 2 2 0 0 1 4 0ZM1.49 15.326a.78.78 0 0 1-.358-.442 3 3 0 0 1 4.308-3.516 6.484 6.484 0 0 0-1.905 3.959c-.023.222-.014.442.025.654a4.97 4.97 0 0 1-2.07-.655ZM16.44 15.98a4.97 4.97 0 0 0 2.07-.654.78.78 0 0 0 .357-.442 3 3 0 0 0-4.308-3.517 6.484 6.484 0 0 1 1.907 3.96 2.32 2.32 0 0 1-.026.654ZM18 8a2 2 0 1 1-4 0 2 2 0 0 1 4 0ZM5.304 16.19a.844.844 0 0 1-.277-.71 5 5 0 0 1 9.947 0 .843.843 0 0 1-.277.71A6.975 6.975 0 0 1 10 18a6.974 6.974 0 0 1-4.696-1.81Z"/></svg>`,
		monitor: `<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 20 20" fill="currentColor" class="w-4 h-4"><path fill-rule="evenodd" d="M2 4.25A2.25 2.25 0 0 1 4.25 2h11.5A2.25 2.25 0 0 1 18 4.25v8.5A2.25 2.25 0 0 1 15.75 15h-3.105a3.501 3.501 0 0 0 1.1 1.677A.75.75 0 0 1 13.26 18H6.74a.75.75 0 0 1-.484-1.323A3.501 3.501 0 0 0 7.355 15H4.25A2.25 2.25 0 0 1 2 12.75v-8.5Zm1.5 0a.75.75 0 0 1 .75-.75h11.5a.75.75 0 0 1 .75.75v7.5a.75.75 0 0 1-.75.75H4.25a.75.75 0 0 1-.75-.75v-7.5Z" clip-rule="evenodd"/></svg>`,
		lock:    `<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 20 20" fill="currentColor" class="w-3.5 h-3.5"><path fill-rule="evenodd" d="M10 1a4.5 4.5 0 0 0-4.5 4.5V9H5a2 2 0 0 0-2 2v6a2 2 0 0 0 2 2h10a2 2 0 0 0 2-2v-6a2 2 0 0 0-2-2h-.5V5.5A4.5 4.5 0 0 0 10 1Zm3 8V5.5a3 3 0 1 0-6 0V9h6Z" clip-rule="evenodd"/></svg>`,
		logout:  `<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 20 20" fill="currentColor" class="w-3.5 h-3.5"><path fill-rule="evenodd" d="M3 4.25A2.25 2.25 0 0 1 5.25 2h5.5A2.25 2.25 0 0 1 13 4.25v2a.75.75 0 0 1-1.5 0v-2a.75.75 0 0 0-.75-.75h-5.5a.75.75 0 0 0-.75.75v11.5c0 .414.336.75.75.75h5.5a.75.75 0 0 0 .75-.75v-2a.75.75 0 0 1 1.5 0v2A2.25 2.25 0 0 1 10.75 18h-5.5A2.25 2.25 0 0 1 3 15.75V4.25Zm10.47 4.97a.75.75 0 0 1 1.06 0l2.25 2.25a.75.75 0 0 1 0 1.06l-2.25 2.25a.75.75 0 1 1-1.06-1.06l.97-.97H6.75a.75.75 0 0 1 0-1.5h7.69l-.97-.97a.75.75 0 0 1 0-1.06Z" clip-rule="evenodd"/></svg>`
	};
</script>

<header class="navbar-bar sticky top-0 z-40 w-full">
	<nav class="max-w-7xl mx-auto px-3 sm:px-6 lg:px-8 flex items-center justify-between h-15">

		<!-- Logo -->
		<a href="/" class="flex items-center gap-2.5 group shrink-0">
			<div class="w-8 h-8 rounded-lg flex items-center justify-center text-white font-black text-sm"
				style="background: linear-gradient(135deg, #059669, #10b981); box-shadow: 0 2px 8px rgba(16,185,129,0.4);">
				TH
			</div>
			<span class="font-black text-base tracking-tight text-white">
				Torneo<span style="color: var(--accent-green);">Hub</span>
			</span>
		</a>

		<!-- Links escritorio -->
		<div class="hidden md:flex items-center gap-1">
			{#each publicLinks as link}
				<a href={link.href}
					class="nav-link {$page.url.pathname === link.href ? 'nav-link-active' : 'nav-link-inactive'}">
					{@html icons[link.icon]}
					{link.label}
				</a>
			{/each}

			{#if isAdmin}
				<div class="w-px h-4 bg-slate-700/80 mx-1"></div>
				{#each adminLinks as link}
					<a href={link.href}
						class="nav-link {$page.url.pathname === link.href ? 'nav-link-admin-active' : 'nav-link-admin'}">
						{@html icons[link.icon]}
						{link.label}
					</a>
				{/each}
				<button onclick={handleLogout} class="nav-logout ml-1">
					{@html icons.logout}
					Salir
				</button>
			{:else}
				<a href="/mesa-control" class="nav-admin-hint ml-1">
					{@html icons.lock}
					Admin
				</a>
			{/if}
		</div>

		<!-- Indicador API + hamburguesa -->
		<div class="flex items-center gap-3">
			<div class="hidden md:flex items-center gap-1.5 text-xs text-slate-600">
				<span class="w-1.5 h-1.5 rounded-full bg-emerald-500"></span>
				Live
			</div>
			<button
				class="md:hidden w-9 h-9 rounded-lg flex items-center justify-center text-slate-400 hover:text-white hover:bg-slate-800 transition"
				onclick={toggleMenu}
				aria-label="Menú"
			>
				{#if mobileMenuOpen}
					<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 20 20" fill="currentColor" class="w-5 h-5">
						<path d="M6.28 5.22a.75.75 0 0 0-1.06 1.06L8.94 10l-3.72 3.72a.75.75 0 1 0 1.06 1.06L10 11.06l3.72 3.72a.75.75 0 1 0 1.06-1.06L11.06 10l3.72-3.72a.75.75 0 0 0-1.06-1.06L10 8.94 6.28 5.22Z"/>
					</svg>
				{:else}
					<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 20 20" fill="currentColor" class="w-5 h-5">
						<path fill-rule="evenodd" d="M2 4.75A.75.75 0 0 1 2.75 4h14.5a.75.75 0 0 1 0 1.5H2.75A.75.75 0 0 1 2 4.75Zm0 10.5a.75.75 0 0 1 .75-.75h14.5a.75.75 0 0 1 0 1.5H2.75a.75.75 0 0 1-.75-.75ZM2 10a.75.75 0 0 1 .75-.75h7.5a.75.75 0 0 1 0 1.5h-7.5A.75.75 0 0 1 2 10Z" clip-rule="evenodd"/>
					</svg>
				{/if}
			</button>
		</div>
	</nav>

	<!-- Menú móvil -->
	{#if mobileMenuOpen}
		<div class="md:hidden border-t border-slate-800 px-4 py-3 flex flex-col gap-1 animate-fade-in"
			style="background: #0b1120;">
			{#each publicLinks as link}
				<a href={link.href}
					class="mobile-link {$page.url.pathname === link.href ? 'mobile-link-active' : 'mobile-link-inactive'}"
					onclick={() => (mobileMenuOpen = false)}>
					{@html icons[link.icon]}
					{link.label}
				</a>
			{/each}

			{#if isAdmin}
				<div class="my-1.5 border-t border-slate-800 pt-1.5">
					<p class="px-3 pb-1 text-xs section-label">Admin</p>
					{#each adminLinks as link}
						<a href={link.href}
							class="mobile-link {$page.url.pathname === link.href ? 'mobile-link-admin-active' : 'mobile-link-admin'}"
							onclick={() => (mobileMenuOpen = false)}>
							{@html icons[link.icon]}
							{link.label}
						</a>
					{/each}
					<button onclick={handleLogout} class="mobile-link mobile-link-logout w-full">
						{@html icons.logout}
						Cerrar sesión
					</button>
				</div>
			{:else}
				<a href="/mesa-control"
					class="mobile-link mobile-link-inactive"
					onclick={() => (mobileMenuOpen = false)}>
					{@html icons.lock}
					Acceso Admin
				</a>
			{/if}
		</div>
	{/if}
</header>

<style>
	.navbar-bar {
		background: rgba(8, 12, 20, 0.92);
		border-bottom: 1px solid rgba(148, 163, 184, 0.08);
		backdrop-filter: blur(12px);
		-webkit-backdrop-filter: blur(12px);
		height: 60px;
	}

	/* Links de escritorio */
	.nav-link {
		display: flex;
		align-items: center;
		gap: 0.4rem;
		padding: 0.45rem 0.9rem;
		border-radius: 0.5rem;
		font-size: 0.85rem;
		font-weight: 600;
		transition: color 0.15s, background 0.15s;
	}
	.nav-link-active  { color: #10b981; background: rgba(16,185,129,0.1); }
	.nav-link-inactive { color: #64748b; }
	.nav-link-inactive:hover { color: #e2e8f0; background: rgba(255,255,255,0.05); }

	.nav-link-admin-active { color: #fbbf24; background: rgba(245,158,11,0.1); }
	.nav-link-admin { color: #64748b; }
	.nav-link-admin:hover { color: #fbbf24; background: rgba(245,158,11,0.07); }

	.nav-logout {
		display: flex; align-items: center; gap: 0.35rem;
		padding: 0.35rem 0.75rem; border-radius: 0.5rem;
		font-size: 0.75rem; font-weight: 600;
		color: #64748b; transition: color 0.15s, background 0.15s;
	}
	.nav-logout:hover { color: #f87171; background: rgba(239,68,68,0.08); }

	.nav-admin-hint {
		display: flex; align-items: center; gap: 0.35rem;
		padding: 0.35rem 0.75rem; border-radius: 0.5rem;
		font-size: 0.75rem; font-weight: 600;
		color: #334155; transition: color 0.15s;
	}
	.nav-admin-hint:hover { color: #64748b; }

	/* Links móvil */
	.mobile-link {
		display: flex; align-items: center; gap: 0.6rem;
		padding: 0.625rem 0.75rem; border-radius: 0.625rem;
		font-size: 0.875rem; font-weight: 600;
		transition: color 0.15s, background 0.15s;
	}
	.mobile-link-active       { color: #10b981; background: rgba(16,185,129,0.08); }
	.mobile-link-inactive     { color: #94a3b8; }
	.mobile-link-inactive:hover { color: white; background: rgba(255,255,255,0.05); }
	.mobile-link-admin-active { color: #fbbf24; background: rgba(245,158,11,0.08); }
	.mobile-link-admin        { color: #94a3b8; }
	.mobile-link-admin:hover  { color: #fbbf24; background: rgba(245,158,11,0.06); }
	.mobile-link-logout       { color: #64748b; text-align: left; }
	.mobile-link-logout:hover { color: #f87171; background: rgba(239,68,68,0.08); }
</style>
