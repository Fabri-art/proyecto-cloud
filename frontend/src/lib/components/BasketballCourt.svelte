<script>
	/**
	 * BasketballCourt.svelte
	 * Representación visual táctica de una pista de básquetbol (5 vs 5).
	 * - Mitad Superior: Zona Rival / Aro Opuesto (claramente identificada).
	 * - Centro: Línea de medio campo destacada.
	 * - Mitad Inferior: Nuestro Campo con las 5 posiciones (Base, Escolta, Alero, Ala-Pívot, Pívot).
	 */

	let {
		players = [],
		interactive = false,
		teamName = 'Equipo de Básquet',
		teamColor = '#ea580c',
		onAddPlayer = null,
		onRemovePlayer = null,
		onSelectPlayer = null
	} = $props();

	let courtPlayers = $derived(players.filter((p) => p.is_starter !== false));
	let benchPlayers = $derived(players.filter((p) => p.is_starter === false));

	let pointGuards = $derived(courtPlayers.filter((p) => p.position === 'point_guard'));
	let shootingGuards = $derived(courtPlayers.filter((p) => p.position === 'shooting_guard'));
	let smallForwards = $derived(courtPlayers.filter((p) => p.position === 'small_forward'));
	let powerForwards = $derived(courtPlayers.filter((p) => p.position === 'power_forward'));
	let centers = $derived(courtPlayers.filter((p) => p.position === 'center'));

	function getShortDisplayName(p) {
		if (p.first_name) {
			return `${p.first_name.slice(0, 1)}. ${p.last_name || ''}`.trim();
		}
		return p.last_name || `Jugador #${p.shirt_number ?? '?'}`;
	}
</script>

