<script>
	/**
	 * routes/fixture/+page.svelte — Página de Fixture (/fixture)
	 *
	 * ¿Qué muestra?
	 * - Selector de jornadas (Jornada 1, Jornada 2, etc.)
	 * - Tarjetas de partidos de la jornada seleccionada
	 * - Estado de cada partido (Programado / En Juego / Finalizado / Cancelado)
	 */
	import { onMount } from 'svelte';
	import { fixtureApi, teamsApi } from '$lib/api/client';
	import SoccerPitch from '$lib/components/SoccerPitch.svelte';
	import BasketballCourt from '$lib/components/BasketballCourt.svelte';
	import VolleyballCourt from '$lib/components/VolleyballCourt.svelte';
	import { toast } from '$lib/stores/toast';

	const TOURNAMENT_ID = 1;

	let rounds = $state([]);
	let teamsMap = $state({});
	let selectedRound = $state(1);
	let loading = $state(true);
	let error = $state(null);
	let pitchModalTeam = $state(null);
	let now = $state(Date.now());
	let tickInterval = null;

	function getMatchTimer(match) {
		if ((match.status ?? '').toLowerCase() !== 'live') return null;
		if (!match.started_at) return '00:00';
		const iso = match.started_at.endsWith('Z') ? match.started_at : match.started_at + 'Z';
		const startedMs = new Date(iso).getTime();
		const totalSec = Math.max(0, Math.floor((now - startedMs) / 1000));
		const m = Math.floor(totalSec / 60);
		const s = totalSec % 60;
		return `${String(m).padStart(2, '0')}:${String(s).padStart(2, '0')}`;
	}
	let selectedSport = $state('all'); // 'all' | 'football' | 'basketball'
	function getMatchSport(match) {
		return match.sport || teamsMap[match.home_team_id]?.sport || 'football';
	}
	let filteredMatches = $derived(
		selectedSport === 'all'
			? currentMatches
			: currentMatches.filter((m) => getMatchSport(m) === selectedSport)
	);

	async function showTeamPitch(teamId) {
		let t = teamsMap[teamId];
		if (!t) return;
		if (!t.players || t.players.length === 0) {
			try {
				const full = await teamsApi.get(teamId);
				teamsMap[teamId] = full;
				t = full;
			} catch (_) {}
		}
		pitchModalTeam = t;
	}

	// Partidos de la jornada seleccionada (soporta tanto matchday como round)
	let currentMatches = $derived(
		rounds.find((r) => (r.matchday ?? r.round) === selectedRound)?.matches ?? []
	);

	onMount(async () => {
		try {
			const [fixtureData, teamsList] = await Promise.all([
				fixtureApi.get(TOURNAMENT_ID).catch(() => ({ rounds: [] })),
				teamsApi.list(TOURNAMENT_ID, true).catch(() => [])
			]);

			const map = {};
			for (const t of teamsList) {
				map[t.id] = t;
			}
			teamsMap = map;

			rounds = fixtureData.rounds ?? [];
			if (rounds.length > 0) {
				selectedRound = rounds[0].matchday ?? rounds[0].round ?? 1;
			}
		} catch (e) {
			error = e.message;
			toast.error('No se pudo cargar el fixture.');
		} finally {
			loading = false;
		}
	});

	// Configuración visual por estado de partido (claves en minúscula para coincidir con la API)
	const statusConfig = {
		scheduled:   { label: 'Programado',     badgeClass: 'badge-scheduled',   icon: '🕐' },
		live:        { label: 'En Juego (LIVE)',badgeClass: 'badge-in-progress', icon: '⚽' },
		in_progress: { label: 'En Juego',       badgeClass: 'badge-in-progress', icon: '⚽' },
		finished:    { label: 'Finalizado',     badgeClass: 'badge-finished',    icon: '✅' },
		cancelled:   { label: 'Cancelado',      badgeClass: 'badge-cancelled',   icon: '❌' },
		postponed:   { label: 'Pospuesto',      badgeClass: 'badge-scheduled',   icon: '⏸️' }
	};

	function getStatus(rawStatus) {
		const key = (rawStatus ?? 'scheduled').toLowerCase();
		return statusConfig[key] ?? statusConfig.scheduled;
	}

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
			El fixture se puede generar desde la <a href="/mesa-control" class="text-emerald-400 underline">Mesa de Control</a>.
		</p>
	</div>

