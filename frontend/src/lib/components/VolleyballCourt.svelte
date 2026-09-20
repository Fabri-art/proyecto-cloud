<script>
	/**
	 * VolleyballCourt.svelte
	 * Representación visual táctica de una cancha reglamentaria de Vóley (6 vs 6).
	 * - Mitad Superior: Campo Rival / Zona Opuesta (claramente identificada).
	 * - Centro: Red de vóley de alta visibilidad con postes y antenas.
	 * - Mitad Inferior: Nuestro Campo con las 6 posiciones (3 de ataque y 3 de defensa).
	 */

	let {
		players = [],
		interactive = false,
		teamName = 'Equipo de Vóley',
		teamColor = '#8b5cf6',
		onAddPlayer = null,
		onRemovePlayer = null,
		onSelectPlayer = null
	} = $props();

	let courtPlayers = $derived(players.filter((p) => p.is_starter !== false));
	let benchPlayers = $derived(players.filter((p) => p.is_starter === false));

	let setters = $derived(courtPlayers.filter((p) => p.position === 'setter'));
	let outsideHitters = $derived(courtPlayers.filter((p) => p.position === 'outside_hitter'));
	let middleBlockers = $derived(courtPlayers.filter((p) => p.position === 'middle_blocker'));
	let opposites = $derived(courtPlayers.filter((p) => p.position === 'opposite'));
	let liberos = $derived(courtPlayers.filter((p) => p.position === 'libero'));

	function getShortDisplayName(p) {
		if (p.first_name) {
			return `${p.first_name.slice(0, 1)}. ${p.last_name || ''}`.trim();
		}
		return p.last_name || `Jugador #${p.shirt_number ?? '?'}`;
	}
</script>

