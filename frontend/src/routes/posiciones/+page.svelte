<script>
	/**
	 * routes/posiciones/+page.svelte — Tabla de Posiciones (/posiciones)
	 *
	 * ¿Qué muestra?
	 * - Tabla de clasificación completa con todas las estadísticas
	 * - Columnas: Pos, Equipo, PJ, PG, PE, PP, GF, GC, DG, PTS
	 * - El líder (1er lugar) se resalta en verde
	 *
	 * ¿Qué llama al backend?
	 * - GET /api/v1/tournaments/1/standings
	 *   Devuelve: [{ team, points, played, won, drawn, lost, goals_for, goals_against }, ...]
	 *   El backend ya devuelve la lista ordenada por puntos (mayor a menor).
	 *
	 * Significado de las columnas:
	 *   PJ = Partidos Jugados
	 *   PG = Partidos Ganados
	 *   PE = Empates
	 *   PP = Partidos Perdidos
	 *   GF = Goles a Favor
	 *   GC = Goles en Contra
	 *   DG = Diferencia de Gol (GF - GC)
	 *   PTS = Puntos totales (Victoria=3, Empate=1, Derrota=0)
	 */
	import { onMount } from 'svelte';
	import { standingsApi, teamsApi } from '$lib/api/client';
	import { toast } from '$lib/stores/toast';

	const TOURNAMENT_ID = 1;

	let standings = $state([]);
	let teamsMap = $state({});
	let loading = $state(true);
	let error = $state(null);

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
	<title>Posiciones — Nombre-Creativo</title>
	<meta name="description" content="Tabla de posiciones del torneo con estadísticas completas de cada equipo." />
</svelte:head>

<!-- ── Encabezado ─────────────────────────────────────────────────────────── -->
<div class="mb-8 animate-fade-in-up">
	<h1 class="text-3xl font-black text-white flex items-center gap-3">📊 Tabla de Posiciones</h1>
	<p class="text-slate-400 mt-1">Clasificación actualizada en tiempo real</p>
</div>

<!-- ── Estado: cargando ───────────────────────────────────────────────────── -->
{#if loading}
	<div class="glass-card overflow-hidden">
		<div class="skeleton h-10 w-full rounded-t-xl mb-px"></div>
		{#each Array(6) as _}
			<div class="skeleton h-14 w-full mb-px"></div>
		{/each}
	</div>

<!-- ── Estado: error ─────────────────────────────────────────────────────── -->
{:else if error}
	<div class="glass-card p-8 text-center">
		<div class="text-4xl mb-3">⚠️</div>
		<p class="text-white font-semibold">No se pudo cargar la tabla</p>
		<p class="text-slate-400 text-sm mt-2">{error}</p>
	</div>

<!-- ── Sin datos ──────────────────────────────────────────────────────────── -->
{:else if standings.length === 0}
	<div class="glass-card p-12 text-center animate-fade-in-up">
		<div class="text-5xl mb-4">📊</div>
		<h2 class="text-xl font-bold text-white mb-2">Sin estadísticas todavía</h2>
		<p class="text-slate-400 text-sm">
			Las posiciones se actualizan automáticamente cuando se registran resultados de partidos.
		</p>
	</div>

<!-- ── Tabla de posiciones ────────────────────────────────────────────────── -->
{:else}
	<div class="glass-card overflow-hidden animate-fade-in-up">
		<!-- Leyenda de colores -->
		<div class="px-4 pt-4 pb-2 flex gap-4 text-xs text-slate-500">
			<span class="flex items-center gap-1"><span class="w-2 h-2 rounded bg-emerald-500 inline-block"></span> Líder</span>
			<span class="flex items-center gap-1"><span class="w-2 h-2 rounded bg-slate-400 inline-block"></span> 2do lugar</span>
			<span class="flex items-center gap-1"><span class="w-2 h-2 rounded bg-amber-600 inline-block"></span> 3er lugar</span>
		</div>

		<!-- Tabla responsive -->
		<div class="overflow-x-auto">
			<table class="w-full text-sm">
				<!-- Encabezados -->
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

				<!-- Filas -->
				<tbody>
					{#each standings as s, i}
						<tr
							class="standings-row transition-colors {rowClass(i)}"
							style="border-bottom: 1px solid var(--border-color); animation: fadeInUp 0.3s {i * 0.05}s both;"
						>
							<!-- Posición -->
							<td class="px-4 py-3 text-center">
								{#if i === 0}
									<span class="text-base">🥇</span>
								{:else if i === 1}
									<span class="text-base">🥈</span>
								{:else if i === 2}
									<span class="text-base">🥉</span>
								{:else}
									<span class="text-slate-500 font-mono">{i + 1}</span>
								{/if}
							</td>

							<!-- Nombre del equipo -->
							<td class="px-4 py-3">
								<div class="flex items-center gap-3">
									<div class="w-8 h-8 rounded-full flex items-center justify-center text-sm font-black text-white shrink-0"
										style="background: linear-gradient(135deg, var(--accent-green), #16a34a);">
										{teamsMap[s.team_id]?.name?.[0]?.toUpperCase() ?? '?'}
									</div>
									<span class="font-semibold text-white">{teamsMap[s.team_id]?.name ?? `Equipo #${s.team_id}`}</span>
								</div>
							</td>

							<!-- Estadísticas numéricas -->
							<td class="px-3 py-3 text-center text-slate-300">{s.played ?? 0}</td>
							<td class="px-3 py-3 text-center text-emerald-400 font-medium">{s.won ?? 0}</td>
							<td class="px-3 py-3 text-center text-slate-400">{s.drawn ?? 0}</td>
							<td class="px-3 py-3 text-center text-red-400">{s.lost ?? 0}</td>
							<td class="px-3 py-3 text-center text-slate-300">{s.goals_for ?? 0}</td>
							<td class="px-3 py-3 text-center text-slate-300">{s.goals_against ?? 0}</td>
							<td class="px-3 py-3 text-center font-mono text-slate-300">{goalDiff(s)}</td>

							<!-- Puntos (resaltado) -->
							<td class="px-3 py-3 text-center">
								<span class="font-black text-lg {i === 0 ? 'text-emerald-400' : 'text-white'}">
									{s.points ?? 0}
								</span>
							</td>
						</tr>
					{/each}
				</tbody>
			</table>
		</div>

		<!-- Pie de tabla: leyenda de puntuación -->
		<div class="px-4 py-3 text-xs text-slate-600 border-t" style="border-color: var(--border-color);">
			Victoria = 3 pts &nbsp;|&nbsp; Empate = 1 pt &nbsp;|&nbsp; Derrota = 0 pts
		</div>
	</div>
{/if}