<div class="flex flex-col gap-3 w-full">
	<!-- ══ PISTA DE BÁSQUETBOL ══════════════════════════════════════════════════ -->
	<div
		class="basketball-court tactical-court-scope relative w-full max-w-xl mx-auto rounded-2xl overflow-hidden border-2 border-amber-600/70 shadow-2xl flex flex-col"
		style="min-height: 480px; background: linear-gradient(180deg, #9a3412 0%, #7c2d12 40%, #c2410c 55%, #7c2d12 100%);"
	>
		<!-- Textura de duela de madera (SVG overlay) -->
		<svg class="absolute inset-0 w-full h-full pointer-events-none" xmlns="http://www.w3.org/2000/svg">
			<defs>
				<pattern id="hardwood" width="12" height="100%" patternUnits="userSpaceOnUse">
					<rect width="11" height="100%" fill="rgba(0,0,0,0.06)" />
					<line x1="12" y1="0" x2="12" y2="100%" stroke="rgba(255,255,255,0.05)" stroke-width="1" />
				</pattern>
			</defs>
			<rect width="100%" height="100%" fill="url(#hardwood)" />

			<!-- Líneas reglamentarias de la pista -->
			<!-- Perímetro -->
			<rect x="4%" y="3%" width="92%" height="94%" fill="none" stroke="rgba(255,255,255,0.45)" stroke-width="2" rx="6" />

			<!-- Aro rival (arriba) -->
			<rect x="36%" y="3%" width="28%" height="18%" fill="rgba(0,0,0,0.18)" stroke="rgba(255,255,255,0.35)" stroke-width="1.5" />
			<circle cx="50%" cy="15%" r="4.5%" fill="none" stroke="rgba(255,255,255,0.35)" stroke-width="1.5" />
			<path d="M 18% 3% A 38% 34% 0 0 0 82% 3%" fill="none" stroke="rgba(255,255,255,0.25)" stroke-width="1.5" />
			<line x1="45%" y1="4%" x2="55%" y2="4%" stroke="#f97316" stroke-width="3" />
			<circle cx="50%" cy="6%" r="2%" fill="none" stroke="#ea580c" stroke-width="2" />

			<!-- Medio campo -->
			<line x1="4%" y1="38%" x2="96%" y2="38%" stroke="rgba(255,255,255,0.6)" stroke-width="2" />
			<circle cx="50%" cy="38%" r="8%" fill="rgba(0,0,0,0.12)" stroke="rgba(255,255,255,0.5)" stroke-width="2" />

			<!-- Nuestro aro (abajo) -->
			<!-- Arco de 3 puntos de nuestro campo -->
			<path d="M 16% 97% A 42% 38% 0 0 1 84% 97%" fill="none" stroke="rgba(255,255,255,0.4)" stroke-width="2" />
			<!-- Zona pintada / Llave de nuestro campo -->
			<rect x="34%" y="75%" width="32%" height="22%" fill="rgba(0,0,0,0.2)" stroke="rgba(255,255,255,0.45)" stroke-width="1.5" />
			<!-- Círculo de tiro libre de nuestro campo -->
			<circle cx="50%" cy="75%" r="8%" fill="none" stroke="rgba(255,255,255,0.45)" stroke-width="1.5" />
			<!-- Tablero y Canasta de nuestro campo -->
			<line x1="44%" y1="95%" x2="56%" y2="95%" stroke="#f97316" stroke-width="3.5" />
			<circle cx="50%" cy="93%" r="2.2%" fill="none" stroke="#ea580c" stroke-width="2.5" />
		</svg>
		<!-- Standardized Header de la Pista de Básquetbol -->
		<div class="court-header-bar relative z-20 flex items-center justify-between px-4 py-2.5 sm:px-5 sm:py-3 border-b border-amber-500/40 bg-black/75 backdrop-blur-md">
			<div class="flex items-center gap-2.5 min-w-0">
				<span class="text-2xl shrink-0">🏀</span>
				<div class="min-w-0">
					<h4 class="text-xs sm:text-sm font-black text-white uppercase tracking-wider leading-none truncate" style="color: #ffffff !important;">
						Pista Oficial — Baloncesto Táctico
					</h4>
					<span class="text-[10px] text-amber-300 font-mono block truncate mt-0.5" style="color: #fcd34d !important;">
						5 Posiciones en Duela · Quinteto Titular
					</span>
				</div>
			</div>
			<div class="px-2.5 py-1 rounded-full text-[11px] font-bold bg-amber-950/90 text-amber-300 border border-amber-500/50 shrink-0 ml-2 truncate max-w-[130px]" style="color: #fcd34d !important;">
				{teamName}
			</div>
		</div>


		<!-- ══ PARTE SUPERIOR: ZONA OPUESTA (CAMPO RIVAL / ARO OPUESTO) ═════════ -->
		<div class="relative z-10 w-full flex flex-col items-center justify-center py-7 px-4" style="height: 36%; background: rgba(0, 0, 0, 0.32);">
			<div class="px-4 py-1.5 rounded-full bg-slate-950/90 border border-amber-500/40 shadow-lg flex items-center gap-2">
				<span class="text-sm">🎯</span>
				<span class="text-[11px] font-black tracking-wider text-amber-300 uppercase">Zona Rival (Aro Opuesto)</span>
			</div>
			<p class="text-[10px] text-amber-200/70 mt-1 font-mono tracking-wide">Canasta y área del equipo contrario</p>
		</div>

		<!-- ══ CENTRO: LÍNEA DE MEDIO CAMPO ═════════════════════════════════════ -->
		<div class="relative z-20 w-full flex items-center justify-between px-3 py-1 bg-amber-950/90 border-y border-white/40 shadow">
			<div class="h-0.5 flex-1 bg-white/40"></div>
			<span class="px-3 py-0.5 rounded-full bg-slate-950 border border-amber-500/40 text-amber-300 text-[10px] font-black tracking-widest uppercase shadow flex items-center gap-1.5">
				<span>🏀</span> MEDIO CAMPO <span>🏀</span>
			</span>
			<div class="h-0.5 flex-1 bg-white/40"></div>
		</div>

		<!-- ══ PARTE INFERIOR: NUESTRO CAMPO (ZONA DE NUESTRO EQUIPO) ═════════════ -->
		<div class="relative z-10 flex-1 flex flex-col justify-between p-3" style="background: rgba(30, 10, 0, 0.25);">

			<!-- ── LÍNEA EXTERIOR: PERÍMETRO (BASE, ESCOLTA, ALERO) ───────────── -->
			<div class="flex flex-col gap-1">
				<div class="flex items-center justify-center gap-1.5 mb-1">
					<span class="text-[9px] font-black text-amber-300 uppercase tracking-widest bg-amber-950/80 px-2.5 py-0.5 rounded-full border border-amber-500/30">
						Perímetro Exterior (Línea de 3 Puntos)
					</span>
				</div>

				<div class="grid grid-cols-3 gap-2 px-1 text-center">
					<!-- Escolta (SG) - Ala Izquierda -->
					<div class="flex flex-col items-center gap-1">
						<span class="text-[9px] font-bold text-blue-300 uppercase tracking-wider">Escolta</span>
						{#each shootingGuards as p}
							<div class="flex flex-col items-center group transition-transform hover:scale-110">
								<div class="relative">
									<button
										type="button"
										class="w-11 h-11 rounded-full flex items-center justify-center text-xs font-black text-white shadow-xl border-2 border-white/90 cursor-pointer bg-blue-700"
										onclick={() => onSelectPlayer?.(p)}
										title="{p.first_name} {p.last_name} (Escolta)"
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
						{#if interactive && onAddPlayer}
							<button
								type="button"
								onclick={() => onAddPlayer('shooting_guard')}
								title="Agregar Escolta"
								class="w-10 h-10 rounded-full border-2 border-dashed border-blue-300/80 bg-blue-500/20 hover:bg-blue-500/40 text-blue-200 flex flex-col items-center justify-center text-[11px] font-bold transition shadow cursor-pointer"
							>
								<span>+</span>
								<span class="text-[8px] font-mono leading-none">ESC</span>
							</button>
						{:else if shootingGuards.length === 0}
							<span class="text-[9px] text-white/50 bg-black/40 px-2 py-0.5 rounded-full border border-white/10">Sin escolta</span>
						{/if}
					</div>

					<!-- Base (PG) - Centro / Cabeza de la llave -->
					<div class="flex flex-col items-center gap-1">
						<span class="text-[9px] font-bold text-amber-300 uppercase tracking-wider">Base</span>
						{#each pointGuards as p}
							<div class="flex flex-col items-center group transition-transform hover:scale-110">
								<div class="relative">
									<button
										type="button"
										class="w-11 h-11 rounded-full flex items-center justify-center text-xs font-black text-white shadow-xl border-2 border-white/90 cursor-pointer bg-amber-600"
										onclick={() => onSelectPlayer?.(p)}
										title="{p.first_name} {p.last_name} (Base)"
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
								onclick={() => onAddPlayer('point_guard')}
								title="Agregar Base"
								class="w-10 h-10 rounded-full border-2 border-dashed border-amber-300/80 bg-amber-500/20 hover:bg-amber-500/40 text-amber-200 flex flex-col items-center justify-center text-[11px] font-bold transition shadow cursor-pointer"
							>
								<span>+</span>
								<span class="text-[8px] font-mono leading-none">BAS</span>
							</button>
						{:else if pointGuards.length === 0}
							<span class="text-[9px] text-white/50 bg-black/40 px-2 py-0.5 rounded-full border border-white/10">Sin base</span>
						{/if}
					</div>

					<!-- Alero (SF) - Ala Derecha -->
					<div class="flex flex-col items-center gap-1">
						<span class="text-[9px] font-bold text-emerald-300 uppercase tracking-wider">Alero</span>
						{#each smallForwards as p}
							<div class="flex flex-col items-center group transition-transform hover:scale-110">
								<div class="relative">
									<button
										type="button"
										class="w-11 h-11 rounded-full flex items-center justify-center text-xs font-black text-white shadow-xl border-2 border-white/90 cursor-pointer bg-emerald-700"
										onclick={() => onSelectPlayer?.(p)}
										title="{p.first_name} {p.last_name} (Alero)"
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
								onclick={() => onAddPlayer('small_forward')}
								title="Agregar Alero"
								class="w-10 h-10 rounded-full border-2 border-dashed border-emerald-300/80 bg-emerald-500/20 hover:bg-emerald-500/40 text-emerald-200 flex flex-col items-center justify-center text-[11px] font-bold transition shadow cursor-pointer"
							>
								<span>+</span>
								<span class="text-[8px] font-mono leading-none">ALE</span>
							</button>
						{:else if smallForwards.length === 0}
							<span class="text-[9px] text-white/50 bg-black/40 px-2 py-0.5 rounded-full border border-white/10">Sin alero</span>
						{/if}
					</div>
				</div>
			</div>

			<!-- ── LÍNEA INTERIOR: PINTURA / POSTE BAJO (ALA-PÍVOT, PÍVOT) ─────── -->
			<div class="flex flex-col gap-1 pt-2 border-t border-dashed border-white/20">
				<div class="flex items-center justify-center gap-1.5 mb-1">
					<span class="text-[9px] font-black text-orange-300 uppercase tracking-widest bg-orange-950/80 px-2.5 py-0.5 rounded-full border border-orange-500/30">
						Pintura y Poste Bajo (Protección de Canasta)
					</span>
				</div>

				<div class="grid grid-cols-2 gap-4 px-8 text-center">
					<!-- Ala-Pívot (PF) - Poste Izquierdo -->
					<div class="flex flex-col items-center gap-1">
						<span class="text-[9px] font-bold text-purple-300 uppercase tracking-wider">Ala-Pívot</span>
						{#each powerForwards as p}
							<div class="flex flex-col items-center group transition-transform hover:scale-110">
								<div class="relative">
									<button
										type="button"
										class="w-11 h-11 rounded-full flex items-center justify-center text-xs font-black text-white shadow-xl border-2 border-white/90 cursor-pointer bg-purple-700"
										onclick={() => onSelectPlayer?.(p)}
										title="{p.first_name} {p.last_name} (Ala-Pívot)"
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
								onclick={() => onAddPlayer('power_forward')}
								title="Agregar Ala-Pívot"
								class="w-10 h-10 rounded-full border-2 border-dashed border-purple-300/80 bg-purple-500/20 hover:bg-purple-500/40 text-purple-200 flex flex-col items-center justify-center text-[11px] font-bold transition shadow cursor-pointer"
							>
								<span>+</span>
								<span class="text-[8px] font-mono leading-none">A-P</span>
							</button>
						{:else if powerForwards.length === 0}
							<span class="text-[9px] text-white/50 bg-black/40 px-2 py-0.5 rounded-full border border-white/10">Sin ala-pívot</span>
						{/if}
					</div>

					<!-- Pívot (Center) - Centro de la pintura -->
					<div class="flex flex-col items-center gap-1">
						<span class="text-[9px] font-bold text-orange-300 uppercase tracking-wider">Pívot</span>
						{#each centers as p}
							<div class="flex flex-col items-center group transition-transform hover:scale-110">
								<div class="relative">
									<button
										type="button"
										class="w-11 h-11 rounded-full flex items-center justify-center text-xs font-black text-white shadow-xl border-2 border-white/90 cursor-pointer bg-orange-700"
										onclick={() => onSelectPlayer?.(p)}
										title="{p.first_name} {p.last_name} (Pívot)"
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
						{#if interactive && onAddPlayer}
							<button
								type="button"
								onclick={() => onAddPlayer('center')}
								title="Agregar Pívot"
								class="w-10 h-10 rounded-full border-2 border-dashed border-orange-300/80 bg-orange-500/20 hover:bg-orange-500/40 text-orange-200 flex flex-col items-center justify-center text-[11px] font-bold transition shadow cursor-pointer"
							>
								<span>+</span>
								<span class="text-[8px] font-mono leading-none">PIV</span>
							</button>
						{:else if centers.length === 0}
							<span class="text-[9px] text-white/50 bg-black/40 px-2 py-0.5 rounded-full border border-white/10">Sin pívot</span>
						{/if}
					</div>
				</div>
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
						<span class="text-white font-medium" style="color: #ffffff !important;">{getShortDisplayName(p)}</span>
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
