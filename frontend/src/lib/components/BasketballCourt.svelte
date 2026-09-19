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
	 *   - point_guard    → Base (1)
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
</script>

<div class="flex flex-col gap-3 w-full select-none">
	<!-- ── HEADER DE LA PISTA ──────────────────────────────────────────────── -->
	<div class="flex items-center justify-between px-3.5 py-2.5 rounded-xl bg-slate-900/90 border border-slate-800 text-xs shadow-md">
		<div class="flex items-center gap-2">
			<span class="w-3.5 h-3.5 rounded-full shadow border border-white/30" style="background-color: {teamColor};"></span>
			<span class="font-black text-white text-sm">{teamName}</span>
			<span class="text-slate-400">({players.length} jugador{players.length !== 1 ? 'es' : ''})</span>
		</div>
		<div class="flex items-center gap-1.5 font-mono text-[11px] flex-wrap justify-end">
			<span class="px-2 py-0.5 rounded font-bold bg-amber-500/15 text-amber-300 border border-amber-500/30">
				🎯 {pointGuards.length} BAS
			</span>
			<span class="px-2 py-0.5 rounded font-bold bg-blue-500/15 text-blue-300 border border-blue-500/30">
				⚡ {shootingGuards.length} ESC
			</span>
			<span class="px-2 py-0.5 rounded font-bold bg-emerald-500/15 text-emerald-300 border border-emerald-500/30">
				🏃 {smallForwards.length} ALE
			</span>
			<span class="px-2 py-0.5 rounded font-bold bg-purple-500/15 text-purple-300 border border-purple-500/30">
				💪 {powerForwards.length} A-P
			</span>
			<span class="px-2 py-0.5 rounded font-bold bg-orange-500/15 text-orange-300 border border-orange-500/30">
				🏀 {centers.length} PIV
			</span>
		</div>
	</div>

	<!-- ── PISTA DE BÁSQUETBOL (DUELA DE MADERA PROFESIONAL) ───────────────── -->
	<div
		class="relative w-full rounded-2xl overflow-hidden shadow-2xl border-4 border-amber-900/80 flex flex-col justify-between"
		style="
			background: repeating-linear-gradient(
				90deg,
				#a25a22 0px,
				#a25a22 18px,
				#b86a2e 18px,
				#b86a2e 36px,
				#97501a 36px,
				#97501a 54px
			);
			min-height: 580px;
			height: 580px;
		"
	>
		<!-- Línea perimetral de la pista -->
		<div class="absolute inset-3.5 border-2 border-white/50 rounded-lg pointer-events-none"></div>

		<!-- Línea de medio campo y círculo central -->
		<div class="absolute top-1/2 left-3.5 right-3.5 h-0.5 bg-white/45 -translate-y-1/2 pointer-events-none"></div>
		<div class="absolute top-1/2 left-1/2 w-28 h-28 border-2 border-white/45 rounded-full -translate-x-1/2 -translate-y-1/2 pointer-events-none"></div>
		<div class="absolute top-1/2 left-1/2 w-2.5 h-2.5 bg-white/70 rounded-full -translate-x-1/2 -translate-y-1/2 pointer-events-none"></div>

		<!-- Canasta y Línea de 3 puntos Superior (Lado Rival) -->
		<div class="absolute top-3.5 left-1/2 -translate-x-1/2 w-32 h-24 border-b-2 border-x-2 border-white/40 pointer-events-none rounded-b-md bg-amber-950/20"></div>
		<div class="absolute top-3.5 left-1/2 -translate-x-1/2 w-12 h-3.5 bg-orange-600/60 border border-white/40 rounded-b pointer-events-none"></div>
		<div class="absolute top-27 left-1/2 -translate-x-1/2 w-20 h-10 border-b-2 border-white/35 rounded-b-full pointer-events-none"></div>

		<!-- Canasta y Línea de 3 puntos Inferior (Nuestra Zona / Aro) -->
		<div class="absolute bottom-3.5 left-1/2 -translate-x-1/2 w-32 h-24 border-t-2 border-x-2 border-white/40 pointer-events-none rounded-t-md bg-amber-950/20"></div>
		<div class="absolute bottom-3.5 left-1/2 -translate-x-1/2 w-12 h-3.5 bg-orange-600/60 border border-white/40 rounded-t pointer-events-none"></div>
		<div class="absolute bottom-27 left-1/2 -translate-x-1/2 w-20 h-10 border-t-2 border-white/35 rounded-t-full pointer-events-none"></div>

		<!-- ── ZONA 1: BASE / POINT GUARD (Armador ofensivo arriba) ────────────── -->
		<div class="relative z-10 flex-1 flex flex-col items-center justify-center pt-5 pb-1">
			<div class="flex items-center justify-center flex-wrap gap-4 sm:gap-6 w-full px-4">
				{#each pointGuards as p}
					<div class="flex flex-col items-center group transition-transform hover:scale-110">
						<div class="relative">
							<button
								type="button"
								class="w-12 h-12 rounded-full flex items-center justify-center text-sm font-black text-slate-900 shadow-2xl border-2 border-white/90 cursor-pointer bg-amber-400"
								onclick={() => onSelectPlayer?.(p)}
								title="{p.first_name} {p.last_name} (Base)"
							>
								{p.shirt_number ?? '1'}
							</button>
							{#if interactive && onRemovePlayer}
								<button
									type="button"
									onclick={() => onRemovePlayer(p)}
									title="Quitar de la pista"
									class="absolute -top-1.5 -right-1.5 w-5 h-5 bg-red-600 hover:bg-red-500 text-white rounded-full text-xs font-black flex items-center justify-center shadow-lg z-20 cursor-pointer"
								>
									✕
								</button>
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
						class="w-11 h-11 rounded-full border-2 border-dashed border-amber-300/80 bg-amber-500/20 hover:bg-amber-500/40 text-amber-200 flex flex-col items-center justify-center text-xs font-bold transition shadow cursor-pointer"
					>
						<span>+</span>
						<span class="text-[9px] font-mono leading-none">BAS</span>
					</button>
				{:else if pointGuards.length === 0}
					<span class="text-[11px] text-white/60 bg-black/40 px-3 py-1 rounded-full border border-white/10">Sin base asignado</span>
				{/if}
			</div>
		</div>

		<!-- ── ZONA 2: ESCOLTA / SHOOTING GUARD ───────────────────────────────── -->
		<div class="relative z-10 flex-1 flex flex-col items-center justify-center py-1">
			<div class="flex items-center justify-center flex-wrap gap-4 sm:gap-6 w-full px-4">
				{#each shootingGuards as p}
					<div class="flex flex-col items-center group transition-transform hover:scale-110">
						<div class="relative">
							<button
								type="button"
								class="w-12 h-12 rounded-full flex items-center justify-center text-sm font-black text-white shadow-2xl border-2 border-white/90 cursor-pointer bg-blue-500"
								onclick={() => onSelectPlayer?.(p)}
								title="{p.first_name} {p.last_name} (Escolta)"
							>
								{p.shirt_number ?? '2'}
							</button>
							{#if interactive && onRemovePlayer}
								<button
									type="button"
									onclick={() => onRemovePlayer(p)}
									title="Quitar de la pista"
									class="absolute -top-1.5 -right-1.5 w-5 h-5 bg-red-600 hover:bg-red-500 text-white rounded-full text-xs font-black flex items-center justify-center shadow-lg z-20 cursor-pointer"
								>
									✕
								</button>
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

		<!-- ── ZONA 3: ALERO / SMALL FORWARD (Medio campo) ────────────────────── -->
		<div class="relative z-10 flex-1 flex flex-col items-center justify-center py-1">
			<div class="flex items-center justify-center flex-wrap gap-4 sm:gap-6 w-full px-4">
				{#each smallForwards as p}
					<div class="flex flex-col items-center group transition-transform hover:scale-110">
						<div class="relative">
							<button
								type="button"
								class="w-12 h-12 rounded-full flex items-center justify-center text-sm font-black text-white shadow-2xl border-2 border-white/90 cursor-pointer bg-emerald-600"
								onclick={() => onSelectPlayer?.(p)}
								title="{p.first_name} {p.last_name} (Alero)"
							>
								{p.shirt_number ?? '3'}
							</button>
							{#if interactive && onRemovePlayer}
								<button
									type="button"
									onclick={() => onRemovePlayer(p)}
									title="Quitar de la pista"
									class="absolute -top-1.5 -right-1.5 w-5 h-5 bg-red-600 hover:bg-red-500 text-white rounded-full text-xs font-black flex items-center justify-center shadow-lg z-20 cursor-pointer"
								>
									✕
								</button>
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

		<!-- ── ZONA 4: ALA-PÍVOT / POWER FORWARD ───────────────────────────────── -->
		<div class="relative z-10 flex-1 flex flex-col items-center justify-center py-1">
			<div class="flex items-center justify-center flex-wrap gap-4 sm:gap-6 w-full px-4">
				{#each powerForwards as p}
					<div class="flex flex-col items-center group transition-transform hover:scale-110">
						<div class="relative">
							<button
								type="button"
								class="w-12 h-12 rounded-full flex items-center justify-center text-sm font-black text-white shadow-2xl border-2 border-white/90 cursor-pointer bg-purple-600"
								onclick={() => onSelectPlayer?.(p)}
								title="{p.first_name} {p.last_name} (Ala-Pívot)"
							>
								{p.shirt_number ?? '4'}
							</button>
							{#if interactive && onRemovePlayer}
								<button
									type="button"
									onclick={() => onRemovePlayer(p)}
									title="Quitar de la pista"
									class="absolute -top-1.5 -right-1.5 w-5 h-5 bg-red-600 hover:bg-red-500 text-white rounded-full text-xs font-black flex items-center justify-center shadow-lg z-20 cursor-pointer"
								>
									✕
								</button>
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

		<!-- ── ZONA 5: PÍVOT / CENTER (Zona baja de la canasta) ────────────────── -->
		<div class="relative z-10 flex-1 flex flex-col items-center justify-center pb-4 pt-1">
			<div class="flex items-center justify-center flex-wrap gap-4 sm:gap-6 w-full px-4">
				{#each centers as p}
					<div class="flex flex-col items-center group transition-transform hover:scale-110">
						<div class="relative">
							<button
								type="button"
								class="w-12 h-12 rounded-full flex items-center justify-center text-sm font-black text-white shadow-2xl border-2 border-white/90 cursor-pointer bg-orange-600"
								onclick={() => onSelectPlayer?.(p)}
								title="{p.first_name} {p.last_name} (Pívot)"
							>
								{p.shirt_number ?? '5'}
							</button>
							{#if interactive && onRemovePlayer}
								<button
									type="button"
									onclick={() => onRemovePlayer(p)}
									title="Quitar de la pista"
									class="absolute -top-1.5 -right-1.5 w-5 h-5 bg-red-600 hover:bg-red-500 text-white rounded-full text-xs font-black flex items-center justify-center shadow-lg z-20 cursor-pointer"
								>
									✕
								</button>
							{/if}
						</div>
						<span class="mt-1 px-2 py-0.5 rounded-md text-[11px] font-bold text-orange-300 bg-slate-950/90 border border-orange-400/30 truncate max-w-[90px] text-center shadow">
							{getShortDisplayName(p)}
						</span>
					</div>
				{/each}

				{#if interactive && onAddPlayer}
					<button
						type="button"
						onclick={() => onAddPlayer('center')}
						title="Agregar Pívot"
						class="w-11 h-11 rounded-full border-2 border-dashed border-orange-300/80 bg-orange-500/20 hover:bg-orange-500/40 text-orange-200 flex flex-col items-center justify-center text-xs font-bold transition shadow cursor-pointer"
					>
						<span>+</span>
						<span class="text-[9px] font-mono leading-none">PIV</span>
					</button>
				{:else if centers.length === 0}
					<span class="text-[11px] text-white/60 bg-black/40 px-3 py-1 rounded-full border border-white/10">Sin pívot asignado</span>
				{/if}
			</div>
		</div>
	</div>

	<!-- ── BANCA / SUPLENTES DE BÁSQUETBOL ─────────────────────────────────── -->
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
							>
								✕
							</button>
						{/if}
					</div>
				{/each}
			</div>
		</div>
	{/if}
</div>
