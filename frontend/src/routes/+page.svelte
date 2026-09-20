<script>
	/**
	 * routes/+page.svelte — Página de Inicio Multi-Deporte (/)
	 *
	 * - Hero section multideportivo de alta gama con estética Sofascore/ESPN
	 * - Métricas en tiempo real de equipos, partidos, puntos y disciplinas
	 * - Showcase de las 4 disciplinas oficiales con identidades visuales únicas
	 * - Cards de acceso rápido enriquecidas con micro-interacciones
	 */
	import { onMount } from 'svelte';
	import { healthApi, teamsApi, matchesApi } from '$lib/api/client';

	const TOURNAMENT_ID = 1;

	let apiStatus = $state('checking');
	let stats = $state({ teams: null, matches: null, goals: null, live: 0 });
	let sportCounts = $state({
		football: 0,
		basketball: 0,
		volleyball: 0,
		underwater_chess: 0
	});

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

			const counts = { football: 0, basketball: 0, volleyball: 0, underwater_chess: 0, aura_battle: 0, sperm_triathlon: 0, tire_race: 0, mosquito_marathon: 0 };
			for (const t of teamsList) {
				const sp = t.sport || 'football';
				if (counts[sp] !== undefined) counts[sp]++;
				else counts.football++;
			}
			sportCounts = counts;

			const finishedMatches = matchList.filter(
				(m) => (m.status ?? '').toLowerCase() === 'finished'
			);
			const totalPoints = finishedMatches.reduce(
				(acc, m) => acc + (m.home_score ?? 0) + (m.away_score ?? 0),
				0
			);
			const liveCount = matchList.filter(
				(m) => (m.status ?? '').toLowerCase() === 'live'
			).length;

			stats = {
				teams: teamsList.length,
				matches: finishedMatches.length,
				goals: totalPoints,
				live: liveCount
			};
		} catch {
			// stats permanecen null
		}
	});

	const sports = [
		{
			id: 'football',
			name: 'Fútbol',
			category: 'Césped 11v11',
			icon: '⚽',
			accent: '#10b981',
			accentBg: 'rgba(16, 185, 129, 0.12)',
			border: 'rgba(16, 185, 129, 0.3)',
			desc: 'Cancha completa, táctica 11v11, tabla de posiciones y goles.',
			tag: 'Oficial'
		},
		{
			id: 'basketball',
			name: 'Básquetbol',
			category: 'Parquet FIBA',
			icon: '🏀',
			accent: '#f59e0b',
			accentBg: 'rgba(245, 158, 11, 0.12)',
			border: 'rgba(245, 158, 11, 0.3)',
			desc: 'Quintetos titulares con zona rival delimitada y tanteador dinámico.',
			tag: 'Oficial'
		},
		{
			id: 'volleyball',
			name: 'Voleibol',
			category: 'Red Oficial 6v6',
			icon: '🏐',
			accent: '#38bdf8',
			accentBg: 'rgba(56, 189, 248, 0.12)',
			border: 'rgba(56, 189, 248, 0.3)',
			desc: 'Red central visible, rotación de 6 posiciones y puntuación por sets.',
			tag: 'Oficial'
		},
		{
			id: 'underwater_chess',
			name: 'Ajedrez Acuático',
			category: 'Subacuático 8x8',
			icon: '🌊♟️',
			accent: '#a855f7',
			accentBg: 'rgba(168, 85, 247, 0.15)',
			border: 'rgba(168, 85, 247, 0.35)',
			desc: 'Tablero subacuático 8x8, posicionamiento estratégico y tiempos.',
			tag: 'Especial'
		},
		{
			id: 'aura_battle',
			name: 'Batalla de Aura',
			category: 'Cuadrilátero de Asfalto',
			icon: '🕺',
			accent: '#facc15',
			accentBg: 'rgba(250, 204, 21, 0.15)',
			border: 'rgba(250, 204, 21, 0.35)',
			desc: 'Duelo callejero de baile y farmeo de aura con pasos prohibidos en cuadrado de asfalto.',
			tag: 'Urbano'
		},
		{
			id: 'sperm_triathlon',
			name: 'Triatlón Espermatozoide',
			category: 'Carril Celular',
			icon: '🧬',
			accent: '#22d3ee',
			accentBg: 'rgba(34, 211, 238, 0.15)',
			border: 'rgba(34, 211, 238, 0.35)',
			desc: 'Velocidad microscópica, registro en micras (µm) y fertilización meta.',
			tag: 'Micro'
		},
		{
			id: 'tire_race',
			name: 'Carrera de Llantas',
			category: 'Pista Olímpica Naranja',
			icon: '🛞',
			accent: '#fbbf24',
			accentBg: 'rgba(251, 191, 36, 0.15)',
			border: 'rgba(251, 191, 36, 0.35)',
			desc: 'Roles DIR, ROD y FREN en pista olímpica naranja de tartán, rotación y velocidad.',
			tag: 'Velocidad'
		},
		{
			id: 'mosquito_marathon',
			name: 'Maratón de Mosquitos',
			category: 'Radar Nocturno',
			icon: '🦟',
			accent: '#a3e635',
			accentBg: 'rgba(163, 230, 53, 0.15)',
			border: 'rgba(163, 230, 53, 0.35)',
			desc: 'Escuadrón de zancudos PIC, ZUM y EVAS, sigilo en radar y picaduras.',
			tag: 'Nocturno'
		}
	];

	const navCards = [
		{
			href: '/publico',
			icon: `<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" class="w-7 h-7"><circle cx="12" cy="12" r="10"/><circle cx="12" cy="12" r="3"/><line x1="12" y1="2" x2="12" y2="5"/><line x1="12" y1="19" x2="12" y2="22"/><line x1="2" y1="12" x2="5" y2="12"/><line x1="19" y1="12" x2="22" y2="12"/></svg>`,
			title: 'Vista Pública',
			description: 'Fixture en vivo, resultados y tabla de clasificaciones para hinchas y jugadores.',
			accent: '#10b981',
			accentBg: 'rgba(16,185,129,0.08)',
			accentBorder: 'rgba(16,185,129,0.3)',
			badge: null,
			cta: 'Ver fixture y tablas →'
		},
		{
			href: '/equipos',
			icon: `<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" class="w-7 h-7"><path d="M17 21v-2a4 4 0 0 0-4-4H5a4 4 0 0 0-4 4v2"/><circle cx="9" cy="7" r="4"/><path d="M23 21v-2a4 4 0 0 0-3-3.87"/><path d="M16 3.13a4 4 0 0 1 0 7.75"/></svg>`,
			title: 'Directorio de Equipos',
			description: 'Registro de clubes por disciplina, tácticas en cancha interactiva y delegados.',
			accent: '#3b82f6',
			accentBg: 'rgba(59,130,246,0.08)',
			accentBorder: 'rgba(59,130,246,0.3)',
			badge: null,
			cta: 'Ver equipos y canchas →'
		},
		{
			href: '/mesa-control',
			icon: `<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" class="w-7 h-7"><rect x="2" y="3" width="20" height="14" rx="2" ry="2"/><line x1="8" y1="21" x2="16" y2="21"/><line x1="12" y1="17" x2="12" y2="21"/></svg>`,
			title: 'Mesa de Control',
			description: 'Arbitraje táctil en tiempo real: registro de puntos y cronómetro sincronizado instantáneo.',
			accent: '#f59e0b',
			accentBg: 'rgba(245,158,11,0.08)',
			accentBorder: 'rgba(245,158,11,0.3)',
			badge: 'Solo admin',
			cta: 'Ingresar a arbitraje →'
		}
	];
