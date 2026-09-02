<script>
	/**
	 * routes/mesa-control/+page.svelte — Panel de Mesa de Control y Arbitraje (NOM-12)
	 *
	 * ★ Ruta protegida con PIN. Solo delegados y árbitros.
	 * ★ Cronómetro calculado desde match.started_at (persiste entre recargas).
	 * ★ Goles se sincronizan al backend en tiempo real con PATCH /matches/{id}/score.
	 * ★ Botón "Regenerar Fixture" para incluir equipos registrados después de generar.
	 */
	import { onMount, onDestroy } from 'svelte';
	import { goto } from '$app/navigation';
	import { fixtureApi, matchesApi, teamsApi } from '$lib/api/client';
	import { auth } from '$lib/stores/auth';
	import { toast } from '$lib/stores/toast';
	import AdminPinModal from '$lib/components/AdminPinModal.svelte';

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

	// Configuración visual de badges de estado (claves en minúsculas)
	const statusConfig = {
		scheduled: { label: 'Programado',      badgeClass: 'badge-scheduled',   icon: '🕐' },
		live:      { label: 'EN JUEGO (LIVE)', badgeClass: 'badge-in-progress', icon: '⚽' },
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
			const teamsList = await teamsApi.list(TOURNAMENT_ID);
			const map = {};
			for (const t of teamsList) map[t.id] = t;
			teamsMap = map;
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
			if (rounds.length > 0) {
				const hasSelected = rounds.some((r) => (r.matchday ?? r.round) === selectedRound);
				if (!hasSelected) selectedRound = rounds[0].matchday ?? rounds[0].round ?? 1;
			}
		} catch {
			rounds = [];
		}
	}

	async function handleGenerateFixture() {
		generatingFixture = true;
		try {
			await fixtureApi.generate(TOURNAMENT_ID);
			toast.success('¡Fixture generado exitosamente!');
			await loadFixture();
		} catch (err) {
			toast.error(err.message || 'No se pudo generar el fixture. Verifica tener al menos 2 equipos.');
		} finally {
			generatingFixture = false;
		}
	}

	async function handleRegenerateFixture() {
		if (!confirm('⚠️ Esto regenerará el fixture completo con todos los equipos actuales. Los partidos sin resultado se perderán. ¿Continuar?')) return;
		regeneratingFixture = true;
		try {
			await fixtureApi.generate(TOURNAMENT_ID);
			toast.success('¡Fixture regenerado! Todos los equipos están incluidos.');
			await loadFixture();
			activeMatch = null;
		} catch (err) {
			toast.error(err.message || 'No se pudo regenerar el fixture.');
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

		// Calcular tiempo real transcurrido si el partido está EN VIVO
		if (normalStatus === 'live' && match.started_at) {
			const startedMs = new Date(match.started_at + 'Z').getTime(); // UTC
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

	// ── Goles táctiles (se sincronizan al backend) ─────────────────────────────
	async function adjustScore(team, delta) {
		if (!activeMatch || activeMatch.status === 'finished') return;

		if (team === 'home') liveHomeScore = Math.max(0, liveHomeScore + delta);
		else liveAwayScore = Math.max(0, liveAwayScore + delta);

		// Si el partido estaba programado, pasarlo a LIVE automáticamente
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

	// ── Cambio de Estado de Partido ─────────────────────────────────────────────
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
				toast.success('El partido ahora está EN JUEGO (LIVE) ⚽');
			} else {
				pauseTimer();
				toast.info(`Estado actualizado a: ${statusConfig[activeMatch.status]?.label ?? status}`);
			}
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

	onMount(() => { loadData(); });
	onDestroy(() => {
		if (timerInterval) clearInterval(timerInterval);
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
							▶️ Poner en Juego
						</button>
					{/if}
					{#if activeMatch.status === 'live'}
						<button onclick={() => setMatchStatus('scheduled')} class="px-3 py-1.5 rounded-lg text-xs font-semibold bg-slate-800 hover:bg-slate-700 text-slate-300 transition">
							⏸️ Pausar
						</button>
					{/if}
					{#if activeMatch.status !== 'finished'}
						<button onclick={() => (showFinishModal = true)} class="px-4 py-1.5 rounded-lg text-xs font-bold bg-amber-600 hover:bg-amber-500 text-white transition flex items-center gap-1">
							🏁 Finalizar Partido
						</button>
					{:else}
						<span class="text-xs font-bold text-emerald-400 px-3 py-1.5 rounded-lg bg-emerald-950/40 border border-emerald-800/60">
							✅ Partido Finalizado Oficialmente
						</span>
					{/if}
				</div>
			</div>

			<!-- CRONÓMETRO DIGITAL -->
			<div class="glass-card p-6 text-center flex flex-col items-center gap-3">
				<p class="text-xs font-bold uppercase tracking-wider text-slate-400">Tiempo de Juego</p>
				<div class="text-5xl sm:text-6xl font-black font-mono tracking-widest text-emerald-400">
					{formatTime(timerSeconds)}
				</div>
				{#if activeMatch.status === 'live'}
					<p class="text-xs text-slate-500 italic">Cronómetro sincronizado desde el inicio real del partido</p>
				{/if}
				<div class="flex items-center gap-2 mt-1">
					{#if !timerRunning}
						<button onclick={startTimer} disabled={activeMatch.status === 'finished'} class="px-4 py-1.5 rounded-lg text-xs font-bold bg-emerald-600 hover:bg-emerald-500 text-white transition disabled:opacity-30">
							▶️ Iniciar
						</button>
					{:else}
						<button onclick={pauseTimer} class="px-4 py-1.5 rounded-lg text-xs font-bold bg-yellow-600 hover:bg-yellow-500 text-white transition">
							⏸️ Pausar
						</button>
					{/if}
					<button onclick={resetTimer} class="px-3 py-1.5 rounded-lg text-xs font-semibold bg-slate-800 hover:bg-slate-700 text-slate-400 transition">
						🔄 00:00
					</button>
				</div>
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
					<div class="flex items-center gap-3 w-full max-w-xs">
						<button onclick={() => adjustScore('home', -1)} disabled={activeMatch.status === 'finished' || liveHomeScore <= 0}
							class="p-4 rounded-xl font-black text-lg bg-slate-800 hover:bg-slate-700 text-slate-300 disabled:opacity-30 transition">-1</button>
						<button onclick={() => adjustScore('home', 1)} disabled={activeMatch.status === 'finished'}
							class="flex-1 py-4 rounded-xl font-black text-lg text-white bg-emerald-600 hover:bg-emerald-500 active:scale-95 disabled:opacity-30 transition flex items-center justify-center gap-2">
							⚽ +1 GOL
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
							<p class="text-xs font-mono font-bold text-slate-400 uppercase">{awayTeam?.short_name ?? 'VIS'} · VISITANTE</p>
						</div>
					</div>
					<span class="text-7xl sm:text-8xl font-black font-mono text-blue-400">{liveAwayScore}</span>
					<div class="flex items-center gap-3 w-full max-w-xs">
						<button onclick={() => adjustScore('away', -1)} disabled={activeMatch.status === 'finished' || liveAwayScore <= 0}
							class="p-4 rounded-xl font-black text-lg bg-slate-800 hover:bg-slate-700 text-slate-300 disabled:opacity-30 transition">-1</button>
						<button onclick={() => adjustScore('away', 1)} disabled={activeMatch.status === 'finished'}
							class="flex-1 py-4 rounded-xl font-black text-lg text-white bg-blue-600 hover:bg-blue-500 active:scale-95 disabled:opacity-30 transition flex items-center justify-center gap-2">
							⚽ +1 GOL
						</button>
					</div>
				</div>
			</div>
		</div>

	<!-- ── SELECTOR DE PARTIDOS ───────────────────────────────────────────── -->
	{:else}
		{#if rounds.length === 0}
			<!-- Sin fixture -->
			<div class="glass-card p-12 text-center max-w-xl mx-auto">
				<div class="text-6xl mb-4">📅</div>
				<h2 class="text-2xl font-bold text-white mb-2">Fixture no generado</h2>
				<p class="text-slate-400 text-sm mb-6">Necesitas al menos 2 equipos registrados para generar el fixture.</p>
				<button onclick={handleGenerateFixture} disabled={generatingFixture}
					class="px-6 py-3 rounded-xl font-bold text-white bg-emerald-600 hover:bg-emerald-500 transition flex items-center gap-2 mx-auto disabled:opacity-50">
					{#if generatingFixture}
						<span class="w-4 h-4 border-2 border-white border-t-transparent rounded-full animate-spin"></span>
						Generando...
					{:else}
						⚡ Generar Fixture Automático
					{/if}
				</button>
			</div>
		{:else}
			<!-- Selector de Jornadas + botón Regenerar -->
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
				<button onclick={handleRegenerateFixture} disabled={regeneratingFixture}
					class="px-3 py-2 rounded-lg text-xs font-semibold text-slate-400 hover:text-amber-400 bg-slate-800/60 border border-slate-700/50 hover:border-amber-500/30 transition flex items-center gap-1.5 whitespace-nowrap disabled:opacity-50">
					{#if regeneratingFixture}
						<span class="w-3 h-3 border-2 border-amber-400 border-t-transparent rounded-full animate-spin"></span>
					{:else}
						🔄
					{/if}
					Regenerar Fixture
				</button>
			</div>

			<!-- Lista de Partidos -->
			<div class="grid grid-cols-1 md:grid-cols-2 gap-4">
				{#each currentMatches as match}
					{@const homeTeam = teamsMap[match.home_team_id]}
					{@const awayTeam = teamsMap[match.away_team_id]}
					{@const status = getStatus(match.status)}
					<div class="glass-card p-5 flex flex-col justify-between gap-4 transition">
						<div class="flex items-center justify-between border-b border-slate-800/80 pb-3">
							<span class="text-xs font-mono font-bold text-slate-400">Partido #{match.id}</span>
							<span class="text-xs px-2.5 py-1 rounded-full font-bold {status.badgeClass} flex items-center gap-1.5">
								{#if (match.status ?? '').toLowerCase() === 'live'}
									<span class="w-1.5 h-1.5 rounded-full bg-emerald-400"></span>
								{/if}
								{status.icon} {status.label}
							</span>
						</div>
						<div class="flex items-center justify-between gap-4 py-1">
							<div class="flex-1 text-center sm:text-left">
								<p class="font-bold text-white text-base truncate">{homeTeam?.name ?? `Equipo #${match.home_team_id}`}</p>
								<p class="text-xs text-slate-500 font-mono">{homeTeam?.short_name ?? '---'}</p>
							</div>
							<div class="px-4 py-1.5 rounded-xl bg-slate-900 border border-slate-800 text-center min-w-[70px]">
								{#if match.home_score !== null && match.away_score !== null}
									<span class="text-xl font-black font-mono text-emerald-400">{match.home_score} - {match.away_score}</span>
								{:else}
									<span class="text-sm font-bold text-slate-500">VS</span>
								{/if}
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
