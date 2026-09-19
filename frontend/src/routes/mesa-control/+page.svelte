<script>
	/**
	 * routes/mesa-control/+page.svelte â€” Panel de Mesa de Control y Arbitraje (NOM-12)
	 *
	 * â˜… Ruta protegida con PIN. Solo delegados y Ã¡rbitros.
	 * â˜… CronÃ³metro calculado desde match.started_at (persiste entre recargas).
	 * â˜… Goles se sincronizan al backend en tiempo real con PATCH /matches/{id}/score.
	 * â˜… BotÃ³n "Eliminar Fixture" (destructivo) + Modal interactivo de Reset/Regenerar.
	 * â˜… Flujo automÃ¡tico: si existe fixture, muestra diÃ¡logo antes de regenerar.
	 */
	import { onMount, onDestroy } from 'svelte';
	import { goto } from '$app/navigation';
	import { fixtureApi, matchesApi, teamsApi, tournamentsApi } from '$lib/api/client';
	import { auth } from '$lib/stores/auth';
	import { toast } from '$lib/stores/toast';
	import AdminPinModal from '$lib/components/AdminPinModal.svelte';
	import SoccerPitch from '$lib/components/SoccerPitch.svelte';
	import BasketballCourt from '$lib/components/BasketballCourt.svelte';

	const TOURNAMENT_ID = 1;

	// â”€â”€ AutenticaciÃ³n â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€
	let isAdmin = $state(false);
	let showPinModal = $state(false);
	const unsub = auth.subscribe((val) => {
		isAdmin = val;
		if (!val) showPinModal = true;
	});

	// â”€â”€ Estados generales â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€
	let rounds = $state([]);
	let teamsMap = $state({});
	let selectedRound = $state(1);
	let loading = $state(true);
	let generatingFixture = $state(false);
	let regeneratingFixture = $state(false);

	// â”€â”€ Estados para reset/eliminar fixture â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€
	let showResetFixtureModal = $state(false);
	let deletingFixture = $state(false);
	/** NÃºmero de partidos con resultados registrados (FINISHED o LIVE) en el fixture actual */
	let playedMatchesCount = $state(0);
	/** NÃºmero total de equipos activos en el torneo */
	let totalTeamsCount = $state(0);
	
	let tournament = $state(null);

	// Partido actualmente seleccionado para arbitrar
	let activeMatch = $state(null);

	// Marcadores en vivo en la mesa de control
	let liveHomeScore = $state(0);
	let liveAwayScore = $state(0);

	// â”€â”€ CronÃ³metro â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€
	let timerSeconds = $state(0);
	let timerRunning = $state(false);
	let timerInterval = null;

	// Modal de confirmaciÃ³n de cierre
	let showFinishModal = $state(false);
	let isClosingMatch = $state(false);
	let tacticalTeam = $state(null);
	let now = $state(Date.now());
	let globalTick = null;

	function getMatchTimer(match, _tick) {
		if ((match.status ?? '').toLowerCase() !== 'live') return null;
		if (!match.started_at) return '00:00';
		const iso = match.started_at.endsWith('Z') ? match.started_at : match.started_at + 'Z';
		const startedMs = new Date(iso).getTime();
		const current = now || Date.now();
		const totalSec = Math.max(0, Math.floor((current - startedMs) / 1000));
		return formatTime(totalSec);
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

	// ConfiguraciÃ³n visual de badges de estado (claves en minÃºsculas)
	const statusConfig = {
		scheduled: { label: 'Programado',      badgeClass: 'badge-scheduled',   icon: 'ðŸ•' },
		live:      { label: 'EN JUEGO (LIVE)', badgeClass: 'badge-in-progress', icon: 'âš½' },
		finished:  { label: 'Finalizado',      badgeClass: 'badge-finished',    icon: 'ðŸ' },
		cancelled: { label: 'Cancelado',       badgeClass: 'badge-cancelled',   icon: 'âŒ' },
		postponed: { label: 'Pospuesto',       badgeClass: 'badge-scheduled',   icon: 'â¸ï¸' }
	};

	function getStatus(rawStatus) {
		const key = (rawStatus ?? 'scheduled').toLowerCase();
		return statusConfig[key] ?? statusConfig.scheduled;
	}

	// â”€â”€ Carga inicial de datos â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€
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

			// Calcular cuÃ¡ntos partidos tienen resultados (para el modal de advertencia)
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

	// â”€â”€ GeneraciÃ³n inicial del fixture (cuando no existe ninguno) â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€
	async function handleGenerateFixture() {
		generatingFixture = true;
		try {
			await fixtureApi.generate(TOURNAMENT_ID);
			toast.success('Â¡Fixture generado exitosamente!');
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
			// No hay fixture â€” generar directamente
			await handleGenerateFixture();
			return;
		}
		// Hay fixture activo â†’ mostrar modal de confirmaciÃ³n
		showResetFixtureModal = true;
	}

	/**
	 * Elimina el fixture actual sin regenerar. Retorna al estado "sin fixture".
	 * Invocado desde el modal de confirmaciÃ³n con el botÃ³n "Solo Eliminar".
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
	 * Resetea el fixture y vacÃ­a los equipos, dejando el torneo limpio para nuevos registros.
	 */
	async function handleResetAndRegenerate() {
		regeneratingFixture = true;
		try {
			await fixtureApi.generateForce(TOURNAMENT_ID);
			rounds = [];
			playedMatchesCount = 0;
			activeMatch = null;
			showResetFixtureModal = false;
			await loadFixture();
			toast.success('Fixture regenerado exitosamente. Los equipos se han mantenido intactos.');
		} catch (err) {
			toast.error(err.message || 'No se pudo reiniciar el torneo.');
		} finally {
			regeneratingFixture = false;
		}
	}

	// â”€â”€ Manejo de selecciÃ³n de partido â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€
	function selectMatch(match) {
		pauseTimer();

		const normalStatus = (match.status ?? 'scheduled').toLowerCase();
		activeMatch = { ...match, status: normalStatus };
		liveHomeScore = match.home_score ?? 0;
		liveAwayScore = match.away_score ?? 0;

		// Calcular tiempo real transcurrido si el partido estÃ¡ EN VIVO
		if (normalStatus === 'live' && match.started_at) {
			const iso = match.started_at.endsWith('Z') ? match.started_at : match.started_at + 'Z';
			const startedMs = new Date(iso).getTime();
			timerSeconds = Math.max(0, Math.floor((Date.now() - startedMs) / 1000));
			startTimer();
		} else {
			timerSeconds = 0;
		}
	}

	function closeActiveMatch() {
		pauseTimer();
		activeMatch = null;
		timerSeconds = 0;
	}

	// â”€â”€ CronÃ³metro â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€
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

	// â”€â”€ Goles tÃ¡ctiles (se sincronizan al backend) â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€
	async function adjustScore(team, delta) {
		if (!activeMatch || activeMatch.status === 'finished') return;

		if (team === 'home') liveHomeScore = Math.max(0, liveHomeScore + delta);
		else liveAwayScore = Math.max(0, liveAwayScore + delta);

		// Si el partido estaba programado, pasarlo a LIVE automÃ¡ticamente
		if (activeMatch.status === 'scheduled') {
			await setMatchStatus('live');
		}

		// Sincronizar al backend inmediatamente
		try {
			await matchesApi.updateScore(activeMatch.id, liveHomeScore, liveAwayScore);
		} catch (err) {
			toast.error('Error al sincronizar el marcador: ' + (err.message || ''));
		}
	}

	// â”€â”€ Cambio de Estado de Partido â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€
	async function setMatchStatus(status) {
		if (!activeMatch) return;
		const norm = status.toLowerCase();
		try {
			const updated = await matchesApi.updateStatus(activeMatch.id, norm);
			activeMatch.status = (updated.status ?? norm).toLowerCase();

			// Si acaba de ponerse en LIVE, calcular timer desde started_at
			if (activeMatch.status === 'live') {
				if (updated.started_at) {
					const startedMs = new Date(updated.started_at + 'Z').getTime();
					timerSeconds = Math.max(0, Math.floor((Date.now() - startedMs) / 1000));
				}
				startTimer();
				toast.success('El partido ahora estÃ¡ EN JUEGO (LIVE) âš½');
			} else {
				pauseTimer();
				toast.info(`Estado actualizado a: ${statusConfig[activeMatch.status]?.label ?? status}`);
			}
			await loadFixture();
		} catch (err) {
			toast.error(err.message || 'Error al cambiar estado del partido.');
		}
	}

	// â”€â”€ Cierre definitivo del partido â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€
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
			showFinishModal = false;
			toast.success(`Â¡Partido finalizado! ${liveHomeScore} - ${liveAwayScore}. Posiciones actualizadas.`);
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

	onMount(() => {
		loadData();
		globalTick = setInterval(() => {
			now = Date.now();
		}, 1000);
	});
	onDestroy(() => {
		if (timerInterval) clearInterval(timerInterval);
		if (globalTick) clearInterval(globalTick);
		unsub();
	});
</script>


<svelte:head>
	<title>Mesa de Control â€” Nombre-Creativo</title>
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
	<!-- â”€â”€ ENCABEZADO â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€ -->
	<div class="flex flex-col sm:flex-row sm:items-center justify-between gap-4 mb-8">
		<div>
			<h1 class="text-3xl font-black text-white flex items-center gap-3">
				ðŸŽ® Mesa de Control
				<span class="text-xs font-bold px-2 py-1 rounded-md bg-amber-500/15 text-amber-400 border border-amber-500/25">ADMIN</span>
			</h1>
			<p class="text-slate-400 mt-1">Gestiona cronÃ³metro, goles en tiempo real y cierre de partidos.</p>
		</div>
		{#if activeMatch}
			<button onclick={closeActiveMatch} class="inline-flex items-center gap-2 px-4 py-2 rounded-xl text-sm font-semibold bg-slate-800 hover:bg-slate-700 text-slate-300 hover:text-white transition">
				â† Volver al Fixture
			</button>
		{/if}
	</div>

	<!-- â”€â”€ ESTADO: CARGANDO â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€ -->
	{#if loading}
		<div class="space-y-4">
			<div class="skeleton h-12 w-full rounded-xl"></div>
			<div class="grid grid-cols-1 md:grid-cols-2 gap-4">
				{#each Array(4) as _}
					<div class="skeleton h-32 w-full rounded-xl"></div>
				{/each}
			</div>
		</div>

	<!-- â”€â”€ CONSOLA DE ARBITRAJE (PARTIDO SELECCIONADO) â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€ -->
	{:else if activeMatch}
		{@const homeTeam = teamsMap[activeMatch.home_team_id]}
		{@const awayTeam = teamsMap[activeMatch.away_team_id]}
		{@const status = getStatus(activeMatch.status)}

		<div class="space-y-6">
			<!-- Barra de Estado -->
			<div class="glass-card p-4 sm:p-6 flex flex-col sm:flex-row items-center justify-between gap-4">
				<div class="flex items-center gap-3">
					<span class="text-xs px-3 py-1.5 rounded-full font-bold {status.badgeClass} flex items-center gap-1.5">
						{#if activeMatch.status === 'live'}
							<span class="w-2 h-2 rounded-full bg-emerald-400"></span>
						{/if}
						{status.icon} {status.label}
					</span>
					<span class="text-sm font-semibold text-slate-400">Jornada {activeMatch.matchday ?? 1}</span>
				</div>

				<div class="flex flex-wrap items-center gap-2">
					{#if activeMatch.status !== 'live' && activeMatch.status !== 'finished'}
						<button onclick={() => setMatchStatus('live')} class="px-3.5 py-1.5 rounded-lg text-xs font-bold bg-emerald-600 hover:bg-emerald-500 text-white transition flex items-center gap-1">
							â–¶ï¸ Poner en Juego
						</button>
					{/if}
					{#if activeMatch.status === 'live'}
						<button onclick={() => setMatchStatus('scheduled')} class="px-3 py-1.5 rounded-lg text-xs font-semibold bg-slate-800 hover:bg-slate-700 text-slate-300 transition">
							â¸ï¸ Pausar
						</button>
					{/if}
					{#if activeMatch.status !== 'finished'}
						<button onclick={() => (showFinishModal = true)} class="px-4 py-1.5 rounded-lg text-xs font-bold bg-amber-600 hover:bg-amber-500 text-white transition flex items-center gap-1">
							ðŸ Finalizar Partido
						</button>
					{:else}
						<span class="text-xs font-bold text-emerald-400 px-3 py-1.5 rounded-lg bg-emerald-950/40 border border-emerald-800/60">
							âœ… Partido Finalizado Oficialmente
						</span>
					{/if}
				</div>
			</div>

			<!-- CRONÃ“METRO DIGITAL -->
			<div class="glass-card p-6 text-center flex flex-col items-center gap-3">
				<p class="text-xs font-bold uppercase tracking-wider text-slate-400">Tiempo de Juego</p>
				<div class="text-5xl sm:text-6xl font-black font-mono tracking-widest text-emerald-400">
					{formatTime(timerSeconds)}
				</div>
				{#if activeMatch.status === 'live'}
					<p class="text-xs text-slate-500 italic">CronÃ³metro sincronizado desde el inicio real del partido</p>
				{/if}
				<div class="flex items-center gap-2 mt-1">
					{#if !timerRunning}
						<button onclick={startTimer} disabled={activeMatch.status === 'finished'} class="px-4 py-1.5 rounded-lg text-xs font-bold bg-emerald-600 hover:bg-emerald-500 text-white transition disabled:opacity-30">
							â–¶ï¸ Iniciar
						</button>
					{:else}
						<button onclick={pauseTimer} class="px-4 py-1.5 rounded-lg text-xs font-bold bg-yellow-600 hover:bg-yellow-500 text-white transition">
							â¸ï¸ Pausar
						</button>
					{/if}
					<button onclick={resetTimer} class="px-3 py-1.5 rounded-lg text-xs font-semibold bg-slate-800 hover:bg-slate-700 text-slate-400 transition">
						ðŸ”„ 00:00
					</button>
				</div>
			</div>

			<!-- Botones de Cancha TÃ¡ctica -->
			<div class="flex items-center justify-center gap-3 py-1">
				<button type="button" onclick={() => showTeamTactical(activeMatch.home_team_id)} class="px-3.5 py-1.5 rounded-xl text-xs font-bold bg-emerald-950/60 hover:bg-emerald-900/60 text-emerald-300 border border-emerald-700/50 transition flex items-center gap-1.5 shadow-sm">
					<span>ðŸŸï¸</span> Ver alineaciÃ³n ({homeTeam?.short_name ?? 'Local'})
				</button>
				<button type="button" onclick={() => showTeamTactical(activeMatch.away_team_id)} class="px-3.5 py-1.5 rounded-xl text-xs font-bold bg-blue-950/60 hover:bg-blue-900/60 text-blue-300 border border-blue-700/50 transition flex items-center gap-1.5 shadow-sm">
					<span>ðŸŸï¸</span> Ver alineaciÃ³n ({awayTeam?.short_name ?? 'Visita'})
				</button>
			</div>

			<!-- MARCADOR TÃCTIL -->
			<div class="grid grid-cols-1 md:grid-cols-2 gap-6">
				<!-- LOCAL -->
				<div class="glass-card p-6 sm:p-8 flex flex-col items-center text-center gap-5 border-t-4 border-emerald-500">
					<div class="flex flex-col items-center gap-2">
						<div class="w-16 h-16 rounded-2xl flex items-center justify-center text-2xl font-black text-white shadow-xl bg-emerald-700">
							{homeTeam?.name?.[0]?.toUpperCase() ?? 'L'}
						</div>
						<div>
							<h2 class="text-2xl font-black text-white">{homeTeam?.name ?? 'Equipo Local'}</h2>
							<p class="text-xs font-mono font-bold text-slate-400 uppercase">{homeTeam?.short_name ?? 'LOC'} Â· LOCAL</p>
						</div>
					</div>
					<span class="text-7xl sm:text-8xl font-black font-mono text-emerald-400">{liveHomeScore}</span>
					<div class="flex items-center gap-3 w-full max-w-xs">
						<button onclick={() => adjustScore('home', -1)} disabled={activeMatch.status === 'finished' || liveHomeScore <= 0}
							class="p-4 rounded-xl font-black text-lg bg-slate-800 hover:bg-slate-700 text-slate-300 disabled:opacity-30 transition">-1</button>
						<button onclick={() => adjustScore('home', 1)} disabled={activeMatch.status === 'finished'}
							class="flex-1 py-4 rounded-xl font-black text-lg text-white bg-emerald-600 hover:bg-emerald-500 active:scale-95 disabled:opacity-30 transition flex items-center justify-center gap-2">
							{homeTeam?.sport === 'basketball' ? 'ðŸ€ +1 PUNTO' : 'âš½ +1 GOL'}
						</button>
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
							<p class="text-xs font-mono font-bold text-slate-400 uppercase">{awayTeam?.short_name ?? 'VIS'} Â· VISITANTE</p>
						</div>
					</div>
					<span class="text-7xl sm:text-8xl font-black font-mono text-blue-400">{liveAwayScore}</span>
					<div class="flex items-center gap-3 w-full max-w-xs">
						<button onclick={() => adjustScore('away', -1)} disabled={activeMatch.status === 'finished' || liveAwayScore <= 0}
							class="p-4 rounded-xl font-black text-lg bg-slate-800 hover:bg-slate-700 text-slate-300 disabled:opacity-30 transition">-1</button>
						<button onclick={() => adjustScore('away', 1)} disabled={activeMatch.status === 'finished'}
							class="flex-1 py-4 rounded-xl font-black text-lg text-white bg-blue-600 hover:bg-blue-500 active:scale-95 disabled:opacity-30 transition flex items-center justify-center gap-2">
							{homeTeam?.sport === 'basketball' ? 'ðŸ€ +1 PUNTO' : 'âš½ +1 GOL'}
						</button>
					</div>
				</div>
			</div>
		</div>

	<!-- â”€â”€ SELECTOR DE PARTIDOS â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€ -->
	{:else}
		{#if rounds.length === 0}
			<!-- Sin fixture -->
			<div class="glass-card p-12 text-center max-w-xl mx-auto animate-fade-in-up">
				<div class="text-6xl mb-4">ðŸ“…</div>
				<h2 class="text-2xl font-bold text-white mb-2">Fixture vacÃ­o</h2>
				<p class="text-slate-400 text-sm mb-6">
					{#if totalTeamsCount < 2}
						Actualmente hay {totalTeamsCount} equipo(s) registrado(s). Registra al menos 2 equipos para generar el fixture.
					{:else}
						Hay {totalTeamsCount} equipos listos. Puedes generar el fixture automÃ¡tico ahora.
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
								âš¡ Generar Fixture AutomÃ¡tico
							{/if}
						</button>
					{/if}
					<a href="/equipos/nuevo" class="px-5 py-3 rounded-xl font-bold text-emerald-400 bg-emerald-500/10 hover:bg-emerald-500/20 border border-emerald-500/30 transition flex items-center justify-center gap-2 text-sm">
						âž• Inscribir Nuevos Equipos
					</a>
				</div>
				
			</div>
		{:else}
			
			<!-- â”€â”€ Filtro por Deporte â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€ -->
			<div class="flex items-center gap-2 mb-4 p-1 bg-slate-900/90 rounded-xl border border-slate-800 w-fit">
				<button
					type="button"
					onclick={() => (selectedSport = 'all')}
					class="px-3.5 py-1.5 rounded-lg text-xs font-bold transition {selectedSport === 'all' ? 'bg-slate-700 text-white' : 'text-slate-400 hover:text-white'}"
				>
					ðŸŒ Todos
				</button>
				<button
					type="button"
					onclick={() => (selectedSport = 'football')}
					class="px-3.5 py-1.5 rounded-lg text-xs font-bold transition {selectedSport === 'football' ? 'bg-emerald-600 text-white' : 'text-slate-400 hover:text-white'}"
				>
					âš½ FÃºtbol
				</button>
				<button
					type="button"
					onclick={() => (selectedSport = 'basketball')}
					class="px-3.5 py-1.5 rounded-lg text-xs font-bold transition {selectedSport === 'basketball' ? 'bg-amber-600 text-white' : 'text-slate-400 hover:text-white'}"
				>
					ðŸ€ BÃ¡squetbol
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
				<!-- Botones de gestiÃ³n de fixture -->
				<div class="flex items-center gap-2">
					<!-- Eliminar fixture (destructivo, rojo/outline) -->
					<button
						onclick={handleDeleteOnlyFixture}
						disabled={deletingFixture || regeneratingFixture}
						title="Eliminar fixture actual. Se perderÃ¡n todos los partidos."
						class="px-3 py-2 rounded-lg text-xs font-semibold text-red-400 hover:text-red-300 bg-slate-800/60 border border-red-500/30 hover:border-red-400/60 hover:bg-red-500/10 transition flex items-center gap-1.5 whitespace-nowrap disabled:opacity-40"
					>
						{#if deletingFixture}
							<span class="w-3 h-3 border-2 border-red-400 border-t-transparent rounded-full animate-spin"></span>
						{:else}
							ðŸ—‘ï¸
						{/if}
						Eliminar Fixture
					</button>
					<!-- Regenerar fixture -->
					<button onclick={handleRegenerateFixture} disabled={regeneratingFixture || deletingFixture}
						class="px-3 py-2 rounded-lg text-xs font-semibold text-slate-400 hover:text-amber-400 bg-slate-800/60 border border-slate-700/50 hover:border-amber-500/30 transition flex items-center gap-1.5 whitespace-nowrap disabled:opacity-50">
						{#if regeneratingFixture}
							<span class="w-3 h-3 border-2 border-amber-400 border-t-transparent rounded-full animate-spin"></span>
						{:else}
							ðŸ”„
						{/if}
						Regenerar Fixture
					</button>
				</div>
			</div>

			<!-- Lista de Partidos -->
			<div class="grid grid-cols-1 md:grid-cols-2 gap-4">
				{#if filteredMatches.length === 0}
					<div class="col-span-full glass-card p-8 text-center">
						<p class="text-slate-400 text-sm">No hay partidos de {selectedSport === 'basketball' ? 'bÃ¡squetbol' : 'fÃºtbol'} en esta jornada.</p>
					</div>
				{/if}
				{#each filteredMatches as match}
					{@const homeTeam = teamsMap[match.home_team_id]}
					{@const awayTeam = teamsMap[match.away_team_id]}
					{@const status = getStatus(match.status)}
					{@const mSport = getMatchSport(match)}
										<div class="glass-card p-5 flex flex-col justify-between gap-4 transition">
						<div class="flex items-center justify-between border-b border-slate-800/80 pb-3">
							<div class="flex items-center gap-2">
								<span class="text-xs font-mono font-bold text-slate-400">#{match.id}</span>
								{#if mSport === 'basketball'}
									<span class="text-[11px] font-bold px-2 py-0.5 rounded-full bg-amber-500/15 text-amber-300 border border-amber-500/30 flex items-center gap-1">
										ðŸ€ BÃ¡squet
									</span>
								{:else}
									<span class="text-[11px] font-bold px-2 py-0.5 rounded-full bg-emerald-500/15 text-emerald-300 border border-emerald-500/30 flex items-center gap-1">
										âš½ FÃºtbol
									</span>
								{/if}
							</div>
							<span class="text-xs px-2.5 py-1 rounded-full font-bold {status.badgeClass} flex items-center gap-1.5">
								{#if (match.status ?? '').toLowerCase() === 'live'}
									<span class="w-1.5 h-1.5 rounded-full bg-emerald-400 animate-ping"></span>
									{status.icon} {status.label} Â· <span class="font-mono font-black text-emerald-300">â±ï¸ {getMatchTimer(match, now)}</span>
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
										â±ï¸ {getMatchTimer(match, now)}
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
							class="w-full py-2.5 rounded-xl text-xs font-bold transition flex items-center justify-center gap-2 {(match.status ?? '').toLowerCase() === 'live'
								? 'bg-emerald-600 hover:bg-emerald-500 text-white'
								: 'bg-slate-800 hover:bg-slate-700 text-slate-200'}">
							ðŸŽ® {(match.status ?? '').toLowerCase() === 'finished' ? 'Ver Registro' : 'Arbitrar Partido'}
						</button>
					</div>
				{/each}
			</div>
		{/if}
	{/if}
</div>
{/if}

<!-- Modal de ConfirmaciÃ³n de FinalizaciÃ³n -->
{#if showFinishModal && activeMatch}
	{@const homeTeam = teamsMap[activeMatch.home_team_id]}
	{@const awayTeam = teamsMap[activeMatch.away_team_id]}
	<div class="fixed inset-0 z-50 flex items-center justify-center p-4 bg-slate-950/80" role="dialog" aria-modal="true">
		<div class="glass-card w-full max-w-md p-6 flex flex-col gap-5 border border-slate-700 shadow-2xl">
			<div class="text-center">
				<div class="text-4xl mb-2">ðŸ</div>
				<h3 class="text-xl font-black text-white">Â¿Finalizar Partido Oficial?</h3>
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
				â„¹ï¸ Al confirmar, el partido quedarÃ¡ como <strong>FINALIZADO</strong> y la tabla de posiciones se recalcularÃ¡ automÃ¡ticamente.
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

<!-- â”€â”€ MODAL INTERACTIVO: RESET / REGENERAR FIXTURE â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€ -->
{#if showResetFixtureModal}
	<div class="fixed inset-0 z-50 flex items-center justify-center p-4 bg-slate-950/85" role="dialog" aria-modal="true" aria-labelledby="reset-fixture-title">
		<div class="glass-card w-full max-w-lg p-6 flex flex-col gap-5 border border-slate-700 shadow-2xl">
			<!-- Encabezado del modal -->
			<div class="text-center">
				<div class="text-5xl mb-3">âš ï¸</div>
				<h3 id="reset-fixture-title" class="text-xl font-black text-white">
					Â¿QuÃ© deseas hacer con el torneo?
				</h3>
				<p class="text-sm text-slate-400 mt-1">
					Elige si quieres conservar los equipos o eliminar absolutamente todo.
				</p>
			</div>

			<!-- InformaciÃ³n del estado actual -->
			<div class="flex flex-col gap-2.5 p-4 rounded-xl bg-slate-900/70 border border-slate-800">
				<!-- OpciÃ³n 1: Regenerar (conservando equipos) -->
				<div class="flex items-start gap-3 p-3 rounded-lg bg-amber-500/10 border border-amber-500/30">
					<span class="text-xl flex-shrink-0">ðŸ”„</span>
					<div>
						<p class="text-sm font-bold text-amber-300">
							Regenerar Fixture (Conservar Equipos)
						</p>
						<p class="text-xs text-amber-400/80 mt-0.5">
							Se borrarÃ¡n todos los partidos actuales ({playedMatchesCount} jugados) y la tabla de posiciones, pero los <strong class="text-white">{totalTeamsCount} equipos</strong> seguirÃ¡n inscritos y se generarÃ¡n nuevos cruces entre ellos.
						</p>
					</div>
				</div>

				<!-- OpciÃ³n 2: Eliminar Todo -->
				<div class="flex items-start gap-3 p-3 rounded-lg bg-red-500/10 border border-red-500/30">
					<span class="text-xl flex-shrink-0">ðŸ—‘ï¸</span>
					<div>
						<p class="text-sm font-bold text-red-300">
							Eliminar Todo (Fixture y Equipos)
						</p>
						<p class="text-xs text-red-400/80 mt-0.5">
							Se borrarÃ¡ absolutamente todo. El fixture quedarÃ¡ vacÃ­o y tendrÃ¡s que volver a inscribir equipos desde cero.
						</p>
					</div>
				</div>
			</div>

			<!-- Botones de acciÃ³n -->
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
						ðŸ—‘ï¸ Eliminar Todo
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
						ðŸ”„ Regenerar Fixture
					{/if}
				</button>
			</div>
		</div>
	</div>
{/if}

<!-- MODAL DE CANCHA TÃCTICA PARA MESA DE CONTROL -->
{#if tacticalTeam}
	<div
		class="fixed inset-0 z-50 flex items-center justify-center p-4 bg-slate-950/85 backdrop-blur-sm animate-fade-in"
		role="dialog"
		aria-modal="true"
		onclick={(e) => e.target === e.currentTarget && (tacticalTeam = null)}
	>
		<div class="glass-card w-full max-w-2xl max-h-[90vh] overflow-y-auto p-5 rounded-2xl border border-slate-700 shadow-2xl flex flex-col gap-4">
			<div class="flex items-center justify-between border-b border-slate-800 pb-3">
				<div>
					<h3 class="text-base font-bold text-white leading-tight">{tacticalTeam.name}</h3>
					<p class="text-xs text-slate-400 font-mono">{(tacticalTeam.sport === 'basketball' || (activeMatch && getMatchSport(activeMatch) === 'basketball')) ? 'AlineaciÃ³n TÃ¡ctica en Pista de BÃ¡squetbol' : 'AlineaciÃ³n TÃ¡ctica en Cancha de FÃºtbol'}</p>
				</div>
				<button
					type="button"
					onclick={() => (tacticalTeam = null)}
					class="text-slate-400 hover:text-white p-1 rounded-lg text-lg"
				>
					âœ•
				</button>
			</div>

			<SoccerPitch
				players={tacticalTeam.players || []}
				interactive={false}
				teamName={tacticalTeam.name}
				teamColor="#10b981"
			/>

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