</script>

<svelte:head>
	<title>Torneo Hub — Plataforma Multideportiva</title>
	<meta name="description" content="Plataforma profesional de gestión deportiva multidisciplinaria: Fútbol, Básquetbol, Vóley y Ajedrez Subacuático." />
</svelte:head>

<!-- ── HERO MULTIDEPORTIVO ─────────────────────────────────────────────────── -->
<section class="relative mb-10 overflow-hidden rounded-3xl border border-slate-800 shadow-2xl">
	<!-- Fondo ambiental con gradiente multi-deporte -->
	<div class="hero-bg absolute inset-0 rounded-3xl"></div>
	
	<!-- Resplandores dinámicos ambientales -->
	<div class="absolute -top-32 -left-32 w-80 h-80 rounded-full bg-emerald-500/10 blur-3xl pointer-events-none"></div>
	<div class="absolute -top-32 right-10 w-80 h-80 rounded-full bg-amber-500/10 blur-3xl pointer-events-none"></div>
	<div class="absolute -bottom-32 left-1/3 w-96 h-96 rounded-full bg-purple-500/10 blur-3xl pointer-events-none"></div>

	<!-- Líneas de arena deportiva SVG abstracta -->
	<div class="absolute inset-0 opacity-[0.06] pointer-events-none">
		<svg width="100%" height="100%" viewBox="0 0 900 400" preserveAspectRatio="xMidYMid slice" xmlns="http://www.w3.org/2000/svg">
			<circle cx="450" cy="200" r="120" fill="none" stroke="white" stroke-width="2"/>
			<circle cx="450" cy="200" r="6" fill="white"/>
			<line x1="450" y1="0" x2="450" y2="400" stroke="white" stroke-width="2"/>
			<!-- Arcos y áreas de baloncesto/fútbol -->
			<path d="M 0 100 Q 180 200 0 300" fill="none" stroke="white" stroke-width="2"/>
			<path d="M 900 100 Q 720 200 900 300" fill="none" stroke="white" stroke-width="2"/>
			<!-- Retícula sutil ajedrecística -->
			<line x1="0" y1="50" x2="900" y2="50" stroke="white" stroke-width="1" stroke-dasharray="4 8"/>
			<line x1="0" y1="350" x2="900" y2="350" stroke="white" stroke-width="1" stroke-dasharray="4 8"/>
		</svg>
	</div>

	<!-- Contenido del Hero -->
	<div class="relative z-10 px-5 py-12 sm:px-12 sm:py-20 text-center animate-fade-in-up">
		<!-- Estado de conexión del servidor -->
		<div class="inline-flex items-center gap-2 px-4 py-1.5 rounded-full text-xs font-semibold mb-6 border shadow-inner"
			style="background: rgba(10, 16, 28, 0.85); border-color: rgba(148, 163, 184, 0.18);">
			{#if apiStatus === 'checking'}
				<span class="w-2 h-2 rounded-full bg-amber-400 animate-pulse shrink-0"></span>
				<span class="text-slate-300">Conectando con el servidor...</span>
			{:else if apiStatus === 'ok'}
				<span class="w-2 h-2 rounded-full bg-emerald-400 shrink-0 shadow-sm" style="animation: pulse-green 2s ease infinite;"></span>
				<span class="text-emerald-400 font-medium tracking-wide">Servidor sincronizado · Multi-deporte activo</span>
			{:else}
				<span class="w-2 h-2 rounded-full bg-red-400 shrink-0"></span>
				<span class="text-red-400">Servidor en espera</span>
			{/if}
		</div>

		<!-- Título principal con gradiente moderno -->
		<h1 class="text-4xl sm:text-6xl lg:text-7xl font-black text-white leading-tight mb-4 tracking-tight font-display">
			Torneo <span class="brand-gradient">Hub</span>
		</h1>
		<p class="text-slate-300 text-base sm:text-xl max-w-2xl mx-auto mb-8 font-medium leading-relaxed">
			Plataforma profesional de gestión deportiva multidisciplinaria.<br class="hidden sm:block"/>
			Fixture, arbitraje en vivo y clasificaciones en tiempo real.
		</p>

		<!-- Píldoras de las 4 Disciplinas Oficiales -->
		<div class="flex flex-wrap items-center justify-center gap-2.5 max-w-2xl mx-auto mb-10">
			{#each sports as s}
				<a href="/publico"
					class="inline-flex items-center gap-2 px-3.5 py-1.5 rounded-xl text-xs font-bold transition-all transform hover:scale-105 shadow-sm"
					style="background: {s.accentBg}; border: 1px solid {s.border}; color: {s.accent};">
					<span class="text-sm">{s.icon}</span>
					<span>{s.name}</span>
					{#if sportCounts[s.id] > 0}
						<span class="text-[10px] px-1.5 py-0.2 rounded-full bg-black/40 text-white/90 font-mono">
							{sportCounts[s.id]}
						</span>
					{/if}
				</a>
			{/each}
		</div>

		<!-- Estadísticas Globales del Torneo -->
		{#if stats.teams !== null}
			<div class="flex flex-wrap items-center justify-center gap-4 sm:gap-8 pt-4 border-t border-slate-800/80 max-w-3xl mx-auto">
				<div class="stat-chip">
					<span class="stat-num">{stats.teams}</span>
					<span class="stat-label">Equipos Registrados</span>
				</div>
				<div class="stat-divider hidden sm:block"></div>
				<div class="stat-chip">
					<span class="stat-num">{stats.matches}</span>
					<span class="stat-label">Partidos Disputados</span>
				</div>
				<div class="stat-divider"></div>
				<div class="stat-chip">
					<span class="stat-num text-amber-400">{stats.goals}</span>
					<span class="stat-label">Puntos / Goles Anotados</span>
				</div>
				<div class="stat-divider hidden sm:block"></div>
				<div class="stat-chip">
					<span class="stat-num text-sky-400">4</span>
					<span class="stat-label">Disciplinas Activas</span>
				</div>
				{#if stats.live > 0}
					<div class="stat-divider"></div>
					<div class="stat-chip">
						<span class="stat-num text-emerald-400 flex items-center gap-1.5">
							<span class="w-2.5 h-2.5 rounded-full bg-emerald-400 animate-ping"></span>
							{stats.live}
						</span>
						<span class="stat-label text-emerald-300 font-bold">En Juego Ahora</span>
					</div>
				{/if}
			</div>
		{/if}
	</div>
</section>

<!-- ── SHOWCASE DE DISCIPLINAS ─────────────────────────────────────────────── -->
<section class="mb-12">
	<div class="flex items-center justify-between mb-5">
		<div>
			<p class="section-label mb-1">Disciplinas en Competencia</p>
			<h2 class="text-xl sm:text-2xl font-black text-white tracking-tight">Canchas & Modalidades</h2>
		</div>
		<a href="/publico" class="text-xs font-bold text-emerald-400 hover:text-emerald-300 transition flex items-center gap-1">
			Ver fixture completo →
		</a>
	</div>

	<div class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
		{#each sports as s}
			<a
				href="/publico"
				class="glass-card p-5 rounded-2xl flex flex-col justify-between transition-all duration-200 group hover:-translate-y-1 hover:shadow-xl relative overflow-hidden"
				style="border-top: 3px solid {s.accent};"
			>
				<div>
					<div class="flex items-center justify-between mb-3">
						<div class="w-10 h-10 rounded-xl flex items-center justify-center text-xl shadow-inner"
							style="background: {s.accentBg}; border: 1px solid {s.border};">
							{s.icon}
						</div>
						<span class="text-[10px] uppercase font-black px-2.5 py-0.5 rounded-full tracking-wider"
							style="background: {s.accentBg}; color: {s.accent}; border: 1px solid {s.border};">
							{s.category}
						</span>
					</div>
					<h3 class="text-white font-extrabold text-lg mb-1 group-hover:text-emerald-400 transition-colors">
						{s.name}
					</h3>
					<p class="text-slate-400 text-xs leading-relaxed mb-4">
						{s.desc}
					</p>
				</div>

				<div class="pt-3 border-t border-slate-800/80 flex items-center justify-between text-xs font-bold"
					style="color: {s.accent};">
					<span>{sportCounts[s.id]} equipos registrados</span>
					<span class="group-hover:translate-x-1 transition-transform">→</span>
				</div>
			</a>
		{/each}
	</div>
</section>

<!-- ── CARDS DE ACCESO RÁPIDO ───────────────────────────────────────────────── -->
<section>
	<p class="section-label mb-5">Acceso al Sistema</p>
	<div class="grid grid-cols-1 sm:grid-cols-3 gap-5">
		{#each navCards as card, i}
			<a
				href={card.href}
				class="glass-card p-6 flex flex-col gap-5 group nav-card animate-fade-in-up"
				style="animation-delay: {i * 0.08}s; --card-accent: {card.accent};"
			>
				<!-- Icono con halo brillante -->
				<div class="w-12 h-12 rounded-xl flex items-center justify-center transition-transform group-hover:scale-110"
					style="background: {card.accentBg}; border: 1px solid {card.accentBorder}; color: {card.accent};">
					{@html card.icon}
				</div>

				<!-- Texto descriptivo -->
				<div class="flex-1">
					<div class="flex items-center gap-2 mb-1.5">
						<h2 class="text-white font-bold text-lg leading-tight">{card.title}</h2>
						{#if card.badge}
							<span class="text-xs px-2 py-0.5 rounded-full font-semibold"
								style="background: rgba(245,158,11,0.15); color: #fbbf24; border: 1px solid rgba(245,158,11,0.3);">
								{card.badge}
							</span>
						{/if}
					</div>
					<p class="text-slate-400 text-sm leading-relaxed">{card.description}</p>
				</div>

				<!-- Botón Call to Action -->
				<div class="flex items-center gap-1.5 text-xs font-extrabold transition-colors pt-2 border-t border-slate-800/60"
					style="color: {card.accent};">
					<span>{card.cta}</span>
				</div>
			</a>
		{/each}
	</div>
</section>

<style>
	/* Hero background multideportivo */
	.hero-bg {
		background: radial-gradient(circle at 50% 20%, #0d2319 0%, #0c182a 40%, #070b14 100%);
	}

	.brand-gradient {
		background: linear-gradient(135deg, #10b981 0%, #38bdf8 50%, #a855f7 100%);
		-webkit-background-clip: text;
		-webkit-text-fill-color: transparent;
		filter: drop-shadow(0 0 35px rgba(16, 185, 129, 0.45));
	}

	/* Estadísticas del torneo */
	.stat-chip {
		display: flex;
		flex-direction: column;
		align-items: center;
		gap: 0.2rem;
	}
	.stat-num {
		font-family: 'Space Grotesk', sans-serif;
		font-size: 2.2rem;
		font-weight: 800;
		color: white;
		line-height: 1;
	}
	.stat-label {
		font-size: 0.7rem;
		font-weight: 700;
		letter-spacing: 0.08em;
		text-transform: uppercase;
		color: #64748b;
	}
	.stat-divider {
		width: 1px;
		height: 2.5rem;
		background: rgba(148, 163, 184, 0.15);
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
	.nav-card:hover::after { opacity: 0.4; }
	.nav-card:hover { transform: translateY(-2px); box-shadow: 0 12px 35px rgba(0,0,0,0.35); }
</style>
