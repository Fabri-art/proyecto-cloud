<script>
	/**
	 * routes/equipos/+page.svelte — Página de Equipos (/equipos)
	 *
	 * ¿Qué muestra?
	 * - Lista de todos los equipos registrados en el torneo.
	 * - Botón "+ Registrar Nuevo Club" que conduce a /equipos/nuevo (NOM-11).
	 * - Vista interactiva de la plantilla (jugadores) de cada equipo con modal de detalle.
	 */
	import { onMount } from 'svelte';
	import { teamsApi } from '$lib/api/client';
	import { toast } from '$lib/stores/toast';

	// Estado de la página
	let teams = $state([]);
	let loading = $state(true);
	let error = $state(null);

	// Estado para modal de detalles del equipo
	let selectedTeam = $state(null);
	let loadingRoster = $state(false);

	// Posiciones disponibles con etiquetas amigables
	const positionLabels = {
		goalkeeper: { label: 'Arquero', icon: '🧤' },
		defender:   { label: 'Defensa', icon: '🛡️' },
		midfielder: { label: 'Mediocampista', icon: '⚙️' },
		forward:    { label: 'Delantero', icon: '⚽' }
	};

	async function loadTeams() {
		loading = true;
		error = null;
		try {
			teams = await teamsApi.list();
		} catch (e) {
			error = e.message;
			toast.error('No se pudieron cargar los equipos.');
		} finally {
			loading = false;
		}
	}

	async function viewTeamRoster(team) {
		selectedTeam = team;
		loadingRoster = true;
		try {
			const fullTeam = await teamsApi.get(team.id);
			selectedTeam = fullTeam;
		} catch (e) {
			toast.error('No se pudo cargar la plantilla del equipo.');
		} finally {
			loadingRoster = false;
		}
	}

	function closeModal() {
		selectedTeam = null;
	}

	onMount(() => {
		loadTeams();
	});
</script>

<svelte:head>
	<title>Equipos — Nombre-Creativo</title>
	<meta name="description" content="Listado de todos los equipos registrados en el torneo." />
</svelte:head>

