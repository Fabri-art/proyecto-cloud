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
	let auraStandings = $derived(getSportStandings('aura_battle'));
	let spermStandings = $derived(getSportStandings('sperm_triathlon'));
	let tireStandings = $derived(getSportStandings('tire_race'));
	let mosquitoStandings = $derived(getSportStandings('mosquito_marathon'));

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
	<div class="flex flex-wrap items-center gap-1.5 mb-8 p-1.5 bg-slate-900/90 rounded-2xl border border-slate-800 max-w-full backdrop-blur-sm shadow-xl shrink-0">
		<button type="button" onclick={() => (selectedSport = 'all')}
			class="px-3.5 py-1.5 rounded-xl text-xs font-bold transition-all flex items-center gap-1.5 {selectedSport === 'all' ? 'bg-slate-700 text-white shadow-md' : 'text-slate-400 hover:text-white'}">
			<span>🌐</span><span>Todos</span>
		</button>
		<button type="button" onclick={() => (selectedSport = 'football')}
			class="px-3.5 py-1.5 rounded-xl text-xs font-bold transition-all flex items-center gap-1.5 {selectedSport === 'football' ? 'bg-emerald-600 text-white shadow-md shadow-emerald-950/40' : 'text-slate-400 hover:text-white'}">
			<span>⚽</span><span>Fútbol</span>
			<span class="text-[10px] px-1.5 py-0.5 rounded-full bg-black/40 font-mono">{footballStandings.length}</span>
		</button>
		<button type="button" onclick={() => (selectedSport = 'basketball')}
			class="px-3.5 py-1.5 rounded-xl text-xs font-bold transition-all flex items-center gap-1.5 {selectedSport === 'basketball' ? 'bg-amber-600 text-white shadow-md shadow-amber-950/40' : 'text-slate-400 hover:text-white'}">
			<span>🏀</span><span>Básquetbol</span>
			<span class="text-[10px] px-1.5 py-0.5 rounded-full bg-black/40 font-mono">{basketballStandings.length}</span>
		</button>
		<button type="button" onclick={() => (selectedSport = 'volleyball')}
			class="px-3.5 py-1.5 rounded-xl text-xs font-bold transition-all flex items-center gap-1.5 {selectedSport === 'volleyball' ? 'bg-violet-600 text-white shadow-md shadow-violet-950/40' : 'text-slate-400 hover:text-white'}">
			<span>🏐</span><span>Vóley</span>
			<span class="text-[10px] px-1.5 py-0.5 rounded-full bg-black/40 font-mono">{volleyballStandings.length}</span>
		</button>
		<button type="button" onclick={() => (selectedSport = 'underwater_chess')}
			class="px-3.5 py-1.5 rounded-xl text-xs font-bold transition-all flex items-center gap-1.5 {selectedSport === 'underwater_chess' ? 'bg-cyan-600 text-white shadow-md shadow-cyan-950/40' : 'text-slate-400 hover:text-white'}">
			<span>🌊♟️</span><span>Ajedrez acuático</span>
			<span class="text-[10px] px-1.5 py-0.5 rounded-full bg-black/40 font-mono">{chessStandings.length}</span>
		</button>
		<button type="button" onclick={() => (selectedSport = 'aura_battle')}
			class="px-3.5 py-1.5 rounded-xl text-xs font-bold transition-all flex items-center gap-1.5 {selectedSport === 'aura_battle' ? 'bg-yellow-500 text-black shadow-md shadow-yellow-950/40' : 'text-slate-400 hover:text-white'}">
			<span>🕺</span><span>Batalla de aura</span>
			<span class="text-[10px] px-1.5 py-0.5 rounded-full bg-black/40 font-mono">{auraStandings.length}</span>
		</button>
		<button type="button" onclick={() => (selectedSport = 'sperm_triathlon')}
			class="px-3.5 py-1.5 rounded-xl text-xs font-bold transition-all flex items-center gap-1.5 {selectedSport === 'sperm_triathlon' ? 'bg-cyan-500 text-black shadow-md shadow-cyan-950/40' : 'text-slate-400 hover:text-white'}">
			<span>🧬</span><span>Triatlón esperm.</span>
			<span class="text-[10px] px-1.5 py-0.5 rounded-full bg-black/40 font-mono">{spermStandings.length}</span>
		</button>
		<button type="button" onclick={() => (selectedSport = 'tire_race')}
			class="px-3.5 py-1.5 rounded-xl text-xs font-bold transition-all flex items-center gap-1.5 {selectedSport === 'tire_race' ? 'bg-orange-600 text-white shadow-md shadow-orange-950/40' : 'text-slate-400 hover:text-white'}">
			<span>🛞</span><span>Carrera llantas</span>
			<span class="text-[10px] px-1.5 py-0.5 rounded-full bg-black/40 font-mono">{tireStandings.length}</span>
		</button>
		<button type="button" onclick={() => (selectedSport = 'mosquito_marathon')}
			class="px-3.5 py-1.5 rounded-xl text-xs font-bold transition-all flex items-center gap-1.5 {selectedSport === 'mosquito_marathon' ? 'bg-lime-600 text-white shadow-md shadow-lime-950/40' : 'text-slate-400 hover:text-white'}">
			<span>🦟</span><span>Maratón mosquitos</span>
			<span class="text-[10px] px-1.5 py-0.5 rounded-full bg-black/40 font-mono">{mosquitoStandings.length}</span>
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

	<!-- BATALLA DE AURA -->
	{#if (selectedSport === 'all' || selectedSport === 'aura_battle') && (auraStandings.length > 0 || selectedSport === 'aura_battle')}
		<div class="glass-card overflow-hidden animate-fade-in-up">
			<div class="px-5 py-3 border-b border-slate-800 flex items-center gap-3" style="background: rgba(234,179,8,0.1);">
				<span class="text-xl">🕺</span>
				<div>
					<h2 class="font-black text-white text-lg leading-tight">Batalla de Aura</h2>
					<p class="text-xs text-yellow-300/80 font-mono">Duelo de Baile Callejero y Farmeo de Aura</p>
				</div>
				<span class="text-xs px-2.5 py-0.5 rounded-full bg-yellow-500/15 text-yellow-300 border border-yellow-500/25 font-semibold ml-auto">{auraStandings.length} crews</span>
			</div>
			<div class="overflow-x-auto -mx-1 sm:mx-0">
				<table class="w-full text-sm min-w-[540px]">
					<thead>
						<tr class="text-xs text-slate-400 uppercase tracking-wider" style="border-bottom: 1px solid var(--border-color); background: rgba(15,23,42,0.5);">
							<th class="px-4 py-3 text-left w-8">#</th>
							<th class="px-4 py-3 text-left">Crew / Club</th>
							<th class="px-3 py-3 text-center">PJ</th>
							<th class="px-3 py-3 text-center">PG</th>
							<th class="px-3 py-3 text-center">PP</th>
							<th class="px-3 py-3 text-center">PA Favor</th>
							<th class="px-3 py-3 text-center">PA Contra</th>
							<th class="px-3 py-3 text-center">Dif. PA</th>
							<th class="px-3 py-3 text-center font-bold text-yellow-400">PTS</th>
						</tr>
					</thead>
					<tbody>
						{#if auraStandings.length === 0}
							<tr><td colspan="9" class="text-center py-6 text-slate-500 text-xs">No hay crews registradas en Batalla de Aura todavía</td></tr>
						{/if}
						{#each auraStandings as s, i}
							<tr class="standings-row transition-colors {rowClass(i)}" style="border-bottom: 1px solid var(--border-color); animation: fadeInUp 0.3s {i * 0.05}s both;">
								<td class="px-4 py-3 text-center">
									{#if i === 0}<span class="text-base">🥇</span>
									{:else if i === 1}<span class="text-base">🥈</span>
									{:else if i === 2}<span class="text-base">🥉</span>
									{:else}<span class="text-slate-500 font-mono">{i + 1}</span>{/if}
								</td>
								<td class="px-4 py-3">
									<div class="flex items-center gap-3">
										<div class="w-8 h-8 rounded-full flex items-center justify-center text-sm font-black text-black shrink-0" style="background: linear-gradient(135deg, #facc15, #eab308);">
											{teamsMap[s.team_id]?.name?.[0]?.toUpperCase() ?? '?'}
										</div>
										<span class="font-semibold text-white">{teamsMap[s.team_id]?.name ?? `Equipo #${s.team_id}`}</span>
									</div>
								</td>
								<td class="px-3 py-3 text-center text-slate-300">{s.played ?? 0}</td>
								<td class="px-3 py-3 text-center text-emerald-400 font-medium">{s.won ?? 0}</td>
								<td class="px-3 py-3 text-center text-red-400">{s.lost ?? 0}</td>
								<td class="px-3 py-3 text-center text-slate-300 font-mono">{s.goals_for ?? 0}</td>
								<td class="px-3 py-3 text-center text-slate-300 font-mono">{s.goals_against ?? 0}</td>
								<td class="px-3 py-3 text-center font-mono text-slate-300">{goalDiff(s)}</td>
								<td class="px-3 py-3 text-center"><span class="font-black text-lg {i === 0 ? 'text-yellow-400' : 'text-white'}">{s.points ?? 0}</span></td>
							</tr>
						{/each}
					</tbody>
				</table>
			</div>
			<div class="px-4 py-3 text-xs text-slate-600 border-t" style="border-color: var(--border-color);">
				Victoria de Aura = 3 pts &nbsp;|&nbsp; Derrota = 0 pts &nbsp;|&nbsp; PA = Puntos de Aura
			</div>
		</div>
	{/if}

	<!-- TRIATLÓN DE ESPERMATOZOIDE -->
	{#if (selectedSport === 'all' || selectedSport === 'sperm_triathlon') && (spermStandings.length > 0 || selectedSport === 'sperm_triathlon')}
		<div class="glass-card overflow-hidden animate-fade-in-up">
			<div class="px-5 py-3 border-b border-slate-800 flex items-center gap-3" style="background: rgba(6,182,212,0.1);">
				<span class="text-xl">🧬</span>
				<div>
					<h2 class="font-black text-white text-lg leading-tight">Triatlón de Espermatozoide</h2>
					<p class="text-xs text-cyan-300/80 font-mono">Circuito Celular de Resistencia Flagelar</p>
				</div>
				<span class="text-xs px-2.5 py-0.5 rounded-full bg-cyan-500/15 text-cyan-300 border border-cyan-500/25 font-semibold ml-auto">{spermStandings.length} nadadores</span>
			</div>
			<div class="overflow-x-auto -mx-1 sm:mx-0">
				<table class="w-full text-sm min-w-[540px]">
					<thead>
						<tr class="text-xs text-slate-400 uppercase tracking-wider" style="border-bottom: 1px solid var(--border-color); background: rgba(15,23,42,0.5);">
							<th class="px-4 py-3 text-left w-8">#</th>
							<th class="px-4 py-3 text-left">Nadador / Club</th>
							<th class="px-3 py-3 text-center">PJ</th>
							<th class="px-3 py-3 text-center">PG</th>
							<th class="px-3 py-3 text-center">PP</th>
							<th class="px-3 py-3 text-center">Dist. Favor (µm)</th>
							<th class="px-3 py-3 text-center">Dist. Contra (µm)</th>
							<th class="px-3 py-3 text-center">Dif. µm</th>
							<th class="px-3 py-3 text-center font-bold text-cyan-400">PTS</th>
						</tr>
					</thead>
					<tbody>
						{#if spermStandings.length === 0}
							<tr><td colspan="9" class="text-center py-6 text-slate-500 text-xs">No hay nadadores registrados todavía</td></tr>
						{/if}
						{#each spermStandings as s, i}
							<tr class="standings-row transition-colors {rowClass(i)}" style="border-bottom: 1px solid var(--border-color); animation: fadeInUp 0.3s {i * 0.05}s both;">
								<td class="px-4 py-3 text-center">
									{#if i === 0}<span class="text-base">🥇</span>
									{:else if i === 1}<span class="text-base">🥈</span>
									{:else if i === 2}<span class="text-base">🥉</span>
									{:else}<span class="text-slate-500 font-mono">{i + 1}</span>{/if}
								</td>
								<td class="px-4 py-3">
									<div class="flex items-center gap-3">
										<div class="w-8 h-8 rounded-full flex items-center justify-center text-sm font-black text-black shrink-0" style="background: linear-gradient(135deg, #22d3ee, #06b6d4);">
											{teamsMap[s.team_id]?.name?.[0]?.toUpperCase() ?? '?'}
										</div>
										<span class="font-semibold text-white">{teamsMap[s.team_id]?.name ?? `Equipo #${s.team_id}`}</span>
									</div>
								</td>
								<td class="px-3 py-3 text-center text-slate-300">{s.played ?? 0}</td>
								<td class="px-3 py-3 text-center text-emerald-400 font-medium">{s.won ?? 0}</td>
								<td class="px-3 py-3 text-center text-red-400">{s.lost ?? 0}</td>
								<td class="px-3 py-3 text-center text-slate-300 font-mono">{s.goals_for ?? 0}</td>
								<td class="px-3 py-3 text-center text-slate-300 font-mono">{s.goals_against ?? 0}</td>
								<td class="px-3 py-3 text-center font-mono text-slate-300">{goalDiff(s)}</td>
								<td class="px-3 py-3 text-center"><span class="font-black text-lg {i === 0 ? 'text-cyan-400' : 'text-white'}">{s.points ?? 0}</span></td>
							</tr>
						{/each}
					</tbody>
				</table>
			</div>
			<div class="px-4 py-3 text-xs text-slate-600 border-t" style="border-color: var(--border-color);">
				Victoria = 3 pts &nbsp;|&nbsp; Derrota = 0 pts &nbsp;|&nbsp; µm = Micrómetros de avance
			</div>
		</div>
	{/if}

	<!-- CARRERA DE LLANTAS -->
	{#if (selectedSport === 'all' || selectedSport === 'tire_race') && (tireStandings.length > 0 || selectedSport === 'tire_race')}
		<div class="glass-card overflow-hidden animate-fade-in-up">
			<div class="px-5 py-3 border-b border-slate-800 flex items-center gap-3" style="background: rgba(234,88,12,0.1);">
				<span class="text-xl">🛞</span>
				<div>
					<h2 class="font-black text-white text-lg leading-tight">Carrera de Llantas</h2>
					<p class="text-xs text-orange-300/80 font-mono">Pista Olímpica Naranja de Rodamiento</p>
				</div>
				<span class="text-xs px-2.5 py-0.5 rounded-full bg-orange-500/15 text-orange-300 border border-orange-500/25 font-semibold ml-auto">{tireStandings.length} escuderías</span>
			</div>
			<div class="overflow-x-auto -mx-1 sm:mx-0">
				<table class="w-full text-sm min-w-[540px]">
					<thead>
						<tr class="text-xs text-slate-400 uppercase tracking-wider" style="border-bottom: 1px solid var(--border-color); background: rgba(15,23,42,0.5);">
							<th class="px-4 py-3 text-left w-8">#</th>
							<th class="px-4 py-3 text-left">Escudería / Club</th>
							<th class="px-3 py-3 text-center">PJ</th>
							<th class="px-3 py-3 text-center">PG</th>
							<th class="px-3 py-3 text-center">PP</th>
							<th class="px-3 py-3 text-center">VLT Favor</th>
							<th class="px-3 py-3 text-center">VLT Contra</th>
							<th class="px-3 py-3 text-center">Dif. VLT</th>
							<th class="px-3 py-3 text-center font-bold text-orange-400">PTS</th>
						</tr>
					</thead>
					<tbody>
						{#if tireStandings.length === 0}
							<tr><td colspan="9" class="text-center py-6 text-slate-500 text-xs">No hay escuderías registradas todavía</td></tr>
						{/if}
						{#each tireStandings as s, i}
							<tr class="standings-row transition-colors {rowClass(i)}" style="border-bottom: 1px solid var(--border-color); animation: fadeInUp 0.3s {i * 0.05}s both;">
								<td class="px-4 py-3 text-center">
									{#if i === 0}<span class="text-base">🥇</span>
									{:else if i === 1}<span class="text-base">🥈</span>
									{:else if i === 2}<span class="text-base">🥉</span>
									{:else}<span class="text-slate-500 font-mono">{i + 1}</span>{/if}
								</td>
								<td class="px-4 py-3">
									<div class="flex items-center gap-3">
										<div class="w-8 h-8 rounded-full flex items-center justify-center text-sm font-black text-white shrink-0" style="background: linear-gradient(135deg, #ea580c, #c2410c);">
											{teamsMap[s.team_id]?.name?.[0]?.toUpperCase() ?? '?'}
										</div>
										<span class="font-semibold text-white">{teamsMap[s.team_id]?.name ?? `Equipo #${s.team_id}`}</span>
									</div>
								</td>
								<td class="px-3 py-3 text-center text-slate-300">{s.played ?? 0}</td>
								<td class="px-3 py-3 text-center text-emerald-400 font-medium">{s.won ?? 0}</td>
								<td class="px-3 py-3 text-center text-red-400">{s.lost ?? 0}</td>
								<td class="px-3 py-3 text-center text-slate-300 font-mono">{s.goals_for ?? 0}</td>
								<td class="px-3 py-3 text-center text-slate-300 font-mono">{s.goals_against ?? 0}</td>
								<td class="px-3 py-3 text-center font-mono text-slate-300">{goalDiff(s)}</td>
								<td class="px-3 py-3 text-center"><span class="font-black text-lg {i === 0 ? 'text-orange-400' : 'text-white'}">{s.points ?? 0}</span></td>
							</tr>
						{/each}
					</tbody>
				</table>
			</div>
			<div class="px-4 py-3 text-xs text-slate-600 border-t" style="border-color: var(--border-color);">
				Victoria = 3 pts &nbsp;|&nbsp; Derrota = 0 pts &nbsp;|&nbsp; VLT = Vueltas completadas
			</div>
		</div>
	{/if}

	<!-- MARATÓN DE MOSQUITOS -->
	{#if (selectedSport === 'all' || selectedSport === 'mosquito_marathon') && (mosquitoStandings.length > 0 || selectedSport === 'mosquito_marathon')}
		<div class="glass-card overflow-hidden animate-fade-in-up">
			<div class="px-5 py-3 border-b border-slate-800 flex items-center gap-3" style="background: rgba(132,204,22,0.1);">
				<span class="text-xl">🦟</span>
				<div>
					<h2 class="font-black text-white text-lg leading-tight">Maratón de Mosquitos</h2>
					<p class="text-xs text-lime-300/80 font-mono">Pista de Vuelo Nocturno hacia la Farola</p>
				</div>
				<span class="text-xs px-2.5 py-0.5 rounded-full bg-lime-500/15 text-lime-300 border border-lime-500/25 font-semibold ml-auto">{mosquitoStandings.length} escuadrones</span>
			</div>
			<div class="overflow-x-auto -mx-1 sm:mx-0">
				<table class="w-full text-sm min-w-[540px]">
					<thead>
						<tr class="text-xs text-slate-400 uppercase tracking-wider" style="border-bottom: 1px solid var(--border-color); background: rgba(15,23,42,0.5);">
							<th class="px-4 py-3 text-left w-8">#</th>
							<th class="px-4 py-3 text-left">Escuadrón / Club</th>
							<th class="px-3 py-3 text-center">PJ</th>
							<th class="px-3 py-3 text-center">PG</th>
							<th class="px-3 py-3 text-center">PP</th>
							<th class="px-3 py-3 text-center">PC Favor</th>
							<th class="px-3 py-3 text-center">PC Contra</th>
							<th class="px-3 py-3 text-center">Dif. PC</th>
							<th class="px-3 py-3 text-center font-bold text-lime-400">PTS</th>
						</tr>
					</thead>
					<tbody>
						{#if mosquitoStandings.length === 0}
							<tr><td colspan="9" class="text-center py-6 text-slate-500 text-xs">No hay escuadrones registrados todavía</td></tr>
						{/if}
						{#each mosquitoStandings as s, i}
							<tr class="standings-row transition-colors {rowClass(i)}" style="border-bottom: 1px solid var(--border-color); animation: fadeInUp 0.3s {i * 0.05}s both;">
								<td class="px-4 py-3 text-center">
									{#if i === 0}<span class="text-base">🥇</span>
									{:else if i === 1}<span class="text-base">🥈</span>
									{:else if i === 2}<span class="text-base">🥉</span>
									{:else}<span class="text-slate-500 font-mono">{i + 1}</span>{/if}
								</td>
								<td class="px-4 py-3">
									<div class="flex items-center gap-3">
										<div class="w-8 h-8 rounded-full flex items-center justify-center text-sm font-black text-white shrink-0" style="background: linear-gradient(135deg, #84cc16, #65a30d);">
											{teamsMap[s.team_id]?.name?.[0]?.toUpperCase() ?? '?'}
										</div>
										<span class="font-semibold text-white">{teamsMap[s.team_id]?.name ?? `Equipo #${s.team_id}`}</span>
									</div>
								</td>
								<td class="px-3 py-3 text-center text-slate-300">{s.played ?? 0}</td>
								<td class="px-3 py-3 text-center text-emerald-400 font-medium">{s.won ?? 0}</td>
								<td class="px-3 py-3 text-center text-red-400">{s.lost ?? 0}</td>
								<td class="px-3 py-3 text-center text-slate-300 font-mono">{s.goals_for ?? 0}</td>
								<td class="px-3 py-3 text-center text-slate-300 font-mono">{s.goals_against ?? 0}</td>
								<td class="px-3 py-3 text-center font-mono text-slate-300">{goalDiff(s)}</td>
								<td class="px-3 py-3 text-center"><span class="font-black text-lg {i === 0 ? 'text-lime-400' : 'text-white'}">{s.points ?? 0}</span></td>
							</tr>
						{/each}
					</tbody>
				</table>
			</div>
			<div class="px-4 py-3 text-xs text-slate-600 border-t" style="border-color: var(--border-color);">
				Victoria = 3 pts &nbsp;|&nbsp; Derrota = 0 pts &nbsp;|&nbsp; PC = Picaduras concretadas
			</div>
		</div>
	{/if}


	</div>
{/if}