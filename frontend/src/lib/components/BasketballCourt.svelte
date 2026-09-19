<script>
	/**
	 * BasketballCourt.svelte — Diagrama Interactivo y Visual de Cancha de Básquetbol
	 *
	 * Modos:
	 * 1. interactive = true: Permite agregar jugadores haciendo clic en los botones (+),
	 *    y eliminar o interactuar con cada jugador en la pista.
	 * 2. interactive = false: Modo de solo lectura / visualización para ver alineaciones
	 *    en detalle de equipos, partidos y público.
	 *
	 * Posiciones:
	 *   - point_guard   → Base (1)
	 *   - shooting_guard → Escolta (2)
	 *   - small_forward  → Alero (3)
	 *   - power_forward  → Ala-Pívot (4)
	 *   - center         → Pívot (5)
	 */

	let {
		players = [],
		interactive = false,
		teamName = 'Equipo',
		teamColor = '#f59e0b',
		onAddPlayer = null,
		onRemovePlayer = null,
		onSelectPlayer = null
	} = $props();

	// Agrupación de jugadores por posición
	let pointGuards    = $derived(players.filter((p) => p.position === 'point_guard'));
	let shootingGuards = $derived(players.filter((p) => p.position === 'shooting_guard'));
	let smallForwards  = $derived(players.filter((p) => p.position === 'small_forward'));
	let powerForwards  = $derived(players.filter((p) => p.position === 'power_forward'));
	let centers        = $derived(players.filter((p) => p.position === 'center'));

	// Posiciones no estándar van a "banca"
	const basketballPositions = ['point_guard', 'shooting_guard', 'small_forward', 'power_forward', 'center'];
	let benchPlayers = $derived(players.filter((p) => !basketballPositions.includes(p.position)));

	function getShortDisplayName(player) {
		if (player.last_name) return player.last_name;
		if (player.first_name) return player.first_name.split(' ')[0];
		return `#${player.shirt_number ?? '?'}`;
	}

	/** Genera un botón de jugador en cancha */
	function playerColor(position) {
		const colors = {
			point_guard:    { bg: teamColor, text: '#1e293b' },
			shooting_guard: { bg: '#3b82f6', text: '#fff' },
			small_forward:  { bg: '#10b981', text: '#fff' },
			power_forward:  { bg: '#8b5cf6', text: '#fff' },
			center:         { bg: '#f59e0b', text: '#1e293b' },
		};
		return colors[position] ?? { bg: teamColor, text: '#fff' };
	}
</script>

