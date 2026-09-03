<script>
	/**
	 * routes/publico/+page.svelte — Vista Pública para Hinchas y Jugadores (/publico)
	 *
	 * ¿Qué muestra?
	 * - Pestaña "Fixture": selector de jornadas + tarjetas de partidos con marcadores y badges.
	 * - Pestaña "Posiciones": tabla de clasificación con estadísticas oficiales.
	 *
	 * ¿Qué llama al backend?
	 * - GET /api/v1/tournaments/1/fixture   → fixture con rondas y partidos
	 * - GET /api/v1/tournaments/1/standings → tabla de posiciones
	 * - GET /api/v1/teams?tournament_id=1   → lista de equipos para mapear IDs a nombres
	 *
	 * Características:
	 * - Auto-refresh cada 30 segundos para datos en tiempo real.
	 * - Badge EN VIVO (⚽) para partidos con status === 'live'.
	 * - Solo lectura: sin botones de administración.
	 * - Optimizado para móvil.
	 */
	import { onMount, onDestroy } from 'svelte';
	import { fixtureApi, standingsApi, teamsApi } from '$lib/api/client';

	const TOURNAMENT_ID = 1;
	const REFRESH_INTERVAL_MS = 30_000; // 30 segundos en condiciones normales
	const LIVE_REFRESH_INTERVAL_MS = 10_000; // 10 segundos si hay partido en VIVO

	// ── Estado ─────────────────────────────────────────────────────────────────
	let activeTab = $state('fixture'); // 'fixture' | 'posiciones'

	let rounds = $state([]);
	let standings = $state([]);
	let teamsMap = $state({});
	let selectedRound = $state(1);

	let loading = $state(true);
	let lastUpdated = $state(null);   // Date del último fetch exitoso
	let secondsSince = $state(0);     // Segundos desde el último refresh

	let refreshTimer = null;
	let clockTimer = null;

	// ── Datos derivados ─────────────────────────────────────────────────────────
	let currentMatches = $derived(
		rounds.find((r) => (r.matchday ?? r.round) === selectedRound)?.matches ?? []
	);

	// Ordena partidos: primero los LIVE, luego el resto
	let sortedMatches = $derived(
		[...currentMatches].sort((a, b) => {
			const aLive = (a.status ?? '').toLowerCase() === 'live' ? -1 : 0;
			const bLive = (b.status ?? '').toLowerCase() === 'live' ? -1 : 0;
			return aLive - bLive;
		})
	);

	// ¿Hay algún partido en vivo en todo el fixture?
	let hasLiveMatch = $derived(
		rounds.some((r) =>
			(r.matches ?? []).some((m) => (m.status ?? '').toLowerCase() === 'live')
		)
	);

	// ── Configuración de estado visual ─────────────────────────────────────────
	const statusConfig = {
		scheduled: { label: 'Programado', badgeClass: 'badge-scheduled', icon: '🕐' },
		live:      { label: 'EN VIVO',    badgeClass: 'badge-live',      icon: '⚽' },
		finished:  { label: 'Finalizado', badgeClass: 'badge-finished',  icon: '✅' },
		cancelled: { label: 'Cancelado',  badgeClass: 'badge-cancelled', icon: '❌' },
		postponed: { label: 'Pospuesto',  badgeClass: 'badge-scheduled', icon: '⏸️' }
	};

	function getStatus(rawStatus) {
		const key = (rawStatus ?? 'scheduled').toLowerCase();
		return statusConfig[key] ?? statusConfig.scheduled;
	}

	function formatDate(dateStr) {
		if (!dateStr) return null;
		return new Date(dateStr).toLocaleDateString('es', {
			weekday: 'short', day: 'numeric', month: 'short',
			hour: '2-digit', minute: '2-digit'
		});
	}

	function goalDiff(s) {
		const diff = (s.goals_for ?? 0) - (s.goals_against ?? 0);
		return diff > 0 ? `+${diff}` : `${diff}`;
	}

	// ── Carga de datos ──────────────────────────────────────────────────────────
	async function fetchAll() {
		try {
			const [fixtureData, standingsData, teamsList] = await Promise.all([
				fixtureApi.get(TOURNAMENT_ID).catch(() => ({ rounds: [] })),
				standingsApi.get(TOURNAMENT_ID).catch(() => []),
				teamsApi.list(TOURNAMENT_ID).catch(() => [])
			]);

			const map = {};
			for (const t of teamsList) map[t.id] = t;
			teamsMap = map;

			rounds = fixtureData.rounds ?? [];
			standings = standingsData;

			// Selecciona automáticamente la jornada con partidos EN VIVO o la primera
			const liveRound = rounds.find((r) =>
				(r.matches ?? []).some((m) => (m.status ?? '').toLowerCase() === 'live')
			);
			if (liveRound) {
				selectedRound = liveRound.matchday ?? liveRound.round ?? 1;
			} else if (rounds.length > 0 && !rounds.some((r) => (r.matchday ?? r.round) === selectedRound)) {
				selectedRound = rounds[0].matchday ?? rounds[0].round ?? 1;
			}

			lastUpdated = new Date();
			secondsSince = 0;
		} catch (_) {
			// Silently fail on refresh errors to avoid disrupting the UI
		} finally {
			loading = false;
		}
	}

	// ── Ciclo de vida ───────────────────────────────────────────────────────────
	onMount(() => {
		fetchAll();

		// Intervalo dinámico: 10s si hay partido en VIVO, 30s en condiciones normales
		refreshTimer = setInterval(async () => {
			await fetchAll();
			// Reiniciar el intervalo si cambió el estado LIVE
			const interval = hasLiveMatch ? LIVE_REFRESH_INTERVAL_MS : REFRESH_INTERVAL_MS;
			clearInterval(refreshTimer);
			refreshTimer = setInterval(fetchAll, interval);
		}, hasLiveMatch ? LIVE_REFRESH_INTERVAL_MS : REFRESH_INTERVAL_MS);

		clockTimer = setInterval(() => { secondsSince++; }, 1000);
	});

	onDestroy(() => {
		if (refreshTimer) clearInterval(refreshTimer);
		if (clockTimer) clearInterval(clockTimer);
	});

	// Nombre del equipo con fallback
	function teamName(id) {
		return teamsMap[id]?.name ?? `Equipo #${id}`;
	}
	function teamShort(id) {
		return teamsMap[id]?.short_name ?? '---';
	}
	function teamInitial(id) {
		return teamsMap[id]?.name?.[0]?.toUpperCase() ?? '?';
	}
