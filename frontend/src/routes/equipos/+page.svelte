<script>
	/**
	 * routes/equipos/+page.svelte — Página de Equipos (/equipos)
	 * Rediseñada con escudos únicos por equipo y modal mejorado.
	 */
	import { onMount } from 'svelte';
	import { teamsApi, tournamentsApi } from '$lib/api/client';
	import SoccerPitch from '$lib/components/SoccerPitch.svelte';
	import BasketballCourt from '$lib/components/BasketballCourt.svelte';
	import VolleyballCourt from '$lib/components/VolleyballCourt.svelte';
	import UnderwaterChessBoard from '$lib/components/UnderwaterChessBoard.svelte';
	import { toast } from '$lib/stores/toast';

	let teams = $state([]);
	let loading = $state(true);
	let error = $state(null);
	let selectedTeam = $state(null);
	let loadingRoster = $state(false);
	let rosterViewMode = $state('list'); // 'list' | 'pitch'
	let tournament = $state(null);
	const TOURNAMENT_ID = 1;

	const positionLabels = {
		// Fútbol
		goalkeeper: { label: 'Arquero',       icon: '🧤', color: '#f59e0b' },
		defender:   { label: 'Defensa',       icon: '🛡️',  color: '#3b82f6' },
		midfielder: { label: 'Mediocampista', icon: '⚡', color: '#10b981' },
		forward:    { label: 'Delantero',     icon: '⚽', color: '#ef4444' },
		// Básquetbol
		point_guard:    { label: 'Base (PG)',      icon: '🏀', color: '#f59e0b' },
		shooting_guard: { label: 'Escolta (SG)',   icon: '🎯', color: '#ec4899' },
		small_forward:  { label: 'Alero (SF)',     icon: '⚡', color: '#8b5cf6' },
		power_forward:  { label: 'Ala-Pívot (PF)', icon: '🛡️', color: '#3b82f6' },
		center:         { label: 'Pívot (C)',      icon: '👑', color: '#10b981' },
		// Vóley
		setter:         { label: 'Armador',   icon: '🎯', color: '#8b5cf6' },
		libero:         { label: 'Líbero',    icon: '🛡️', color: '#06b6d4' },
		outside_hitter: { label: 'Punta',     icon: '⚡', color: '#ec4899' },
		opposite:       { label: 'Opuesto',   icon: '💥', color: '#f59e0b' },
		middle_blocker: { label: 'Central',   icon: '🧱', color: '#10b981' },
		// Ajedrez
		chess_player:   { label: 'Ajedrecista', icon: '♟️', color: '#06b6d4' }
	};

	let selectedSportFilter = $state('all'); // 'all' | 'football' | 'basketball' | 'volleyball'
	let filteredTeams = $derived(
		selectedSportFilter === 'all'
			? teams
			: teams.filter((t) => (t.sport || 'football') === selectedSportFilter)
	);

	// Color único por equipo basado en su ID
	const palette = [
		{ bg: 'linear-gradient(135deg,#065f46,#047857)', text: '#34d399' },
		{ bg: 'linear-gradient(135deg,#1e3a8a,#1d4ed8)', text: '#93c5fd' },
		{ bg: 'linear-gradient(135deg,#7c2d12,#c2410c)', text: '#fdba74' },
		{ bg: 'linear-gradient(135deg,#4c1d95,#6d28d9)', text: '#c4b5fd' },
		{ bg: 'linear-gradient(135deg,#881337,#be123c)', text: '#fda4af' },
		{ bg: 'linear-gradient(135deg,#164e63,#0e7490)', text: '#67e8f9' },
		{ bg: 'linear-gradient(135deg,#78350f,#b45309)', text: '#fcd34d' },
		{ bg: 'linear-gradient(135deg,#134e4a,#0f766e)', text: '#5eead4' },
	];
	function teamPalette(id) { return palette[(id ?? 0) % palette.length]; }

	async function loadTeams() {
		loading = true; error = null;
		try {
			// Pre-cargar la lista de equipos junto con su plantilla de jugadores en 1 sola consulta
			// y cargar la info del torneo para saber el deporte
			const [teamsRes, tourRes] = await Promise.all([
				teamsApi.list(TOURNAMENT_ID, true),
				tournamentsApi.get(TOURNAMENT_ID).catch(() => null)
			]);
			teams = teamsRes;
			tournament = tourRes;
		} catch (e) {
			error = e.message;
			toast.error('No se pudieron cargar los equipos.');
		} finally {
			loading = false;
		}
	}

	async function viewTeamRoster(team) {
		selectedTeam = team;
		// Si la plantilla ya está pre-cargada en memoria, abrir modal al instante sin delay
		if (team.players && Array.isArray(team.players)) {
			loadingRoster = false;
			return;
		}

		// Fallback por si no estuviese en memoria
		loadingRoster = true;
		try {
			const fullTeam = await teamsApi.get(team.id);
			team.players = fullTeam.players;
			selectedTeam = fullTeam;
		} catch {
			toast.error('No se pudo cargar la plantilla del equipo.');
		} finally {
			loadingRoster = false;
		}
	}

	function closeModal() { selectedTeam = null; }

	// Cerrar modal con Escape
	function handleKeydown(e) { if (e.key === 'Escape') closeModal(); }

	onMount(() => { loadTeams(); });
