<script>
	/**
	 * routes/+page.svelte — Página de Inicio (/)
	 *
	 * - Hero section con estadísticas del torneo en vivo
	 * - Cards de acceso rápido con diseño premium
	 * - Ping al backend para mostrar estado del servidor
	 */
	import { onMount } from 'svelte';
	import { healthApi, teamsApi, matchesApi, standingsApi } from '$lib/api/client';

	const TOURNAMENT_ID = 1;

	let apiStatus = $state('checking');
	let stats = $state({ teams: null, matches: null, goals: null });

	onMount(async () => {
		try {
			await healthApi.check();
			apiStatus = 'ok';
		} catch {
			apiStatus = 'error';
		}

		// Cargar estadísticas del torneo en paralelo
		try {
			const [teamsList, matchList] = await Promise.all([
				teamsApi.list(TOURNAMENT_ID).catch(() => []),
				matchesApi.list(TOURNAMENT_ID).catch(() => [])
			]);

			const finishedMatches = matchList.filter(
				(m) => (m.status ?? '').toLowerCase() === 'finished'
			);
			const totalGoals = finishedMatches.reduce(
				(acc, m) => acc + (m.home_score ?? 0) + (m.away_score ?? 0),
				0
			);
			const liveCount = matchList.filter(
				(m) => (m.status ?? '').toLowerCase() === 'live'
			).length;

			stats = {
				teams: teamsList.length,
				matches: finishedMatches.length,
				goals: totalGoals,
				live: liveCount
			};
		} catch {
			// stats permanecen null — se ocultará el bloque
		}
	});

	const navCards = [
		{
			href: '/publico',
			icon: `<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" class="w-7 h-7"><circle cx="12" cy="12" r="10"/><circle cx="12" cy="12" r="3"/><line x1="12" y1="2" x2="12" y2="5"/><line x1="12" y1="19" x2="12" y2="22"/><line x1="2" y1="12" x2="5" y2="12"/><line x1="19" y1="12" x2="22" y2="12"/></svg>`,
			title: 'Vista Pública',
			description: 'Fixture en vivo, resultados y tabla de posiciones para hinchas y jugadores.',
			accent: '#10b981',
			accentBg: 'rgba(16,185,129,0.08)',
			accentBorder: 'rgba(16,185,129,0.3)',
			badge: null,
			cta: 'Ver ahora →'
		},
		{
			href: '/equipos',
			icon: `<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" class="w-7 h-7"><path d="M17 21v-2a4 4 0 0 0-4-4H5a4 4 0 0 0-4 4v2"/><circle cx="9" cy="7" r="4"/><path d="M23 21v-2a4 4 0 0 0-3-3.87"/><path d="M16 3.13a4 4 0 0 1 0 7.75"/></svg>`,
			title: 'Equipos',
			description: 'Directorio de clubes, plantillas de jugadores y datos de delegados.',
			accent: '#3b82f6',
			accentBg: 'rgba(59,130,246,0.08)',
			accentBorder: 'rgba(59,130,246,0.3)',
			badge: null,
			cta: 'Ver equipos →'
		},
		{
			href: '/mesa-control',
			icon: `<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" class="w-7 h-7"><rect x="2" y="3" width="20" height="14" rx="2" ry="2"/><line x1="8" y1="21" x2="16" y2="21"/><line x1="12" y1="17" x2="12" y2="21"/></svg>`,
			title: 'Mesa de Control',
			description: 'Panel de arbitraje para registrar goles y cronometrar partidos en tiempo real.',
			accent: '#f59e0b',
			accentBg: 'rgba(245,158,11,0.08)',
			accentBorder: 'rgba(245,158,11,0.3)',
			badge: 'Solo admin',
			cta: 'Ingresar →'
		}
	];
</script>

<svelte:head>
	<title>Torneo Hub — Gestión Deportiva</title>
	<meta name="description" content="Plataforma profesional de gestión de torneos de fútbol. Fixture en tiempo real, tabla de posiciones, equipos y panel de arbitraje." />
</svelte:head>

