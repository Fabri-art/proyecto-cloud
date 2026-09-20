<script>
	/**
	 * routes/mesa-control/+page.svelte — Panel de Mesa de Control y Arbitraje (NOM-12)
	 *
	 * ★ Ruta protegida con PIN. Solo delegados y árbitros.
	 * ★ Cronómetro calculado desde match.started_at (persiste entre recargas).
	 * ★ Goles se sincronizan al backend en tiempo real con PATCH /matches/{id}/score.
	 * ★ Botón "Eliminar Fixture" (destructivo) + Modal interactivo de Reset/Regenerar.
	 * ★ Flujo automático: si existe fixture, muestra diálogo antes de regenerar.
	 */
	import { onMount, onDestroy } from 'svelte';
	import { goto } from '$app/navigation';
	import { fixtureApi, matchesApi, teamsApi, tournamentsApi } from '$lib/api/client';
	import { auth } from '$lib/stores/auth';
	import { toast } from '$lib/stores/toast';
	import AdminPinModal from '$lib/components/AdminPinModal.svelte';
	import SoccerPitch from '$lib/components/SoccerPitch.svelte';
	import BasketballCourt from '$lib/components/BasketballCourt.svelte';
	import VolleyballCourt from '$lib/components/VolleyballCourt.svelte';
	import UnderwaterChessBoard from '$lib/components/UnderwaterChessBoard.svelte';
	import AuraBattleArena from '$lib/components/AuraBattleArena.svelte';
	import SpermTriathlonTrack from '$lib/components/SpermTriathlonTrack.svelte';
	import TireRaceTrack from '$lib/components/TireRaceTrack.svelte';
	import MosquitoRadar from '$lib/components/MosquitoRadar.svelte';

	const TOURNAMENT_ID = 1;

	// ── Autenticación ───────────────────────────────────────────────────────────
	let isAdmin = $state(false);
	let showPinModal = $state(false);
	const unsub = auth.subscribe((val) => {
		isAdmin = val;
		if (!val) showPinModal = true;
	});

	// ── Estados generales ──────────────────────────────────────────────────────
	let rounds = $state([]);
	let teamsMap = $state({});
	let selectedRound = $state(1);
	let loading = $state(true);
	let generatingFixture = $state(false);
	let regeneratingFixture = $state(false);

	// ── Estados para reset/eliminar fixture ────────────────────────────────────
	let showResetFixtureModal = $state(false);
	let deletingFixture = $state(false);
	/** Número de partidos con resultados registrados (FINISHED o LIVE) en el fixture actual */
	let playedMatchesCount = $state(0);
	/** Número total de equipos activos en el torneo */
	let totalTeamsCount = $state(0);
	
	let tournament = $state(null);

	// Partido actualmente seleccionado para arbitrar
	let activeMatch = $state(null);

	// Marcadores en vivo en la mesa de control
	let liveHomeScore = $state(0);
	let liveAwayScore = $state(0);

	// ── Cronómetro ─────────────────────────────────────────────────────────────
	let timerSeconds = $state(0);
	let timerRunning = $state(false);
	let timerInterval = null;

	// Modal de confirmación de cierre
	let showFinishModal = $state(false);
	let isClosingMatch = $state(false);
	let tacticalTeam = $state(null);
	let now = $state(Date.now());
	let globalTick = null;

	function getMatchTimer(match, _tick) {
		const s = (match.status ?? '').toLowerCase();
		if (s === 'paused') {
			return formatTime(match.elapsed_seconds || 0);
		}
		if (s !== 'live') return null;
		if (!match.started_at) return '00:00';
		const iso = match.started_at.endsWith('Z') ? match.started_at : match.started_at + 'Z';
		const startedMs = new Date(iso).getTime();
		const current = now || Date.now();
		const totalSec = Math.max(0, Math.floor((current - startedMs) / 1000));
		return formatTime(totalSec);
	}
	let selectedSport = $state('all'); // 'all' | 'football' | 'basketball' | 'volleyball'
	function getMatchSport(match) {
		return match.sport || teamsMap[match.home_team_id]?.sport || teamsMap[match.away_team_id]?.sport || 'football';
	}

	function getSportBadge(sport) {
		switch (sport) {
			case 'basketball':
				return { name: 'Básquetbol', icon: '🏀', bg: 'bg-amber-500/15', text: 'text-amber-300', border: 'border-amber-500/30' };
			case 'volleyball':
				return { name: 'Vóley', icon: '🏐', bg: 'bg-sky-500/15', text: 'text-sky-300', border: 'border-sky-500/30' };
			case 'underwater_chess':
				return { name: 'Ajedrez bajo el agua', icon: '♟️', bg: 'bg-cyan-500/15', text: 'text-cyan-300', border: 'border-cyan-500/30' };
			case 'aura_battle':
				return { name: 'Batalla de aura', icon: '🕺', bg: 'bg-yellow-500/15', text: 'text-yellow-300', border: 'border-yellow-500/30' };
			case 'sperm_triathlon':
				return { name: 'Triatlón espermatozoide', icon: '🧬', bg: 'bg-cyan-500/15', text: 'text-cyan-300', border: 'border-cyan-500/30' };
			case 'tire_race':
				return { name: 'Carrera de llantas', icon: '🛞', bg: 'bg-orange-500/15', text: 'text-orange-300', border: 'border-orange-500/30' };
			case 'mosquito_marathon':
				return { name: 'Maratón de mosquitos', icon: '🦟', bg: 'bg-lime-500/15', text: 'text-lime-300', border: 'border-lime-500/30' };
			case 'football':
			default:
				return { name: 'Fútbol', icon: '⚽', bg: 'bg-emerald-500/15', text: 'text-emerald-300', border: 'border-emerald-500/30' };
		}
	}
	let filteredMatches = $derived(
		selectedSport === 'all'
			? currentMatches
			: currentMatches.filter((m) => getMatchSport(m) === selectedSport)
	);

	async function showTeamTactical(teamId) {
		let t = teamsMap[teamId];
		if (!t) return;
		if (!t.players || t.players.length === 0) {
			try {
				const full = await teamsApi.get(teamId);
				teamsMap[teamId] = full;
				t = full;
			} catch (_) {}
		}
		tacticalTeam = t;
	}

	// Configuración visual de badges de estado (claves en minúsculas)
	const statusConfig = {
		scheduled: { label: 'Programado',      badgeClass: 'badge-scheduled',   icon: '🕐' },
		live:      { label: 'EN JUEGO (LIVE)', badgeClass: 'badge-in-progress', icon: '⚽' },
		paused:    { label: 'Pausado',         badgeClass: 'badge-scheduled text-amber-300 border-amber-500/40 bg-amber-500/15', icon: '⏸️' },
		finished:  { label: 'Finalizado',      badgeClass: 'badge-finished',    icon: '🏁' },
		cancelled: { label: 'Cancelado',       badgeClass: 'badge-cancelled',   icon: '❌' },
		postponed: { label: 'Pospuesto',       badgeClass: 'badge-scheduled',   icon: '⏸️' }
	};

	function getStatus(rawStatus) {
		const key = (rawStatus ?? 'scheduled').toLowerCase();
		return statusConfig[key] ?? statusConfig.scheduled;
	}

	// ── Carga inicial de datos ─────────────────────────────────────────────────
	async function loadData() {
		loading = true;
		try {
			const teamsList = await teamsApi.list(TOURNAMENT_ID, true);
			const map = {};
			for (const t of teamsList) map[t.id] = t;
			teamsMap = map;
			totalTeamsCount = teamsList.length;
			tournament = await tournamentsApi.get(TOURNAMENT_ID).catch(() => null);
			await loadFixture();
		} catch (err) {
			toast.error('Error al cargar datos del torneo.');
		} finally {
			loading = false;
		}
	}

	async function loadFixture() {
		try {
			const data = await fixtureApi.get(TOURNAMENT_ID);
			rounds = data.rounds ?? [];

			// Calcular cuántos partidos tienen resultados (para el modal de advertencia)
			playedMatchesCount = rounds
				.flatMap((r) => r.matches ?? [])
				.filter((m) => {
					const s = (m.status ?? '').toLowerCase();
					return s === 'finished' || s === 'live';
				}).length;

			if (rounds.length > 0) {
				const hasSelected = rounds.some((r) => (r.matchday ?? r.round) === selectedRound);
				if (!hasSelected) selectedRound = rounds[0].matchday ?? rounds[0].round ?? 1;
			}
		} catch {
			rounds = [];
			playedMatchesCount = 0;
		}
	}

	// ── Generación inicial del fixture (cuando no existe ninguno) ──────────────
	async function handleGenerateFixture() {
		generatingFixture = true;
		try {
			await fixtureApi.generate(TOURNAMENT_ID);
			toast.success('¡Fixture generado exitosamente!');
			try {
				const teamsList = await teamsApi.list(TOURNAMENT_ID, true);
				const map = {};
				for (const tm of teamsList) map[tm.id] = tm;
				teamsMap = map;
			} catch (_) {}
			await loadFixture();
		} catch (err) {
			toast.error(err.message || 'No se pudo generar el fixture. Verifica tener al menos 2 equipos.');
		} finally {
			generatingFixture = false;
		}
	}

	/**
	 * Al hacer clic en "Regenerar Fixture":
	 * - Si ya hay un fixture activo, abre el modal interactivo en lugar de fallar.
	 * - El modal permite elegir entre "Solo eliminar" o "Eliminar y regenerar".
	 */
	async function handleRegenerateFixture() {
		if (rounds.length === 0) {
			// No hay fixture — generar directamente
			await handleGenerateFixture();
			return;
		}
		// Hay fixture activo → mostrar modal de confirmación
		showResetFixtureModal = true;
	}

	/**
	 * Elimina el fixture actual sin regenerar. Retorna al estado "sin fixture".
	 * Invocado desde el modal de confirmación con el botón "Solo Eliminar".
	 */
	async function handleDeleteOnlyFixture() {
		deletingFixture = true;
		try {
			await fixtureApi.deleteFixture(TOURNAMENT_ID, true);
			rounds = [];
			playedMatchesCount = 0;
			activeMatch = null;
			showResetFixtureModal = false;
			await loadData();
			toast.success('Torneo reiniciado: fixture y equipos eliminados. Listo para registrar nuevos equipos.');
		} catch (err) {
			toast.error(err.message || 'No se pudo eliminar el fixture.');
		} finally {
			deletingFixture = false;
		}
	}

	/**
	 * Resetea el fixture y vacía los equipos, dejando el torneo limpio para nuevos registros.
	 */
	async function handleResetAndRegenerate() {
		regeneratingFixture = true;
		try {
			await fixtureApi.generateForce(TOURNAMENT_ID);
			rounds = [];
			playedMatchesCount = 0;
			activeMatch = null;
			showResetFixtureModal = false;
			try {
				const teamsList = await teamsApi.list(TOURNAMENT_ID, true);
				const map = {};
				for (const tm of teamsList) map[tm.id] = tm;
				teamsMap = map;
			} catch (_) {}
			await loadFixture();
			toast.success('Fixture regenerado exitosamente. Los equipos se han mantenido intactos.');
		} catch (err) {
			toast.error(err.message || 'No se pudo reiniciar el torneo.');
		} finally {
			regeneratingFixture = false;
		}
	}

	// ── Manejo de selección de partido ─────────────────────────────────────────
	function selectMatch(match) {
		pauseTimer();

		const normalStatus = (match.status ?? 'scheduled').toLowerCase();
		activeMatch = { ...match, status: normalStatus };
		liveHomeScore = match.home_score ?? 0;
		liveAwayScore = match.away_score ?? 0;

		// Calcular tiempo real transcurrido según estado
		if (normalStatus === 'live' && match.started_at) {
			const iso = match.started_at.endsWith('Z') ? match.started_at : match.started_at + 'Z';
			const startedMs = new Date(iso).getTime();
			timerSeconds = Math.max(0, Math.floor((Date.now() - startedMs) / 1000));
			startTimer();
		} else if (normalStatus === 'paused') {
			timerSeconds = match.elapsed_seconds || 0;
		} else {
			timerSeconds = 0;
		}
	}

	function closeActiveMatch() {
		pauseTimer();
		activeMatch = null;
		timerSeconds = 0;
	}

	// ── Cronómetro ─────────────────────────────────────────────────────────────
	function startTimer() {
		if (timerRunning) return;
		timerRunning = true;
		timerInterval = setInterval(() => { timerSeconds++; }, 1000);
	}

	function pauseTimer() {
		timerRunning = false;
		if (timerInterval) { clearInterval(timerInterval); timerInterval = null; }
	}

	function resetTimer() {
		pauseTimer();
		timerSeconds = 0;
	}

	function formatTime(s) {
		const m = Math.floor(s / 60);
		const sec = s % 60;
		return `${String(m).padStart(2, '0')}:${String(sec).padStart(2, '0')}`;
	}

	// ── Sincronización en tiempo real y cola de peticiones ─────────────────────
	let scoreUpdateQueue = Promise.resolve();

	function syncScoreToBackend(matchId, homeScore, awayScore) {
		scoreUpdateQueue = scoreUpdateQueue
			.then(async () => {
				await matchesApi.updateScore(matchId, homeScore, awayScore);
			})
			.catch((err) => {
				console.error('Error al sincronizar marcador en backend:', err);
				toast.error('Error al sincronizar marcador: ' + (err.message || ''));
			});
	}

	function broadcastScoreSync(matchId, homeScore, awayScore, status) {
		const payload = {
			matchId,
			home_score: homeScore,
			away_score: awayScore,
			status: status || 'live',
			timestamp: Date.now()
		};
		try {
			if (typeof window !== 'undefined') {
				if ('BroadcastChannel' in window) {
					const channel = new BroadcastChannel('torneo_live_sync');
					channel.postMessage(payload);
					channel.close();
				}
				localStorage.setItem('torneo_score_sync', JSON.stringify(payload));
			}
		} catch (_) {}
	}

	// ── Goles / Puntos táctiles con actualización instantánea y multitab ───────
	async function adjustScore(team, delta) {
		if (!activeMatch || activeMatch.status === 'finished') return;

		if (team === 'home') liveHomeScore = Math.max(0, liveHomeScore + delta);
		else liveAwayScore = Math.max(0, liveAwayScore + delta);

		// Actualizar objeto activeMatch de inmediato
		activeMatch.home_score = liveHomeScore;
		activeMatch.away_score = liveAwayScore;

		// Si el partido estaba programado, pasarlo a LIVE de inmediato
		if (activeMatch.status === 'scheduled') {
			activeMatch.status = 'live';
			startTimer();
			matchesApi.updateStatus(activeMatch.id, 'live').catch(() => {});
		}

		// Actualizar de inmediato en el array de rondas (para reflejar en la lista sin lag)
		for (const r of rounds) {
			const found = (r.matches || []).find((m) => m.id === activeMatch.id);
			if (found) {
				found.home_score = liveHomeScore;
				found.away_score = liveAwayScore;
				found.status = activeMatch.status;
			}
		}
		rounds = [...rounds];

		// Notificar a todas las vistas y pestañas abiertas
		broadcastScoreSync(activeMatch.id, liveHomeScore, liveAwayScore, activeMatch.status);

		// Encolar persistencia garantizada en backend
		syncScoreToBackend(activeMatch.id, liveHomeScore, liveAwayScore);
	}

	// ── Cambio de Estado de Partido ─────────────────────────────────────────────
	async function setMatchStatus(status) {
		if (!activeMatch) return;
		const norm = status.toLowerCase();
		try {
			const elapsedSec = norm === 'paused' ? timerSeconds : (norm === 'live' && activeMatch.elapsed_seconds ? activeMatch.elapsed_seconds : null);
			const updated = await matchesApi.updateStatus(activeMatch.id, norm, elapsedSec);
			activeMatch.status = (updated.status ?? norm).toLowerCase();
			activeMatch.elapsed_seconds = updated.elapsed_seconds ?? (norm === 'paused' ? timerSeconds : activeMatch.elapsed_seconds);
			activeMatch.started_at = updated.started_at ?? activeMatch.started_at;

			// Si acaba de ponerse en LIVE, calcular timer desde started_at
			if (activeMatch.status === 'live') {
				if (updated.started_at) {
					const iso = updated.started_at.endsWith('Z') ? updated.started_at : updated.started_at + 'Z';
					const startedMs = new Date(iso).getTime();
					timerSeconds = Math.max(0, Math.floor((Date.now() - startedMs) / 1000));
				}
				startTimer();
				toast.success('El partido ahora está EN JUEGO (LIVE) ⚽');
			} else if (activeMatch.status === 'paused') {
				pauseTimer();
				timerSeconds = activeMatch.elapsed_seconds || timerSeconds;
				toast.info('Partido en PAUSA ⏸️');
			} else {
				pauseTimer();
				toast.info(`Estado actualizado a: ${statusConfig[activeMatch.status]?.label ?? status}`);
			}
			broadcastScoreSync(activeMatch.id, liveHomeScore, liveAwayScore, activeMatch.status);
			await loadFixture();
		} catch (err) {
			toast.error(err.message || 'Error al cambiar estado del partido.');
		}
	}

	// ── Cierre definitivo del partido ─────────────────────────────────────────
	async function confirmFinishMatch() {
		if (!activeMatch) return;
		isClosingMatch = true;
		try {
			const finished = await matchesApi.registerResult(activeMatch.id, {
				home_score: liveHomeScore,
				away_score: liveAwayScore
			});
			pauseTimer();
			activeMatch = { ...finished, status: 'finished' };
			broadcastScoreSync(activeMatch.id, liveHomeScore, liveAwayScore, 'finished');
			showFinishModal = false;
			toast.success(`¡Partido finalizado! ${liveHomeScore} - ${liveAwayScore}. Posiciones actualizadas.`);
			await loadFixture();
		} catch (err) {
			toast.error(err.message || 'No se pudo finalizar el partido.');
		} finally {
			isClosingMatch = false;
		}
	}

	// Partidos de la jornada seleccionada
	let currentMatches = $derived(
		rounds.find((r) => (r.matchday ?? r.round) === selectedRound)?.matches ?? []
	);

	let hasLiveMatch = $derived(
		rounds.some((r) =>
			(r.matches ?? []).some((m) => (m.status ?? '').toLowerCase() === 'live')
		)
	);

	onMount(() => {
		loadData();
		globalTick = setInterval(() => {
			if (hasLiveMatch || timerMatch) {
				now = Date.now();
			}
		}, 1000);
	});
	onDestroy(() => {
		if (timerInterval) clearInterval(timerInterval);
		if (globalTick) clearInterval(globalTick);
		unsub();
	});