<div class="flex flex-col gap-3 w-full select-none">
	<!-- ── HEADER ─────────────────────────────────────────────────────────────── -->
	<div class="flex items-center justify-between px-3.5 py-2.5 rounded-xl bg-slate-900/90 border border-slate-800 text-xs shadow-md">
		<div class="flex items-center gap-2">
			<span class="w-3.5 h-3.5 rounded-full shadow border border-white/30" style="background-color: {teamColor};"></span>
			<span class="font-black text-white text-sm">{teamName}</span>
			<span class="text-slate-400">({players.length} jugador{players.length !== 1 ? 'es' : ''})</span>
		</div>
		<div class="flex items-center gap-1.5 font-mono text-[11px]">
			<span class="px-2 py-0.5 rounded font-bold" style="background-color: {teamColor}22; color: {teamColor}; border: 1px solid {teamColor}44;">
				🏀 {pointGuards.length} BASE
			</span>
			<span class="px-2 py-0.5 rounded bg-blue-950/70 text-blue-300 border border-blue-700/50 font-bold">
				🎯 {shootingGuards.length} ESC
			</span>
			<span class="px-2 py-0.5 rounded bg-emerald-950/70 text-emerald-300 border border-emerald-700/50 font-bold">
				🏃 {smallForwards.length} ALE
			</span>
			<span class="px-2 py-0.5 rounded bg-purple-950/70 text-purple-300 border border-purple-700/50 font-bold">
				💪 {powerForwards.length} AP
			</span>
			<span class="px-2 py-0.5 rounded bg-amber-950/70 text-amber-300 border border-amber-700/50 font-bold">
				🛡️ {centers.length} PIV
			</span>
		</div>
	</div>

	<!-- ── PISTA DE BALONCESTO ─────────────────────────────────────────────────── -->
	<div
		class="relative w-full rounded-2xl overflow-hidden shadow-2xl border-4 border-slate-700/90 flex flex-col justify-between"
		style="
			background: repeating-linear-gradient(
				180deg,
				#7c3c0e 0px,
				#7c3c0e 60px,
				#8a4510 60px,
				#8a4510 120px
			);
			min-height: 520px;
			height: 520px;
		"
	>
		<!-- Línea perimetral blanca -->
		<div class="absolute inset-3 border-2 border-white/50 rounded-lg pointer-events-none"></div>

		<!-- Aro y área superior (zona rival) -->
		<div class="absolute top-3 left-1/2 -translate-x-1/2 w-32 h-20 border-b-2 border-x-2 border-white/50 pointer-events-none rounded-b-3xl"></div>
		<div class="absolute top-3 left-1/2 -translate-x-1/2 w-10 h-10 border-2 border-white/60 rounded-full pointer-events-none"
			style="top: 3.2rem; transform: translateX(-50%);">
		</div>
		<!-- Línea de 3 puntos superior (arco) -->
		<div class="absolute pointer-events-none" style="top: 3px; left: 50%; transform: translateX(-50%); width: 220px; height: 110px; border: 2px solid rgba(255,255,255,0.35); border-top: none; border-radius: 0 0 110px 110px;"></div>

		<!-- Línea central y círculo central -->
		<div class="absolute top-1/2 left-3 right-3 h-0.5 bg-white/45 -translate-y-1/2 pointer-events-none"></div>
		<div class="absolute top-1/2 left-1/2 w-24 h-24 border-2 border-white/45 rounded-full -translate-x-1/2 -translate-y-1/2 pointer-events-none"></div>
		<div class="absolute top-1/2 left-1/2 w-2.5 h-2.5 bg-white/60 rounded-full -translate-x-1/2 -translate-y-1/2 pointer-events-none"></div>

		<!-- Aro y área inferior (nuestra canasta) -->
		<div class="absolute bottom-3 left-1/2 -translate-x-1/2 w-32 h-20 border-t-2 border-x-2 border-white/50 pointer-events-none rounded-t-3xl"></div>
		<div class="absolute pointer-events-none" style="bottom: calc(1rem + 20px); left: 50%; transform: translateX(-50%); width: 40px; height: 40px; border: 2px solid rgba(255,255,255,0.6); border-radius: 50%;"></div>
		<!-- Línea de 3 puntos inferior (arco) -->
		<div class="absolute pointer-events-none" style="bottom: 3px; left: 50%; transform: translateX(-50%); width: 220px; height: 110px; border: 2px solid rgba(255,255,255,0.35); border-bottom: none; border-radius: 110px 110px 0 0;"></div>

		<!-- ── ZONA 1: BASES (+ button → point_guard) ── -->
		<div class="relative z-10 flex-1 flex flex-col items-center justify-end pb-2 pt-3">
			<div class="flex items-center justify-center flex-wrap gap-4 sm:gap-5 w-full px-4">
				{#each pointGuards as p}
					<div class="flex flex-col items-center group transition-transform hover:scale-110">
						<div class="relative">
							<button
								type="button"
								class="w-12 h-12 rounded-full flex items-center justify-center text-sm font-black shadow-2xl border-2 border-white/90 cursor-pointer"
								style="background: {playerColor('point_guard').bg}; color: {playerColor('point_guard').text};"
								onclick={() => onSelectPlayer?.(p)}
								title="{p.first_name} {p.last_name} (Base)"
							>
								{p.shirt_number ?? '🏀'}
							</button>
							{#if interactive && onRemovePlayer}
								<button
									type="button"
									onclick={() => onRemovePlayer(p)}
									title="Quitar de la cancha"
									class="absolute -top-1.5 -right-1.5 w-5 h-5 bg-red-600 hover:bg-red-500 text-white rounded-full text-xs font-black flex items-center justify-center shadow-lg z-20 cursor-pointer"
								>✕</button>
							{/if}
						</div>
						<span class="mt-1 px-2 py-0.5 rounded-md text-[11px] font-bold text-white bg-slate-950/85 border border-white/20 truncate max-w-[90px] text-center shadow">
							{getShortDisplayName(p)}
						</span>
					</div>
				{/each}

				{#if interactive && onAddPlayer}
					<button
						type="button"
						onclick={() => onAddPlayer('point_guard')}
						title="Agregar Base"
						class="w-11 h-11 rounded-full border-2 border-dashed text-xs font-bold transition shadow cursor-pointer flex flex-col items-center justify-center"
						style="border-color: {teamColor}cc; background-color: {teamColor}22; color: {teamColor};"
					>
						<span>+</span>
						<span class="text-[9px] font-mono leading-none">BASE</span>
					</button>
				{:else if pointGuards.length === 0}
					<span class="text-[11px] text-white/60 bg-black/40 px-3 py-1 rounded-full border border-white/10">Sin base</span>
				{/if}
			</div>
		</div>

		<!-- ── ZONA 2: ESCOLTAS (shooting_guard) ── -->
		<div class="relative z-10 flex-1 flex flex-col items-center justify-center py-1">
			<div class="flex items-center justify-center flex-wrap gap-4 sm:gap-5 w-full px-4">
				{#each shootingGuards as p}
					<div class="flex flex-col items-center group transition-transform hover:scale-110">
						<div class="relative">
							<button
								type="button"
								class="w-12 h-12 rounded-full flex items-center justify-center text-sm font-black text-white shadow-2xl border-2 border-white/90 cursor-pointer bg-blue-500"
								onclick={() => onSelectPlayer?.(p)}
								title="{p.first_name} {p.last_name} (Escolta)"
							>
								{p.shirt_number ?? '🎯'}
							</button>
							{#if interactive && onRemovePlayer}
								<button
									type="button"
									onclick={() => onRemovePlayer(p)}
									title="Quitar de la cancha"
									class="absolute -top-1.5 -right-1.5 w-5 h-5 bg-red-600 hover:bg-red-500 text-white rounded-full text-xs font-black flex items-center justify-center shadow-lg z-20 cursor-pointer"
								>✕</button>
							{/if}
						</div>
						<span class="mt-1 px-2 py-0.5 rounded-md text-[11px] font-bold text-white bg-slate-950/85 border border-white/20 truncate max-w-[90px] text-center shadow">
							{getShortDisplayName(p)}
						</span>
					</div>
				{/each}

				{#if interactive && onAddPlayer}
					<button
						type="button"
						onclick={() => onAddPlayer('shooting_guard')}
						title="Agregar Escolta"
						class="w-11 h-11 rounded-full border-2 border-dashed border-blue-300/80 bg-blue-500/20 hover:bg-blue-500/40 text-blue-200 flex flex-col items-center justify-center text-xs font-bold transition shadow cursor-pointer"
					>
						<span>+</span>
						<span class="text-[9px] font-mono leading-none">ESC</span>
					</button>
				{:else if shootingGuards.length === 0}
					<span class="text-[11px] text-white/60 bg-black/40 px-3 py-1 rounded-full border border-white/10">Sin escoltas</span>
				{/if}
			</div>
		</div>

		<!-- ── ZONA 3: ALEROS (small_forward) — CRUCE LINEA CENTRAL ── -->
		<div class="relative z-10 flex-1 flex flex-col items-center justify-center py-1">
			<div class="flex items-center justify-center flex-wrap gap-4 sm:gap-5 w-full px-4">
				{#each smallForwards as p}
					<div class="flex flex-col items-center group transition-transform hover:scale-110">
						<div class="relative">
							<button
								type="button"
								class="w-12 h-12 rounded-full flex items-center justify-center text-sm font-black text-white shadow-2xl border-2 border-white/90 cursor-pointer bg-emerald-500"
								onclick={() => onSelectPlayer?.(p)}
								title="{p.first_name} {p.last_name} (Alero)"
							>
								{p.shirt_number ?? '🏃'}
							</button>
							{#if interactive && onRemovePlayer}
								<button
									type="button"
									onclick={() => onRemovePlayer(p)}
									title="Quitar de la cancha"
									class="absolute -top-1.5 -right-1.5 w-5 h-5 bg-red-600 hover:bg-red-500 text-white rounded-full text-xs font-black flex items-center justify-center shadow-lg z-20 cursor-pointer"
								>✕</button>
							{/if}
						</div>
						<span class="mt-1 px-2 py-0.5 rounded-md text-[11px] font-bold text-white bg-slate-950/85 border border-white/20 truncate max-w-[90px] text-center shadow">
							{getShortDisplayName(p)}
						</span>
					</div>
				{/each}

				{#if interactive && onAddPlayer}
					<button
						type="button"
						onclick={() => onAddPlayer('small_forward')}
						title="Agregar Alero"
						class="w-11 h-11 rounded-full border-2 border-dashed border-emerald-300/80 bg-emerald-500/20 hover:bg-emerald-500/40 text-emerald-200 flex flex-col items-center justify-center text-xs font-bold transition shadow cursor-pointer"
					>
						<span>+</span>
						<span class="text-[9px] font-mono leading-none">ALE</span>
					</button>
				{:else if smallForwards.length === 0}
					<span class="text-[11px] text-white/60 bg-black/40 px-3 py-1 rounded-full border border-white/10">Sin aleros</span>
				{/if}
			</div>
		</div>

		<!-- ── ZONA 4: ALA-PÍVOTS (power_forward) ── -->
		<div class="relative z-10 flex-1 flex flex-col items-center justify-center py-1">
			<div class="flex items-center justify-center flex-wrap gap-4 sm:gap-5 w-full px-4">
				{#each powerForwards as p}
					<div class="flex flex-col items-center group transition-transform hover:scale-110">
						<div class="relative">
							<button
								type="button"
								class="w-12 h-12 rounded-full flex items-center justify-center text-sm font-black text-white shadow-2xl border-2 border-white/90 cursor-pointer bg-purple-500"
								onclick={() => onSelectPlayer?.(p)}
								title="{p.first_name} {p.last_name} (Ala-Pívot)"
							>
								{p.shirt_number ?? '💪'}
							</button>
							{#if interactive && onRemovePlayer}
								<button
									type="button"
									onclick={() => onRemovePlayer(p)}
									title="Quitar de la cancha"
									class="absolute -top-1.5 -right-1.5 w-5 h-5 bg-red-600 hover:bg-red-500 text-white rounded-full text-xs font-black flex items-center justify-center shadow-lg z-20 cursor-pointer"
								>✕</button>
							{/if}
						</div>
						<span class="mt-1 px-2 py-0.5 rounded-md text-[11px] font-bold text-white bg-slate-950/85 border border-white/20 truncate max-w-[90px] text-center shadow">
							{getShortDisplayName(p)}
						</span>
					</div>
				{/each}

				{#if interactive && onAddPlayer}
					<button
						type="button"
						onclick={() => onAddPlayer('power_forward')}
						title="Agregar Ala-Pívot"
						class="w-11 h-11 rounded-full border-2 border-dashed border-purple-300/80 bg-purple-500/20 hover:bg-purple-500/40 text-purple-200 flex flex-col items-center justify-center text-xs font-bold transition shadow cursor-pointer"
					>
						<span>+</span>
						<span class="text-[9px] font-mono leading-none">A-P</span>
					</button>
				{:else if powerForwards.length === 0}
					<span class="text-[11px] text-white/60 bg-black/40 px-3 py-1 rounded-full border border-white/10">Sin ala-pívots</span>
				{/if}
			</div>
		</div>

		<!-- ── ZONA 5: PÍVOTS/CENTERS (center) — nuestra canasta ── -->
		<div class="relative z-10 flex-1 flex flex-col items-center justify-center pb-3 pt-1">
			<div class="flex items-center justify-center flex-wrap gap-4 sm:gap-5 w-full px-4">
				{#each centers as p}
					<div class="flex flex-col items-center group transition-transform hover:scale-110">
						<div class="relative">
							<button
								type="button"
								class="w-12 h-12 rounded-full flex items-center justify-center text-sm font-black text-slate-950 bg-amber-400 shadow-2xl border-2 border-white/90 cursor-pointer"
								onclick={() => onSelectPlayer?.(p)}
								title="{p.first_name} {p.last_name} (Pívot)"
							>
								{p.shirt_number ?? '5'}
							</button>
							{#if interactive && onRemovePlayer}
								<button
									type="button"
									onclick={() => onRemovePlayer(p)}
									title="Quitar de la cancha"
									class="absolute -top-1.5 -right-1.5 w-5 h-5 bg-red-600 hover:bg-red-500 text-white rounded-full text-xs font-black flex items-center justify-center shadow-lg z-20 cursor-pointer"
								>✕</button>
							{/if}
						</div>
						<span class="mt-1 px-2 py-0.5 rounded-md text-[11px] font-bold text-amber-300 bg-slate-950/90 border border-amber-400/30 truncate max-w-[90px] text-center shadow">
							{getShortDisplayName(p)}
						</span>
					</div>
				{/each}

				{#if interactive && onAddPlayer}
					<button
						type="button"
						onclick={() => onAddPlayer('center')}
						title="Agregar Pívot / Center"
						class="w-11 h-11 rounded-full border-2 border-dashed border-amber-300/80 bg-amber-500/20 hover:bg-amber-500/40 text-amber-200 flex flex-col items-center justify-center text-xs font-bold transition shadow cursor-pointer"
					>
						<span>+</span>
						<span class="text-[9px] font-mono leading-none">PIV</span>
					</button>
				{:else if centers.length === 0}
					<span class="text-[11px] text-white/60 bg-black/40 px-3 py-1 rounded-full border border-white/10">Sin pívot</span>
				{/if}
			</div>
		</div>
	</div>

	<!-- ── BANCA ──────────────────────────────────────────────────────────────── -->
	{#if benchPlayers.length > 0}
		<div class="p-3 rounded-xl bg-slate-900/70 border border-slate-800">
			<span class="text-xs font-bold text-slate-400 flex items-center gap-1.5 mb-2">
				🪑 Reserva / Suplentes ({benchPlayers.length})
			</span>
			<div class="flex items-center gap-2 overflow-x-auto pb-1">
				{#each benchPlayers as p}
					<div class="flex items-center gap-1.5 px-2.5 py-1 rounded-lg bg-slate-800/80 border border-slate-700 text-xs shrink-0">
						<span class="font-mono font-black text-amber-400">#{p.shirt_number ?? '?'}</span>
						<span class="text-white font-medium">{getShortDisplayName(p)}</span>
						{#if interactive && onRemovePlayer}
							<button
								type="button"
								onclick={() => onRemovePlayer(p)}
								class="text-red-400 hover:text-red-300 ml-1 font-bold cursor-pointer"
								title="Eliminar de la banca"
							>✕</button>
						{/if}
					</div>
				{/each}
			</div>
		</div>
	{/if}
</div>