</script>

<svelte:head>
	<title>Vista Pública — Nombre-Creativo</title>
	<meta name="description" content="Fixture y tabla de posiciones del torneo en tiempo real. Consulta resultados, próximos partidos y clasificación actualizada." />
</svelte:head>

<!-- ── ENCABEZADO PÚBLICO ─────────────────────────────────────────────────── -->
<div class="mb-6">
	<div class="flex flex-col sm:flex-row sm:items-center justify-between gap-3">
		<div>
			<h1 class="text-3xl font-black text-white flex items-center gap-3">
				🌐 Vista Pública
				{#if hasLiveMatch}
					<span class="live-pill">⚽ EN VIVO</span>
				{/if}
			</h1>
			<p class="text-slate-400 mt-1 text-sm">Fixture y posiciones del torneo en tiempo real</p>
		</div>

		<!-- Indicador de última actualización -->
		{#if lastUpdated}
			<div class="flex items-center gap-2 text-xs text-slate-500 bg-slate-800/60 px-3 py-2 rounded-lg border border-slate-700/50">
				<span class="w-1.5 h-1.5 rounded-full {hasLiveMatch ? 'bg-emerald-400' : 'bg-slate-500'}"></span>
				{#if secondsSince < 5}
					<span>Actualizado ahora</span>
				{:else}
					<span>Actualizado hace {secondsSince}s</span>
				{/if}
				<span class="text-slate-600">· Refresca cada 30s</span>
			</div>
		{/if}
	</div>
</div>

<!-- ── SELECTOR DE PESTAÑAS ───────────────────────────────────────────────── -->
<div class="flex gap-1 p-1 bg-slate-800/60 rounded-xl border border-slate-700/40 mb-6 w-fit">
	<button
		onclick={() => (activeTab = 'fixture')}
		class="tab-btn {activeTab === 'fixture' ? 'tab-active' : 'tab-inactive'}"
	>
		📅 Fixture
	</button>
	<button
		onclick={() => (activeTab = 'posiciones')}
		class="tab-btn {activeTab === 'posiciones' ? 'tab-active' : 'tab-inactive'}"
	>
		📊 Posiciones
	</button>
</div>

<!-- ── ESTADO: CARGANDO ───────────────────────────────────────────────────── -->
{#if loading}
	<div class="space-y-3">
		<div class="skeleton h-10 w-full max-w-xs rounded-lg"></div>
		{#each Array(3) as _}
			<div class="skeleton h-24 w-full rounded-xl"></div>
		{/each}
	</div>

<!-- ── CONTENIDO PRINCIPAL ────────────────────────────────────────────────── -->
{:else}

	<!-- ════════════════════════════════════════════════════════════════════════ -->
	<!-- PESTAÑA: FIXTURE                                                       -->
	<!-- ════════════════════════════════════════════════════════════════════════ -->
	{#if activeTab === 'fixture'}
		{#if rounds.length === 0}
			<div class="glass-card p-12 text-center">
				<div class="text-5xl mb-4">📅</div>
				<h2 class="text-xl font-bold text-white mb-2">Fixture no disponible</h2>
				<p class="text-slate-400 text-sm">El fixture se publicará próximamente.</p>
			</div>
		{:else}
			<!-- Selector de jornadas -->
			<div class="flex flex-wrap gap-2 mb-5">
				{#each rounds as r}
					{@const mday = r.matchday ?? r.round ?? 1}
					{@const hasLive = (r.matches ?? []).some((m) => (m.status ?? '').toLowerCase() === 'live')}
					<button
						onclick={() => (selectedRound = mday)}
						class="px-4 py-2 rounded-lg text-sm font-semibold transition-colors flex items-center gap-1.5 {selectedRound === mday
							? 'bg-emerald-600 text-white shadow-md shadow-emerald-950/50'
							: 'bg-slate-800/80 text-slate-300 hover:text-white hover:bg-slate-700 border border-slate-700/60'}"
					>
						{#if hasLive}<span class="w-1.5 h-1.5 rounded-full bg-emerald-400 shrink-0"></span>{/if}
						Jornada {mday}
					</button>
				{/each}
			</div>

			<!-- Tarjetas de partidos -->
			<div class="flex flex-col gap-3">
				{#each sortedMatches as match}
					{@const status = getStatus(match.status)}
					{@const isLive = (match.status ?? '').toLowerCase() === 'live'}
					{@const isFinished = (match.status ?? '').toLowerCase() === 'finished'}

					<div class="match-card {isLive ? 'match-card-live' : ''}">
						<!-- Fila superior: estado + fecha -->
						<div class="flex items-center justify-between mb-4">
							<span class="status-badge {status.badgeClass}">
								{#if isLive}<span class="live-dot"></span>{/if}
								{status.icon} {status.label}
							</span>
							{#if match.scheduled_at}
								<span class="text-xs text-slate-500">{formatDate(match.scheduled_at)}</span>
							{/if}
						</div>

						<!-- Fila central: equipos y marcador -->
						<div class="flex items-center justify-between gap-3">
							<!-- Local -->
							<div class="flex-1 flex flex-col sm:flex-row items-center sm:justify-end gap-2 text-center sm:text-right">
								<div>
									<p class="font-bold text-white text-base sm:text-lg leading-tight">
										{teamName(match.home_team_id)}
									</p>
									<p class="text-xs text-slate-500 font-mono">{teamShort(match.home_team_id)} · Local</p>
								</div>
								<div class="team-avatar-home">{teamInitial(match.home_team_id)}</div>
							</div>

							<!-- Marcador central -->
							<div class="score-box {isLive ? 'score-box-live' : isFinished ? 'score-box-done' : 'score-box-upcoming'}">
								{#if match.home_score !== null && match.away_score !== null}
									<span class="text-2xl sm:text-3xl font-black font-mono tabular-nums">
										{match.home_score}–{match.away_score}
									</span>
								{:else}
									<span class="text-lg font-bold text-slate-500">VS</span>
								{/if}
							</div>

							<!-- Visitante -->
							<div class="flex-1 flex flex-col sm:flex-row items-center sm:justify-start gap-2 text-center sm:text-left">
								<div class="team-avatar-away">{teamInitial(match.away_team_id)}</div>
								<div>
									<p class="font-bold text-white text-base sm:text-lg leading-tight">
										{teamName(match.away_team_id)}
									</p>
									<p class="text-xs text-slate-500 font-mono">{teamShort(match.away_team_id)} · Visitante</p>
								</div>
							</div>
						</div>
					</div>
				{/each}
			</div>
		{/if}
	{/if}

	<!-- ════════════════════════════════════════════════════════════════════════ -->
	<!-- PESTAÑA: POSICIONES                                                    -->
	<!-- ════════════════════════════════════════════════════════════════════════ -->
	{#if activeTab === 'posiciones'}
		{#if standings.length === 0}
			<div class="glass-card p-12 text-center">
				<div class="text-5xl mb-4">📊</div>
				<h2 class="text-xl font-bold text-white mb-2">Sin estadísticas todavía</h2>
				<p class="text-slate-400 text-sm">
					La tabla se actualiza automáticamente al finalizar partidos.
				</p>
			</div>
		{:else}
			<!-- Leyenda -->
			<div class="flex flex-wrap gap-3 text-xs text-slate-500 mb-4">
				<span class="flex items-center gap-1.5"><span class="w-2 h-2 rounded-sm bg-emerald-500"></span>Líder</span>
				<span class="flex items-center gap-1.5"><span class="w-2 h-2 rounded-sm bg-slate-400"></span>2do lugar</span>
				<span class="flex items-center gap-1.5"><span class="w-2 h-2 rounded-sm bg-amber-500"></span>3er lugar</span>
			</div>

			<div class="glass-card overflow-hidden">
				<div class="overflow-x-auto">
					<table class="w-full text-sm">
						<thead>
							<tr class="text-xs text-slate-400 uppercase tracking-wider border-b border-slate-700/60 bg-slate-900/40">
								<th class="px-4 py-3 text-left w-10">#</th>
								<th class="px-4 py-3 text-left">Equipo</th>
								<th class="px-3 py-3 text-center" title="Partidos Jugados">PJ</th>
								<th class="px-3 py-3 text-center" title="Partidos Ganados">PG</th>
								<th class="px-3 py-3 text-center" title="Empates">PE</th>
								<th class="px-3 py-3 text-center" title="Partidos Perdidos">PP</th>
								<th class="px-3 py-3 text-center hidden sm:table-cell" title="Goles a Favor">GF</th>
								<th class="px-3 py-3 text-center hidden sm:table-cell" title="Goles en Contra">GC</th>
								<th class="px-3 py-3 text-center hidden sm:table-cell" title="Diferencia de Gol">DG</th>
								<th class="px-3 py-3 text-center font-bold" title="Puntos">PTS</th>
							</tr>
						</thead>
						<tbody>
							{#each standings as s, i}
								{@const accentClass = i === 0 ? 'border-l-2 border-emerald-500' : i === 1 ? 'border-l-2 border-slate-400' : i === 2 ? 'border-l-2 border-amber-500' : ''}
								<tr class="standings-row border-b border-slate-800/60 transition-colors {accentClass}">
									<!-- Posición con medalla -->
									<td class="px-4 py-3 text-center">
										{#if i === 0}
											<span class="text-base">🥇</span>
										{:else if i === 1}
											<span class="text-base">🥈</span>
										{:else if i === 2}
											<span class="text-base">🥉</span>
										{:else}
											<span class="text-slate-500 font-mono text-xs">{i + 1}</span>
										{/if}
									</td>

									<!-- Equipo -->
									<td class="px-4 py-3">
										<div class="flex items-center gap-3">
											<div class="w-8 h-8 rounded-lg flex items-center justify-center text-sm font-black text-white shrink-0
												{i === 0 ? 'bg-emerald-700' : i === 1 ? 'bg-slate-600' : i === 2 ? 'bg-amber-700' : 'bg-slate-700'}">
												{teamInitial(s.team_id)}
											</div>
											<div>
												<span class="font-semibold text-white block leading-tight">
													{teamName(s.team_id)}
												</span>
												<span class="text-xs text-slate-500 font-mono">{teamShort(s.team_id)}</span>
											</div>
										</div>
									</td>

									<!-- Estadísticas -->
									<td class="px-3 py-3 text-center text-slate-300">{s.played ?? 0}</td>
									<td class="px-3 py-3 text-center font-medium text-emerald-400">{s.won ?? 0}</td>
									<td class="px-3 py-3 text-center text-slate-400">{s.drawn ?? 0}</td>
									<td class="px-3 py-3 text-center text-red-400">{s.lost ?? 0}</td>
									<td class="px-3 py-3 text-center text-slate-300 hidden sm:table-cell">{s.goals_for ?? 0}</td>
									<td class="px-3 py-3 text-center text-slate-300 hidden sm:table-cell">{s.goals_against ?? 0}</td>
									<td class="px-3 py-3 text-center font-mono text-slate-300 hidden sm:table-cell">{goalDiff(s)}</td>

									<!-- Puntos (resaltado) -->
									<td class="px-3 py-3 text-center">
										<span class="font-black text-xl {i === 0 ? 'text-emerald-400' : 'text-white'}">
											{s.points ?? 0}
										</span>
									</td>
								</tr>
							{/each}
						</tbody>
					</table>
				</div>

				<!-- Pie con leyenda de puntos -->
				<div class="px-4 py-3 text-xs text-slate-600 border-t border-slate-800/60">
					Victoria = 3 pts &nbsp;|&nbsp; Empate = 1 pt &nbsp;|&nbsp; Derrota = 0 pts
					&nbsp;·&nbsp; PJ=Jugados · PG=Ganados · PE=Empates · PP=Perdidos · GF=Goles Favor · GC=Goles Contra · DG=Diferencia
				</div>
			</div>
		{/if}
	{/if}
{/if}

<style>
	/* Pestañas */
	.tab-btn {
		padding: 0.5rem 1.25rem;
		border-radius: 0.625rem;
		font-size: 0.875rem;
		font-weight: 600;
		transition: all 0.15s;
		white-space: nowrap;
	}
	.tab-active {
		background: #059669;
		color: white;
		box-shadow: 0 2px 8px rgba(5, 150, 105, 0.35);
	}
	.tab-inactive {
		color: #94a3b8;
	}
	.tab-inactive:hover {
		color: white;
	}

	/* Tarjeta de partido normal */
	.match-card {
		background: #162032;
		border: 1px solid rgba(148, 163, 184, 0.1);
		border-radius: 0.875rem;
		padding: 1.125rem 1.25rem;
		transition: border-color 0.15s;
	}

	/* Tarjeta de partido EN VIVO */
	.match-card-live {
		border-color: rgba(16, 185, 129, 0.4);
		background: linear-gradient(135deg, #162032, #0d2218);
	}

	/* Badge de estado de partido */
	.status-badge {
		display: inline-flex;
		align-items: center;
		gap: 0.35rem;
		font-size: 0.7rem;
		font-weight: 700;
		padding: 0.25rem 0.75rem;
		border-radius: 9999px;
		text-transform: uppercase;
		letter-spacing: 0.04em;
	}
	.badge-scheduled { background: rgba(148,163,184,0.12); color: #94a3b8; }
	.badge-live      { background: rgba(16,185,129,0.2);   color: #34d399; }
	.badge-finished  { background: rgba(99,102,241,0.15);  color: #a5b4fc; }
	.badge-cancelled { background: rgba(239,68,68,0.15);   color: #f87171; }

	/* Punto pulsante para partidos en vivo */
	.live-dot {
		display: inline-block;
		width: 6px;
		height: 6px;
		border-radius: 50%;
		background: #34d399;
		animation: live-pulse 1.4s ease-in-out infinite;
		flex-shrink: 0;
	}
	@keyframes live-pulse {
		0%, 100% { opacity: 1; transform: scale(1); }
		50%       { opacity: 0.4; transform: scale(0.75); }
	}

	/* Píldora "EN VIVO" en el encabezado */
	.live-pill {
		font-size: 0.7rem;
		font-weight: 800;
		padding: 0.2rem 0.6rem;
		border-radius: 9999px;
		background: rgba(16, 185, 129, 0.2);
		color: #34d399;
		border: 1px solid rgba(16, 185, 129, 0.35);
		letter-spacing: 0.05em;
		text-transform: uppercase;
	}

	/* Avatares de equipo */
	.team-avatar-home {
		width: 2.25rem;
		height: 2.25rem;
		border-radius: 0.5rem;
		background: linear-gradient(135deg, #059669, #047857);
		display: flex;
		align-items: center;
		justify-content: center;
		font-size: 1rem;
		font-weight: 900;
		color: white;
		flex-shrink: 0;
	}
	.team-avatar-away {
		width: 2.25rem;
		height: 2.25rem;
		border-radius: 0.5rem;
		background: linear-gradient(135deg, #3b82f6, #1d4ed8);
		display: flex;
		align-items: center;
		justify-content: center;
		font-size: 1rem;
		font-weight: 900;
		color: white;
		flex-shrink: 0;
	}

	/* Recuadro central del marcador */
	.score-box {
		padding: 0.5rem 1.25rem;
		border-radius: 0.75rem;
		text-align: center;
		min-width: 90px;
		display: flex;
		align-items: center;
		justify-content: center;
	}
	.score-box-live {
		background: rgba(16, 185, 129, 0.15);
		border: 1px solid rgba(16, 185, 129, 0.4);
		color: #34d399;
	}
	.score-box-done {
		background: rgba(99, 102, 241, 0.1);
		border: 1px solid rgba(99, 102, 241, 0.25);
		color: #a5b4fc;
	}
	.score-box-upcoming {
		background: #0b0f19;
		border: 1px solid rgba(148, 163, 184, 0.12);
		color: #64748b;
	}
</style>