<!-- ── Sin fixture generado ──────────────────────────────────────────────── -->
{:else if rounds.length === 0}
	<div class="glass-card p-12 text-center animate-fade-in-up">
		<div class="text-5xl mb-4">📅</div>
		<h2 class="text-xl font-bold text-white mb-2">Fixture no generado</h2>
		<p class="text-slate-400 text-sm mb-4">
			El fixture se genera automáticamente una vez que los equipos estén inscritos.
		</p>
		<a
			href="/mesa-control"
			class="inline-flex items-center gap-2 px-5 py-2.5 rounded-xl font-bold text-white bg-emerald-600 hover:bg-emerald-500 transition shadow-lg"
		>
			<span>🎮</span>
			<span>Ir a Mesa de Control para Generar Fixture</span>
		</a>
	</div>

<!-- ── Fixture con jornadas ───────────────────────────────────────────────── -->
{:else}
	<!-- ── Filtro por Deporte ────────────────────────────────────────────────── -->
	<div class="flex items-center gap-2 mb-6 p-1.5 bg-slate-900/90 rounded-2xl border border-slate-800 w-fit backdrop-blur-sm shadow-xl">
		<button
			type="button"
			onclick={() => (selectedSport = 'all')}
			class="px-4 py-2 rounded-xl text-xs font-bold transition-all flex items-center gap-2 {selectedSport === 'all' ? 'bg-slate-700 text-white shadow-md' : 'text-slate-400 hover:text-white'}"
		>
			<span>🌐</span>
			<span>Todos</span>
		</button>
		<button
			type="button"
			onclick={() => (selectedSport = 'football')}
			class="px-4 py-2 rounded-xl text-xs font-bold transition-all flex items-center gap-2 {selectedSport === 'football' ? 'bg-emerald-600 text-white shadow-md shadow-emerald-950/40' : 'text-slate-400 hover:text-white'}"
		>
			<span>⚽</span>
			<span>Fútbol</span>
		</button>
		<button
			type="button"
			onclick={() => (selectedSport = 'basketball')}
			class="px-4 py-2 rounded-xl text-xs font-bold transition-all flex items-center gap-2 {selectedSport === 'basketball' ? 'bg-amber-600 text-white shadow-md shadow-amber-950/40' : 'text-slate-400 hover:text-white'}"
		>
			<span>🏀</span>
			<span>Básquetbol</span>
		</button>
	</div>

	<!-- Selector de jornadas -->
	<div class="flex flex-wrap gap-2 mb-6">
		{#each rounds as r}
			{@const mday = r.matchday ?? r.round ?? 1}
			<button
				class="px-4 py-2 rounded-lg text-sm font-semibold transition-colors {selectedRound === mday
					? 'bg-emerald-600 text-white shadow-md shadow-emerald-950/50'
					: 'bg-slate-800/80 text-slate-300 hover:text-white hover:bg-slate-700 border border-slate-700/60'}"
				onclick={() => (selectedRound = mday)}
			>
				Jornada {mday}
			</button>
		{/each}
	</div>

	<!-- Partidos de la jornada seleccionada -->
	<div class="flex flex-col gap-3">
		{#if filteredMatches.length === 0}
			<div class="col-span-full glass-card p-10 text-center">
				<p class="text-slate-400 text-sm">No hay partidos de {selectedSport === 'basketball' ? 'básquetbol' : selectedSport === 'volleyball' ? 'vóley' : 'fútbol'} en la jornada {selectedRound}.</p>
			</div>
		{/if}
		{#each filteredMatches as match}
			{@const status = getStatus(match.status)}
			<div class="glass-card p-5 flex flex-col sm:flex-row items-center gap-4">
				<!-- Equipo local -->
				<div class="flex-1 text-center sm:text-right">
					<p class="font-bold text-white text-lg leading-tight">
						{teamsMap[match.home_team_id]?.name ?? `Equipo #${match.home_team_id}`}
					</p>
					<p class="text-xs text-slate-500 font-mono">
						{teamsMap[match.home_team_id]?.short_name ?? 'LOC'} • Local
					</p>
					<button type="button" onclick={() => showTeamPitch(match.home_team_id)} class="mt-1 text-[11px] text-slate-400 hover:text-emerald-400 transition inline-flex items-center gap-1 font-semibold">
						<span>🏟️</span> Cancha Táctica
					</button>
				</div>

				<!-- Marcador / Estado -->
				<div class="flex flex-col items-center gap-1.5 px-4 min-w-[130px]">
					{#if match.home_score !== null && match.away_score !== null}
						<div class="text-2xl font-black text-white font-mono">
							{match.home_score} – {match.away_score}
						</div>
					{:else}
						<div class="text-xl font-bold text-slate-500">VS</div>
					{/if}
					<span class="text-xs px-2.5 py-0.5 rounded-full font-bold {status.badgeClass} flex items-center gap-1">
						{#if (match.status ?? '').toLowerCase() === 'live'}
							<span class="w-1.5 h-1.5 rounded-full bg-emerald-400 animate-ping"></span>
						{/if}
						{status.icon} {status.label}
					</span>
					{#if match.scheduled_at}
						<p class="text-xs text-slate-500 mt-1">{formatDate(match.scheduled_at)}</p>
					{/if}
				</div>

				<!-- Equipo visitante -->
				<div class="flex-1 text-center sm:text-left">
					<p class="font-bold text-white text-lg leading-tight">
						{teamsMap[match.away_team_id]?.name ?? `Equipo #${match.away_team_id}`}
					</p>
					<p class="text-xs text-slate-500 font-mono">
						{teamsMap[match.away_team_id]?.short_name ?? 'VIS'} • Visitante
					</p>
					<button type="button" onclick={() => showTeamPitch(match.away_team_id)} class="mt-1 text-[11px] text-slate-400 hover:text-emerald-400 transition inline-flex items-center gap-1 font-semibold">
						<span>🏟️</span> Cancha Táctica
					</button>
				</div>
			</div>
		{/each}
	</div>
{/if}

<!-- MODAL DE CANCHA TÁCTICA -->
{#if pitchModalTeam}
	<div
		class="fixed inset-0 z-50 flex items-center justify-center p-4 bg-slate-950/85 backdrop-blur-sm animate-fade-in"
		role="dialog"
		aria-modal="true"
		onclick={(e) => e.target === e.currentTarget && (pitchModalTeam = null)}
	>
		<div class="glass-card w-full max-w-2xl max-h-[90vh] overflow-y-auto p-5 rounded-2xl border border-slate-700 shadow-2xl flex flex-col gap-4">
			<div class="flex items-center justify-between border-b border-slate-800 pb-3">
				<div>
					<h3 class="text-base font-bold text-white leading-tight">{pitchModalTeam.name}</h3>
					<p class="text-xs text-slate-400 font-mono">Alineación y Plantilla en Cancha</p>
				</div>
				<button
					type="button"
					onclick={() => (pitchModalTeam = null)}
					class="text-slate-400 hover:text-white p-1 rounded-lg text-lg"
				>
					✕
				</button>
			</div>

			<SoccerPitch
				players={pitchModalTeam.players || []}
				interactive={false}
				teamName={pitchModalTeam.name}
				teamColor="#10b981"
			/>

			<div class="flex justify-end pt-2 border-t border-slate-800">
				<button
					type="button"
					onclick={() => (pitchModalTeam = null)}
					class="px-4 py-2 text-xs font-semibold rounded-lg bg-slate-800 text-slate-300 hover:text-white transition"
				>
					Cerrar
				</button>
			</div>
		</div>
	</div>
{/if}