</script>


<svelte:head>
	<title>Mesa de Control — Nombre-Creativo</title>
</svelte:head>

<!-- Modal de PIN (si no es admin) -->
{#if showPinModal && !isAdmin}
	<AdminPinModal
		onSuccess={() => { showPinModal = false; }}
		onCancel={() => goto('/publico')}
	/>
{/if}

{#if isAdmin}
<div class="animate-fade-in-up pb-12">
	<!-- ── ENCABEZADO ──────────────────────────────────────────────────────── -->
	<div class="flex flex-col sm:flex-row sm:items-center justify-between gap-4 mb-8">
		<div>
			<h1 class="text-3xl font-black text-white flex items-center gap-3">
				🎮 Mesa de Control
				<span class="text-xs font-bold px-2 py-1 rounded-md bg-amber-500/15 text-amber-400 border border-amber-500/25">ADMIN</span>
			</h1>
			<p class="text-slate-400 mt-1">Gestiona cronómetro, goles en tiempo real y cierre de partidos.</p>
		</div>
		{#if activeMatch}
			<button onclick={closeActiveMatch} class="inline-flex items-center gap-2 px-4 py-2 rounded-xl text-sm font-semibold bg-slate-800 hover:bg-slate-700 text-slate-300 hover:text-white transition">
				← Volver al Fixture
			</button>
		{/if}
	</div>

	<!-- ── ESTADO: CARGANDO ────────────────────────────────────────────────── -->
	{#if loading}
		<div class="space-y-4">
			<div class="skeleton h-12 w-full rounded-xl"></div>
			<div class="grid grid-cols-1 md:grid-cols-2 gap-4">
				{#each Array(4) as _}
					<div class="skeleton h-32 w-full rounded-xl"></div>
				{/each}
			</div>
		</div>

	<!-- ── CONSOLA DE ARBITRAJE (PARTIDO SELECCIONADO) ────────────────────── -->
	{:else if activeMatch}
		{@const homeTeam = teamsMap[activeMatch.home_team_id]}
		{@const awayTeam = teamsMap[activeMatch.away_team_id]}
		{@const status = getStatus(activeMatch.status)}
		{@const mSport = getMatchSport(activeMatch)}
		{@const sBadge = getSportBadge(mSport)}

		<div class="space-y-6">
			<!-- Barra de Estado -->
			<div class="glass-card p-4 sm:p-6 flex flex-col sm:flex-row items-center justify-between gap-4">
				<div class="flex items-center gap-3">
					<span class="text-xs px-3 py-1.5 rounded-full font-bold {status.badgeClass} flex items-center gap-1.5">
						{#if activeMatch.status === 'live'}
							<span class="w-2 h-2 rounded-full bg-emerald-400 animate-ping"></span>
						{/if}
						{status.icon} {status.label}
					</span>
					<span class="text-xs font-bold px-2.5 py-1 rounded-full {sBadge.bg} {sBadge.text} border {sBadge.border} flex items-center gap-1">
						<span>{sBadge.icon}</span>
						<span>{sBadge.name}</span>
					</span>
					<span class="text-sm font-semibold text-slate-400">Jornada {activeMatch.matchday ?? 1}</span>
				</div>
				{#if activeMatch.status === 'finished'}
					<span class="text-xs font-bold text-emerald-400 px-3 py-1 rounded-lg bg-emerald-950/40 border border-emerald-800/60 flex items-center gap-1">
						✅ Partido Finalizado Oficialmente
					</span>
				{:else if activeMatch.status === 'live'}
					<span class="text-xs font-semibold text-emerald-400/90 flex items-center gap-1.5">
						<span class="w-2 h-2 rounded-full bg-emerald-400 animate-pulse"></span>
						Arbitraje En Vivo
					</span>
				{/if}
			</div>

			<!-- CRONÓMETRO DIGITAL Y CONTROLES DE PARTIDO -->
			<div class="glass-card p-6 text-center flex flex-col items-center gap-3">
				<p class="text-xs font-bold uppercase tracking-wider text-slate-400">Tiempo de Juego</p>
				<div class="text-5xl sm:text-6xl font-black font-mono tracking-widest text-emerald-400">
					{formatTime(timerSeconds)}
				</div>
				{#if activeMatch.status === 'live'}
					<p class="text-xs text-slate-500 italic">Cronómetro sincronizado desde el inicio real del partido</p>
				{/if}

				<!-- Controles principales de arbitraje -->
				<div class="flex flex-wrap items-center justify-center gap-3 mt-2">
					{#if activeMatch.status !== 'live' && activeMatch.status !== 'finished'}
						<button
							onclick={() => setMatchStatus('live')}
							class="px-5 py-2.5 rounded-xl text-sm font-bold bg-emerald-600 hover:bg-emerald-500 text-white transition-all shadow-lg shadow-emerald-950/40 flex items-center gap-2 hover:scale-[1.02] active:scale-[0.98] cursor-pointer"
						>
							{#if activeMatch.status === 'paused'}
								▶️ Reanudar Partido
							{:else}
								▶️ Poner en Juego
							{/if}
						</button>
					{/if}
					{#if activeMatch.status === 'live'}
						<button
							onclick={() => setMatchStatus('paused')}
							class="px-5 py-2.5 rounded-xl text-sm font-bold bg-amber-600/90 hover:bg-amber-600 text-amber-100 hover:text-white transition-all border border-amber-500/50 shadow-md flex items-center gap-2 hover:scale-[1.02] active:scale-[0.98] cursor-pointer"
						>
							⏸️ Pausar
						</button>
					{/if}
					{#if activeMatch.status !== 'finished'}
						<button
							onclick={() => (showFinishModal = true)}
							class="px-5 py-2.5 rounded-xl text-sm font-bold bg-gradient-to-r from-amber-600 to-orange-600 hover:from-amber-500 hover:to-orange-500 text-white transition-all shadow-lg shadow-amber-950/40 flex items-center gap-2 hover:scale-[1.02] active:scale-[0.98] cursor-pointer"
						>
							🏁 Finalizar Partido
						</button>
					{:else}
						<span class="text-xs font-bold text-emerald-400 px-4 py-2 rounded-xl bg-emerald-950/60 border border-emerald-800/60 flex items-center gap-1.5">
							✅ Partido Finalizado Oficialmente
						</span>
					{/if}
				</div>
			</div>

			<!-- Botones de Cancha Táctica -->
			<div class="flex items-center justify-center gap-3 py-1">
				<button type="button" onclick={() => showTeamTactical(activeMatch.home_team_id)} class="px-3.5 py-1.5 rounded-xl text-xs font-bold bg-emerald-950/60 hover:bg-emerald-900/60 text-emerald-300 border border-emerald-700/50 transition flex items-center gap-1.5 shadow-sm">
					<span>🏟️</span> Ver alineación ({homeTeam?.short_name ?? 'Local'})
				</button>
				<button type="button" onclick={() => showTeamTactical(activeMatch.away_team_id)} class="px-3.5 py-1.5 rounded-xl text-xs font-bold bg-blue-950/60 hover:bg-blue-900/60 text-blue-300 border border-blue-700/50 transition flex items-center gap-1.5 shadow-sm">
					<span>🏟️</span> Ver alineación ({awayTeam?.short_name ?? 'Visita'})
				</button>
			</div>

			<!-- MARCADOR TÁCTIL -->
			<div class="grid grid-cols-1 md:grid-cols-2 gap-6">
				<!-- LOCAL -->
				<div class="glass-card p-6 sm:p-8 flex flex-col items-center text-center gap-5 border-t-4 border-emerald-500">
					<div class="flex flex-col items-center gap-2">
						<div class="w-16 h-16 rounded-2xl flex items-center justify-center text-2xl font-black text-white shadow-xl bg-emerald-700">
							{homeTeam?.name?.[0]?.toUpperCase() ?? 'L'}
						</div>
						<div>
							<h2 class="text-2xl font-black text-white">{homeTeam?.name ?? 'Equipo Local'}</h2>
							<p class="text-xs font-mono font-bold text-slate-400 uppercase">{homeTeam?.short_name ?? 'LOC'} · LOCAL</p>
						</div>
					</div>
					<span class="text-7xl sm:text-8xl font-black font-mono text-emerald-400">{liveHomeScore}</span>
					<!-- Controles de anotación deportiva específica (LOCAL) -->
					<div class="flex flex-col gap-2.5 w-full max-w-sm">
						{#if homeTeam?.sport === 'aura_battle'}
							<div class="flex items-center gap-2 w-full">
								<button onclick={() => adjustScore('home', -10)} disabled={activeMatch.status === 'finished' || liveHomeScore <= 0}
									class="px-3 py-3 rounded-xl font-black text-sm bg-slate-800 hover:bg-slate-700 text-slate-300 disabled:opacity-30 transition">-10</button>
								<button onclick={() => adjustScore('home', 10)} disabled={activeMatch.status === 'finished'}
									class="flex-1 py-3 rounded-xl font-black text-base text-black bg-yellow-400 hover:bg-yellow-300 active:scale-95 disabled:opacity-30 transition flex items-center justify-center gap-1.5 shadow-lg shadow-yellow-950/40">
									🕺 +10 PA (Pasito)
								</button>
								<button onclick={() => adjustScore('home', 50)} disabled={activeMatch.status === 'finished'}
									class="px-3.5 py-3 rounded-xl font-black text-sm text-black bg-yellow-500 hover:bg-yellow-400 transition">
									+50
								</button>
							</div>
							<button onclick={() => adjustScore('home', -50)} disabled={activeMatch.status === 'finished' || liveHomeScore <= 0}
								class="w-full py-2 px-3 rounded-lg text-xs font-bold text-red-300 bg-red-950/40 hover:bg-red-900/60 border border-red-500/30 transition flex items-center justify-center gap-1">
								⚠️ Tropiezo en pista (-50 PA)
							</button>
						{:else if homeTeam?.sport === 'sperm_triathlon'}
							<div class="flex items-center gap-2 w-full">
								<button onclick={() => adjustScore('home', -50)} disabled={activeMatch.status === 'finished' || liveHomeScore <= 0}
									class="px-3 py-3 rounded-xl font-black text-sm bg-slate-800 hover:bg-slate-700 text-slate-300 disabled:opacity-30 transition">-50</button>
								<button onclick={() => adjustScore('home', 100)} disabled={activeMatch.status === 'finished'}
									class="flex-1 py-3 rounded-xl font-black text-base text-white bg-cyan-600 hover:bg-cyan-500 active:scale-95 disabled:opacity-30 transition flex items-center justify-center gap-1.5 shadow-lg shadow-cyan-950/40">
									🧬 +100 µm
								</button>
								<button onclick={() => adjustScore('home', 500)} disabled={activeMatch.status === 'finished'}
									class="px-3.5 py-3 rounded-xl font-black text-sm text-white bg-cyan-700 hover:bg-cyan-600 transition">
									+500
								</button>
							</div>
							<button onclick={() => adjustScore('home', -200)} disabled={activeMatch.status === 'finished' || liveHomeScore <= 0}
								class="w-full py-2 px-3 rounded-lg text-xs font-bold text-amber-300 bg-amber-950/40 hover:bg-amber-900/60 border border-amber-500/30 transition flex items-center justify-center gap-1">
								🛑 Frenado viscoso (-200 µm)
							</button>
						{:else if homeTeam?.sport === 'tire_race'}
							<div class="flex items-center gap-2 w-full">
								<button onclick={() => adjustScore('home', -1)} disabled={activeMatch.status === 'finished' || liveHomeScore <= 0}
									class="px-3 py-3 rounded-xl font-black text-sm bg-slate-800 hover:bg-slate-700 text-slate-300 disabled:opacity-30 transition">-1</button>
								<button onclick={() => adjustScore('home', 1)} disabled={activeMatch.status === 'finished'}
									class="flex-1 py-3 rounded-xl font-black text-base text-white bg-amber-600 hover:bg-amber-500 active:scale-95 disabled:opacity-30 transition flex items-center justify-center gap-1.5 shadow-lg shadow-amber-950/40">
									🛞 +1 VLT
								</button>
								<button onclick={() => adjustScore('home', 3)} disabled={activeMatch.status === 'finished'}
									class="px-3.5 py-3 rounded-xl font-black text-sm text-white bg-amber-700 hover:bg-amber-600 transition">
									+3
								</button>
							</div>
							<button onclick={() => adjustScore('home', -1)} disabled={activeMatch.status === 'finished' || liveHomeScore <= 0}
								class="w-full py-2 px-3 rounded-lg text-xs font-bold text-red-300 bg-red-950/40 hover:bg-red-900/60 border border-red-500/30 transition flex items-center justify-center gap-1">
								💥 Pinchazo / Salida carril (-1 VLT)
							</button>
						{:else if homeTeam?.sport === 'mosquito_marathon'}
							<div class="flex items-center gap-2 w-full">
								<button onclick={() => adjustScore('home', -1)} disabled={activeMatch.status === 'finished' || liveHomeScore <= 0}
									class="px-3 py-3 rounded-xl font-black text-sm bg-slate-800 hover:bg-slate-700 text-slate-300 disabled:opacity-30 transition">-1</button>
								<button onclick={() => adjustScore('home', 1)} disabled={activeMatch.status === 'finished'}
									class="flex-1 py-3 rounded-xl font-black text-base text-white bg-lime-600 hover:bg-lime-500 active:scale-95 disabled:opacity-30 transition flex items-center justify-center gap-1.5 shadow-lg shadow-lime-950/40">
									🦟 +1 PC
								</button>
								<button onclick={() => adjustScore('home', 5)} disabled={activeMatch.status === 'finished'}
									class="px-3.5 py-3 rounded-xl font-black text-sm text-white bg-lime-700 hover:bg-lime-600 transition">
									+5
								</button>
							</div>
							<div class="flex items-center gap-2 w-full">
								<button onclick={() => adjustScore('home', 2)} disabled={activeMatch.status === 'finished'}
									class="flex-1 py-1.5 px-2 rounded-lg text-xs font-bold text-emerald-300 bg-emerald-950/40 hover:bg-emerald-900/60 border border-emerald-500/30 transition">
									💨 Manotazo esquivado (+2)
								</button>
								<button onclick={() => adjustScore('home', -1)} disabled={activeMatch.status === 'finished' || liveHomeScore <= 0}
									class="flex-1 py-1.5 px-2 rounded-lg text-xs font-bold text-amber-300 bg-amber-950/40 hover:bg-amber-900/60 border border-amber-500/30 transition">
									🧴 Repelente (-1)
								</button>
							</div>
						{:else}
							<div class="flex items-center gap-3 w-full">
								<button onclick={() => adjustScore('home', -1)} disabled={activeMatch.status === 'finished' || liveHomeScore <= 0}
									class="p-4 rounded-xl font-black text-lg bg-slate-800 hover:bg-slate-700 text-slate-300 disabled:opacity-30 transition">-1</button>
								<button onclick={() => adjustScore('home', 1)} disabled={activeMatch.status === 'finished'}
									class="flex-1 py-4 rounded-xl font-black text-lg text-white bg-emerald-600 hover:bg-emerald-500 active:scale-95 disabled:opacity-30 transition flex items-center justify-center gap-2">
									{homeTeam?.sport === 'basketball' ? '🏀 +1 PTO' : homeTeam?.sport === 'volleyball' ? '🏐 +1 PTO' : homeTeam?.sport === 'underwater_chess' ? '♟️ +1 PTO' : '⚽ +1 GOL'}
								</button>
								{#if homeTeam?.sport === 'basketball'}
									<button onclick={() => adjustScore('home', 2)} disabled={activeMatch.status === 'finished'}
										class="px-3 py-4 rounded-xl font-black text-base text-white bg-amber-600 hover:bg-amber-500 transition">+2</button>
									<button onclick={() => adjustScore('home', 3)} disabled={activeMatch.status === 'finished'}
										class="px-3 py-4 rounded-xl font-black text-base text-white bg-amber-700 hover:bg-amber-600 transition">+3</button>
								{/if}
							</div>
						{/if}
					</div>
				</div>

				<!-- VISITANTE -->
				<div class="glass-card p-6 sm:p-8 flex flex-col items-center text-center gap-5 border-t-4 border-blue-500">
					<div class="flex flex-col items-center gap-2">
						<div class="w-16 h-16 rounded-2xl flex items-center justify-center text-2xl font-black text-white shadow-xl bg-blue-700">
							{awayTeam?.name?.[0]?.toUpperCase() ?? 'V'}
						</div>
						<div>
							<h2 class="text-2xl font-black text-white">{awayTeam?.name ?? 'Equipo Visitante'}</h2>
							<p class="text-xs font-mono font-bold text-slate-400 uppercase">{awayTeam?.short_name ?? 'VIS'} · VISITANTE</p>
						</div>
					</div>
					<span class="text-7xl sm:text-8xl font-black font-mono text-blue-400">{liveAwayScore}</span>
					<!-- Controles de anotación deportiva específica (VISITANTE) -->
					<div class="flex flex-col gap-2.5 w-full max-w-sm">
						{#if awayTeam?.sport === 'aura_battle' || homeTeam?.sport === 'aura_battle'}
							<div class="flex items-center gap-2 w-full">
								<button onclick={() => adjustScore('away', -10)} disabled={activeMatch.status === 'finished' || liveAwayScore <= 0}
									class="px-3 py-3 rounded-xl font-black text-sm bg-slate-800 hover:bg-slate-700 text-slate-300 disabled:opacity-30 transition">-10</button>
								<button onclick={() => adjustScore('away', 10)} disabled={activeMatch.status === 'finished'}
									class="flex-1 py-3 rounded-xl font-black text-base text-black bg-yellow-400 hover:bg-yellow-300 active:scale-95 disabled:opacity-30 transition flex items-center justify-center gap-1.5 shadow-lg shadow-yellow-950/40">
									🕺 +10 PA (Pasito)
								</button>
								<button onclick={() => adjustScore('away', 50)} disabled={activeMatch.status === 'finished'}
									class="px-3.5 py-3 rounded-xl font-black text-sm text-black bg-yellow-500 hover:bg-yellow-400 transition">
									+50
								</button>
							</div>
							<button onclick={() => adjustScore('away', -50)} disabled={activeMatch.status === 'finished' || liveAwayScore <= 0}
								class="w-full py-2 px-3 rounded-lg text-xs font-bold text-red-300 bg-red-950/40 hover:bg-red-900/60 border border-red-500/30 transition flex items-center justify-center gap-1">
								⚠️ Tropiezo en pista (-50 PA)
							</button>
						{:else if awayTeam?.sport === 'sperm_triathlon' || homeTeam?.sport === 'sperm_triathlon'}
							<div class="flex items-center gap-2 w-full">
								<button onclick={() => adjustScore('away', -50)} disabled={activeMatch.status === 'finished' || liveAwayScore <= 0}
									class="px-3 py-3 rounded-xl font-black text-sm bg-slate-800 hover:bg-slate-700 text-slate-300 disabled:opacity-30 transition">-50</button>
								<button onclick={() => adjustScore('away', 100)} disabled={activeMatch.status === 'finished'}
									class="flex-1 py-3 rounded-xl font-black text-base text-white bg-cyan-600 hover:bg-cyan-500 active:scale-95 disabled:opacity-30 transition flex items-center justify-center gap-1.5 shadow-lg shadow-cyan-950/40">
									🧬 +100 µm
								</button>
								<button onclick={() => adjustScore('away', 500)} disabled={activeMatch.status === 'finished'}
									class="px-3.5 py-3 rounded-xl font-black text-sm text-white bg-cyan-700 hover:bg-cyan-600 transition">
									+500
								</button>
							</div>
							<button onclick={() => adjustScore('away', -200)} disabled={activeMatch.status === 'finished' || liveAwayScore <= 0}
								class="w-full py-2 px-3 rounded-lg text-xs font-bold text-amber-300 bg-amber-950/40 hover:bg-amber-900/60 border border-amber-500/30 transition flex items-center justify-center gap-1">
								🛑 Frenado viscoso (-200 µm)
							</button>
						{:else if awayTeam?.sport === 'tire_race' || homeTeam?.sport === 'tire_race'}
							<div class="flex items-center gap-2 w-full">
								<button onclick={() => adjustScore('away', -1)} disabled={activeMatch.status === 'finished' || liveAwayScore <= 0}
									class="px-3 py-3 rounded-xl font-black text-sm bg-slate-800 hover:bg-slate-700 text-slate-300 disabled:opacity-30 transition">-1</button>
								<button onclick={() => adjustScore('away', 1)} disabled={activeMatch.status === 'finished'}
									class="flex-1 py-3 rounded-xl font-black text-base text-white bg-amber-600 hover:bg-amber-500 active:scale-95 disabled:opacity-30 transition flex items-center justify-center gap-1.5 shadow-lg shadow-amber-950/40">
									🛞 +1 VLT
								</button>
								<button onclick={() => adjustScore('away', 3)} disabled={activeMatch.status === 'finished'}
									class="px-3.5 py-3 rounded-xl font-black text-sm text-white bg-amber-700 hover:bg-amber-600 transition">
									+3
								</button>
							</div>
							<button onclick={() => adjustScore('away', -1)} disabled={activeMatch.status === 'finished' || liveAwayScore <= 0}
								class="w-full py-2 px-3 rounded-lg text-xs font-bold text-red-300 bg-red-950/40 hover:bg-red-900/60 border border-red-500/30 transition flex items-center justify-center gap-1">
								💥 Pinchazo / Salida carril (-1 VLT)
							</button>
						{:else if awayTeam?.sport === 'mosquito_marathon' || homeTeam?.sport === 'mosquito_marathon'}
							<div class="flex items-center gap-2 w-full">
								<button onclick={() => adjustScore('away', -1)} disabled={activeMatch.status === 'finished' || liveAwayScore <= 0}
									class="px-3 py-3 rounded-xl font-black text-sm bg-slate-800 hover:bg-slate-700 text-slate-300 disabled:opacity-30 transition">-1</button>
								<button onclick={() => adjustScore('away', 1)} disabled={activeMatch.status === 'finished'}
									class="flex-1 py-3 rounded-xl font-black text-base text-white bg-lime-600 hover:bg-lime-500 active:scale-95 disabled:opacity-30 transition flex items-center justify-center gap-1.5 shadow-lg shadow-lime-950/40">
									🦟 +1 PC
								</button>
								<button onclick={() => adjustScore('away', 5)} disabled={activeMatch.status === 'finished'}
									class="px-3.5 py-3 rounded-xl font-black text-sm text-white bg-lime-700 hover:bg-lime-600 transition">
									+5
								</button>
							</div>
							<div class="flex items-center gap-2 w-full">
								<button onclick={() => adjustScore('away', 2)} disabled={activeMatch.status === 'finished'}
									class="flex-1 py-1.5 px-2 rounded-lg text-xs font-bold text-emerald-300 bg-emerald-950/40 hover:bg-emerald-900/60 border border-emerald-500/30 transition">
									💨 Manotazo esquivado (+2)
								</button>
								<button onclick={() => adjustScore('away', -1)} disabled={activeMatch.status === 'finished' || liveAwayScore <= 0}
									class="flex-1 py-1.5 px-2 rounded-lg text-xs font-bold text-amber-300 bg-amber-950/40 hover:bg-amber-900/60 border border-amber-500/30 transition">
									🧴 Repelente (-1)
								</button>
							</div>
						{:else}
							<div class="flex items-center gap-3 w-full">
								<button onclick={() => adjustScore('away', -1)} disabled={activeMatch.status === 'finished' || liveAwayScore <= 0}
									class="p-4 rounded-xl font-black text-lg bg-slate-800 hover:bg-slate-700 text-slate-300 disabled:opacity-30 transition">-1</button>
								<button onclick={() => adjustScore('away', 1)} disabled={activeMatch.status === 'finished'}
									class="flex-1 py-4 rounded-xl font-black text-lg text-white bg-blue-600 hover:bg-blue-500 active:scale-95 disabled:opacity-30 transition flex items-center justify-center gap-2">
									{homeTeam?.sport === 'basketball' ? '🏀 +1 PTO' : homeTeam?.sport === 'volleyball' ? '🏐 +1 PTO' : homeTeam?.sport === 'underwater_chess' ? '♟️ +1 PTO' : '⚽ +1 GOL'}
								</button>
								{#if awayTeam?.sport === 'basketball' || homeTeam?.sport === 'basketball'}
									<button onclick={() => adjustScore('away', 2)} disabled={activeMatch.status === 'finished'}
										class="px-3 py-4 rounded-xl font-black text-base text-white bg-blue-700 hover:bg-blue-600 transition">+2</button>
									<button onclick={() => adjustScore('away', 3)} disabled={activeMatch.status === 'finished'}
										class="px-3 py-4 rounded-xl font-black text-base text-white bg-blue-800 hover:bg-blue-700 transition">+3</button>
								{/if}
							</div>
						{/if}
					</div>
				</div>
			</div>
		</div>

	<!-- ── SELECTOR DE PARTIDOS ───────────────────────────────────────────── -->
	{:else}
		{#if rounds.length === 0}
			<!-- Sin fixture -->
			<div class="glass-card p-12 text-center max-w-xl mx-auto animate-fade-in-up">
				<div class="text-6xl mb-4">📅</div>
				<h2 class="text-2xl font-bold text-white mb-2">Fixture vacío</h2>
				<p class="text-slate-400 text-sm mb-6">
					{#if totalTeamsCount < 2}
						Actualmente hay {totalTeamsCount} equipo(s) registrado(s). Registra al menos 2 equipos para generar el fixture.
					{:else}
						Hay {totalTeamsCount} equipos listos. Puedes generar el fixture automático ahora.
					{/if}
				</p>
				<div class="flex flex-col sm:flex-row items-center justify-center gap-3">
					{#if totalTeamsCount >= 2}
						<button onclick={handleGenerateFixture} disabled={generatingFixture}
							class="px-6 py-3 rounded-xl font-bold text-white bg-emerald-600 hover:bg-emerald-500 transition flex items-center gap-2 mx-auto sm:mx-0 disabled:opacity-50 shadow-lg shadow-emerald-950/50">
							{#if generatingFixture}
								<span class="w-4 h-4 border-2 border-white border-t-transparent rounded-full animate-spin"></span>
								Generando...
							{:else}
								⚡ Generar Fixture Automático
							{/if}
						</button>
					{/if}
					<a href="/equipos/nuevo" class="px-5 py-3 rounded-xl font-bold text-emerald-400 bg-emerald-500/10 hover:bg-emerald-500/20 border border-emerald-500/30 transition flex items-center justify-center gap-2 text-sm">
						➕ Inscribir Nuevos Equipos
					</a>
				</div>
				
			</div>
		{:else}
			
			<!-- ── Filtro por Deporte ────────────────────────────────────────── -->
			<div class="flex flex-wrap items-center gap-1.5 mb-4 p-1.5 bg-slate-900/90 rounded-xl border border-slate-800 max-w-full">
				<button
					type="button"
					onclick={() => (selectedSport = 'all')}
					class="px-3.5 py-1.5 rounded-lg text-xs font-bold transition {selectedSport === 'all' ? 'bg-slate-700 text-white' : 'text-slate-400 hover:text-white'}"
				>
					🌐 Todos
				</button>
				<button
					type="button"
					onclick={() => (selectedSport = 'football')}
					class="px-3.5 py-1.5 rounded-lg text-xs font-bold transition {selectedSport === 'football' ? 'bg-emerald-600 text-white' : 'text-slate-400 hover:text-white'}"
				>
					⚽ Fútbol
				</button>
				<button
					type="button"
					onclick={() => (selectedSport = 'basketball')}
					class="px-3.5 py-1.5 rounded-lg text-xs font-bold transition {selectedSport === 'basketball' ? 'bg-amber-600 text-white' : 'text-slate-400 hover:text-white'}"
				>
					🏀 Básquetbol
				</button>
		<button
			type="button"
			onclick={() => (selectedSport = 'volleyball')}
			class="px-3.5 py-1.5 rounded-lg text-xs font-bold transition {selectedSport === 'volleyball' ? 'bg-violet-600 text-white' : 'text-slate-400 hover:text-white'}"
		>
			🏐 Vóley
		</button>
		<button
			type="button"
			onclick={() => (selectedSport = 'underwater_chess')}
			class="px-3.5 py-1.5 rounded-lg text-xs font-bold transition {selectedSport === 'underwater_chess' ? 'bg-cyan-600 text-white' : 'text-slate-400 hover:text-white'}"
		>
			♟️ Ajedrez bajo el agua
		</button>
		<button
			type="button"
			onclick={() => (selectedSport = 'aura_battle')}
			class="px-3.5 py-1.5 rounded-lg text-xs font-bold transition {selectedSport === 'aura_battle' ? 'bg-yellow-500 text-black' : 'text-slate-400 hover:text-white'}"
		>
			🕺 Batalla de aura
		</button>
		<button
			type="button"
			onclick={() => (selectedSport = 'sperm_triathlon')}
			class="px-3.5 py-1.5 rounded-lg text-xs font-bold transition {selectedSport === 'sperm_triathlon' ? 'bg-cyan-600 text-white' : 'text-slate-400 hover:text-white'}"
		>
			🧬 Triatlón espermatozoide
		</button>
		<button
			type="button"
			onclick={() => (selectedSport = 'tire_race')}
			class="px-3.5 py-1.5 rounded-lg text-xs font-bold transition {selectedSport === 'tire_race' ? 'bg-orange-600 text-white' : 'text-slate-400 hover:text-white'}"
		>
			🛞 Carrera de llantas
		</button>
		<button
			type="button"
			onclick={() => (selectedSport = 'mosquito_marathon')}
			class="px-3.5 py-1.5 rounded-lg text-xs font-bold transition {selectedSport === 'mosquito_marathon' ? 'bg-lime-600 text-white' : 'text-slate-400 hover:text-white'}"
		>
			🦟 Maratón de mosquitos
		</button>
			</div>
			<div class="flex items-center justify-between gap-3 mb-6 flex-wrap">
				<div class="flex items-center gap-2 overflow-x-auto pb-1">
					{#each rounds as r}
						{@const mday = r.matchday ?? r.round ?? 1}
						<button onclick={() => (selectedRound = mday)}
							class="px-4 py-2 rounded-lg font-semibold text-sm transition-colors whitespace-nowrap {selectedRound === mday
								? 'bg-emerald-600 text-white shadow-md shadow-emerald-950/50'
								: 'bg-slate-800/80 text-slate-300 hover:text-white hover:bg-slate-700 border border-slate-700/60'}">
							Jornada {mday}
						</button>
					{/each}
				</div>
				<!-- Botones de gestión de fixture -->
				<div class="flex items-center gap-2">
					<!-- Eliminar fixture (destructivo, rojo/outline) -->
					<button
						onclick={handleDeleteOnlyFixture}
						disabled={deletingFixture || regeneratingFixture}
						title="Eliminar fixture actual. Se perderán todos los partidos."
						class="px-3 py-2 rounded-lg text-xs font-semibold text-red-400 hover:text-red-300 bg-slate-800/60 border border-red-500/30 hover:border-red-400/60 hover:bg-red-500/10 transition flex items-center gap-1.5 whitespace-nowrap disabled:opacity-40"
					>
						{#if deletingFixture}
							<span class="w-3 h-3 border-2 border-red-400 border-t-transparent rounded-full animate-spin"></span>
						{:else}
							🗑️
						{/if}
						Eliminar Fixture
					</button>
					<!-- Regenerar fixture -->
					<button onclick={handleRegenerateFixture} disabled={regeneratingFixture || deletingFixture}
						class="px-3 py-2 rounded-lg text-xs font-semibold text-slate-400 hover:text-amber-400 bg-slate-800/60 border border-slate-700/50 hover:border-amber-500/30 transition flex items-center gap-1.5 whitespace-nowrap disabled:opacity-50">
						{#if regeneratingFixture}
							<span class="w-3 h-3 border-2 border-amber-400 border-t-transparent rounded-full animate-spin"></span>
						{:else}
							🔄
						{/if}
						Regenerar Fixture
					</button>
				</div>
			</div>

			<!-- Lista de Partidos -->
			<div class="grid grid-cols-1 md:grid-cols-2 gap-4">
				{#if filteredMatches.length === 0}
					<div class="col-span-full glass-card p-8 text-center">
						<p class="text-slate-400 text-sm">No hay partidos registrados para esta disciplina en la jornada seleccionada.</p>
					</div>
				{/if}
				{#each filteredMatches as match}
					{@const homeTeam = teamsMap[match.home_team_id]}
					{@const awayTeam = teamsMap[match.away_team_id]}
					{@const status = getStatus(match.status)}
					{@const mSport = getMatchSport(match)}
					{@const sBadge = getSportBadge(mSport)}
										<div class="glass-card p-5 flex flex-col justify-between gap-4 transition">
						<div class="flex items-center justify-between border-b border-slate-800/80 pb-3">
							<div class="flex items-center gap-2">
								<span class="text-xs font-mono font-bold text-slate-400">#{match.id}</span>
								<span class="text-[11px] font-bold px-2.5 py-0.5 rounded-full {sBadge.bg} {sBadge.text} border {sBadge.border} flex items-center gap-1">
									<span>{sBadge.icon}</span>
									<span>{sBadge.name}</span>
								</span>
							</div>
							<span class="text-xs px-2.5 py-1 rounded-full font-bold {status.badgeClass} flex items-center gap-1.5">
								{#if (match.status ?? '').toLowerCase() === 'live'}
									<span class="w-1.5 h-1.5 rounded-full bg-emerald-400 animate-ping"></span>
									{status.icon} {status.label} · <span class="font-mono font-black text-emerald-300">⏱️ {getMatchTimer(match, now)}</span>
								{:else if (match.status ?? '').toLowerCase() === 'paused'}
									{status.icon} {status.label} · <span class="font-mono font-black text-amber-300">⏱️ {getMatchTimer(match, now)}</span>
								{:else}
									{status.icon} {status.label}
								{/if}
							</span>
						</div>
						<div class="flex items-center justify-between gap-4 py-1">
							<div class="flex-1 text-center sm:text-left">
								<p class="font-bold text-white text-base truncate">{homeTeam?.name ?? `Equipo #${match.home_team_id}`}</p>
								<p class="text-xs text-slate-500 font-mono">{homeTeam?.short_name ?? '---'}</p>
							</div>
							<div class="flex flex-col items-center gap-1 min-w-[80px]">
								{#if (match.status ?? '').toLowerCase() === 'live'}
									<span class="text-[11px] font-mono font-black text-emerald-400 bg-emerald-950/90 px-2.5 py-0.5 rounded-full border border-emerald-500/40 shadow-sm animate-pulse tracking-wide">
										⏱️ {getMatchTimer(match, now)}
									</span>
								{:else if (match.status ?? '').toLowerCase() === 'paused'}
									<span class="text-[11px] font-mono font-black text-amber-400 bg-amber-950/90 px-2.5 py-0.5 rounded-full border border-amber-500/40 shadow-sm tracking-wide">
										⏱️ {getMatchTimer(match, now)}
									</span>
								{/if}
								<div class="px-4 py-1.5 rounded-xl bg-slate-900 border border-slate-800 text-center w-full">
									{#if match.home_score !== null && match.away_score !== null}
										<span class="text-xl font-black font-mono text-emerald-400">{match.home_score} - {match.away_score}</span>
									{:else}
										<span class="text-sm font-bold text-slate-500">VS</span>
									{/if}
								</div>
							</div>
							<div class="flex-1 text-center sm:text-right">
								<p class="font-bold text-white text-base truncate">{awayTeam?.name ?? `Equipo #${match.away_team_id}`}</p>
								<p class="text-xs text-slate-500 font-mono">{awayTeam?.short_name ?? '---'}</p>
							</div>
						</div>
						<button onclick={() => selectMatch(match)}
							class="match-arbitrate-btn cursor-pointer w-full py-2.5 rounded-xl text-xs font-bold transition-all flex items-center justify-center gap-2 hover:scale-[1.01] active:scale-[0.99] {(match.status ?? '').toLowerCase() === 'live'
								? 'bg-emerald-600 hover:bg-emerald-500 text-white shadow-md shadow-emerald-950/40'
								: 'bg-slate-800 hover:bg-slate-700 text-slate-200 border border-slate-700/60'}">
							🎮 {(match.status ?? '').toLowerCase() === 'finished' ? 'Ver Registro' : 'Arbitrar Partido'}
						</button>
					</div>
				{/each}
			</div>
		{/if}
	{/if}
</div>
{/if}

<!-- Modal de Confirmación de Finalización -->
{#if showFinishModal && activeMatch}
	{@const homeTeam = teamsMap[activeMatch.home_team_id]}
	{@const awayTeam = teamsMap[activeMatch.away_team_id]}
	<div class="fixed inset-0 z-50 flex items-center justify-center p-4 bg-slate-950/80" role="dialog" aria-modal="true">
		<div class="glass-card w-full max-w-md p-6 flex flex-col gap-5 border border-slate-700 shadow-2xl">
			<div class="text-center">
				<div class="text-4xl mb-2">🏁</div>
				<h3 class="text-xl font-black text-white">¿Finalizar Partido Oficial?</h3>
				<p class="text-xs text-slate-400 mt-1">Verifica el marcador final antes de cerrar el acta.</p>
			</div>
			<div class="p-4 rounded-xl bg-slate-900 border border-slate-800 text-center">
				<p class="text-xs text-slate-500 uppercase font-semibold mb-2">Resultado Final</p>
				<div class="flex items-center justify-center gap-4 text-xl font-black text-white">
					<span class="truncate">{homeTeam?.name ?? 'Local'}</span>
					<span class="text-3xl font-mono text-emerald-400 px-3 py-1 rounded bg-slate-950 border border-slate-800">{liveHomeScore} - {liveAwayScore}</span>
					<span class="truncate">{awayTeam?.name ?? 'Visitante'}</span>
				</div>
			</div>
			<p class="text-xs text-slate-400 bg-emerald-500/10 border border-emerald-500/20 p-3 rounded-lg">
				ℹ️ Al confirmar, el partido quedará como <strong>FINALIZADO</strong> y la tabla de posiciones se recalculará automáticamente.
			</p>
			<div class="flex items-center justify-end gap-3">
				<button type="button" onclick={() => (showFinishModal = false)} disabled={isClosingMatch}
					class="px-4 py-2 rounded-lg text-sm font-semibold text-slate-400 hover:text-white transition">
					Seguir jugando
				</button>
				<button type="button" onclick={confirmFinishMatch} disabled={isClosingMatch}
					class="px-5 py-2.5 rounded-lg text-sm font-bold text-white bg-amber-600 hover:bg-amber-500 transition flex items-center gap-2 disabled:opacity-50">
					{#if isClosingMatch}
						<span class="w-4 h-4 border-2 border-white border-t-transparent rounded-full animate-spin"></span>
						Cerrando...
					{:else}
						Confirmar Cierre
					{/if}
				</button>
			</div>
		</div>
	</div>
{/if}

<!-- ── MODAL INTERACTIVO: RESET / REGENERAR FIXTURE ──────────────────────────── -->
{#if showResetFixtureModal}
	<div class="fixed inset-0 z-50 flex items-center justify-center p-4 bg-slate-950/85" role="dialog" aria-modal="true" aria-labelledby="reset-fixture-title">
		<div class="glass-card w-full max-w-lg p-6 flex flex-col gap-5 border border-slate-700 shadow-2xl">
			<!-- Encabezado del modal -->
			<div class="text-center">
				<div class="text-5xl mb-3">⚠️</div>
				<h3 id="reset-fixture-title" class="text-xl font-black text-white">
					¿Qué deseas hacer con el torneo?
				</h3>
				<p class="text-sm text-slate-400 mt-1">
					Elige si quieres conservar los equipos o eliminar absolutamente todo.
				</p>
			</div>

			<!-- Información del estado actual -->
			<div class="flex flex-col gap-2.5 p-4 rounded-xl bg-slate-900/70 border border-slate-800">
				<!-- Opción 1: Regenerar (conservando equipos) -->
				<div class="flex items-start gap-3 p-3 rounded-lg bg-amber-500/10 border border-amber-500/30">
					<span class="text-xl flex-shrink-0">🔄</span>
					<div>
						<p class="text-sm font-bold text-amber-300">
							Regenerar Fixture (Conservar Equipos)
						</p>
						<p class="text-xs text-amber-400/80 mt-0.5">
							Se borrarán todos los partidos actuales ({playedMatchesCount} jugados) y la tabla de posiciones, pero los <strong class="text-white">{totalTeamsCount} equipos</strong> seguirán inscritos y se generarán nuevos cruces entre ellos.
						</p>
					</div>
				</div>

				<!-- Opción 2: Eliminar Todo -->
				<div class="flex items-start gap-3 p-3 rounded-lg bg-red-500/10 border border-red-500/30">
					<span class="text-xl flex-shrink-0">🗑️</span>
					<div>
						<p class="text-sm font-bold text-red-300">
							Eliminar Todo (Fixture y Equipos)
						</p>
						<p class="text-xs text-red-400/80 mt-0.5">
							Se borrará absolutamente todo. El fixture quedará vacío y tendrás que volver a inscribir equipos desde cero.
						</p>
					</div>
				</div>
			</div>

			<!-- Botones de acción -->
			<div class="flex flex-col sm:flex-row items-stretch sm:items-center justify-end gap-2.5">
				<!-- Cancelar -->
				<button
					type="button"
					onclick={() => (showResetFixtureModal = false)}
					disabled={deletingFixture || regeneratingFixture}
					class="px-4 py-2.5 rounded-lg text-sm font-semibold text-slate-400 hover:text-white transition disabled:opacity-40 order-last sm:order-first"
				>
					Cancelar
				</button>

				<!-- Eliminar y reiniciar -->
				<button
					type="button"
					onclick={handleDeleteOnlyFixture}
					disabled={deletingFixture || regeneratingFixture}
					class="flex-1 px-4 py-2.5 rounded-lg text-sm font-bold text-white bg-red-600 hover:bg-red-500 border border-red-500/40 transition flex items-center justify-center gap-2 disabled:opacity-40"
				>
					{#if deletingFixture}
						<span class="w-4 h-4 border-2 border-white border-t-transparent rounded-full animate-spin"></span>
					{:else}
						🗑️ Eliminar Todo
					{/if}
				</button>
				
				<!-- Regenerar -->
				<button
					type="button"
					onclick={handleResetAndRegenerate}
					disabled={deletingFixture || regeneratingFixture}
					class="flex-1 px-4 py-2.5 rounded-lg text-sm font-bold text-slate-900 bg-amber-400 hover:bg-amber-300 border border-amber-400/50 transition flex items-center justify-center gap-2 disabled:opacity-40 shadow-lg shadow-amber-900/20"
				>
					{#if regeneratingFixture}
						<span class="w-4 h-4 border-2 border-slate-900 border-t-transparent rounded-full animate-spin"></span>
					{:else}
						🔄 Regenerar Fixture
					{/if}
				</button>
			</div>
		</div>
	</div>
{/if}

<!-- MODAL DE CANCHA TÁCTICA PARA MESA DE CONTROL -->
{#if tacticalTeam}
	<div
		class="fixed inset-0 z-50 flex items-center justify-center p-4 bg-slate-950/85 backdrop-blur-sm animate-fade-in"
		role="dialog"
		aria-modal="true"
		onclick={(e) => e.target === e.currentTarget && (tacticalTeam = null)}
	>
		<div class="team-detail-modal-box glass-card w-full max-w-2xl max-h-[90vh] overflow-y-auto p-5 rounded-2xl border border-slate-700 shadow-2xl flex flex-col gap-4">
			<div class="flex items-center justify-between border-b border-slate-800 pb-3">
				<div>
					<h3 class="text-base font-bold text-white leading-tight">{tacticalTeam.name}</h3>
					<p class="text-xs text-slate-400 font-mono">{tacticalTeam.sport === 'basketball' ? 'Alineación — Básquetbol' : tacticalTeam.sport === 'volleyball' ? 'Alineación — Vóley' : tacticalTeam.sport === 'underwater_chess' ? 'Tablero — Ajedrez acuático' : tacticalTeam.sport === 'aura_battle' ? 'Pista Callejera — Batalla de Aura' : tacticalTeam.sport === 'sperm_triathlon' ? 'Circuito — Triatlón de Espermatozoide' : tacticalTeam.sport === 'tire_race' ? 'Pista Olímpica — Carrera de Llantas' : tacticalTeam.sport === 'mosquito_marathon' ? 'Pista de Vuelo — Maratón de Mosquitos' : 'Alineación — Fútbol'}</p>
				</div>
				<button
					type="button"
					onclick={() => (tacticalTeam = null)}
					class="text-slate-400 hover:text-white p-1 rounded-lg text-lg"
				>
					✕
				</button>
			</div>

			{#if (tacticalTeam.sport === 'basketball')}
				<BasketballCourt
					players={tacticalTeam.players || []}
					interactive={false}
					teamName={tacticalTeam.name}
					teamColor="#f59e0b"
				/>
			{:else if (tacticalTeam.sport === 'volleyball')}
				<VolleyballCourt
					players={tacticalTeam.players || []}
					interactive={false}
					teamName={tacticalTeam.name}
					teamColor="#8b5cf6"
				/>
			{:else if (tacticalTeam.sport === 'underwater_chess')}
				<UnderwaterChessBoard
					players={tacticalTeam.players || []}
					interactive={false}
					teamName={tacticalTeam.name}
					teamColor="#06b6d4"
				/>
			{:else if (tacticalTeam.sport === 'aura_battle')}
				<AuraBattleArena
					players={tacticalTeam.players || []}
					interactive={false}
					teamName={tacticalTeam.name}
					teamColor="#a855f7"
				/>
			{:else if (tacticalTeam.sport === 'sperm_triathlon')}
				<SpermTriathlonTrack
					players={tacticalTeam.players || []}
					interactive={false}
					teamName={tacticalTeam.name}
					teamColor="#06b6d4"
				/>
			{:else if (tacticalTeam.sport === 'tire_race')}
				<TireRaceTrack
					players={tacticalTeam.players || []}
					interactive={false}
					teamName={tacticalTeam.name}
					teamColor="#f97316"
				/>
			{:else if (tacticalTeam.sport === 'mosquito_marathon')}
				<MosquitoRadar
					players={tacticalTeam.players || []}
					interactive={false}
					teamName={tacticalTeam.name}
					teamColor="#84cc16"
				/>
			{:else}
				<SoccerPitch
					players={tacticalTeam.players || []}
					interactive={false}
					teamName={tacticalTeam.name}
					teamColor="#10b981"
				/>
			{/if}

			<div class="flex justify-end pt-2 border-t border-slate-800">
				<button
					type="button"
					onclick={() => (tacticalTeam = null)}
					class="px-4 py-2 text-xs font-semibold rounded-lg bg-slate-800 text-slate-300 hover:text-white transition"
				>
					Cerrar
				</button>
			</div>
		</div>
	</div>
{/if}