<div class="flex flex-col gap-3 w-full">
	<!-- ══ CANCHA DE VÓLEY ══════════════════════════════════════════════════════ -->
	<div
		class="volleyball-court tactical-court-scope relative w-full max-w-xl mx-auto rounded-2xl overflow-hidden border-2 border-violet-500/60 shadow-2xl flex flex-col"
		style="min-height: 480px; background: linear-gradient(180deg, #160d33 0%, #201248 45%, #2a155c 60%, #170b3b 100%);"
	>
		<!-- SVG con líneas reglamentarias de cancha -->
		<svg class="absolute inset-0 w-full h-full pointer-events-none" xmlns="http://www.w3.org/2000/svg">
			<!-- Perímetro general de juego -->
			<rect x="4%" y="3%" width="92%" height="94%" fill="none" stroke="rgba(255,255,255,0.3)" stroke-width="2" rx="6" />

			<!-- Línea de 3m del rival (arriba) -->
			<line x1="4%" y1="18%" x2="96%" y2="18%" stroke="rgba(255,255,255,0.18)" stroke-width="1.5" stroke-dasharray="6,4" />

			<!-- Línea de 3m de nuestro campo (abajo) -->
			<line x1="4%" y1="64%" x2="96%" y2="64%" stroke="rgba(255,255,255,0.25)" stroke-width="1.5" stroke-dasharray="6,4" />

			<!-- Líneas verticales de separación de carril -->
			<line x1="36%" y1="38%" x2="36%" y2="97%" stroke="rgba(255,255,255,0.08)" stroke-width="1" />
			<line x1="64%" y1="38%" x2="64%" y2="97%" stroke="rgba(255,255,255,0.08)" stroke-width="1" />
		</svg>
		<!-- Standardized Header de la Cancha de Vóley -->
		<div class="court-header-bar relative z-20 flex items-center justify-between px-4 py-2.5 sm:px-5 sm:py-3 border-b border-violet-500/40 bg-black/75 backdrop-blur-md">
			<div class="flex items-center gap-2.5 min-w-0">
				<span class="text-2xl shrink-0">🏐</span>
				<div class="min-w-0">
					<h4 class="text-xs sm:text-sm font-black text-white uppercase tracking-wider leading-none truncate" style="color: #ffffff !important;">
						Cancha Oficial — Voleibol Táctico
					</h4>
					<span class="text-[10px] text-violet-300 font-mono block truncate mt-0.5" style="color: #c4b5fd !important;">
						6 Posiciones Reglamentarias · Rotación Activa
					</span>
				</div>
			</div>
			<div class="px-2.5 py-1 rounded-full text-[11px] font-bold bg-violet-950/90 text-violet-300 border border-violet-500/50 shrink-0 ml-2 truncate max-w-[130px]" style="color: #c4b5fd !important;">
				{teamName}
			</div>
		</div>


		<!-- ══ PARTE SUPERIOR: ZONA OPUESTA (CAMPO RIVAL) ═══════════════════════ -->
		<div class="relative z-10 w-full flex flex-col items-center justify-center py-6 px-4" style="height: 33%; background: rgba(0, 0, 0, 0.28);">
			<div class="px-4 py-1.5 rounded-full bg-slate-950/90 border border-red-500/30 shadow-lg flex items-center gap-2">
				<span class="text-sm">🛡️</span>
				<span class="text-[11px] font-black tracking-wider text-red-300 uppercase">Zona Opuesta (Campo Rival)</span>
			</div>
			<p class="text-[10px] text-slate-400 mt-1 font-mono tracking-wide">Área del equipo oponente al otro lado de la red</p>
		</div>

		<!-- ══ CENTRO: LA RED (SÚPER VISIBLE Y DESTACADA) ═════════════════════════ -->
		<div
			class="relative z-20 w-full flex items-center justify-between px-3 py-1.5 border-y-2 border-white shadow-xl"
			style="background: repeating-linear-gradient(45deg, rgba(255,255,255,0.18) 0, rgba(255,255,255,0.18) 3px, transparent 3px, transparent 8px), #0e0926;"
		>
			<!-- Antena izquierda -->
			<div class="w-2.5 h-6 bg-red-500 border border-white rounded-sm shadow shrink-0" title="Antena de Red"></div>

			<!-- Texto central de la red -->
			<div class="flex items-center gap-2">
				<div class="h-0.5 w-8 sm:w-16 bg-white/70"></div>
				<span class="px-3 py-0.5 rounded-full bg-slate-950 border border-white text-white text-[11px] font-black tracking-widest uppercase shadow-md flex items-center gap-1.5">
					<span>🏐</span> RED DE VÓLEY <span>🏐</span>
				</span>
				<div class="h-0.5 w-8 sm:w-16 bg-white/70"></div>
			</div>

			<!-- Antena derecha -->
			<div class="w-2.5 h-6 bg-red-500 border border-white rounded-sm shadow shrink-0" title="Antena de Red"></div>
		</div>

		<!-- ══ PARTE INFERIOR: NUESTRO CAMPO (ZONA DE NUESTRO EQUIPO) ═════════════ -->
		<div class="relative z-10 flex-1 flex flex-col justify-between p-3" style="background: rgba(30, 16, 68, 0.4);">

			<!-- ── FILA 1: ZONA DELANTERA (ATAQUE - JUNTO A LA RED) ───────────── -->
			<div class="flex flex-col gap-1">
				<div class="flex items-center justify-center gap-1.5 mb-1">
					<span class="text-[9px] font-black text-violet-300 uppercase tracking-widest bg-violet-950/80 px-2.5 py-0.5 rounded-full border border-violet-500/30">
						Zona Delantera (Ataque)
					</span>
				</div>

				<div class="grid grid-cols-3 gap-2 px-1 text-center">
					<!-- Opuesto (Zona 4) -->
					<div class="flex flex-col items-center gap-1">
						<span class="text-[9px] font-bold text-fuchsia-300 uppercase tracking-wider">Opuesto</span>
						{#each opposites as p}
							<div class="flex flex-col items-center group transition-transform hover:scale-110">
								<div class="relative">
									<button
										type="button"
										class="w-11 h-11 rounded-full flex items-center justify-center text-xs font-black text-white shadow-xl border-2 border-white/90 cursor-pointer bg-fuchsia-700"
										onclick={() => onSelectPlayer?.(p)}
										title="{p.first_name} {p.last_name} (Opuesto)"
									>
										{p.shirt_number ?? '4'}
									</button>
									{#if interactive && onRemovePlayer}
										<button
											type="button"
											onclick={() => onRemovePlayer(p)}
											title="Quitar"
											class="absolute -top-1.5 -right-1.5 w-4 h-4 bg-red-600 hover:bg-red-500 text-white rounded-full text-[10px] font-black flex items-center justify-center shadow z-20 cursor-pointer"
										>✕</button>
									{/if}
								</div>
								<span class="court-player-badge mt-0.5 px-2 py-0.5 rounded text-[10px] font-bold text-white truncate max-w-[95px] shadow block" style="color: #ffffff !important;">
									{getShortDisplayName(p)}
								</span>
							</div>
						{/each}
						{#if interactive && onAddPlayer}
							<button
								type="button"
								onclick={() => onAddPlayer('opposite')}
								title="Agregar Opuesto"
								class="w-10 h-10 rounded-full border-2 border-dashed border-fuchsia-300/80 bg-fuchsia-500/20 hover:bg-fuchsia-500/40 text-fuchsia-200 flex flex-col items-center justify-center text-[11px] font-bold transition shadow cursor-pointer"
							>
								<span>+</span>
								<span class="text-[8px] font-mono leading-none">OPU</span>
							</button>
						{:else if opposites.length === 0}
							<span class="text-[9px] text-white/50 bg-black/40 px-2 py-0.5 rounded-full border border-white/10">Sin opuesto</span>
						{/if}
					</div>

					<!-- Central Delantero (Zona 3) -->
					<div class="flex flex-col items-center gap-1">
						<span class="text-[9px] font-bold text-purple-300 uppercase tracking-wider">Central</span>
						{#each middleBlockers as p}
							<div class="flex flex-col items-center group transition-transform hover:scale-110">
								<div class="relative">
									<button
										type="button"
										class="w-11 h-11 rounded-full flex items-center justify-center text-xs font-black text-white shadow-xl border-2 border-white/90 cursor-pointer bg-purple-700"
										onclick={() => onSelectPlayer?.(p)}
										title="{p.first_name} {p.last_name} (Central)"
									>
										{p.shirt_number ?? '3'}
									</button>
									{#if interactive && onRemovePlayer}
										<button
											type="button"
											onclick={() => onRemovePlayer(p)}
											title="Quitar"
											class="absolute -top-1.5 -right-1.5 w-4 h-4 bg-red-600 hover:bg-red-500 text-white rounded-full text-[10px] font-black flex items-center justify-center shadow z-20 cursor-pointer"
										>✕</button>
									{/if}
								</div>
								<span class="court-player-badge mt-0.5 px-2 py-0.5 rounded text-[10px] font-bold text-white truncate max-w-[95px] shadow block" style="color: #ffffff !important;">
									{getShortDisplayName(p)}
								</span>
							</div>
						{/each}
						{#if interactive && onAddPlayer}
							<button
								type="button"
								onclick={() => onAddPlayer('middle_blocker')}
								title="Agregar Central"
								class="w-10 h-10 rounded-full border-2 border-dashed border-purple-300/80 bg-purple-500/20 hover:bg-purple-500/40 text-purple-200 flex flex-col items-center justify-center text-[11px] font-bold transition shadow cursor-pointer"
							>
								<span>+</span>
								<span class="text-[8px] font-mono leading-none">CEN</span>
							</button>
						{:else if middleBlockers.length === 0}
							<span class="text-[9px] text-white/50 bg-black/40 px-2 py-0.5 rounded-full border border-white/10">Sin central</span>
						{/if}
					</div>

					<!-- Punta Delantero (Zona 2) -->
					<div class="flex flex-col items-center gap-1">
						<span class="text-[9px] font-bold text-blue-300 uppercase tracking-wider">Punta Del.</span>
						{#each outsideHitters.slice(0, 1) as p}
							<div class="flex flex-col items-center group transition-transform hover:scale-110">
								<div class="relative">
									<button
										type="button"
										class="w-11 h-11 rounded-full flex items-center justify-center text-xs font-black text-white shadow-xl border-2 border-white/90 cursor-pointer bg-blue-700"
										onclick={() => onSelectPlayer?.(p)}
										title="{p.first_name} {p.last_name} (Punta Delantero)"
									>
										{p.shirt_number ?? '2'}
									</button>
									{#if interactive && onRemovePlayer}
										<button
											type="button"
											onclick={() => onRemovePlayer(p)}
											title="Quitar"
											class="absolute -top-1.5 -right-1.5 w-4 h-4 bg-red-600 hover:bg-red-500 text-white rounded-full text-[10px] font-black flex items-center justify-center shadow z-20 cursor-pointer"
										>✕</button>
									{/if}
								</div>
								<span class="court-player-badge mt-0.5 px-2 py-0.5 rounded text-[10px] font-bold text-white truncate max-w-[95px] shadow block" style="color: #ffffff !important;">
									{getShortDisplayName(p)}
								</span>
							</div>
						{/each}
						{#if interactive && onAddPlayer && outsideHitters.length === 0}
							<button
								type="button"
								onclick={() => onAddPlayer('outside_hitter')}
								title="Agregar Punta Delantero"
								class="w-10 h-10 rounded-full border-2 border-dashed border-blue-300/80 bg-blue-500/20 hover:bg-blue-500/40 text-blue-200 flex flex-col items-center justify-center text-[11px] font-bold transition shadow cursor-pointer"
							>
								<span>+</span>
								<span class="text-[8px] font-mono leading-none">PUN</span>
							</button>
						{:else if outsideHitters.length === 0}
							<span class="text-[9px] text-white/50 bg-black/40 px-2 py-0.5 rounded-full border border-white/10">Sin punta</span>
						{/if}
					</div>
				</div>
			</div>

			<!-- ── FILA 2: ZONA TRASERA (DEFENSA / RECEPCIÓN) ──────────────────── -->
			<div class="flex flex-col gap-1 pt-2 border-t border-dashed border-white/20">
				<div class="flex items-center justify-center gap-1.5 mb-1">
					<span class="text-[9px] font-black text-amber-300 uppercase tracking-widest bg-amber-950/80 px-2.5 py-0.5 rounded-full border border-amber-500/30">
						Zona Trasera (Defensa / Saque)
					</span>
				</div>

				<div class="grid grid-cols-3 gap-2 px-1 text-center">
					<!-- Armador (Zona 5) -->
					<div class="flex flex-col items-center gap-1">
						<span class="text-[9px] font-bold text-cyan-300 uppercase tracking-wider">Armador</span>
						{#each setters as p}
							<div class="flex flex-col items-center group transition-transform hover:scale-110">
								<div class="relative">
									<button
										type="button"
										class="w-11 h-11 rounded-full flex items-center justify-center text-xs font-black text-white shadow-xl border-2 border-white/90 cursor-pointer bg-cyan-700"
										onclick={() => onSelectPlayer?.(p)}
										title="{p.first_name} {p.last_name} (Armador)"
									>
										{p.shirt_number ?? '1'}
									</button>
									{#if interactive && onRemovePlayer}
										<button
											type="button"
											onclick={() => onRemovePlayer(p)}
											title="Quitar"
											class="absolute -top-1.5 -right-1.5 w-4 h-4 bg-red-600 hover:bg-red-500 text-white rounded-full text-[10px] font-black flex items-center justify-center shadow z-20 cursor-pointer"
										>✕</button>
									{/if}
								</div>
								<span class="court-player-badge mt-0.5 px-2 py-0.5 rounded text-[10px] font-bold text-white truncate max-w-[95px] shadow block" style="color: #ffffff !important;">
									{getShortDisplayName(p)}
								</span>
							</div>
						{/each}
						{#if interactive && onAddPlayer}
							<button
								type="button"
								onclick={() => onAddPlayer('setter')}
								title="Agregar Armador"
								class="w-10 h-10 rounded-full border-2 border-dashed border-cyan-300/80 bg-cyan-500/20 hover:bg-cyan-500/40 text-cyan-200 flex flex-col items-center justify-center text-[11px] font-bold transition shadow cursor-pointer"
							>
								<span>+</span>
								<span class="text-[8px] font-mono leading-none">ARM</span>
							</button>
						{:else if setters.length === 0}
							<span class="text-[9px] text-white/50 bg-black/40 px-2 py-0.5 rounded-full border border-white/10">Sin armador</span>
						{/if}
					</div>

					<!-- Líbero (Zona 6) -->
					<div class="flex flex-col items-center gap-1">
						<span class="text-[9px] font-bold text-yellow-300 uppercase tracking-wider">Líbero</span>
						{#each liberos as p}
							<div class="flex flex-col items-center group transition-transform hover:scale-110">
								<div class="relative">
									<button
										type="button"
										class="w-11 h-11 rounded-full flex items-center justify-center text-xs font-black text-white shadow-xl border-2 border-yellow-300 cursor-pointer bg-yellow-600"
										onclick={() => onSelectPlayer?.(p)}
										title="{p.first_name} {p.last_name} (Líbero)"
									>
										{p.shirt_number ?? 'L'}
									</button>
									{#if interactive && onRemovePlayer}
										<button
											type="button"
											onclick={() => onRemovePlayer(p)}
											title="Quitar"
											class="absolute -top-1.5 -right-1.5 w-4 h-4 bg-red-600 hover:bg-red-500 text-white rounded-full text-[10px] font-black flex items-center justify-center shadow z-20 cursor-pointer"
										>✕</button>
									{/if}
								</div>
								<span class="court-player-badge mt-0.5 px-2 py-0.5 rounded text-[10px] font-bold text-white truncate max-w-[95px] shadow block" style="color: #ffffff !important;">
									{getShortDisplayName(p)}
								</span>
							</div>
						{/each}
						{#if interactive && onAddPlayer}
							<button
								type="button"
								onclick={() => onAddPlayer('libero')}
								title="Agregar Líbero"
								class="w-10 h-10 rounded-full border-2 border-dashed border-yellow-300/80 bg-yellow-500/20 hover:bg-yellow-500/40 text-yellow-200 flex flex-col items-center justify-center text-[11px] font-bold transition shadow cursor-pointer"
							>
								<span>+</span>
								<span class="text-[8px] font-mono leading-none">LIB</span>
							</button>
						{:else if liberos.length === 0}
							<span class="text-[9px] text-white/50 bg-black/40 px-2 py-0.5 rounded-full border border-white/10">Sin líbero</span>
						{/if}
					</div>

					<!-- Punta Trasero (Zona 1) -->
					<div class="flex flex-col items-center gap-1">
						<span class="text-[9px] font-bold text-indigo-300 uppercase tracking-wider">Punta Tras.</span>
						{#each outsideHitters.slice(1, 2) as p}
							<div class="flex flex-col items-center group transition-transform hover:scale-110">
								<div class="relative">
									<button
										type="button"
										class="w-11 h-11 rounded-full flex items-center justify-center text-xs font-black text-white shadow-xl border-2 border-white/90 cursor-pointer bg-indigo-700"
										onclick={() => onSelectPlayer?.(p)}
										title="{p.first_name} {p.last_name} (Punta Trasero)"
									>
										{p.shirt_number ?? '5'}
									</button>
									{#if interactive && onRemovePlayer}
										<button
											type="button"
											onclick={() => onRemovePlayer(p)}
											title="Quitar"
											class="absolute -top-1.5 -right-1.5 w-4 h-4 bg-red-600 hover:bg-red-500 text-white rounded-full text-[10px] font-black flex items-center justify-center shadow z-20 cursor-pointer"
										>✕</button>
									{/if}
								</div>
								<span class="court-player-badge mt-0.5 px-2 py-0.5 rounded text-[10px] font-bold text-white truncate max-w-[95px] shadow block" style="color: #ffffff !important;">
									{getShortDisplayName(p)}
								</span>
							</div>
						{/each}
						{#if interactive && onAddPlayer && outsideHitters.length <= 1}
							<button
								type="button"
								onclick={() => onAddPlayer('outside_hitter')}
								title="Agregar Punta Trasero"
								class="w-10 h-10 rounded-full border-2 border-dashed border-indigo-300/80 bg-indigo-500/20 hover:bg-indigo-500/40 text-indigo-200 flex flex-col items-center justify-center text-[11px] font-bold transition shadow cursor-pointer"
							>
								<span>+</span>
								<span class="text-[8px] font-mono leading-none">PUN</span>
							</button>
						{:else if outsideHitters.length <= 1}
							<span class="text-[9px] text-white/50 bg-black/40 px-2 py-0.5 rounded-full border border-white/10">—</span>
						{/if}
					</div>
				</div>
			</div>

		</div>
	</div>

	<!-- ══ BANCA / SUPLENTES ════════════════════════════════════════ -->
	{#if benchPlayers.length > 0}
		<div class="p-3 rounded-xl bg-slate-900/70 border border-slate-800">
			<span class="text-xs font-bold text-slate-400 flex items-center gap-1.5 mb-2">
				🏐 Reserva / Suplentes ({benchPlayers.length})
			</span>
			<div class="flex items-center gap-2 overflow-x-auto pb-1">
				{#each benchPlayers as p}
					<div class="flex items-center gap-1.5 px-2.5 py-1 rounded-lg bg-slate-800/80 border border-slate-700 text-xs shrink-0">
						<span class="font-mono font-black text-violet-400">#{p.shirt_number ?? '?'}</span>
						<span class="text-white font-medium" style="color: #ffffff !important;">{getShortDisplayName(p)}</span>
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
