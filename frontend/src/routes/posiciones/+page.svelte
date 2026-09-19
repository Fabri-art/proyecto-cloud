<script>
	/**
	 * routes/posiciones/+page.svelte — Tabla de Posiciones (/posiciones)
	 *
	 * Muestra tablas separadas por disciplina: Fútbol, Básquetbol, Vóley.
	 */
	import { onMount } from 'svelte';
	import { standingsApi, teamsApi } from '$lib/api/client';
	import { toast } from '$lib/stores/toast';

	const TOURNAMENT_ID = 1;

	let standings = $state([]);
	let teamsMap = $state({});
	let loading = $state(true);
	let error = $state(null);
	let selectedSport = $state('all'); // 'all' | 'football' | 'basketball' | 'volleyball'
	let footballStandings = $derived(
		standings.filter((s) => (teamsMap[s.team_id]?.sport || 'football') === 'football')
	);
	let basketballStandings = $derived(
		standings.filter((s) => teamsMap[s.team_id]?.sport === 'basketball')
	);
	let volleyballStandings = $derived(
		standings.filter((s) => teamsMap[s.team_id]?.sport === 'volleyball')
	);

	onMount(async () => {
		try {
			const [standingsData, teamsList] = await Promise.all([
				standingsApi.get(TOURNAMENT_ID).catch(() => []),
				teamsApi.list(TOURNAMENT_ID).catch(() => [])
			]);

			const map = {};
			for (const t of teamsList) {
				map[t.id] = t;
			}
			teamsMap = map;
			standings = standingsData;
		} catch (e) {
			error = e.message;
			toast.error('No se pudo cargar la tabla de posiciones.');
		} finally {
			loading = false;
		}
	});

	// Calcula la diferencia de gol
	function goalDiff(s) {
		const diff = (s.goals_for ?? 0) - (s.goals_against ?? 0);
		return diff > 0 ? `+${diff}` : `${diff}`;
	}

	// Clase de fila según posición
	function rowClass(index) {
		if (index === 0) return 'border-l-2 border-emerald-500'; // Líder
		if (index === 1) return 'border-l-2 border-slate-400';   // 2do
		if (index === 2) return 'border-l-2 border-amber-600';   // 3ro
		return '';
	}
</script>

<svelte:head>
	<title>Posiciones — Torneo Hub</title>
	<meta name="description" content="Tabla de posiciones del torneo con estadísticas completas de cada equipo." />
</svelte:head>

<!-- ══ Encabezado ══════════════════════════════════════════════════════════ -->
<div class="mb-8 animate-fade-in-up">
	<h1 class="text-3xl font-black text-white flex items-center gap-3">🏆 Tabla de Posiciones</h1>
	<p class="text-slate-400 mt-1">Clasificación actualizada en tiempo real</p>
</div>