<!-- ── HERO ──────────────────────────────────────────────────────────────────── -->
<section class="relative mb-12 overflow-hidden rounded-2xl">
	<!-- Fondo con gradiente y patrón de campo -->
	<div class="hero-bg absolute inset-0 rounded-2xl"></div>
	<!-- Líneas decorativas SVG -->
	<div class="absolute inset-0 opacity-5 pointer-events-none">
		<svg width="100%" height="100%" viewBox="0 0 800 340" preserveAspectRatio="xMidYMid slice" xmlns="http://www.w3.org/2000/svg">
			<circle cx="400" cy="170" r="80" fill="none" stroke="white" stroke-width="2"/>
			<line x1="400" y1="0" x2="400" y2="340" stroke="white" stroke-width="1.5"/>
			<rect x="0" y="85" width="90" height="170" fill="none" stroke="white" stroke-width="1.5"/>
			<rect x="0" y="125" width="35" height="90" fill="none" stroke="white" stroke-width="1.5"/>
			<rect x="710" y="85" width="90" height="170" fill="none" stroke="white" stroke-width="1.5"/>
			<rect x="765" y="125" width="35" height="90" fill="none" stroke="white" stroke-width="1.5"/>
			<rect x="2" y="2" width="796" height="336" fill="none" stroke="white" stroke-width="1.5" rx="4"/>
		</svg>
	</div>

	<!-- Contenido del hero -->
	<div class="relative z-10 px-6 py-16 sm:px-10 sm:py-20 text-center animate-fade-in-up">
		<!-- Badge de estado del servidor -->
		<div class="inline-flex items-center gap-2 px-3.5 py-1.5 rounded-full text-xs font-semibold mb-6 border"
			style="background: rgba(8,12,20,0.7); border-color: rgba(148,163,184,0.15);">
			{#if apiStatus === 'checking'}
				<span class="w-1.5 h-1.5 rounded-full bg-amber-400 animate-pulse shrink-0"></span>
				<span class="text-slate-400">Conectando...</span>
			{:else if apiStatus === 'ok'}
				<span class="w-1.5 h-1.5 rounded-full bg-emerald-400 shrink-0" style="animation: pulse-green 2s ease infinite;"></span>
				<span class="text-emerald-400">Sistema en línea</span>
			{:else}
				<span class="w-1.5 h-1.5 rounded-full bg-red-400 shrink-0"></span>
				<span class="text-red-400">Servidor no disponible</span>
			{/if}
		</div>

		<h1 class="text-5xl sm:text-6xl lg:text-7xl font-black text-white leading-none mb-4 tracking-tight font-display">
			Torneo <span style="color: var(--accent-green); text-shadow: 0 0 40px rgba(16,185,129,0.4);">Hub</span>
		</h1>
		<p class="text-slate-400 text-base sm:text-lg max-w-lg mx-auto mb-10 leading-relaxed">
			Gestión profesional de torneos de fútbol.<br class="hidden sm:block"/>
			Fixture, resultados y posiciones en tiempo real.
		</p>

		<!-- Estadísticas del torneo -->
		{#if stats.teams !== null}
			<div class="flex flex-wrap items-center justify-center gap-4 sm:gap-8">
				<div class="stat-chip">
					<span class="stat-num">{stats.teams}</span>
					<span class="stat-label">Equipos</span>
				</div>
				<div class="stat-divider"></div>
				<div class="stat-chip">
					<span class="stat-num">{stats.matches}</span>
					<span class="stat-label">Partidos jugados</span>
				</div>
				<div class="stat-divider"></div>
				<div class="stat-chip">
					<span class="stat-num">{stats.goals}</span>
					<span class="stat-label">Goles totales</span>
				</div>
				{#if stats.live > 0}
					<div class="stat-divider"></div>
					<div class="stat-chip">
						<span class="stat-num" style="color: #34d399; display:flex; align-items:center; gap:0.3rem;">
							<span class="live-dot"></span>{stats.live}
						</span>
						<span class="stat-label">En juego ahora</span>
					</div>
				{/if}
			</div>
		{/if}
	</div>
</section>

<!-- ── CARDS DE ACCESO RÁPIDO ───────────────────────────────────────────────── -->
<section>
	<p class="section-label mb-5">Acceso rápido</p>
	<div class="grid grid-cols-1 sm:grid-cols-3 gap-4">
		{#each navCards as card, i}
			<a
				href={card.href}
				class="glass-card p-6 flex flex-col gap-5 group nav-card animate-fade-in-up"
				style="animation-delay: {i * 0.08}s; --card-accent: {card.accent};"
			>
				<!-- Icono -->
				<div class="w-12 h-12 rounded-xl flex items-center justify-center transition-colors"
					style="background: {card.accentBg}; border: 1px solid {card.accentBorder}; color: {card.accent};">
					{@html card.icon}
				</div>

				<!-- Texto -->
				<div class="flex-1">
					<div class="flex items-center gap-2 mb-1.5">
						<h2 class="text-white font-bold text-lg leading-tight">{card.title}</h2>
						{#if card.badge}
							<span class="text-xs px-2 py-0.5 rounded-full font-semibold"
								style="background: rgba(245,158,11,0.15); color: #fbbf24;">
								{card.badge}
							</span>
						{/if}
					</div>
					<p class="text-slate-400 text-sm leading-relaxed">{card.description}</p>
				</div>

				<!-- CTA -->
				<div class="flex items-center gap-1 text-xs font-semibold transition-colors"
					style="color: {card.accent};">
					{card.cta}
				</div>
			</a>
		{/each}
	</div>
</section>

<style>
	/* Hero background */
	.hero-bg {
		background: linear-gradient(135deg, #071a0e 0%, #0a1628 40%, #080c14 100%);
		border: 1px solid rgba(16, 185, 129, 0.15);
	}

	/* Estadísticas del torneo */
	.stat-chip {
		display: flex;
		flex-direction: column;
		align-items: center;
		gap: 0.15rem;
	}
	.stat-num {
		font-family: 'Space Grotesk', sans-serif;
		font-size: 2rem;
		font-weight: 800;
		color: white;
		line-height: 1;
	}
	.stat-label {
		font-size: 0.7rem;
		font-weight: 600;
		letter-spacing: 0.07em;
		text-transform: uppercase;
		color: #64748b;
	}
	.stat-divider {
		width: 1px;
		height: 2.5rem;
		background: rgba(148, 163, 184, 0.12);
	}

	/* Nav cards con acento al hover */
	.nav-card {
		position: relative;
		overflow: hidden;
		transition: border-color 0.2s ease, transform 0.15s ease, box-shadow 0.2s ease;
	}
	.nav-card::after {
		content: '';
		position: absolute;
		inset: 0;
		border-radius: 1rem;
		opacity: 0;
		transition: opacity 0.25s ease;
		box-shadow: inset 0 0 0 1px var(--card-accent, #10b981);
	}
	.nav-card:hover::after { opacity: 0.35; }
	.nav-card:hover { transform: translateY(-2px); box-shadow: 0 8px 30px rgba(0,0,0,0.25); }
</style>
