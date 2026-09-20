<script>
	/**
	 * routes/posiciones/+page.svelte
	 * Tablas separadas por disciplina: Futbol | Basquetbol | Voley
	 */
	import { onMount } from 'svelte';
	import { standingsApi, teamsApi } from '$lib/api/client';
	import { toast } from '$lib/stores/toast';

	const TOURNAMENT_ID = 1;

	let standings = $state([]);
	let teamsMap = $state({});
	let loading = $state(true);
	let error = $state(null);
	let selectedSport = $state('all');

	function getSportStandings(sport) {
		const sportTeams = Object.values(teamsMap).filter((t) => (t.sport || 'football') === sport);
		const existingMap = new Map((standings || []).map((s) => [s.team_id, s]));

		const list = sportTeams.map((t) => {
			const s = existingMap.get(t.id);
			if (s) return s;
			return {
				team_id: t.id,
				played: 0,
				won: 0,
				drawn: 0,
				lost: 0,
				goals_for: 0,
				goals_against: 0,
				goal_difference: 0,
				points: 0
			};
		});

		for (const s of (standings || [])) {
			const t = teamsMap[s.team_id];
			if (t && (t.sport || 'football') === sport && !sportTeams.some((team) => team.id === s.team_id)) {
				list.push(s);
			}
		}

		return list.sort((a, b) => {
			if ((b.points ?? 0) !== (a.points ?? 0)) return (b.points ?? 0) - (a.points ?? 0);
			const diffB = (b.goals_for ?? 0) - (b.goals_against ?? 0);
			const diffA = (a.goals_for ?? 0) - (a.goals_against ?? 0);
			if (diffB !== diffA) return diffB - diffA;
			return (b.goals_for ?? 0) - (a.goals_for ?? 0);
		});
	}

	let footballStandings = $derived(getSportStandings('football'));
	let basketballStandings = $derived(getSportStandings('basketball'));
	let volleyballStandings = $derived(getSportStandings('volleyball'));
	let chessStandings = $derived(getSportStandings('underwater_chess'));

	onMount(async () => {
		try {
			const [standingsData, teamsList] = await Promise.all([
				standingsApi.get(TOURNAMENT_ID).catch(() => []),
				teamsApi.list(TOURNAMENT_ID).catch(() => [])
			]);
			const map = {};
			for (const t of teamsList) map[t.id] = t;
			teamsMap = map;
			standings = standingsData;
		} catch (e) {
			error = e.message;
			toast.error('No se pudo cargar la tabla de posiciones.');
		} finally {
			loading = false;
		}
	});

	function goalDiff(s) {
		const diff = (s.goals_for ?? 0) - (s.goals_against ?? 0);
		return diff > 0 ? `+${diff}` : `${diff}`;
	}

	function rowClass(index) {
		if (index === 0) return 'border-l-2 border-emerald-500';
		if (index === 1) return 'border-l-2 border-slate-400';
		if (index === 2) return 'border-l-2 border-amber-600';
		return '';
	}
</script>

<svelte:head>
	<title>Posiciones &mdash; Torneo Hub</title>
	<meta name="description" content="Tabla de posiciones del torneo con estadisticas completas." />
</svelte:head>

<div class="mb-8 animate-fade-in-up">
	<h1 class="text-3xl font-black text-white flex items-center gap-3">Tabla de Posiciones</h1>
	<p class="text-slate-400 mt-1">Clasificacion actualizada en tiempo real</p>
</div>