<!-- ══ Estado: cargando ════════════════════════════════════════════════════ -->
{#if loading}
	<div class="glass-card overflow-hidden">
		<div class="skeleton h-10 w-full rounded-t-xl mb-px"></div>
		{#each Array(6) as _}
			<div class="skeleton h-14 w-full mb-px"></div>
		{/each}
	</div>

<!-- ══ Estado: error ═══════════════════════════════════════════════════════ -->
{:else if error}
	<div class="glass-card p-8 text-center">
		<div class="text-4xl mb-3">⚠️</div>
		<p class="text-white font-semibold">No se pudo cargar la tabla</p>
		<p class="text-slate-400 text-sm mt-2">{error}</p>
	</div>

<!-- ══ Sin datos ═══════════════════════════════════════════════════════════ -->
{:else if standings.length === 0}
	<div class="glass-card p-12 text-center animate-fade-in-up">
		<div class="text-5xl mb-4">🏆</div>
		<h2 class="text-xl font-bold text-white mb-2">Sin estadísticas todavía</h2>
		<p class="text-slate-400 text-sm">
			Las posiciones se actualizan automáticamente cuando se registran resultados de partidos.
		</p>
	</div>

<!-- ══ Tablas de posiciones por disciplina ════════════════════════════════ -->
{:else}
	<!-- Filtro de disciplina -->
	<div class="flex items-center gap-2 mb-8 p-1.5 bg-slate-900/90 rounded-2xl border border-slate-800 w-fit backdrop-blur-sm shadow-xl">
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
			<span class="text-[10px] px-1.5 py-0.5 rounded-full bg-black/40 font-mono">{footballStandings.length}</span>
		</button>
		<button
			type="button"
			onclick={() => (selectedSport = 'basketball')}
			class="px-4 py-2 rounded-xl text-xs font-bold transition-all flex items-center gap-2 {selectedSport === 'basketball' ? 'bg-amber-600 text-white shadow-md shadow-amber-950/40' : 'text-slate-400 hover:text-white'}"
		>
			<span>🏀</span>
			<span>Básquetbol</span>
			<span class="text-[10px] px-1.5 py-0.5 rounded-full bg-black/40 font-mono">{basketballStandings.length}</span>
		</button>
		<button
			type="button"
			onclick={() => (selectedSport = 'volleyball')}
			class="px-4 py-2 rounded-xl text-xs font-bold transition-all flex items-center gap-2 {selectedSport === 'volleyball' ? 'bg-violet-600 text-white shadow-md shadow-violet-950/40' : 'text-slate-400 hover:text-white'}"
		>
			<span>🏐</span>
			<span>Vóley</span>
			<span class="text-[10px] px-1.5 py-0.5 rounded-full bg-black/40 font-mono">{volleyballStandings.length}</span>
		</button>
	</div>

	<div class="flex flex-col gap-8">

	<!-- ══ Tabla Fútbol ════════════════════════════════════════════════════ -->
	{#if (selectedSport === 'all' || selectedSport === 'football') && footballStandings.length > 0}
		<div class="glass-card overflow-hidden animate-fade-in-up">
			<!-- Cabecera de sección -->
			<div class="px-5 py-3 border-b border-slate-800 flex items-center gap-3" style="background: rgba(16,185,129,0.08);">
				<span class="text-2xl">⚽</span>
				<h2 class="font-black text-white text-lg">Fútbol</h2>
				<span class="text-xs px-2.5 py-0.5 rounded-full bg-emerald-500/15 text-emerald-300 border border-emerald-500/25 font-semibold ml-auto">{footballStandings.length} equipos</span>
			</div>
			<!-- Leyenda -->
			<div class="px-4 pt-3 pb-1 flex gap-4 text-xs text-slate-500">
				<span class="flex items-center gap-1"><span class="w-2 h-2 rounded bg-emerald-500 inline-block"></span> Líder</span>
				<span class="flex items-center gap-1"><span class="w-2 h-2 rounded bg-slate-400 inline-block"></span> 2do lugar</span>
				<span class="flex items-center gap-1"><span class="w-2 h-2 rounded bg-amber-600 inline-block"></span> 3er lugar</span>
			</div>
			<!-- Tabla -->
			<div class="overflow-x-auto">
				<table class="w-full text-sm">
					<thead>
						<tr class="text-xs text-slate-400 uppercase tracking-wider" style="border-bottom: 1px solid var(--border-color); background: rgba(15,23,42,0.5);">
							<th class="px-4 py-3 text-left w-8">#</th>
							<th class="px-4 py-3 text-left">Equipo</th>
							<th class="px-3 py-3 text-center" title="Partidos Jugados">PJ</th>
							<th class="px-3 py-3 text-center" title="Partidos Ganados">PG</th>
							<th class="px-3 py-3 text-center" title="Empates">PE</th>
							<th class="px-3 py-3 text-center" title="Partidos Perdidos">PP</th>
							<th class="px-3 py-3 text-center" title="Goles a Favor">GF</th>
							<th class="px-3 py-3 text-center" title="Goles en Contra">GC</th>
							<th class="px-3 py-3 text-center" title="Diferencia de Gol">DG</th>
							<th class="px-3 py-3 text-center font-bold" title="Puntos">PTS</th>
						</tr>
					</thead>
					<tbody>
						{#each footballStandings as s, i}
							<tr class="standings-row transition-colors {rowClass(i)}" style="border-bottom: 1px solid var(--border-color); animation: fadeInUp 0.3s {i * 0.05}s both;">
								<td class="px-4 py-3 text-center">
									{#if i === 0}<span class="text-base">🥇</span>
									{:else if i === 1}<span class="text-base">🥈</span>
									{:else if i === 2}<span class="text-base">🥉</span>
									{:else}<span class="text-slate-500 font-mono">{i + 1}</span>{/if}
								</td>
								<td class="px-4 py-3">
									<div class="flex items-center gap-3">
										<div class="w-8 h-8 rounded-full flex items-center justify-center text-sm font-black text-white shrink-0" style="background: linear-gradient(135deg, #10b981, #16a34a);">
											{teamsMap[s.team_id]?.name?.[0]?.toUpperCase() ?? '?'}
										</div>
										<span class="font-semibold text-white">{teamsMap[s.team_id]?.name ?? `Equipo #${s.team_id}`}</span>
									</div>
								</td>
								<td class="px-3 py-3 text-center text-slate-300">{s.played ?? 0}</td>
								<td class="px-3 py-3 text-center text-emerald-400 font-medium">{s.won ?? 0}</td>
								<td class="px-3 py-3 text-center text-slate-400">{s.drawn ?? 0}</td>
								<td class="px-3 py-3 text-center text-red-400">{s.lost ?? 0}</td>
								<td class="px-3 py-3 text-center text-slate-300">{s.goals_for ?? 0}</td>
								<td class="px-3 py-3 text-center text-slate-300">{s.goals_against ?? 0}</td>
								<td class="px-3 py-3 text-center font-mono text-slate-300">{goalDiff(s)}</td>
								<td class="px-3 py-3 text-center">
									<span class="font-black text-lg {i === 0 ? 'text-emerald-400' : 'text-white'}">{s.points ?? 0}</span>
								</td>
							</tr>
						{/each}
					</tbody>
				</table>
			</div>
			<div class="px-4 py-3 text-xs text-slate-600 border-t" style="border-color: var(--border-color);">
				Victoria = 3 pts &nbsp;|&nbsp; Empate = 1 pt &nbsp;|&nbsp; Derrota = 0 pts
			</div>
		</div>
	{/if}

	<!-- ══ Tabla Básquetbol ════════════════════════════════════════════════ -->
	{#if (selectedSport === 'all' || selectedSport === 'basketball') && basketballStandings.length > 0}
		<div class="glass-card overflow-hidden animate-fade-in-up">
			<div class="px-5 py-3 border-b border-slate-800 flex items-center gap-3" style="background: rgba(245,158,11,0.08);">
				<span class="text-2xl">🏀</span>
				<h2 class="font-black text-white text-lg">Básquetbol</h2>
				<span class="text-xs px-2.5 py-0.5 rounded-full bg-amber-500/15 text-amber-300 border border-amber-500/25 font-semibold ml-auto">{basketballStandings.length} equipos</span>
			</div>
			<div class="px-4 pt-3 pb-1 flex gap-4 text-xs text-slate-500">
				<span class="flex items-center gap-1"><span class="w-2 h-2 rounded bg-emerald-500 inline-block"></span> Líder</span>
				<span class="flex items-center gap-1"><span class="w-2 h-2 rounded bg-slate-400 inline-block"></span> 2do lugar</span>
				<span class="flex items-center gap-1"><span class="w-2 h-2 rounded bg-amber-600 inline-block"></span> 3er lugar</span>
			</div>
			<div class="overflow-x-auto">
				<table class="w-full text-sm">
					<thead>
						<tr class="text-xs text-slate-400 uppercase tracking-wider" style="border-bottom: 1px solid var(--border-color); background: rgba(15,23,42,0.5);">
							<th class="px-4 py-3 text-left w-8">#</th>
							<th class="px-4 py-3 text-left">Equipo</th>
							<th class="px-3 py-3 text-center" title="Partidos Jugados">PJ</th>
							<th class="px-3 py-3 text-center" title="Partidos Ganados">PG</th>
							<th class="px-3 py-3 text-center" title="Empates">PE</th>
							<th class="px-3 py-3 text-center" title="Partidos Perdidos">PP</th>
							<th class="px-3 py-3 text-center" title="Puntos a Favor">PF</th>
							<th class="px-3 py-3 text-center" title="Puntos en Contra">PC</th>
							<th class="px-3 py-3 text-center" title="Diferencia">DP</th>
							<th class="px-3 py-3 text-center font-bold" title="Puntos en Tabla">PTS</th>
						</tr>
					</thead>
					<tbody>
						{#each basketballStandings as s, i}
							<tr class="standings-row transition-colors {rowClass(i)}" style="border-bottom: 1px solid var(--border-color); animation: fadeInUp 0.3s {i * 0.05}s both;">
								<td class="px-4 py-3 text-center">
									{#if i === 0}<span class="text-base">🥇</span>
									{:else if i === 1}<span class="text-base">🥈</span>
									{:else if i === 2}<span class="text-base">🥉</span>
									{:else}<span class="text-slate-500 font-mono">{i + 1}</span>{/if}
								</td>
								<td class="px-4 py-3">
									<div class="flex items-center gap-3">
										<div class="w-8 h-8 rounded-full flex items-center justify-center text-sm font-black text-white shrink-0" style="background: linear-gradient(135deg, #f59e0b, #d97706);">
											{teamsMap[s.team_id]?.name?.[0]?.toUpperCase() ?? '?'}
										</div>
										<span class="font-semibold text-white">{teamsMap[s.team_id]?.name ?? `Equipo #${s.team_id}`}</span>
									</div>
								</td>
								<td class="px-3 py-3 text-center text-slate-300">{s.played ?? 0}</td>
								<td class="px-3 py-3 text-center text-emerald-400 font-medium">{s.won ?? 0}</td>
								<td class="px-3 py-3 text-center text-slate-400">{s.drawn ?? 0}</td>
								<td class="px-3 py-3 text-center text-red-400">{s.lost ?? 0}</td>
								<td class="px-3 py-3 text-center text-slate-300">{s.goals_for ?? 0}</td>
								<td class="px-3 py-3 text-center text-slate-300">{s.goals_against ?? 0}</td>
								<td class="px-3 py-3 text-center font-mono text-slate-300">{goalDiff(s)}</td>
								<td class="px-3 py-3 text-center">
									<span class="font-black text-lg {i === 0 ? 'text-amber-400' : 'text-white'}">{s.points ?? 0}</span>
								</td>
							</tr>
						{/each}
					</tbody>
				</table>
			</div>
			<div class="px-4 py-3 text-xs text-slate-600 border-t" style="border-color: var(--border-color);">
				Victoria = 2 pts &nbsp;|&nbsp; Derrota = 1 pt (llegando a 5 sets) &nbsp;|&nbsp; Derrota = 0 pts
			</div>
		</div>
	{/if}

	<!-- ══ Tabla Vóley ══════════════════════════════════════════════════════ -->
	{#if (selectedSport === 'all' || selectedSport === 'volleyball') && volleyballStandings.length > 0}
		<div class="glass-card overflow-hidden animate-fade-in-up">
			<div class="px-5 py-3 border-b border-slate-800 flex items-center gap-3" style="background: rgba(124,58,237,0.08);">
				<span class="text-2xl">🏐</span>
				<h2 class="font-black text-white text-lg">Vóley</h2>
				<span class="text-xs px-2.5 py-0.5 rounded-full bg-violet-500/15 text-violet-300 border border-violet-500/25 font-semibold ml-auto">{volleyballStandings.length} equipos</span>
			</div>
			<div class="px-4 pt-3 pb-1 flex gap-4 text-xs text-slate-500">
				<span class="flex items-center gap-1"><span class="w-2 h-2 rounded bg-emerald-500 inline-block"></span> Líder</span>
				<span class="flex items-center gap-1"><span class="w-2 h-2 rounded bg-slate-400 inline-block"></span> 2do lugar</span>
				<span class="flex items-center gap-1"><span class="w-2 h-2 rounded bg-amber-600 inline-block"></span> 3er lugar</span>
			</div>
			<div class="overflow-x-auto">
				<table class="w-full text-sm">
					<thead>
						<tr class="text-xs text-slate-400 uppercase tracking-wider" style="border-bottom: 1px solid var(--border-color); background: rgba(15,23,42,0.5);">
							<th class="px-4 py-3 text-left w-8">#</th>
							<th class="px-4 py-3 text-left">Equipo</th>
							<th class="px-3 py-3 text-center" title="Partidos Jugados">PJ</th>
							<th class="px-3 py-3 text-center" title="Partidos Ganados">PG</th>
							<th class="px-3 py-3 text-center" title="Empates">PE</th>
							<th class="px-3 py-3 text-center" title="Partidos Perdidos">PP</th>
							<th class="px-3 py-3 text-center" title="Sets a Favor">SF</th>
							<th class="px-3 py-3 text-center" title="Sets en Contra">SC</th>
							<th class="px-3 py-3 text-center" title="Diferencia">DS</th>
							<th class="px-3 py-3 text-center font-bold" title="Puntos en Tabla">PTS</th>
						</tr>
					</thead>
					<tbody>
						{#each volleyballStandings as s, i}
							<tr class="standings-row transition-colors {rowClass(i)}" style="border-bottom: 1px solid var(--border-color); animation: fadeInUp 0.3s {i * 0.05}s both;">
								<td class="px-4 py-3 text-center">
									{#if i === 0}<span class="text-base">🥇</span>
									{:else if i === 1}<span class="text-base">🥈</span>
									{:else if i === 2}<span class="text-base">🥉</span>
									{:else}<span class="text-slate-500 font-mono">{i + 1}</span>{/if}
								</td>
								<td class="px-4 py-3">
									<div class="flex items-center gap-3">
										<div class="w-8 h-8 rounded-full flex items-center justify-center text-sm font-black text-white shrink-0" style="background: linear-gradient(135deg, #7c3aed, #9333ea);">
											{teamsMap[s.team_id]?.name?.[0]?.toUpperCase() ?? '?'}
										</div>
										<span class="font-semibold text-white">{teamsMap[s.team_id]?.name ?? `Equipo #${s.team_id}`}</span>
									</div>
								</td>
								<td class="px-3 py-3 text-center text-slate-300">{s.played ?? 0}</td>
								<td class="px-3 py-3 text-center text-emerald-400 font-medium">{s.won ?? 0}</td>
								<td class="px-3 py-3 text-center text-slate-400">{s.drawn ?? 0}</td>
								<td class="px-3 py-3 text-center text-red-400">{s.lost ?? 0}</td>
								<td class="px-3 py-3 text-center text-slate-300">{s.goals_for ?? 0}</td>
								<td class="px-3 py-3 text-center text-slate-300">{s.goals_against ?? 0}</td>
								<td class="px-3 py-3 text-center font-mono text-slate-300">{goalDiff(s)}</td>
								<td class="px-3 py-3 text-center">
									<span class="font-black text-lg {i === 0 ? 'text-violet-400' : 'text-white'}">{s.points ?? 0}</span>
								</td>
							</tr>
						{/each}
					</tbody>
				</table>
			</div>
			<div class="px-4 py-3 text-xs text-slate-600 border-t" style="border-color: var(--border-color);">
				Victoria 3-0 / 3-1 = 3 pts &nbsp;|&nbsp; Victoria 3-2 = 2 pts &nbsp;|&nbsp; Derrota 2-3 = 1 pt &nbsp;|&nbsp; Derrota 0/1-3 = 0 pts
			</div>
		</div>
	{/if}

	<!-- Mensaje si no hay datos para el filtro seleccionado -->
	{#if selectedSport !== 'all'}
		{@const activeList = selectedSport === 'football' ? footballStandings : selectedSport === 'basketball' ? basketballStandings : volleyballStandings}
		{#if activeList.length === 0}
			<div class="glass-card p-10 text-center animate-fade-in-up">
				<div class="text-5xl mb-3">{selectedSport === 'football' ? '⚽' : selectedSport === 'basketball' ? '🏀' : '🏐'}</div>
				<p class="text-slate-400">No hay equipos de {selectedSport === 'football' ? 'fútbol' : selectedSport === 'basketball' ? 'básquetbol' : 'vóley'} con partidos registrados aún.</p>
			</div>
		{/if}
	{/if}

	</div>
{/if}
