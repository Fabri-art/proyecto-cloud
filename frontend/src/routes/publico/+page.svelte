<script>
	/**
	 * routes/publico/+page.svelte — Vista Pública para Hinchas y Jugadores (/publico)
	 * Rediseñada con estética deportiva profesional al estilo Sofascore/ESPN.
	 */
	import { onMount, onDestroy } from 'svelte';
	import { fixtureApi, standingsApi, teamsApi } from '$lib/api/client';

	const TOURNAMENT_ID = 1;
	const REFRESH_INTERVAL_MS = 30_000;
	const LIVE_REFRESH_INTERVAL_MS = 10_000;

	let activeTab = $state('fixture');
	let rounds = $state([]);
	let standings = $state([]);
	let teamsMap = $state({});
	let selectedRound = $state(1);
	let loading = $state(true);
	let lastUpdated = $state(null);
	let secondsSince = $state(0);
	let refreshTimer = null;
	let clockTimer = null;

	let currentMatches = $derived(
		rounds.find((r) => (r.matchday ?? r.round) === selectedRound)?.matches ?? []
	);

	let sortedMatches = $derived(
		[...currentMatches].sort((a, b) => {
			const rank = { live: 0, finished: 1, scheduled: 2 };
			const aR = rank[(a.status ?? '').toLowerCase()] ?? 2;
			const bR = rank[(b.status ?? '').toLowerCase()] ?? 2;
			return aR - bR;
		})
	);

	let hasLiveMatch = $derived(
		rounds.some((r) =>
			(r.matches ?? []).some((m) => (m.status ?? '').toLowerCase() === 'live')
		)
	);

	// Colores únicos por equipo (basado en hash del ID)
	const teamColors = ['#10b981','#3b82f6','#f59e0b','#8b5cf6','#ef4444','#06b6d4','#f97316','#ec4899'];
	function teamColor(id) { return teamColors[(id ?? 0) % teamColors.length]; }

	const statusConfig = {
		scheduled: { label: 'Programado', cls: 'badge-scheduled', icon: null },
		live:      { label: 'EN VIVO',    cls: 'badge-live',      icon: 'live' },
		finished:  { label: 'Finalizado', cls: 'badge-finished',  icon: null },
		cancelled: { label: 'Cancelado',  cls: 'badge-cancelled', icon: null },
		postponed: { label: 'Pospuesto',  cls: 'badge-scheduled', icon: null }
	};

	function getStatus(raw) {
		const key = (raw ?? 'scheduled').toLowerCase();
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
		const d = (s.goals_for ?? 0) - (s.goals_against ?? 0);
		return d > 0 ? `+${d}` : `${d}`;
	}

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
		} catch (_) {}
		finally { loading = false; }
	}

	onMount(() => {
		fetchAll();
		refreshTimer = setInterval(async () => {
			await fetchAll();
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

	function teamName(id) { return teamsMap[id]?.name ?? `Equipo #${id}`; }
	function teamShort(id) { return teamsMap[id]?.short_name ?? '???'; }
	function teamInitial(id) { return teamsMap[id]?.name?.[0]?.toUpperCase() ?? '?'; }

	// Porcentaje de progreso del refresh (para la barra)
	let refreshInterval = $derived(hasLiveMatch ? LIVE_REFRESH_INTERVAL_MS : REFRESH_INTERVAL_MS);
	let refreshProgress = $derived(Math.min(100, (secondsSince / (refreshInterval / 1000)) * 100));
</script>

<svelte:head>
	<title>Torneo Hub — Fixture & Posiciones</title>
	<meta name="description" content="Fixture y tabla de posiciones del torneo en tiempo real." />
</svelte:head>

<!-- ── ENCABEZADO ─────────────────────────────────────────────────────────── -->
<div class="mb-7 animate-fade-in-up">
	<div class="flex flex-col sm:flex-row sm:items-center justify-between gap-3">
		<div>
			<div class="flex items-center gap-3 mb-1">
				<h1 class="text-2xl sm:text-3xl font-black text-white tracking-tight font-display">
					Vista Pública
				</h1>
				{#if hasLiveMatch}
					<span class="live-badge-pill">
						<span class="live-dot"></span> EN VIVO
					</span>
				{/if}
			</div>
			<p class="text-slate-500 text-sm">Torneo Hub · Fixture y clasificación en tiempo real</p>
		</div>

		<!-- Refresh indicator -->
		{#if lastUpdated}
			<div class="flex flex-col items-end gap-1.5">
				<div class="flex items-center gap-2 text-xs text-slate-500">
					<span class="w-1.5 h-1.5 rounded-full {hasLiveMatch ? 'bg-emerald-400' : 'bg-slate-600'}"></span>
					{secondsSince < 5 ? 'Actualizado ahora' : `Hace ${secondsSince}s`}
				</div>
				<!-- Barra de progreso de refresh -->
				<div class="w-24 h-0.5 rounded-full overflow-hidden" style="background: rgba(148,163,184,0.12);">
					<div class="h-full rounded-full transition-all duration-1000 ease-linear"
						style="width: {refreshProgress}%; background: {hasLiveMatch ? '#10b981' : '#475569'};"></div>
				</div>
			</div>
		{/if}
	</div>
</div>

<!-- ── PESTAÑAS ───────────────────────────────────────────────────────────── -->
<div class="flex gap-0 p-1 bg-slate-900 rounded-xl border border-slate-800/80 mb-7 w-fit">
	<button
		onclick={() => (activeTab = 'fixture')}
		class="tab-pill {activeTab === 'fixture' ? 'tab-pill-active' : 'tab-pill-inactive'}"
	>
		<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 20 20" fill="currentColor" class="w-4 h-4 shrink-0">
			<path fill-rule="evenodd" d="M5.75 2a.75.75 0 0 1 .75.75V4h7V2.75a.75.75 0 0 1 1.5 0V4h.25A2.75 2.75 0 0 1 18 6.75v8.5A2.75 2.75 0 0 1 15.25 18H4.75A2.75 2.75 0 0 1 2 15.25v-8.5A2.75 2.75 0 0 1 4.75 4H5V2.75A.75.75 0 0 1 5.75 2Z" clip-rule="evenodd"/>
		</svg>
		Fixture
	</button>
	<button
		onclick={() => (activeTab = 'posiciones')}
		class="tab-pill {activeTab === 'posiciones' ? 'tab-pill-active' : 'tab-pill-inactive'}"
	>
		<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 20 20" fill="currentColor" class="w-4 h-4 shrink-0">
			<path d="M15.5 2A1.5 1.5 0 0 0 14 3.5v13a1.5 1.5 0 0 0 3 0v-13A1.5 1.5 0 0 0 15.5 2ZM9.5 6A1.5 1.5 0 0 0 8 7.5v9a1.5 1.5 0 0 0 3 0v-9A1.5 1.5 0 0 0 9.5 6ZM3.5 10A1.5 1.5 0 0 0 2 11.5v5a1.5 1.5 0 0 0 3 0v-5A1.5 1.5 0 0 0 3.5 10Z"/>
		</svg>
		Posiciones
	</button>
</div>

<!-- ── CARGANDO ────────────────────────────────────────────────────────────── -->
{#if loading}
	<div class="space-y-3">
		<div class="flex gap-2 mb-5">
			{#each Array(3) as _}
				<div class="skeleton h-9 w-28 rounded-lg"></div>
			{/each}
		</div>
		{#each Array(3) as _}
			<div class="skeleton h-28 w-full rounded-2xl"></div>
		{/each}
	</div>

{:else}

<!-- ════════ PESTAÑA: FIXTURE ══════════════════════════════════════════════════ -->
{#if activeTab === 'fixture'}
	{#if rounds.length === 0}
		<div class="glass-card p-16 text-center">
			<div class="text-5xl mb-4 opacity-30">📅</div>
			<h2 class="text-lg font-bold text-white mb-2">Fixture no disponible</h2>
			<p class="text-slate-500 text-sm">El fixture del torneo se publicará próximamente.</p>
		</div>
	{:else}
		<!-- Selector de jornadas tipo pill-scroll -->
		<div class="flex gap-2 mb-6 overflow-x-auto pb-1 scrollbar-hide">
			{#each rounds as r}
				{@const mday = r.matchday ?? r.round ?? 1}
				{@const hasLive = (r.matches ?? []).some((m) => (m.status ?? '').toLowerCase() === 'live')}
				<button
					onclick={() => (selectedRound = mday)}
					class="round-btn {selectedRound === mday ? 'round-btn-active' : 'round-btn-inactive'} flex-shrink-0"
				>
					{#if hasLive}<span class="live-dot"></span>{/if}
					J{mday}
				</button>
			{/each}
		</div>

		<!-- Tarjetas de partidos -->
		<div class="flex flex-col gap-3">
			{#each sortedMatches as match, i}
				{@const status = getStatus(match.status)}
				{@const isLive = (match.status ?? '').toLowerCase() === 'live'}
				{@const isFinished = (match.status ?? '').toLowerCase() === 'finished'}
				{@const hColor = teamColor(match.home_team_id)}
				{@const aColor = teamColor(match.away_team_id)}

				<div class="match-card-new {isLive ? 'match-card-live-border' : ''} animate-fade-in-up"
					style="animation-delay: {i * 0.04}s">

					<!-- Franja de estado lateral -->
					<div class="match-status-bar"
						style="background: {isLive ? '#10b981' : isFinished ? '#6366f1' : '#334155'};"></div>

					<div class="match-inner">
						<!-- Badge de estado + fecha -->
						<div class="flex items-center justify-between mb-3">
							<span class="status-pill {status.cls}">
								{#if isLive}<span class="live-dot"></span>{/if}
								{status.label}
							</span>
							{#if match.scheduled_at}
								<span class="text-xs text-slate-600">{formatDate(match.scheduled_at)}</span>
							{/if}
						</div>

						<!-- Equipos y marcador -->
						<div class="flex items-center justify-between gap-2">
							<!-- Local -->
							<div class="flex-1 flex flex-col sm:flex-row items-center sm:justify-end gap-2.5 text-center sm:text-right min-w-0">
								<div class="min-w-0">
									<p class="font-bold text-white text-sm sm:text-base leading-tight truncate">
										{teamName(match.home_team_id)}
									</p>
									<p class="text-xs font-mono" style="color: {hColor}; opacity: 0.8;">
										{teamShort(match.home_team_id)}
									</p>
								</div>
								<div class="team-shield" style="background: linear-gradient(135deg, {hColor}22, {hColor}44); border-color: {hColor}55; color: {hColor};">
									{teamInitial(match.home_team_id)}
								</div>
							</div>

							<!-- Marcador central -->
							<div class="score-center {isLive ? 'score-live' : isFinished ? 'score-done' : 'score-upcoming'}">
								{#if match.home_score !== null && match.away_score !== null}
									<span class="font-score text-2xl sm:text-3xl font-bold tabular-nums">
										{match.home_score}:{match.away_score}
									</span>
								{:else}
									<span class="text-slate-600 font-bold text-sm">VS</span>
								{/if}
							</div>

							<!-- Visitante -->
							<div class="flex-1 flex flex-col sm:flex-row items-center sm:justify-start gap-2.5 text-center sm:text-left min-w-0">
								<div class="team-shield" style="background: linear-gradient(135deg, {aColor}22, {aColor}44); border-color: {aColor}55; color: {aColor};">
									{teamInitial(match.away_team_id)}
								</div>
								<div class="min-w-0">
									<p class="font-bold text-white text-sm sm:text-base leading-tight truncate">
										{teamName(match.away_team_id)}
									</p>
									<p class="text-xs font-mono" style="color: {aColor}; opacity: 0.8;">
										{teamShort(match.away_team_id)}
									</p>
								</div>
							</div>
						</div>
					</div>
				</div>
			{/each}
		</div>
	{/if}
{/if}

<!-- ════════ PESTAÑA: POSICIONES ══════════════════════════════════════════════ -->
{#if activeTab === 'posiciones'}
	{#if standings.length === 0}
		<div class="glass-card p-16 text-center">
			<div class="text-5xl mb-4 opacity-30">📊</div>
			<h2 class="text-lg font-bold text-white mb-2">Sin datos todavía</h2>
			<p class="text-slate-500 text-sm">La tabla se completa automáticamente al finalizar partidos.</p>
		</div>
	{:else}
		<!-- Leyenda de posiciones -->
		<div class="flex flex-wrap items-center gap-4 mb-4 text-xs text-slate-500">
			<div class="flex items-center gap-1.5">
				<span class="w-2.5 h-2.5 rounded-sm bg-emerald-500"></span>
				<span>Líder</span>
			</div>
			<div class="flex items-center gap-1.5">
				<span class="w-2.5 h-2.5 rounded-sm bg-sky-500"></span>
				<span>2.º</span>
			</div>
			<div class="flex items-center gap-1.5">
				<span class="w-2.5 h-2.5 rounded-sm bg-amber-500"></span>
				<span>3.º</span>
			</div>
		</div>

		<div class="rounded-2xl overflow-hidden border border-slate-800">
			<div class="overflow-x-auto">
				<table class="w-full text-sm">
					<thead>
						<tr style="background: #0b1120; border-bottom: 1px solid #1e293b;">
							<th class="px-4 py-3 text-left text-xs section-label w-10">#</th>
							<th class="px-4 py-3 text-left text-xs section-label">Club</th>
							<th class="px-3 py-3 text-center text-xs section-label" title="Partidos Jugados">PJ</th>
							<th class="px-3 py-3 text-center text-xs section-label" title="Ganados">PG</th>
							<th class="px-3 py-3 text-center text-xs section-label" title="Empates">PE</th>
							<th class="px-3 py-3 text-center text-xs section-label" title="Perdidos">PP</th>
							<th class="px-3 py-3 text-center text-xs section-label hidden sm:table-cell" title="Goles Favor">GF</th>
							<th class="px-3 py-3 text-center text-xs section-label hidden sm:table-cell" title="Goles Contra">GC</th>
							<th class="px-3 py-3 text-center text-xs section-label hidden sm:table-cell" title="Diferencia">DG</th>
							<th class="px-4 py-3 text-center text-xs section-label">PTS</th>
						</tr>
					</thead>
					<tbody>
						{#each standings as s, i}
							{@const accentLeft = i === 0 ? '#10b981' : i === 1 ? '#38bdf8' : i === 2 ? '#f59e0b' : 'transparent'}
							{@const tColor = teamColor(s.team_id)}
							<tr class="standings-row border-b border-slate-800/50 transition-colors"
								style="border-left: 3px solid {accentLeft};">
								<!-- Posición -->
								<td class="px-4 py-3 text-center">
									{#if i === 0}
										<span class="text-base">🥇</span>
									{:else if i === 1}
										<span class="text-base">🥈</span>
									{:else if i === 2}
										<span class="text-base">🥉</span>
									{:else}
										<span class="text-xs text-slate-500 font-mono">{i + 1}</span>
									{/if}
								</td>

								<!-- Equipo -->
								<td class="px-4 py-3">
									<div class="flex items-center gap-3">
										<div class="w-8 h-8 rounded-lg flex items-center justify-center text-xs font-black shrink-0"
											style="background: {tColor}20; border: 1px solid {tColor}40; color: {tColor};">
											{teamInitial(s.team_id)}
										</div>
										<div>
											<p class="font-semibold text-white text-sm leading-tight">
												{teamName(s.team_id)}
											</p>
											<p class="text-xs text-slate-500 font-mono">{teamShort(s.team_id)}</p>
										</div>
									</div>
								</td>

								<td class="px-3 py-3 text-center text-slate-400 font-mono text-xs">{s.played ?? 0}</td>
								<td class="px-3 py-3 text-center font-semibold text-emerald-400 text-xs">{s.won ?? 0}</td>
								<td class="px-3 py-3 text-center text-slate-400 text-xs">{s.drawn ?? 0}</td>
								<td class="px-3 py-3 text-center text-rose-400 text-xs">{s.lost ?? 0}</td>
								<td class="px-3 py-3 text-center text-slate-400 text-xs hidden sm:table-cell">{s.goals_for ?? 0}</td>
								<td class="px-3 py-3 text-center text-slate-400 text-xs hidden sm:table-cell">{s.goals_against ?? 0}</td>
								<td class="px-3 py-3 text-center text-xs hidden sm:table-cell">
									<span class="font-mono font-semibold"
										style="color: {(s.goals_for??0)-(s.goals_against??0) >= 0 ? '#34d399' : '#f87171'}">
										{goalDiff(s)}
									</span>
								</td>
								<td class="px-4 py-3 text-center">
									<span class="font-score text-lg font-bold"
										style="color: {i === 0 ? '#10b981' : '#f1f5f9'}">
										{s.points ?? 0}
									</span>
								</td>
							</tr>
						{/each}
					</tbody>
				</table>
			</div>
			<!-- Pie de tabla -->
			<div class="px-4 py-2.5 border-t border-slate-800 text-xs text-slate-600">
				PJ = Jugados · PG = Ganados · PE = Empates · PP = Perdidos · GF = Goles Favor · GC = Goles Contra · DG = Diferencia · PTS = Puntos
			</div>
		</div>
	{/if}
{/if}

{/if}

<style>
	/* ── Pestañas ─────────────────────────────────────────────────────────────── */
	.tab-pill {
		display: flex;
		align-items: center;
		gap: 0.4rem;
		padding: 0.5rem 1.1rem;
		border-radius: 0.6rem;
		font-size: 0.85rem;
		font-weight: 600;
		transition: all 0.15s ease;
	}
	.tab-pill-active {
		background: #10b981;
		color: white;
		box-shadow: 0 2px 10px rgba(16,185,129,0.3);
	}
	.tab-pill-inactive { color: #64748b; }
	.tab-pill-inactive:hover { color: #e2e8f0; }

	/* ── Botones de jornada ─────────────────────────────────────────────────── */
	.round-btn {
		display: flex;
		align-items: center;
		gap: 0.4rem;
		padding: 0.4rem 0.85rem;
		border-radius: 0.5rem;
		font-size: 0.8rem;
		font-weight: 700;
		letter-spacing: 0.02em;
		transition: all 0.15s;
		white-space: nowrap;
	}
	.round-btn-active {
		background: #10b981;
		color: white;
		box-shadow: 0 2px 8px rgba(16,185,129,0.35);
	}
	.round-btn-inactive {
		background: #111827;
		color: #64748b;
		border: 1px solid rgba(148,163,184,0.12);
	}
	.round-btn-inactive:hover { color: #e2e8f0; border-color: rgba(148,163,184,0.25); }

	/* ── Tarjetas de partido ────────────────────────────────────────────────── */
	.match-card-new {
		display: flex;
		align-items: stretch;
		background: #111827;
		border: 1px solid rgba(148,163,184,0.08);
		border-radius: 1rem;
		overflow: hidden;
		transition: border-color 0.15s, box-shadow 0.15s;
	}
	.match-card-new:hover {
		border-color: rgba(148,163,184,0.2);
		box-shadow: 0 4px 20px rgba(0,0,0,0.2);
	}
	.match-card-live-border { border-color: rgba(16,185,129,0.3); }
	.match-card-live-border:hover { border-color: rgba(16,185,129,0.5); }

	.match-status-bar { width: 4px; flex-shrink: 0; }
	.match-inner { flex: 1; padding: 1rem 1.25rem; }

	/* Badge de estado en tarjeta de partido */
	.status-pill {
		display: inline-flex;
		align-items: center;
		gap: 0.35rem;
		font-size: 0.65rem;
		font-weight: 800;
		padding: 0.2rem 0.7rem;
		border-radius: 9999px;
		text-transform: uppercase;
		letter-spacing: 0.06em;
	}

	/* Escudo del equipo */
	.team-shield {
		width: 2.25rem;
		height: 2.25rem;
		border-radius: 0.5rem;
		border: 1.5px solid;
		display: flex;
		align-items: center;
		justify-content: center;
		font-size: 0.9rem;
		font-weight: 900;
		flex-shrink: 0;
	}

	/* Marcador central */
	.score-center {
		padding: 0.5rem 1rem;
		border-radius: 0.625rem;
		min-width: 80px;
		display: flex;
		align-items: center;
		justify-content: center;
		flex-shrink: 0;
	}
	.score-live   { background: rgba(16,185,129,0.12); border: 1.5px solid rgba(16,185,129,0.3); color: #34d399; }
	.score-done   { background: rgba(99,102,241,0.1);  border: 1.5px solid rgba(99,102,241,0.25); color: #a5b4fc; }
	.score-upcoming { background: #0b1120; border: 1.5px solid rgba(148,163,184,0.1); }

	/* Píldora LIVE del encabezado */
	.live-badge-pill {
		display: inline-flex;
		align-items: center;
		gap: 0.35rem;
		font-size: 0.65rem;
		font-weight: 800;
		padding: 0.25rem 0.7rem;
		border-radius: 9999px;
		background: rgba(16,185,129,0.15);
		color: #34d399;
		border: 1px solid rgba(16,185,129,0.3);
		letter-spacing: 0.08em;
		text-transform: uppercase;
	}
</style>
