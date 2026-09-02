<script>
	/**
	 * routes/mesa-control/+page.svelte — Panel de Mesa de Control y Arbitraje en Vivo (NOM-12)
	 *
	 * Características:
	 * 1. Selector de partidos por jornada (matchday) y botón para generar fixture si no existe.
	 * 2. Marcador táctil interactivo con botones (+1 / -1) para goles locales y visitantes.
	 * 3. Cronómetro en vivo (MM:SS) con controles Iniciar / Pausar / Reiniciar.
	 * 4. Gestión de estados de partido (scheduled, live, finished, cancelled).
	 * 5. Modal de confirmación para cerrar y finalizar el partido con recálculo de posiciones.
	 */
	import { onMount, onDestroy } from 'svelte';
	import { fixtureApi, matchesApi, teamsApi } from '$lib/api/client';
	import { toast } from '$lib/stores/toast';

	const TOURNAMENT_ID = 1;

	// ── Estados generales ──────────────────────────────────────────────────────
	let rounds = $state([]);
	let teamsMap = $state({});
	let selectedRound = $state(1);
	let loading = $state(true);
	let generatingFixture = $state(false);

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

	// Configuración visual de badges de estado (en minúsculas para empatar con la API)
	const statusConfig = {
		scheduled: { label: 'Programado',     badgeClass: 'badge-scheduled',   icon: '🕐' },
		live:      { label: 'EN JUEGO (LIVE)',badgeClass: 'badge-in-progress', icon: '⚽' },
		finished:  { label: 'Finalizado',     badgeClass: 'badge-finished',    icon: '🏁' },
		cancelled: { label: 'Cancelado',      badgeClass: 'badge-cancelled',   icon: '❌' },
		postponed: { label: 'Pospuesto',      badgeClass: 'badge-scheduled',   icon: '⏸️' }
	};

	function getStatus(rawStatus) {
		const key = (rawStatus ?? 'scheduled').toLowerCase();
		return statusConfig[key] ?? statusConfig.scheduled;
	}

	// ── Carga inicial de datos ─────────────────────────────────────────────────
	async function loadData() {
		loading = true;
		try {
			// Cargar equipos para mapear IDs a nombres y logos
			const teamsList = await teamsApi.list(TOURNAMENT_ID);
			const map = {};
			for (const t of teamsList) {
				map[t.id] = t;
			}
			teamsMap = map;

			// Cargar fixture
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
				if (!hasSelected) {
					selectedRound = rounds[0].matchday ?? rounds[0].round ?? 1;
				}
			}
		} catch (err) {
			rounds = [];
		}
	}

	async function handleGenerateFixture() {
		generatingFixture = true;
		try {
			await fixtureApi.generate(TOURNAMENT_ID);
			toast.success('¡Fixture generado exitosamente para el torneo!');
			await loadFixture();
		} catch (err) {
			toast.error(err.message || 'No se pudo generar el fixture. Verifica tener al menos 2 equipos.');
		} finally {
			generatingFixture = false;
		}
	}

	// ── Manejo de selección de partido ─────────────────────────────────────────
	function selectMatch(match) {
		activeMatch = {
			...match,
			status: (match.status ?? 'scheduled').toLowerCase()
		};
		liveHomeScore = match.home_score ?? 0;
		liveAwayScore = match.away_score ?? 0;

		pauseTimer();
		timerSeconds = 0;
		if (activeMatch.status === 'live') {
			startTimer();
		}
	}

	function closeActiveMatch() {
		pauseTimer();
		activeMatch = null;
	}

	// ── Funciones del Cronómetro ───────────────────────────────────────────────
	function startTimer() {
		if (timerRunning) return;
		timerRunning = true;
		timerInterval = setInterval(() => {
			timerSeconds++;
		}, 1000);
	}

	function pauseTimer() {
		timerRunning = false;
		if (timerInterval) {
			clearInterval(timerInterval);
			timerInterval = null;
		}
	}

	function resetTimer() {
		pauseTimer();
		timerSeconds = 0;
	}

	function formatTime(totalSeconds) {
		const mins = Math.floor(totalSeconds / 60);
		const secs = totalSeconds % 60;
		return `${mins.toString().padStart(2, '0')}:${secs.toString().padStart(2, '0')}`;
	}

	// ── Manejo de Goles Táctiles ───────────────────────────────────────────────
	function adjustScore(team, delta) {
		if (!activeMatch) return;

		if (team === 'home') {
			liveHomeScore = Math.max(0, liveHomeScore + delta);
		} else {
			liveAwayScore = Math.max(0, liveAwayScore + delta);
		}

		// Si el partido estaba programado, al pulsar gol sugerimos pasarlo a live
		if (activeMatch.status === 'scheduled') {
			setMatchStatus('live');
		}
	}

	// ── Cambio de Estado de Partido ───────────────────────────────────────────
	async function setMatchStatus(status) {
		if (!activeMatch) return;
		const norm = status.toLowerCase();
		try {
			const updated = await matchesApi.updateStatus(activeMatch.id, norm);
			activeMatch.status = (updated.status ?? norm).toLowerCase();

			if (activeMatch.status === 'live') {
				startTimer();
				toast.success('El partido ahora está EN JUEGO (LIVE)');
			} else {
				pauseTimer();
				toast.info(`Estado actualizado a ${statusConfig[activeMatch.status]?.label ?? status}`);
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
			const resultPayload = {
				home_score: liveHomeScore,
				away_score: liveAwayScore
			};

			const finished = await matchesApi.registerResult(activeMatch.id, resultPayload);
			pauseTimer();
			activeMatch = {
				...finished,
				status: 'finished'
			};
			showFinishModal = false;

			toast.success(
				`¡Partido finalizado con éxito! Resultado: ${liveHomeScore} - ${liveAwayScore}. Tabla de posiciones recalculada.`
			);

			await loadFixture();
		} catch (err) {
			toast.error(err.message || 'No se pudo finalizar el partido.');
		} finally {
			isClosingMatch = false;
		}
	}

	// Partidos de la jornada seleccionada (matchday o round)
	let currentMatches = $derived(
		rounds.find((r) => (r.matchday ?? r.round) === selectedRound)?.matches ?? []
	);

	onMount(() => {
		loadData();
	});

	onDestroy(() => {
		if (timerInterval) clearInterval(timerInterval);
	});
</script>

<svelte:head>
	<title>Mesa de Control en Vivo — Nombre-Creativo</title>
</svelte:head>

<div class="animate-fade-in-up pb-12">
	<!-- ── ENCABEZADO ────────────────────────────────────────────────────────── -->
	<div class="flex flex-col sm:flex-row sm:items-center justify-between gap-4 mb-8">
		<div>
			<h1 class="text-3xl font-black text-white flex items-center gap-3">
				🎮 Mesa de Control y Arbitraje
			</h1>
			<p class="text-slate-400 mt-1">
				Gestiona cronómetro, goles en tiempo real y finalización de partidos del torneo.
			</p>
		</div>

		{#if activeMatch}
			<button
				onclick={closeActiveMatch}
				class="inline-flex items-center gap-2 px-4 py-2 rounded-xl text-sm font-semibold bg-slate-800 hover:bg-slate-700 text-slate-300 hover:text-white transition"
			>
				← Volver al Fixture
			</button>
		{/if}
	</div>

	<!-- ── ESTADO: CARGANDO ───────────────────────────────────────────────────── -->
	{#if loading}
		<div class="space-y-4">
			<div class="skeleton h-12 w-full rounded-xl"></div>
			<div class="grid grid-cols-1 md:grid-cols-2 gap-4">
				{#each Array(4) as _}
					<div class="skeleton h-32 w-full rounded-xl"></div>
				{/each}
			</div>
		</div>

	<!-- ── CASO A: CONSOLA DE ARBITRAJE EN VIVO (PARTIDO SELECCIONADO) ────────── -->
	{:else if activeMatch}
		{@const homeTeam = teamsMap[activeMatch.home_team_id]}
		{@const awayTeam = teamsMap[activeMatch.away_team_id]}
		{@const status = getStatus(activeMatch.status)}

		<div class="space-y-6">
			<!-- Barra de Estado y Acciones Rápidas -->
			<div class="glass-card p-4 sm:p-6 flex flex-col sm:flex-row items-center justify-between gap-4">
				<div class="flex items-center gap-3">
					<span class="text-xs px-3 py-1.5 rounded-full font-bold {status.badgeClass} flex items-center gap-1.5">
						{#if activeMatch.status === 'live'}
							<span class="w-2 h-2 rounded-full bg-emerald-400"></span>
						{/if}
						{status.icon} {status.label}
					</span>
					<span class="text-sm font-semibold text-slate-400">
						Jornada {activeMatch.matchday ?? 1}
					</span>
				</div>

				<!-- Botones para cambiar estado rápido -->
				<div class="flex flex-wrap items-center gap-2">
					{#if activeMatch.status !== 'live' && activeMatch.status !== 'finished'}
						<button
							onclick={() => setMatchStatus('live')}
							class="px-3.5 py-1.5 rounded-lg text-xs font-bold bg-emerald-600 hover:bg-emerald-500 text-white transition flex items-center gap-1 shadow-md shadow-emerald-950"
						>
							<span>▶️</span> Poner en Juego (LIVE)
						</button>
					{/if}

					{#if activeMatch.status === 'live'}
						<button
							onclick={() => setMatchStatus('scheduled')}
							class="px-3 py-1.5 rounded-lg text-xs font-semibold bg-slate-800 hover:bg-slate-700 text-slate-300 transition"
						>
							⏸️ Pausar Partido
						</button>
					{/if}

					{#if activeMatch.status !== 'finished'}
						<button
							onclick={() => (showFinishModal = true)}
							class="px-4 py-1.5 rounded-lg text-xs font-bold bg-amber-600 hover:bg-amber-500 text-white transition flex items-center gap-1 shadow-md shadow-amber-950"
						>
							<span>🏁</span> Finalizar Partido
						</button>
					{:else}
						<span class="text-xs font-bold text-emerald-400 px-3 py-1.5 rounded-lg bg-emerald-950/40 border border-emerald-800/60 flex items-center gap-1">
							✅ Partido Oficialmente Finalizado
						</span>
					{/if}
				</div>
			</div>

			<!-- CRONÓMETRO DIGITAL -->
			<div class="glass-card p-6 text-center flex flex-col items-center justify-center gap-3">
				<p class="text-xs font-bold uppercase tracking-wider text-slate-400">Tiempo de Juego</p>
				<div class="text-5xl sm:text-6xl font-black font-mono tracking-widest text-emerald-400">
					{formatTime(timerSeconds)}
				</div>

				<div class="flex items-center gap-2 mt-2">
					{#if !timerRunning}
						<button
							onclick={startTimer}
							class="px-4 py-1.5 rounded-lg text-xs font-bold bg-emerald-600 hover:bg-emerald-500 text-white transition"
						>
							▶️ Iniciar
						</button>
					{:else}
						<button
							onclick={pauseTimer}
							class="px-4 py-1.5 rounded-lg text-xs font-bold bg-yellow-600 hover:bg-yellow-500 text-white transition"
						>
							⏸️ Pausar
						</button>
					{/if}
					<button
						onclick={resetTimer}
						class="px-3 py-1.5 rounded-lg text-xs font-semibold bg-slate-800 hover:bg-slate-700 text-slate-400 transition"
					>
						🔄 00:00
					</button>
				</div>
			</div>

			<!-- MARCADOR TÁCTIL (TABLERO DE GOLES) -->
			<div class="grid grid-cols-1 md:grid-cols-2 gap-6">
				<!-- EQUIPO LOCAL -->
				<div class="glass-card p-6 sm:p-8 flex flex-col items-center text-center gap-5 border-t-4 border-emerald-500">
					<div class="flex flex-col items-center gap-2">
						<div
							class="w-16 h-16 rounded-2xl flex items-center justify-center text-2xl font-black text-white shadow-xl"
							style="background: linear-gradient(135deg, var(--accent-green), #16a34a);"
						>
							{homeTeam?.name?.[0]?.toUpperCase() ?? 'L'}
						</div>
						<div>
							<h2 class="text-2xl font-black text-white">{homeTeam?.name ?? 'Equipo Local'}</h2>
							<p class="text-xs font-mono font-bold text-slate-400 uppercase tracking-wider">
								{homeTeam?.short_name ?? 'LOC'} • LOCAL
							</p>
						</div>
					</div>

					<!-- Visualizador gigante del marcador -->
					<div class="py-2">
						<span class="text-7xl sm:text-8xl font-black font-mono text-emerald-400">
							{liveHomeScore}
						</span>
					</div>

					<!-- Botones táctiles -->
					<div class="flex items-center gap-3 w-full max-w-xs">
						<button
							onclick={() => adjustScore('home', -1)}
							disabled={activeMatch.status === 'finished' || liveHomeScore <= 0}
							class="p-4 rounded-xl font-black text-lg bg-slate-800 hover:bg-slate-700 text-slate-300 disabled:opacity-30 disabled:cursor-not-allowed transition"
							title="Restar gol"
						>
							-1
						</button>

						<button
							onclick={() => adjustScore('home', 1)}
							disabled={activeMatch.status === 'finished'}
							class="flex-1 py-4 px-6 rounded-xl font-black text-lg text-white bg-emerald-600 hover:bg-emerald-500 shadow-xl shadow-emerald-950/80 active:scale-95 disabled:opacity-30 disabled:cursor-not-allowed transition flex items-center justify-center gap-2"
						>
							<span>⚽</span>
							<span>+1 GOL</span>
						</button>
					</div>
				</div>

				<!-- EQUIPO VISITANTE -->
				<div class="glass-card p-6 sm:p-8 flex flex-col items-center text-center gap-5 border-t-4 border-blue-500">
					<div class="flex flex-col items-center gap-2">
						<div
							class="w-16 h-16 rounded-2xl flex items-center justify-center text-2xl font-black text-white shadow-xl"
							style="background: linear-gradient(135deg, #3b82f6, #1d4ed8);"
						>
							{awayTeam?.name?.[0]?.toUpperCase() ?? 'V'}
						</div>
						<div>
							<h2 class="text-2xl font-black text-white">{awayTeam?.name ?? 'Equipo Visitante'}</h2>
							<p class="text-xs font-mono font-bold text-slate-400 uppercase tracking-wider">
								{awayTeam?.short_name ?? 'VIS'} • VISITANTE
							</p>
						</div>
					</div>

					<!-- Visualizador gigante del marcador -->
					<div class="py-2">
						<span class="text-7xl sm:text-8xl font-black font-mono text-blue-400">
							{liveAwayScore}
						</span>
					</div>

					<!-- Botones táctiles -->
					<div class="flex items-center gap-3 w-full max-w-xs">
						<button
							onclick={() => adjustScore('away', -1)}
							disabled={activeMatch.status === 'finished' || liveAwayScore <= 0}
							class="p-4 rounded-xl font-black text-lg bg-slate-800 hover:bg-slate-700 text-slate-300 disabled:opacity-30 disabled:cursor-not-allowed transition"
							title="Restar gol"
						>
							-1
						</button>

						<button
							onclick={() => adjustScore('away', 1)}
							disabled={activeMatch.status === 'finished'}
							class="flex-1 py-4 px-6 rounded-xl font-black text-lg text-white bg-blue-600 hover:bg-blue-500 shadow-xl shadow-blue-950/80 active:scale-95 disabled:opacity-30 disabled:cursor-not-allowed transition flex items-center justify-center gap-2"
						>
							<span>⚽</span>
							<span>+1 GOL</span>
						</button>
					</div>
				</div>
			</div>
		</div>

	<!-- ── CASO B: SELECTOR DE PARTIDOS POR JORNADA ───────────────────────────── -->
	{:else}
		{#if rounds.length === 0}
			<!-- Sin fixture: Ofrecer botón para generarlo -->
			<div class="glass-card p-12 text-center max-w-xl mx-auto animate-fade-in-up">
				<div class="text-6xl mb-4">📅</div>
				<h2 class="text-2xl font-bold text-white mb-2">Fixture no generado aún</h2>
				<p class="text-slate-400 text-sm mb-6">
					Para usar la mesa de control de partidos, primero debes generar el fixture del torneo (se requiere al menos 2 equipos).
				</p>

				<button
					onclick={handleGenerateFixture}
					disabled={generatingFixture}
					class="px-6 py-3 rounded-xl font-bold text-white bg-emerald-600 hover:bg-emerald-500 shadow-lg shadow-emerald-950 transition flex items-center justify-center gap-2 mx-auto"
				>
					{#if generatingFixture}
						<span class="w-4 h-4 border-2 border-white border-t-transparent rounded-full animate-spin"></span>
						<span>Generando calendario Round-Robin...</span>
					{:else}
						<span>⚡ Generar Fixture Automático</span>
					{/if}
				</button>
			</div>

		{:else}
			<!-- Selector de Jornadas -->
			<div class="flex items-center gap-2 overflow-x-auto pb-4 mb-6">
				{#each rounds as r}
					{@const mday = r.matchday ?? r.round ?? 1}
					<button
						onclick={() => (selectedRound = mday)}
						class="px-4 py-2 rounded-lg font-semibold text-sm transition-colors whitespace-nowrap {selectedRound === mday
							? 'bg-emerald-600 text-white shadow-md shadow-emerald-950/50'
							: 'bg-slate-800/80 text-slate-300 hover:text-white hover:bg-slate-700 border border-slate-700/60'}"
					>
						Jornada {mday}
					</button>
				{/each}
			</div>

			<!-- Lista de Partidos de la Jornada -->
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

						<!-- Enfrentamiento y marcador -->
						<div class="flex items-center justify-between gap-4 py-2">
							<!-- Local -->
							<div class="flex-1 text-center sm:text-left">
								<p class="font-bold text-white text-base truncate">
									{homeTeam?.name ?? `Equipo #${match.home_team_id}`}
								</p>
								<p class="text-xs text-slate-500 font-mono">{homeTeam?.short_name ?? 'LOC'}</p>
							</div>

							<!-- Marcador central -->
							<div class="px-4 py-1.5 rounded-xl bg-slate-900 border border-slate-800 text-center min-w-[70px]">
								{#if match.home_score !== null && match.away_score !== null}
									<span class="text-xl font-black font-mono text-emerald-400">
										{match.home_score} - {match.away_score}
									</span>
								{:else}
									<span class="text-sm font-bold text-slate-500">VS</span>
								{/if}
							</div>

							<!-- Visitante -->
							<div class="flex-1 text-center sm:text-right">
								<p class="font-bold text-white text-base truncate">
									{awayTeam?.name ?? `Equipo #${match.away_team_id}`}
								</p>
								<p class="text-xs text-slate-500 font-mono">{awayTeam?.short_name ?? 'VIS'}</p>
							</div>
						</div>

						<!-- Botón para abrir la consola del partido -->
						<button
							onclick={() => selectMatch(match)}
							class="w-full py-2.5 px-4 rounded-xl text-xs font-bold transition flex items-center justify-center gap-2 {(match.status ?? '').toLowerCase() === 'live'
								? 'bg-emerald-600 hover:bg-emerald-500 text-white shadow-md shadow-emerald-950'
								: 'bg-slate-800 hover:bg-slate-700 text-slate-200'}"
						>
							<span>🎮</span>
							<span>{(match.status ?? '').toLowerCase() === 'finished' ? 'Ver Registro de Arbitraje' : 'Arbitrar y Controlar Partido'}</span>
						</button>
					</div>
				{/each}
			</div>
		{/if}
	{/if}
</div>

<!-- ── MODAL: CONFIRMACIÓN DE FINALIZACIÓN DE PARTIDO ──────────────────────── -->
{#if showFinishModal && activeMatch}
	{@const homeTeam = teamsMap[activeMatch.home_team_id]}
	{@const awayTeam = teamsMap[activeMatch.away_team_id]}

	<div
		class="fixed inset-0 z-50 flex items-center justify-center p-4 bg-slate-950/80 backdrop-blur-sm animate-fade-in-up"
		role="dialog"
		aria-modal="true"
	>
		<div class="glass-card w-full max-w-md p-6 flex flex-col gap-5 border border-slate-700 shadow-2xl">
			<div class="text-center">
				<div class="text-4xl mb-2">🏁</div>
				<h3 class="text-xl font-black text-white">¿Finalizar Partido Oficial?</h3>
				<p class="text-xs text-slate-400 mt-1">
					Revisa el marcador final antes de cerrar el acta del partido.
				</p>
			</div>

			<!-- Resumen del marcador final -->
			<div class="p-4 rounded-xl bg-slate-900/90 border border-slate-800 text-center">
				<p class="text-xs text-slate-500 uppercase font-semibold mb-2">Resultado Final a Registrar</p>
				<div class="flex items-center justify-center gap-4 text-xl font-black text-white">
					<span class="truncate">{homeTeam?.name ?? 'Local'}</span>
					<span class="text-3xl font-mono text-emerald-400 px-3 py-1 rounded bg-slate-950 border border-slate-800">
						{liveHomeScore} - {liveAwayScore}
					</span>
					<span class="truncate">{awayTeam?.name ?? 'Visitante'}</span>
				</div>
			</div>

			<p class="text-xs text-slate-400 bg-emerald-500/10 border border-emerald-500/20 p-3 rounded-lg leading-relaxed">
				ℹ️ Al confirmar el cierre, el estado del partido cambiará a <strong>FINALIZADO</strong> y la tabla de posiciones del torneo se recalculará automáticamente con los puntos y goles correspondientes.
			</p>

			<!-- Botones de acción -->
			<div class="flex items-center justify-end gap-3 pt-2">
				<button
					type="button"
					onclick={() => (showFinishModal = false)}
					disabled={isClosingMatch}
					class="px-4 py-2 rounded-lg text-sm font-semibold text-slate-400 hover:text-white transition"
				>
					Seguir jugando
				</button>

				<button
					type="button"
					onclick={confirmFinishMatch}
					disabled={isClosingMatch}
					class="px-5 py-2.5 rounded-lg text-sm font-bold text-white bg-amber-600 hover:bg-amber-500 shadow-lg shadow-amber-950 transition flex items-center gap-2 disabled:opacity-50"
				>
					{#if isClosingMatch}
						<span class="w-4 h-4 border-2 border-white border-t-transparent rounded-full animate-spin"></span>
						<span>Cerrando partido...</span>
					{:else}
						<span>Confirmar Cierre</span>
					{/if}
				</button>
			</div>
		</div>
	</div>
{/if}