</script>

<svelte:head>
	<title>Equipos — Torneo Hub</title>
	<meta name="description" content="Directorio de clubes y plantillas registradas en el torneo." />
</svelte:head>

<svelte:window onkeydown={handleKeydown} />

<!-- ── Encabezado ───────────────────────────────────────────────────────────── -->
<div class="flex flex-col sm:flex-row sm:items-center justify-between gap-4 mb-8 animate-fade-in-up">
	<div>
		<h1 class="text-3xl font-black text-white tracking-tight font-display">
			Equipos
			{#if !loading && !error}
				<span class="text-slate-600 text-xl font-semibold ml-2">({teams.length})</span>
			{/if}
		</h1>
		<p class="text-slate-500 mt-1 text-sm">Clubes y plantillas registradas en el torneo</p>
	</div>
	<a href="/equipos/nuevo" class="btn-primary text-sm">
		<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 20 20" fill="currentColor" class="w-4 h-4">
			<path d="M10.75 4.75a.75.75 0 0 0-1.5 0v4.5h-4.5a.75.75 0 0 0 0 1.5h4.5v4.5a.75.75 0 0 0 1.5 0v-4.5h4.5a.75.75 0 0 0 0-1.5h-4.5v-4.5Z"/>
		</svg>
		Registrar Club
	</a>
</div>

<!-- ── Filtro por Deporte ────────────────────────────────────────────────── -->
<div class="flex items-center gap-2 mb-8 p-1.5 bg-slate-900/90 rounded-2xl border border-slate-800 w-fit backdrop-blur-sm shadow-xl">
	<button
		type="button"
		onclick={() => (selectedSportFilter = 'all')}
		class="px-4 py-2 rounded-xl text-xs font-bold transition-all flex items-center gap-2 {selectedSportFilter === 'all' ? 'bg-slate-700 text-white shadow-md' : 'text-slate-400 hover:text-white'}"
	>
		<span>🌐</span>
		<span>Todos</span>
		<span class="text-[10px] px-1.5 py-0.5 rounded-full bg-black/40 font-mono">{teams.length}</span>
	</button>
	<button
		type="button"
		onclick={() => (selectedSportFilter = 'football')}
		class="px-4 py-2 rounded-xl text-xs font-bold transition-all flex items-center gap-2 {selectedSportFilter === 'football' ? 'bg-emerald-600 text-white shadow-md shadow-emerald-950/40' : 'text-slate-400 hover:text-white'}"
	>
		<span>⚽</span>
		<span>Fútbol</span>
		<span class="text-[10px] px-1.5 py-0.5 rounded-full bg-black/40 font-mono">{teams.filter(t => (t.sport || 'football') === 'football').length}</span>
	</button>
	<button
		type="button"
		onclick={() => (selectedSportFilter = 'basketball')}
		class="px-4 py-2 rounded-xl text-xs font-bold transition-all flex items-center gap-2 {selectedSportFilter === 'basketball' ? 'bg-amber-600 text-white shadow-md shadow-amber-950/40' : 'text-slate-400 hover:text-white'}"
	>
		<span>🏀</span>
		<span>Básquetbol</span>
		<span class="text-[10px] px-1.5 py-0.5 rounded-full bg-black/40 font-mono">{teams.filter(t => t.sport === 'basketball').length}</span>
	</button>
	<button
		type="button"
		onclick={() => (selectedSportFilter = 'volleyball')}
		class="px-4 py-2 rounded-xl text-xs font-bold transition-all flex items-center gap-2 {selectedSportFilter === 'volleyball' ? 'bg-violet-600 text-white shadow-md shadow-violet-950/40' : 'text-slate-400 hover:text-white'}"
	>
		<span>🏐</span>
		<span>Vóley</span>
		<span class="text-[10px] px-1.5 py-0.5 rounded-full bg-black/40 font-mono">{teams.filter(t => t.sport === 'volleyball').length}</span>
	</button>
	<button
		type="button"
		onclick={() => (selectedSportFilter = 'underwater_chess')}
		class="px-4 py-2 rounded-xl text-xs font-bold transition-all flex items-center gap-2 {selectedSportFilter === 'underwater_chess' ? 'bg-cyan-600 text-white shadow-md shadow-cyan-950/40' : 'text-slate-400 hover:text-white'}"
	>
		<span>♟️</span>
		<span>Ajedrez bajo el agua</span>
		<span class="text-[10px] px-1.5 py-0.5 rounded-full bg-black/40 font-mono">{teams.filter(t => t.sport === 'underwater_chess').length}</span>
	</button>
</div>

<!-- ── Loading ──────────────────────────────────────────────────────────────── -->
{#if loading}
	<div class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-5">
		{#each Array(6) as _}
			<div class="glass-card p-6 flex flex-col gap-4">
				<div class="flex items-center gap-3">
					<div class="skeleton w-14 h-14 rounded-xl"></div>
					<div class="flex-1 space-y-2">
						<div class="skeleton h-4 w-3/4 rounded"></div>
						<div class="skeleton h-3 w-1/3 rounded"></div>
					</div>
				</div>
				<div class="skeleton h-px w-full"></div>
				<div class="space-y-2">
					<div class="skeleton h-3 w-2/3 rounded"></div>
					<div class="skeleton h-3 w-1/2 rounded"></div>
				</div>
			</div>
		{/each}
	</div>

<!-- ── Error ─────────────────────────────────────────────────────────────────── -->
{:else if error}
	<div class="glass-card p-10 text-center max-w-md mx-auto">
		<div class="w-14 h-14 rounded-2xl bg-red-500/10 border border-red-500/20 flex items-center justify-center mx-auto mb-4">
			<svg xmlns="http://www.w3.org/2000/svg" class="w-7 h-7 text-red-400" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2">
				<path stroke-linecap="round" stroke-linejoin="round" d="M12 9v3.75m-9.303 3.376c-.866 1.5.217 3.374 1.948 3.374h14.71c1.73 0 2.813-1.874 1.948-3.374L13.949 3.378c-.866-1.5-3.032-1.5-3.898 0L2.697 16.126Z"/>
			</svg>
		</div>
		<h2 class="font-bold text-white mb-1">Sin conexión con el servidor</h2>
		<p class="text-slate-500 text-sm mb-5">{error}</p>
		<button onclick={loadTeams} class="btn-ghost text-sm">Reintentar</button>
	</div>

<!-- ── Sin equipos ─────────────────────────────────────────────────────────── -->
{:else if teams.length === 0}
	<div class="glass-card p-16 text-center animate-fade-in-up">
		<div class="w-20 h-20 rounded-3xl bg-emerald-500/10 border border-emerald-500/20 flex items-center justify-center mx-auto mb-5 text-4xl">
			{team.sport === 'basketball' ? '🏀' : team.sport === 'volleyball' ? '🏐' : team.sport === 'underwater_chess' ? '♟️' : '⚽'}
		</div>
		<h2 class="text-xl font-bold text-white mb-2">Sin clubes registrados</h2>
		<p class="text-slate-500 text-sm max-w-sm mx-auto mb-7">
			Sé el primero en inscribir a tu club y cargar la plantilla de jugadores.
		</p>
		<a href="/equipos/nuevo" class="btn-primary">
			Registrar Primer Club
		</a>
	</div>

<!-- ── Lista de equipos ─────────────────────────────────────────────────────── -->
{:else}
	<div class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-5">
		{#if filteredTeams.length === 0}
		<div class="col-span-full glass-card p-12 text-center">
			<div class="text-4xl mb-3">{selectedSportFilter === 'basketball' ? '🏀' : selectedSportFilter === 'volleyball' ? '🏐' : '⚽'}</div>
			<p class="text-white font-bold">No hay equipos de {selectedSportFilter === 'basketball' ? 'básquetbol' : selectedSportFilter === 'volleyball' ? 'vóley' : 'fútbol'} registrados</p>
			<p class="text-slate-400 text-sm mt-1">Registra nuevos clubes para este deporte.</p>
		</div>
	{/if}
	{#each filteredTeams as team, i}
			{@const pal = teamPalette(team.id)}
			<div
				class="glass-card glass-card-green flex flex-col gap-0 animate-fade-in-up overflow-hidden group"
				style="animation-delay: {i * 0.05}s"
			>
				<!-- Cabecera con escudo -->
				<div class="p-5 pb-4 flex items-center gap-4">
					<!-- Escudo del equipo -->
					<div class="w-16 h-16 rounded-2xl flex items-center justify-center text-2xl font-black shadow-lg shrink-0"
						style="background: {pal.bg}; color: {pal.text};">
						{team.name?.[0]?.toUpperCase() ?? '?'}
					</div>
					<div class="min-w-0">
						<h2 class="font-black text-white text-lg leading-tight truncate group-hover:text-emerald-400 transition-colors">
							{team.name}
						</h2>
						<div class="flex items-center gap-2 mt-1">
							<span class="text-xs font-mono font-bold px-2 py-0.5 rounded"
								style="background: {pal.text}18; color: {pal.text};">
								{team.short_name}
							</span>
							{#if team.sport === 'basketball'}
								<span class="text-[11px] font-bold px-2 py-0.5 rounded-full bg-amber-500/15 text-amber-300 border border-amber-500/30 flex items-center gap-1">
									🏀 Básquet
								</span>
							{:else}
								<span class="text-[11px] font-bold px-2 py-0.5 rounded-full bg-emerald-500/15 text-emerald-300 border border-emerald-500/30 flex items-center gap-1">
									⚽ Fútbol
								</span>
							{/if}
							{#if team.city}
								<span class="text-xs text-slate-500 truncate">📍 {team.city}</span>
							{/if}
						</div>
					</div>
				</div>

				<!-- Info del delegado -->
				<div class="px-5 pb-4 border-t border-slate-800/70 pt-3.5 space-y-1.5">
					<div class="flex items-center gap-2 text-sm">
						<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 20 20" fill="currentColor" class="w-4 h-4 text-slate-600 shrink-0">
							<path d="M10 8a3 3 0 1 0 0-6 3 3 0 0 0 0 6ZM3.465 14.493a1.23 1.23 0 0 0 .41 1.412A9.957 9.957 0 0 0 10 18c2.31 0 4.438-.784 6.131-2.1.43-.333.604-.903.408-1.41a7.002 7.002 0 0 0-13.074.003Z"/>
						</svg>
						<span class="text-slate-300 font-medium truncate">{team.delegate_name}</span>
					</div>
					{#if team.delegate_phone}
						<div class="flex items-center gap-2 text-xs text-slate-500">
							<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 20 20" fill="currentColor" class="w-3.5 h-3.5 shrink-0">
								<path fill-rule="evenodd" d="M2 3.5A1.5 1.5 0 0 1 3.5 2h1.148a1.5 1.5 0 0 1 1.465 1.175l.716 3.223a1.5 1.5 0 0 1-1.052 1.767l-.933.267c-.41.117-.643.555-.48.95a11.542 11.542 0 0 0 6.254 6.254c.395.163.833-.07.95-.48l.267-.933a1.5 1.5 0 0 1 1.767-1.052l3.223.716A1.5 1.5 0 0 1 18 15.352V16.5a1.5 1.5 0 0 1-1.5 1.5H15c-1.149 0-2.263-.15-3.326-.43A13.022 13.022 0 0 1 2.43 8.326 13.019 13.019 0 0 1 2 5V3.5Z" clip-rule="evenodd"/>
							</svg>
							<span class="font-mono">{team.delegate_phone}</span>
						</div>
					{/if}
				</div>

				<!-- Botón ver plantilla -->
				<button
					onclick={() => viewTeamRoster(team)}
					class="mt-auto mx-4 mb-4 py-2.5 px-4 rounded-xl text-xs font-bold border border-slate-700/60 bg-slate-800/60 hover:bg-slate-700/60 text-slate-300 hover:text-white transition-colors flex items-center justify-center gap-2"
				>
					<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 20 20" fill="currentColor" class="w-4 h-4">
						<path d="M10 9a3 3 0 1 0 0-6 3 3 0 0 0 0 6ZM6 8a2 2 0 1 1-4 0 2 2 0 0 1 4 0ZM1.49 15.326a.78.78 0 0 1-.358-.442 3 3 0 0 1 4.308-3.516 6.484 6.484 0 0 0-1.905 3.959c-.023.222-.014.442.025.654a4.97 4.97 0 0 1-2.07-.655ZM16.44 15.98a4.97 4.97 0 0 0 2.07-.654.78.78 0 0 0 .357-.442 3 3 0 0 0-4.308-3.517 6.484 6.484 0 0 1 1.907 3.96 2.32 2.32 0 0 1-.026.654ZM18 8a2 2 0 1 1-4 0 2 2 0 0 1 4 0ZM5.304 16.19a.844.844 0 0 1-.277-.71 5 5 0 0 1 9.947 0 .843.843 0 0 1-.277.71A6.975 6.975 0 0 1 10 18a6.974 6.974 0 0 1-4.696-1.81Z"/>
					</svg>
					Ver Plantilla
				</button>
			</div>
		{/each}
	</div>
{/if}

<!-- ── MODAL: PLANTILLA ─────────────────────────────────────────────────────── -->
{#if selectedTeam}
	{@const pal = teamPalette(selectedTeam.id)}
	<div
		class="fixed inset-0 z-50 flex items-center justify-center p-4"
		style="background: rgba(4,8,16,0.85);"
		role="dialog"
		aria-modal="true"
		onclick={(e) => e.target === e.currentTarget && closeModal()}
	>
		<div class="w-full max-w-2xl max-h-[90vh] flex flex-col rounded-2xl overflow-hidden shadow-2xl animate-fade-in-up border border-slate-700/60"
			style="background: #0e1420;">

			<!-- Header del modal -->
			<div class="p-5 flex items-center gap-4 border-b border-slate-800">
				<div class="w-14 h-14 rounded-xl flex items-center justify-center text-2xl font-black shrink-0"
					style="background: {pal.bg}; color: {pal.text};">
					{selectedTeam.name?.[0]?.toUpperCase() ?? '?'}
				</div>
				<div class="flex items-center gap-1.5 p-1 bg-slate-900 rounded-lg border border-slate-800 shrink-0">
					<button
						type="button"
						onclick={() => (rosterViewMode = 'list')}
						class="px-2.5 py-1 rounded text-xs font-bold transition {rosterViewMode === 'list' ? 'bg-slate-700 text-white' : 'text-slate-400 hover:text-white'}"
					>
						📋 Lista
					</button>
					<button
						type="button"
						onclick={() => (rosterViewMode = 'pitch')}
						class="px-2.5 py-1 rounded text-xs font-bold transition {rosterViewMode === 'pitch' ? 'bg-emerald-600 text-white shadow' : 'text-slate-400 hover:text-white'}"
					>
						🏟️ Cancha
					</button>
				</div>
				<div class="flex-1 min-w-0">
					<h3 class="text-lg font-black text-white truncate flex items-center gap-2">
						{selectedTeam.name}
						<span class="text-xs font-mono font-bold px-2 py-0.5 rounded"
							style="background: {pal.text}18; color: {pal.text};">
							{selectedTeam.short_name}
						</span>
					</h3>
					<p class="text-xs text-slate-500 mt-0.5">Delegado: {selectedTeam.delegate_name}</p>
				</div>
				<button
					onclick={closeModal}
					class="w-8 h-8 rounded-lg flex items-center justify-center text-slate-500 hover:text-white hover:bg-slate-800 transition shrink-0"
					aria-label="Cerrar"
				>
					<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 20 20" fill="currentColor" class="w-4 h-4">
						<path d="M6.28 5.22a.75.75 0 0 0-1.06 1.06L8.94 10l-3.72 3.72a.75.75 0 1 0 1.06 1.06L10 11.06l3.72 3.72a.75.75 0 1 0 1.06-1.06L11.06 10l3.72-3.72a.75.75 0 0 0-1.06-1.06L10 8.94 6.28 5.22Z"/>
					</svg>
				</button>
			</div>

			<!-- Plantilla -->
			<div class="flex-1 overflow-y-auto p-5">
				<div class="flex items-center justify-between mb-4">
					<p class="section-label">Jugadores registrados</p>
					{#if selectedTeam.players}
						<span class="text-xs px-2.5 py-1 rounded-full font-semibold"
							style="background: {pal.text}15; color: {pal.text};">
							{selectedTeam.players.length} en plantilla
						</span>
					{/if}
				</div>

				{#if loadingRoster}
					<div class="space-y-3">
						{#each Array(5) as _}
							<div class="skeleton h-14 w-full rounded-xl"></div>
						{/each}
					</div>
				{:else if !selectedTeam.players || selectedTeam.players.length === 0}
					<div class="py-12 text-center text-slate-600">
						<div class="text-3xl mb-3 opacity-40">👥</div>
						<p class="text-sm">Sin jugadores registrados aún.</p>
					</div>
				{:else if rosterViewMode === 'pitch'}
					<div class="py-2">
						{#if selectedTeam.sport === 'basketball'}
						<BasketballCourt
							players={selectedTeam.players}
							interactive={false}
							teamName={selectedTeam.name}
							teamColor={pal.text}
						/>
					{:else if selectedTeam.sport === 'volleyball'}
						<VolleyballCourt
							players={selectedTeam.players}
							interactive={false}
							teamName={selectedTeam.name}
							teamColor={pal.text}
						/>
					{:else if selectedTeam.sport === 'underwater_chess'}
						<UnderwaterChessBoard
							players={selectedTeam.players}
							interactive={false}
							teamName={selectedTeam.name}
							teamColor={pal.text}
						/>
					{:else}
						<SoccerPitch
							players={selectedTeam.players}
							interactive={false}
							teamName={selectedTeam.name}
							teamColor={pal.text}
						/>
					{/if}
					</div>
				{:else}
					<div class="space-y-2">
						{#each [...(selectedTeam.players || [])].sort((a,b) => (a.shirt_number??99)-(b.shirt_number??99)) as p}
							{@const pos = positionLabels[p.position]}
							<div class="flex items-center gap-3 p-3 rounded-xl border border-slate-800/60 hover:border-slate-700 hover:bg-slate-800/30 transition-colors">
								<!-- Dorsal -->
								<div class="w-9 h-9 rounded-lg flex items-center justify-center font-score font-bold text-sm shrink-0"
									style="background: {pal.text}15; color: {pal.text}; border: 1px solid {pal.text}30;">
									{p.shirt_number !== null && p.shirt_number !== undefined ? p.shirt_number : '-'}
								</div>
								<!-- Nombre -->
								<div class="flex-1 min-w-0">
									<p class="font-semibold text-white text-sm leading-tight truncate">
										{p.first_name} {p.last_name}
									</p>
									<p class="text-xs text-slate-500 font-mono">DNI {p.dni}</p>
								</div>
								<!-- Posición -->
								{#if pos}
									<span class="text-xs px-2.5 py-1 rounded-lg font-semibold shrink-0"
										style="background: {pos.color}18; color: {pos.color}; border: 1px solid {pos.color}25;">
										{pos.icon} {pos.label}
									</span>
								{/if}
							</div>
						{/each}
					</div>
				{/if}
			</div>

			<!-- Footer -->
			<div class="p-4 border-t border-slate-800 flex justify-end">
				<button onclick={closeModal} class="btn-ghost text-sm">Cerrar</button>
			</div>
		</div>
	</div>
{/if}
