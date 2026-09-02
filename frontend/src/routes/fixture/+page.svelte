<script>
	/**
	 * routes/fixture/+page.svelte — Página de Fixture (/fixture)
	 *
	 * ¿Qué muestra?
	 * - Selector de jornadas (Jornada 1, Jornada 2, etc.)
	 * - Tarjetas de partidos de la jornada seleccionada
	 * - Estado de cada partido (Programado / En Juego / Finalizado / Cancelado)
	 *
	 * ¿Qué llama al backend?
	 * - GET /api/v1/tournaments/1/fixture
	 *   Devuelve: { rounds: [ { round: 1, matches: [...] }, ... ] }
	 *   Cada partido: { id, home_team, away_team, status, home_score, away_score, scheduled_at }
	 *
	 * NOTA: Por ahora el tournament_id está fijo en 1.
	 * Cuando haya múltiples torneos se puede agregar un selector.
	 */
	import { onMount } from 'svelte';
	import { fixtureApi } from '$lib/api/client';
	import { toast } from '$lib/stores/toast';

	const TOURNAMENT_ID = 1;

	let rounds = $state([]);
	let selectedRound = $state(1);
	let loading = $state(true);
	let error = $state(null);

	// Partidos de la jornada seleccionada
	let currentMatches = $derived(
		rounds.find((r) => r.round === selectedRound)?.matches ?? []
	);

	onMount(async () => {
		try {
			const data = await fixtureApi.get(TOURNAMENT_ID);
			rounds = data.rounds ?? [];
			if (rounds.length > 0) selectedRound = rounds[0].round;
		} catch (e) {
			error = e.message;
			toast.error('No se pudo cargar el fixture. Verifica que el torneo tenga partidos generados.');
		} finally {
			loading = false;
		}
	});

	// Configuración visual por estado de partido
	const statusConfig = {
		SCHEDULED: {
			label: 'Programado',
			badgeClass: 'badge-scheduled',
			icon: '🕐'
		},
		IN_PROGRESS: {
			label: 'En Juego',
			badgeClass: 'badge-in-progress',
			icon: '⚽'
		},
		FINISHED: {
			label: 'Finalizado',
			badgeClass: 'badge-finished',
			icon: '✅'
		},
		CANCELLED: {
			label: 'Cancelado',
			badgeClass: 'badge-cancelled',
			icon: '❌'
		}
	};

	function formatDate(dateStr) {
		if (!dateStr) return 'Fecha por confirmar';
		return new Date(dateStr).toLocaleDateString('es', {
			weekday: 'short',
			day: 'numeric',
			month: 'short',
			hour: '2-digit',
			minute: '2-digit'
		});
	}
</script>

<svelte:head>
	<title>Fixture — Nombre-Creativo</title>
	<meta name="description" content="Calendario completo de partidos del torneo organizado por jornadas." />
</svelte:head>

<!-- ── Encabezado ─────────────────────────────────────────────────────────── -->
<div class="mb-8 animate-fade-in-up">
	<h1 class="text-3xl font-black text-white flex items-center gap-3">📅 Fixture</h1>
	<p class="text-slate-400 mt-1">Calendario de partidos del torneo</p>
</div>

<!-- ── Estado: cargando ───────────────────────────────────────────────────── -->
{#if loading}
	<div class="flex flex-col gap-4">
		<div class="skeleton h-10 w-full rounded-xl"></div>
		{#each Array(4) as _}
			<div class="skeleton h-24 w-full rounded-xl"></div>
		{/each}
	</div>

<!-- ── Estado: error ─────────────────────────────────────────────────────── -->
{:else if error}
	<div class="glass-card p-8 text-center">
		<div class="text-4xl mb-3">⚠️</div>
		<p class="text-white font-semibold">No se pudo cargar el fixture</p>
		<p class="text-slate-400 text-sm mt-2">{error}</p>
		<p class="text-slate-500 text-xs mt-2">
			El fixture se genera con <code class="bg-slate-800 px-1 rounded">POST /tournaments/1/fixture/generate</code>
		</p>
	</div>

<!-- ── Sin fixture generado ──────────────────────────────────────────────── -->
{:else if rounds.length === 0}
	<div class="glass-card p-12 text-center animate-fade-in-up">
		<div class="text-5xl mb-4">📅</div>
		<h2 class="text-xl font-bold text-white mb-2">Fixture no generado</h2>
		<p class="text-slate-400 text-sm">
			El fixture se genera automáticamente una vez que los equipos estén inscritos.
		</p>
	</div>

<!-- ── Fixture con jornadas ───────────────────────────────────────────────── -->
{:else}
	<!-- Selector de jornadas -->
	<div class="flex flex-wrap gap-2 mb-6 animate-fade-in-up">
		{#each rounds as r}
			<button
				class="px-4 py-2 rounded-lg text-sm font-medium transition-all {selectedRound === r.round
					? 'text-white'
					: 'text-slate-400 hover:text-white hover:bg-white/5'}"
				style={selectedRound === r.round
					? 'background: var(--accent-green); color: #0f172a;'
					: 'background: rgba(30,41,59,0.7); border: 1px solid var(--border-color);'}
				onclick={() => (selectedRound = r.round)}
			>
				Jornada {r.round}
			</button>
		{/each}
	</div>

	<!-- Partidos de la jornada seleccionada -->
	<div class="flex flex-col gap-3">
		{#each currentMatches as match, i}
			{@const status = statusConfig[match.status] ?? statusConfig.SCHEDULED}
			<div
				class="glass-card p-5 flex flex-col sm:flex-row items-center gap-4 animate-fade-in-up"
				style="animation-delay: {i * 0.06}s"
			>
				<!-- Equipo local -->
				<div class="flex-1 text-center sm:text-right">
					<p class="font-bold text-white text-lg leading-tight">
						{match.home_team?.name ?? 'Equipo Local'}
					</p>
					<p class="text-xs text-slate-500">Local</p>
				</div>

				<!-- Marcador / Estado -->
				<div class="flex flex-col items-center gap-1 px-4">
					{#if match.status === 'FINISHED' || match.status === 'IN_PROGRESS'}
						<div class="text-2xl font-black text-white">
							{match.home_score ?? 0} – {match.away_score ?? 0}
						</div>
					{:else}
						<div class="text-xl font-bold text-slate-500">VS</div>
					{/if}
					<span class="text-xs px-2 py-0.5 rounded-full font-medium {status.badgeClass}">
						{status.icon} {status.label}
					</span>
					{#if match.scheduled_at}
						<p class="text-xs text-slate-500 mt-1">{formatDate(match.scheduled_at)}</p>
					{/if}
				</div>

				<!-- Equipo visitante -->
				<div class="flex-1 text-center sm:text-left">
					<p class="font-bold text-white text-lg leading-tight">
						{match.away_team?.name ?? 'Equipo Visitante'}
					</p>
					<p class="text-xs text-slate-500">Visitante</p>
				</div>
			</div>
		{/each}
	</div>
{/if}
