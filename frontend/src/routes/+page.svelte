<script>
	/**
	 * routes/+page.svelte — Página de Inicio (/)
	 *
	 * ¿Qué muestra?
	 * - Hero section con el nombre del torneo
	 * - 4 tarjetas que llevan a las secciones principales
	 * - Estado de conexión al backend (ping al health check)
	 *
	 * ¿Qué llama al backend?
	 * - GET /api/v1/health → para verificar que el servidor está vivo
	 */
	import { onMount } from 'svelte';
	import { healthApi } from '$lib/api/client';

	let apiStatus = $state('checking'); // 'checking' | 'ok' | 'error'

	// Al cargar la página, verificamos que el backend responde
	onMount(async () => {
		try {
			await healthApi.check();
			apiStatus = 'ok';
		} catch {
			apiStatus = 'error';
		}
	});

	// Tarjetas de acceso rápido a las secciones
	const sections = [
		{
			href: '/equipos',
			icon: '👕',
			title: 'Equipos',
			description: 'Consulta todos los clubes y plantillas registradas en el torneo.',
			color: 'from-emerald-500/20 to-teal-500/10',
			border: 'hover:border-emerald-500/40'
		},
		{
			href: '/fixture',
			icon: '📅',
			title: 'Fixture',
			description: 'Calendario completo de partidos organizado por jornada.',
			color: 'from-blue-500/20 to-indigo-500/10',
			border: 'hover:border-blue-500/40'
		},
		{
			href: '/posiciones',
			icon: '📊',
			title: 'Posiciones',
			description: 'Tabla de clasificación con puntos, goles y diferencia de gol.',
			color: 'from-amber-500/20 to-yellow-500/10',
			border: 'hover:border-amber-500/40'
		},
		{
			href: '/mesa-control',
			icon: '🎮',
			title: 'Mesa de Control',
			description: 'Panel de arbitraje para registrar resultados en tiempo real.',
			color: 'from-purple-500/20 to-violet-500/10',
			border: 'hover:border-purple-500/40',
			badge: 'Próximamente'
		}
	];
</script>

<svelte:head>
	<title>Inicio — Nombre-Creativo Torneos</title>
	<meta name="description" content="Plataforma de gestión de torneos deportivos. Fixture, posiciones y mesa de control en tiempo real." />
</svelte:head>

<!-- ── Hero Section ────────────────────────────────────────────────────────── -->
<section class="relative text-center py-20 mb-12 overflow-hidden rounded-2xl" style="background: linear-gradient(135deg, #0f172a 0%, #1a2a1a 50%, #0f172a 100%);">

	<!-- Efecto de fondo decorativo -->
	<div class="absolute inset-0 opacity-10" style="background-image: radial-gradient(circle at 20% 50%, #22c55e 0%, transparent 50%), radial-gradient(circle at 80% 50%, #f59e0b 0%, transparent 50%);"></div>

	<div class="relative z-10 animate-fade-in-up">
		<div class="text-6xl mb-4">⚽🏆</div>
		<h1 class="text-4xl sm:text-5xl font-black mb-4 text-white">
			Nombre<span style="color: var(--accent-green);">-Creativo</span>
		</h1>
		<p class="text-lg text-slate-400 max-w-xl mx-auto mb-8">
			La plataforma para gestionar tu torneo: equipos, fixture, resultados y posiciones en un solo lugar.
		</p>

		<!-- Indicador de estado del backend -->
		<div class="inline-flex items-center gap-2 px-4 py-2 rounded-full text-sm font-medium"
			style="background: rgba(30,41,59,0.8); border: 1px solid var(--border-color);">
			{#if apiStatus === 'checking'}
				<span class="w-2 h-2 rounded-full bg-yellow-400 animate-pulse"></span>
				<span class="text-slate-400">Verificando servidor...</span>
			{:else if apiStatus === 'ok'}
				<span class="w-2 h-2 rounded-full bg-emerald-400 animate-pulse"></span>
				<span class="text-emerald-400">Servidor en línea</span>
			{:else}
				<span class="w-2 h-2 rounded-full bg-red-400"></span>
				<span class="text-red-400">Servidor no disponible</span>
			{/if}
		</div>
	</div>
</section>

<!-- ── Tarjetas de navegación ─────────────────────────────────────────────── -->
<section>
	<h2 class="text-xl font-bold text-slate-300 mb-6">Acceso rápido</h2>
	<div class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
		{#each sections as s, i}
			<a
				href={s.href}
				class="glass-card p-6 flex flex-col gap-3 group animate-fade-in-up {s.border}"
				style="animation-delay: {i * 0.08}s; border: 1px solid var(--border-color);"
			>
				<div class="text-3xl">{s.icon}</div>
				<div>
					<div class="flex items-center gap-2">
						<h3 class="font-bold text-white text-lg">{s.title}</h3>
						{#if s.badge}
							<span class="text-xs px-2 py-0.5 rounded-full bg-purple-500/20 text-purple-300 font-medium">{s.badge}</span>
						{/if}
					</div>
					<p class="text-sm text-slate-400 mt-1 leading-relaxed">{s.description}</p>
				</div>
				<div class="flex items-center gap-1 text-xs font-medium text-slate-500 group-hover:text-emerald-400 transition mt-auto">
					Ver más →
				</div>
			</a>
		{/each}
	</div>
</section>