<!-- ── Encabezado con Botón de Registro (NOM-11) ──────────────────────────── -->
<div class="flex flex-col sm:flex-row sm:items-center justify-between gap-4 mb-8 animate-fade-in-up">
	<div>
		<h1 class="text-3xl font-black text-white flex items-center gap-3">
			👕 Equipos
		</h1>
		<p class="text-slate-400 mt-1">
			Equipos registrados en el torneo
			{#if !loading && !error}
				<span class="text-slate-500 font-semibold">({teams.length})</span>
			{/if}
		</p>
	</div>

	<!-- Botón para registrar nuevo equipo -->
	<div>
		<a
			href="/equipos/nuevo"
			class="inline-flex items-center gap-2 px-5 py-2.5 rounded-xl font-bold text-white bg-emerald-600 hover:bg-emerald-500 shadow-lg shadow-emerald-950 transition hover:scale-105"
		>
			<span>➕</span>
			<span>Registrar Nuevo Club</span>
		</a>
	</div>
</div>

<!-- ── Estado: cargando ───────────────────────────────────────────────────── -->
{#if loading}
	<div class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4">
		{#each Array(6) as _}
			<div class="glass-card p-6 flex flex-col gap-3">
				<div class="skeleton h-5 w-2/3"></div>
				<div class="skeleton h-4 w-1/2"></div>
				<div class="skeleton h-4 w-1/3"></div>
			</div>
		{/each}
	</div>

<!-- ── Estado: error ─────────────────────────────────────────────────────── -->
{:else if error}
	<div class="glass-card p-8 text-center">
		<div class="text-4xl mb-3">⚠️</div>
		<h2 class="text-lg font-semibold text-white mb-2">No se pudo conectar con el servidor</h2>
		<p class="text-slate-400 text-sm">{error}</p>
		<div class="mt-4">
			<button
				onclick={loadTeams}
				class="px-4 py-2 rounded-lg text-sm bg-slate-800 text-white hover:bg-slate-700 transition"
			>
				Reintentar
			</button>
		</div>
	</div>

<!-- ── Estado: sin equipos ──────────────────────────────────────────────── -->
{:else if teams.length === 0}
	<div class="glass-card p-12 text-center animate-fade-in-up">
		<div class="text-5xl mb-4">⚽</div>
		<h2 class="text-xl font-bold text-white mb-2">Aún no hay clubes registrados</h2>
		<p class="text-slate-400 text-sm max-w-md mx-auto mb-6">
			Sé el primero en inscribir a tu club y cargar la plantilla de jugadores para el torneo.
		</p>
		<a
			href="/equipos/nuevo"
			class="inline-flex items-center gap-2 px-6 py-3 rounded-xl font-bold text-white bg-emerald-600 hover:bg-emerald-500 transition shadow-lg shadow-emerald-950"
		>
			<span>➕</span>
			<span>Registrar Primer Club</span>
		</a>
	</div>

<!-- ── Lista de equipos ──────────────────────────────────────────────────── -->
{:else}
	<div class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-5">
		{#each teams as team, i}
			<div
				class="glass-card p-6 flex flex-col justify-between gap-5 animate-fade-in-up group"
				style="animation-delay: {i * 0.05}s"
			>
				<div>
					<!-- Cabecera de la tarjeta con inicial y sigla -->
					<div class="flex items-start justify-between gap-3 mb-3">
						<div class="flex items-center gap-3 min-w-0">
							<div
								class="w-12 h-12 rounded-xl flex items-center justify-center text-xl font-black text-white shrink-0 shadow-md"
								style="background: linear-gradient(135deg, var(--accent-green), #16a34a);"
							>
								{team.name?.[0]?.toUpperCase() ?? '?'}
							</div>
							<div class="min-w-0">
								<h2 class="font-bold text-white text-lg truncate group-hover:text-emerald-400 transition">
									{team.name}
								</h2>
								<span class="inline-block px-2 py-0.5 rounded text-xs font-mono font-bold bg-slate-800 text-slate-300">
									{team.short_name}
								</span>
							</div>
						</div>
					</div>

					<!-- Datos del club -->
					<div class="text-sm text-slate-400 space-y-1.5 pt-2 border-t border-slate-800">
						<p class="flex items-center gap-2 truncate">
							<span class="text-slate-500">👤 Delegado:</span>
							<span class="text-slate-300 font-medium">{team.delegate_name}</span>
						</p>
						{#if team.delegate_phone}
							<p class="flex items-center gap-2 text-xs truncate">
								<span class="text-slate-500">📞 Tel:</span>
								<span class="text-slate-400 font-mono">{team.delegate_phone}</span>
							</p>
						{/if}
						{#if team.city || team.country}
							<p class="flex items-center gap-2 text-xs truncate">
								<span class="text-slate-500">📍 Ubicación:</span>
								<span class="text-slate-400">{[team.city, team.country].filter(Boolean).join(', ')}</span>
							</p>
						{/if}
					</div>
				</div>

				<!-- Botón para ver plantilla completa -->
				<button
					onclick={() => viewTeamRoster(team)}
					class="w-full py-2 px-3 rounded-lg text-xs font-semibold bg-slate-800/80 hover:bg-slate-700 text-slate-300 hover:text-white transition flex items-center justify-center gap-2 border border-slate-700/60"
				>
					<span>👥</span>
					<span>Ver Plantilla de Jugadores</span>
				</button>
			</div>
		{/each}
	</div>
{/if}

<!-- ── MODAL: DETALLES Y PLANTILLA DEL EQUIPO ──────────────────────────────── -->
{#if selectedTeam}
	<div
		class="fixed inset-0 z-50 flex items-center justify-center p-4 bg-slate-950/80 backdrop-blur-sm animate-fade-in-up"
		role="dialog"
		aria-modal="true"
	>
		<div class="glass-card w-full max-w-2xl max-h-[90vh] flex flex-col overflow-hidden shadow-2xl border border-slate-700">
			<!-- Encabezado del modal -->
			<div class="p-6 border-b border-slate-800 flex items-center justify-between bg-slate-900/60">
				<div class="flex items-center gap-3">
					<div
						class="w-10 h-10 rounded-lg flex items-center justify-center text-lg font-black text-white"
						style="background: linear-gradient(135deg, var(--accent-green), #16a34a);"
					>
						{selectedTeam.name?.[0]?.toUpperCase() ?? '?'}
					</div>
					<div>
						<h3 class="text-lg font-bold text-white flex items-center gap-2">
							{selectedTeam.name}
							<span class="text-xs px-2 py-0.5 rounded bg-slate-800 font-mono text-emerald-400">
								{selectedTeam.short_name}
							</span>
						</h3>
						<p class="text-xs text-slate-400">Delegado: {selectedTeam.delegate_name}</p>
					</div>
				</div>

				<button
					onclick={closeModal}
					class="p-2 rounded-lg text-slate-400 hover:text-white hover:bg-slate-800 transition"
					aria-label="Cerrar modal"
				>
					✕
				</button>
			</div>

			<!-- Contenido del modal (Plantilla) -->
			<div class="p-6 overflow-y-auto flex-1">
				<h4 class="text-sm font-bold text-slate-300 mb-4 flex items-center justify-between">
					<span>👥 Jugadores Registrados</span>
					{#if selectedTeam.players}
						<span class="text-xs px-2 py-0.5 rounded-full bg-slate-800 text-slate-400 font-semibold">
							{selectedTeam.players.length} en plantilla
						</span>
					{/if}
				</h4>

				{#if loadingRoster}
					<div class="space-y-3">
						{#each Array(4) as _}
							<div class="skeleton h-12 w-full rounded-lg"></div>
						{/each}
					</div>
				{:else if !selectedTeam.players || selectedTeam.players.length === 0}
					<div class="text-center py-8 text-slate-500">
						<p class="text-3xl mb-2">⚽</p>
						<p class="text-sm">Este equipo aún no tiene jugadores registrados.</p>
					</div>
				{:else}
					<div class="divide-y divide-slate-800/80 rounded-xl border border-slate-800 overflow-hidden">
						{#each selectedTeam.players as p}
							<div class="p-3.5 flex items-center justify-between hover:bg-slate-800/30 transition">
								<div class="flex items-center gap-3">
									<div class="w-8 h-8 rounded-full bg-slate-800 flex items-center justify-center font-mono font-bold text-emerald-400 text-xs shrink-0">
										{p.shirt_number ?? '-'}
									</div>
									<div>
										<p class="font-semibold text-white text-sm">
											{p.first_name} {p.last_name}
										</p>
										<p class="text-xs text-slate-400 font-mono">
											DNI: {p.dni}
										</p>
									</div>
								</div>

								<div class="text-right">
									<span class="text-xs px-2.5 py-1 rounded-full bg-slate-800 text-slate-300 font-medium">
										{positionLabels[p.position]?.icon ?? '⚽'}
										{positionLabels[p.position]?.label ?? p.position ?? 'Sin definir'}
									</span>
								</div>
							</div>
						{/each}
					</div>
				{/if}
			</div>

			<!-- Pie del modal -->
			<div class="p-4 border-t border-slate-800 bg-slate-900/60 flex justify-end">
				<button
					onclick={closeModal}
					class="px-4 py-2 rounded-lg text-sm font-semibold bg-slate-800 hover:bg-slate-700 text-white transition"
				>
					Cerrar
				</button>
			</div>
		</div>
	</div>
{/if}