{#if loading}
	<div class="glass-card overflow-hidden">
		<div class="skeleton h-10 w-full rounded-t-xl mb-px"></div>
		{#each Array(6) as _}
			<div class="skeleton h-14 w-full mb-px"></div>
		{/each}
	</div>

{:else if error}
	<div class="glass-card p-8 text-center">
		<p class="text-white font-semibold">No se pudo cargar la tabla</p>
		<p class="text-slate-400 text-sm mt-2">{error}</p>
	</div>

{:else if standings.length === 0 && Object.keys(teamsMap).length === 0}
	<div class="glass-card p-12 text-center animate-fade-in-up">
		<h2 class="text-xl font-bold text-white mb-2">Sin estadisticas todavia</h2>
		<p class="text-slate-400 text-sm">
			Las posiciones se actualizan cuando se registran resultados.
		</p>
	</div>

{:else}
	<!-- Filtro de disciplina -->
	<div class="flex items-center gap-2 mb-8 p-1.5 bg-slate-900/90 rounded-2xl border border-slate-800 w-full sm:w-fit overflow-x-auto no-scrollbar backdrop-blur-sm shadow-xl shrink-0">
		<button type="button" onclick={() => (selectedSport = 'all')}
			class="px-4 py-2 rounded-xl text-xs font-bold transition-all flex items-center gap-2 {selectedSport === 'all' ? 'bg-slate-700 text-white shadow-md' : 'text-slate-400 hover:text-white'}">
			<span>Todos</span>
		</button>
		<button type="button" onclick={() => (selectedSport = 'football')}
			class="px-4 py-2 rounded-xl text-xs font-bold transition-all flex items-center gap-2 {selectedSport === 'football' ? 'bg-emerald-600 text-white shadow-md shadow-emerald-950/40' : 'text-slate-400 hover:text-white'}">
			<span>Futbol</span>
			<span class="text-[10px] px-1.5 py-0.5 rounded-full bg-black/40 font-mono">{footballStandings.length}</span>
		</button>
		<button type="button" onclick={() => (selectedSport = 'basketball')}
			class="px-4 py-2 rounded-xl text-xs font-bold transition-all flex items-center gap-2 {selectedSport === 'basketball' ? 'bg-amber-600 text-white shadow-md shadow-amber-950/40' : 'text-slate-400 hover:text-white'}">
			<span>Basquetbol</span>
			<span class="text-[10px] px-1.5 py-0.5 rounded-full bg-black/40 font-mono">{basketballStandings.length}</span>
		</button>
		<button type="button" onclick={() => (selectedSport = 'volleyball')}
			class="px-4 py-2 rounded-xl text-xs font-bold transition-all flex items-center gap-2 {selectedSport === 'volleyball' ? 'bg-violet-600 text-white shadow-md shadow-violet-950/40' : 'text-slate-400 hover:text-white'}">
			<span>Voley</span>
			<span class="text-[10px] px-1.5 py-0.5 rounded-full bg-black/40 font-mono">{volleyballStandings.length}</span>
		</button>
		<button type="button" onclick={() => (selectedSport = 'underwater_chess')}
			class="px-4 py-2 rounded-xl text-xs font-bold transition-all flex items-center gap-2 {selectedSport === 'underwater_chess' ? 'bg-cyan-600 text-white shadow-md shadow-cyan-950/40' : 'text-slate-400 hover:text-white'}">
			<span>♟️</span>
			<span>Ajedrez bajo el agua</span>
			<span class="text-[10px] px-1.5 py-0.5 rounded-full bg-black/40 font-mono">{chessStandings.length}</span>
		</button>
	</div>

	<div class="flex flex-col gap-8">

	<!-- FUTBOL -->
	{#if (selectedSport === 'all' || selectedSport === 'football') && (footballStandings.length > 0 || selectedSport === 'football')}
		<div class="glass-card overflow-hidden animate-fade-in-up">
			<div class="px-5 py-3 border-b border-slate-800 flex items-center gap-3" style="background: rgba(16,185,129,0.08);">
				<span class="text-xl">&#x26BD;</span>
				<h2 class="font-black text-white text-lg">Futbol</h2>
				<span class="text-xs px-2.5 py-0.5 rounded-full bg-emerald-500/15 text-emerald-300 border border-emerald-500/25 font-semibold ml-auto">{footballStandings.length} equipos</span>
			</div>
			<div class="px-4 pt-3 pb-1 flex gap-4 text-xs text-slate-500">
				<span class="flex items-center gap-1"><span class="w-2 h-2 rounded bg-emerald-500 inline-block"></span> Lider</span>
				<span class="flex items-center gap-1"><span class="w-2 h-2 rounded bg-slate-400 inline-block"></span> 2do lugar</span>
				<span class="flex items-center gap-1"><span class="w-2 h-2 rounded bg-amber-600 inline-block"></span> 3er lugar</span>
			</div>
			<div class="overflow-x-auto -mx-1 sm:mx-0">
				<table class="w-full text-sm min-w-[540px]">
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
									{#if i === 0}<span class="text-base">&#x1F947;</span>
									{:else if i === 1}<span class="text-base">&#x1F948;</span>
									{:else if i === 2}<span class="text-base">&#x1F949;</span>
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
								<td class="px-3 py-3 text-center"><span class="font-black text-lg {i === 0 ? 'text-emerald-400' : 'text-white'}">{s.points ?? 0}</span></td>
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

	<!-- BASQUETBOL -->
	{#if (selectedSport === 'all' || selectedSport === 'basketball') && (basketballStandings.length > 0 || selectedSport === 'basketball')}
		<div class="glass-card overflow-hidden animate-fade-in-up">
			<div class="px-5 py-3 border-b border-slate-800 flex items-center gap-3" style="background: rgba(245,158,11,0.08);">
				<span class="text-xl">&#x1F3C0;</span>
				<h2 class="font-black text-white text-lg">Basquetbol</h2>
				<span class="text-xs px-2.5 py-0.5 rounded-full bg-amber-500/15 text-amber-300 border border-amber-500/25 font-semibold ml-auto">{basketballStandings.length} equipos</span>
			</div>
			<div class="px-4 pt-3 pb-1 flex gap-4 text-xs text-slate-500">
				<span class="flex items-center gap-1"><span class="w-2 h-2 rounded bg-emerald-500 inline-block"></span> Lider</span>
				<span class="flex items-center gap-1"><span class="w-2 h-2 rounded bg-slate-400 inline-block"></span> 2do lugar</span>
				<span class="flex items-center gap-1"><span class="w-2 h-2 rounded bg-amber-600 inline-block"></span> 3er lugar</span>
			</div>
			<div class="overflow-x-auto -mx-1 sm:mx-0">
				<table class="w-full text-sm min-w-[540px]">
					<thead>
						<tr class="text-xs text-slate-400 uppercase tracking-wider" style="border-bottom: 1px solid var(--border-color); background: rgba(15,23,42,0.5);">
							<th class="px-4 py-3 text-left w-8">#</th>
							<th class="px-4 py-3 text-left">Equipo</th>
							<th class="px-3 py-3 text-center">PJ</th>
							<th class="px-3 py-3 text-center">PG</th>
							<th class="px-3 py-3 text-center">PE</th>
							<th class="px-3 py-3 text-center">PP</th>
							<th class="px-3 py-3 text-center">PF</th>
							<th class="px-3 py-3 text-center">PC</th>
							<th class="px-3 py-3 text-center">DP</th>
							<th class="px-3 py-3 text-center font-bold">PTS</th>
						</tr>
					</thead>
					<tbody>
						{#each basketballStandings as s, i}
							<tr class="standings-row transition-colors {rowClass(i)}" style="border-bottom: 1px solid var(--border-color); animation: fadeInUp 0.3s {i * 0.05}s both;">
								<td class="px-4 py-3 text-center">
									{#if i === 0}<span class="text-base">&#x1F947;</span>
									{:else if i === 1}<span class="text-base">&#x1F948;</span>
									{:else if i === 2}<span class="text-base">&#x1F949;</span>
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
								<td class="px-3 py-3 text-center"><span class="font-black text-lg {i === 0 ? 'text-amber-400' : 'text-white'}">{s.points ?? 0}</span></td>
							</tr>
						{/each}
					</tbody>
				</table>
			</div>
			<div class="px-4 py-3 text-xs text-slate-600 border-t" style="border-color: var(--border-color);">
				Victoria = 2 pts &nbsp;|&nbsp; Derrota = 1 pt (5 sets) &nbsp;|&nbsp; Derrota = 0 pts
			</div>
		</div>
	{/if}

	<!-- VOLEY -->
	{#if (selectedSport === 'all' || selectedSport === 'volleyball') && (volleyballStandings.length > 0 || selectedSport === 'volleyball')}
		<div class="glass-card overflow-hidden animate-fade-in-up">
			<div class="px-5 py-3 border-b border-slate-800 flex items-center gap-3" style="background: rgba(124,58,237,0.08);">
				<span class="text-xl">&#x1F3D0;</span>
				<h2 class="font-black text-white text-lg">Voley</h2>
				<span class="text-xs px-2.5 py-0.5 rounded-full bg-violet-500/15 text-violet-300 border border-violet-500/25 font-semibold ml-auto">{volleyballStandings.length} equipos</span>
			</div>
			<div class="px-4 pt-3 pb-1 flex gap-4 text-xs text-slate-500">
				<span class="flex items-center gap-1"><span class="w-2 h-2 rounded bg-emerald-500 inline-block"></span> Lider</span>
				<span class="flex items-center gap-1"><span class="w-2 h-2 rounded bg-slate-400 inline-block"></span> 2do lugar</span>
				<span class="flex items-center gap-1"><span class="w-2 h-2 rounded bg-amber-600 inline-block"></span> 3er lugar</span>
			</div>
			<div class="overflow-x-auto -mx-1 sm:mx-0">
				<table class="w-full text-sm min-w-[540px]">
					<thead>
						<tr class="text-xs text-slate-400 uppercase tracking-wider" style="border-bottom: 1px solid var(--border-color); background: rgba(15,23,42,0.5);">
							<th class="px-4 py-3 text-left w-8">#</th>
							<th class="px-4 py-3 text-left">Equipo</th>
							<th class="px-3 py-3 text-center">PJ</th>
							<th class="px-3 py-3 text-center">PG</th>
							<th class="px-3 py-3 text-center">PE</th>
							<th class="px-3 py-3 text-center">PP</th>
							<th class="px-3 py-3 text-center">SF</th>
							<th class="px-3 py-3 text-center">SC</th>
							<th class="px-3 py-3 text-center">DS</th>
							<th class="px-3 py-3 text-center font-bold">PTS</th>
						</tr>
					</thead>
					<tbody>
						{#each volleyballStandings as s, i}
							<tr class="standings-row transition-colors {rowClass(i)}" style="border-bottom: 1px solid var(--border-color); animation: fadeInUp 0.3s {i * 0.05}s both;">
								<td class="px-4 py-3 text-center">
									{#if i === 0}<span class="text-base">&#x1F947;</span>
									{:else if i === 1}<span class="text-base">&#x1F948;</span>
									{:else if i === 2}<span class="text-base">&#x1F949;</span>
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
								<td class="px-3 py-3 text-center"><span class="font-black text-lg {i === 0 ? 'text-violet-400' : 'text-white'}">{s.points ?? 0}</span></td>
							</tr>
						{/each}
					</tbody>
				</table>
			</div>
			<div class="px-4 py-3 text-xs text-slate-600 border-t" style="border-color: var(--border-color);">
				Victoria 3-0/3-1 = 3 pts &nbsp;|&nbsp; Victoria 3-2 = 2 pts &nbsp;|&nbsp; Derrota 2-3 = 1 pt &nbsp;|&nbsp; Derrota 0/1-3 = 0 pts
			</div>
		</div>
	{/if}

	<!-- AJEDREZ BAJO EL AGUA -->
	{#if (selectedSport === 'all' || selectedSport === 'underwater_chess') && (chessStandings.length > 0 || selectedSport === 'underwater_chess')}
		<div class="glass-card overflow-hidden animate-fade-in-up">
			<div class="px-5 py-3 border-b border-slate-800 flex items-center gap-3" style="background: rgba(6,182,212,0.08);">
				<span class="text-xl">🌊♟️</span>
				<h2 class="font-black text-white text-lg">Ajedrez bajo el agua</h2>
				<span class="text-xs px-2.5 py-0.5 rounded-full bg-cyan-500/15 text-cyan-300 border border-cyan-500/25 font-semibold ml-auto">{chessStandings.length} competidores</span>
			</div>
			<div class="overflow-x-auto -mx-1 sm:mx-0">
				<table class="w-full text-sm min-w-[540px]">
					<thead>
						<tr class="text-xs text-slate-400 uppercase tracking-wider" style="border-bottom: 1px solid var(--border-color); background: rgba(15,23,42,0.5);">
							<th class="px-4 py-3 text-left w-8">#</th>
							<th class="px-4 py-3 text-left">Ajedrecista / Club</th>
							<th class="px-3 py-3 text-center">PJ</th>
							<th class="px-3 py-3 text-center">PG (Victorias)</th>
							<th class="px-3 py-3 text-center">PE (Tablas)</th>
							<th class="px-3 py-3 text-center">PP (Derrotas)</th>
							<th class="px-3 py-3 text-center font-bold">PTS</th>
						</tr>
					</thead>
					<tbody>
						{#each chessStandings as s, i}
							<tr class="standings-row transition-colors {rowClass(i)}" style="border-bottom: 1px solid var(--border-color); animation: fadeInUp 0.3s {i * 0.05}s both;">
								<td class="px-4 py-3 text-center">
									{#if i === 0}<span class="text-base">🥇</span>
									{:else if i === 1}<span class="text-base">🥈</span>
									{:else if i === 2}<span class="text-base">🥉</span>
									{:else}<span class="text-slate-500 font-mono">{i + 1}</span>{/if}
								</td>
								<td class="px-4 py-3">
									<div class="flex items-center gap-3">
										<div class="w-8 h-8 rounded-full flex items-center justify-center text-sm font-black text-white shrink-0" style="background: linear-gradient(135deg, #06b6d4, #0891b2);">
											{teamsMap[s.team_id]?.name?.[0]?.toUpperCase() ?? '?'}
										</div>
										<span class="font-semibold text-white">{teamsMap[s.team_id]?.name ?? `Competidor #${s.team_id}`}</span>
									</div>
								</td>
								<td class="px-3 py-3 text-center text-slate-300">{s.played ?? 0}</td>
								<td class="px-3 py-3 text-center text-emerald-400 font-medium">{s.won ?? 0}</td>
								<td class="px-3 py-3 text-center text-slate-400">{s.drawn ?? 0}</td>
								<td class="px-3 py-3 text-center text-red-400">{s.lost ?? 0}</td>
								<td class="px-3 py-3 text-center"><span class="font-black text-lg {i === 0 ? 'text-cyan-400' : 'text-white'}">{s.points ?? 0}</span></td>
							</tr>
						{/each}
					</tbody>
				</table>
			</div>
			<div class="px-4 py-3 text-xs text-slate-600 border-t" style="border-color: var(--border-color);">
				Victoria = 1 pt &nbsp;|&nbsp; Tablas / Empate = 0.5 pts &nbsp;|&nbsp; Derrota = 0 pts
			</div>
		</div>
	{/if}

	</div>
{/if}