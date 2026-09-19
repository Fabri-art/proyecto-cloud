<script>
	/**
	 * SoccerPitch.svelte ÔÇö Diagrama Interactivo y Visual de Cancha de F├║tbol
	 *
	 * Modos:
	 * 1. interactive = true: Permite agregar jugadores haciendo clic en las l├¡neas (+),
	 *    y eliminar o interactuar con cada jugador en el campo.
	 * 2. interactive = false: Modo de solo lectura / visualizaci├│n para ver alineaciones
	 *    en detalle de equipos, partidos y p├║blico.
	 *
	 * Reglas y Distribuci├│n T├íctica:
	 * - Espaciado proporcional y equilibrado en 4 zonas t├ícticas (Delantera, Mediocampo, Defensa, Porter├¡a).
	 * - Los delanteros se ubican en zona de ataque fuera del ├írea rival.
	 * - Mediocampistas y defensas cuentan con amplia separaci├│n respecto a la l├¡nea central.
	 * - Solo se permite registrar 1 arquero titular (si ya existe, se oculta el bot├│n de agregar arquero).
	 * - Sin l├¡mite de jugadores totales (m├¡nimo 5).
	 */

	let {
		players = [],
		interactive = false,
		teamName = 'Equipo',
		teamColor = '#10b981',
		onAddPlayer = null,
		onRemovePlayer = null,
		onSelectPlayer = null
	} = $props();

	// Agrupaci├│n de jugadores por l├¡nea t├íctica
	let goalkeepers = $derived(players.filter((p) => (p.position ?? '').toLowerCase() === 'goalkeeper'));
	let defenders   = $derived(players.filter((p) => (p.position ?? '').toLowerCase() === 'defender'));
	let midfielders = $derived(players.filter((p) => (p.position ?? '').toLowerCase() === 'midfielder'));
	let forwards    = $derived(players.filter((p) => (p.position ?? '').toLowerCase() === 'forward'));

	// Suplentes / Banca (si hay jugadores sin posici├│n est├índar o adicionales)
	let benchPlayers = $derived(
		players.filter((p) => {
			const pos = (p.position ?? '').toLowerCase();
			return !['goalkeeper', 'defender', 'midfielder', 'forward'].includes(pos);
		})
	);

	function getShortDisplayName(player) {
		if (player.last_name) return player.last_name;
		if (player.first_name) return player.first_name.split(' ')[0];
		return `#${player.shirt_number ?? '?'}`;
	}
</script>

<div class="flex flex-col gap-3 w-full select-none">
	<!-- ÔöÇÔöÇ HEADER DE LA CANCHA ÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇ -->
	<div class="flex items-center justify-between px-3.5 py-2.5 rounded-xl bg-slate-900/90 border border-slate-800 text-xs shadow-md">
		<div class="flex items-center gap-2">
			<span class="w-3.5 h-3.5 rounded-full shadow border border-white/30" style="background-color: {teamColor};"></span>
			<span class="font-black text-white text-sm">{teamName}</span>
			<span class="text-slate-400">({players.length} jugador{players.length !== 1 ? 'es' : ''})</span>
		</div>
		<div class="flex items-center gap-1.5 font-mono text-[11px]">
			<span class="px-2 py-0.5 rounded bg-emerald-950/70 text-emerald-300 border border-emerald-700/50 font-bold" title="M├íximo 1 arquero">
				­ƒºñ {goalkeepers.length}/1 POR
			</span>
			<span class="px-2 py-0.5 rounded bg-blue-950/70 text-blue-300 border border-blue-700/50 font-bold">
				­ƒøí´©Å {defenders.length} DEF
			</span>
			<span class="px-2 py-0.5 rounded bg-amber-950/70 text-amber-300 border border-amber-700/50 font-bold">
				ÔÜÖ´©Å {midfielders.length} MED
			</span>
			<span class="px-2 py-0.5 rounded bg-rose-950/70 text-rose-300 border border-rose-700/50 font-bold">
				ÔÜ¢ {forwards.length} DEL
			</span>
		</div>
	</div>

	<!-- ÔöÇÔöÇ CANCHA DE C├ëSPED T├üCTICA ÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇ -->
	<div
		class="relative w-full rounded-2xl overflow-hidden shadow-2xl border-4 border-slate-700/90 flex flex-col justify-between"
		style="
			background: repeating-linear-gradient(
				180deg,
				#194d27 0px,
				#194d27 50px,
				#1e5b2e 50px,
				#1e5b2e 100px
			);
			min-height: 600px;
			height: 600px;
		"
	>
		<!-- L├¡nea perimetral de Cal Blanca -->
		<div class="absolute inset-3.5 border-2 border-white/45 rounded-lg pointer-events-none"></div>

		<!-- Porter├¡a y ├ürea Superior (Zona Rival - Delantera) -->
		<div class="absolute top-3.5 left-1/2 -translate-x-1/2 w-44 h-14 border-b-2 border-x-2 border-white/40 pointer-events-none rounded-b-md"></div>
		<div class="absolute top-3.5 left-1/2 -translate-x-1/2 w-20 h-5 border-b-2 border-x-2 border-white/40 pointer-events-none"></div>
		<div class="absolute top-11 left-1/2 -translate-x-1/2 w-2 h-2 rounded-full bg-white/50 pointer-events-none"></div>

		<!-- C├¡rculo Central y L├¡nea de Medio Campo -->
		<div class="absolute top-1/2 left-3.5 right-3.5 h-0.5 bg-white/40 -translate-y-1/2 pointer-events-none"></div>
		<div class="absolute top-1/2 left-1/2 w-28 h-28 border-2 border-white/40 rounded-full -translate-x-1/2 -translate-y-1/2 pointer-events-none"></div>
		<div class="absolute top-1/2 left-1/2 w-2.5 h-2.5 bg-white/60 rounded-full -translate-x-1/2 -translate-y-1/2 pointer-events-none"></div>

		<!-- Porter├¡a y ├ürea Inferior (Nuestra Zona Defensiva y Arquero) -->
		<div class="absolute bottom-3.5 left-1/2 -translate-x-1/2 w-44 h-14 border-t-2 border-x-2 border-white/40 pointer-events-none rounded-t-md"></div>
		<div class="absolute bottom-3.5 left-1/2 -translate-x-1/2 w-20 h-5 border-t-2 border-x-2 border-white/40 pointer-events-none"></div>
		<div class="absolute bottom-11 left-1/2 -translate-x-1/2 w-2 h-2 rounded-full bg-white/50 pointer-events-none"></div>

		<!-- ÔöÇÔöÇ ZONA 1: DELANTEROS (ATAQUE - 0% a 25%) ÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇ -->
		<!-- Posicionados holgadamente fuera del ├írea rival en zona de ataque -->
		<div class="relative z-10 flex-1 flex flex-col items-center justify-end pb-3 pt-4">
			<div class="flex items-center justify-center flex-wrap gap-4 sm:gap-6 w-full px-4">
				{#each forwards as p}
					<div class="flex flex-col items-center group transition-transform hover:scale-110">
						<div class="relative">
							<button
								type="button"
								class="w-12 h-12 rounded-full flex items-center justify-center text-sm font-black text-white shadow-2xl border-2 border-white/90 cursor-pointer"
								style="background: {teamColor};"
								onclick={() => onSelectPlayer?.(p)}
								title="{p.first_name} {p.last_name} (Delantero)"
							>
								{p.shirt_number ?? 'ÔÜ¢'}
							</button>
							{#if interactive && onRemovePlayer}
								<button
									type="button"
									onclick={() => onRemovePlayer(p)}
									title="Quitar de la cancha"
									class="absolute -top-1.5 -right-1.5 w-5 h-5 bg-red-600 hover:bg-red-500 text-white rounded-full text-xs font-black flex items-center justify-center shadow-lg z-20 cursor-pointer"
								>
									Ô£ò
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
						onclick={() => onAddPlayer('forward')}
						title="Agregar delantero"
						class="w-11 h-11 rounded-full border-2 border-dashed border-rose-300/80 bg-rose-500/20 hover:bg-rose-500/40 text-rose-200 flex flex-col items-center justify-center text-xs font-bold transition shadow cursor-pointer"
					>
						<span>+</span>
						<span class="text-[9px] font-mono leading-none">DEL</span>
					</button>
				{:else if forwards.length === 0}
					<span class="text-[11px] text-white/60 bg-black/40 px-3 py-1 rounded-full border border-white/10">Sin delanteros asignados</span>
				{/if}
			</div>
		</div>

		<!-- ÔöÇÔöÇ ZONA 2: MEDIOCAMPISTAS (MEDIO CAMPO OFENSIVO - 25% a 50%) ÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇ -->
		<!-- Posicionados con holgura por encima de la l├¡nea central -->
		<div class="relative z-10 flex-1 flex flex-col items-center justify-center py-2">
			<div class="flex items-center justify-center flex-wrap gap-4 sm:gap-6 w-full px-4">
				{#each midfielders as p}
					<div class="flex flex-col items-center group transition-transform hover:scale-110">
						<div class="relative">
							<button
								type="button"
								class="w-12 h-12 rounded-full flex items-center justify-center text-sm font-black text-white shadow-2xl border-2 border-white/90 cursor-pointer"
								style="background: {teamColor};"
								onclick={() => onSelectPlayer?.(p)}
								title="{p.first_name} {p.last_name} (Mediocampista)"
							>
								{p.shirt_number ?? 'ÔÜÖ´©Å'}
							</button>
							{#if interactive && onRemovePlayer}
								<button
									type="button"
									onclick={() => onRemovePlayer(p)}
									title="Quitar de la cancha"
									class="absolute -top-1.5 -right-1.5 w-5 h-5 bg-red-600 hover:bg-red-500 text-white rounded-full text-xs font-black flex items-center justify-center shadow-lg z-20 cursor-pointer"
								>
									Ô£ò
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
						onclick={() => onAddPlayer('midfielder')}
						title="Agregar mediocampista"
						class="w-11 h-11 rounded-full border-2 border-dashed border-amber-300/80 bg-amber-500/20 hover:bg-amber-500/40 text-amber-200 flex flex-col items-center justify-center text-xs font-bold transition shadow cursor-pointer"
					>
						<span>+</span>
						<span class="text-[9px] font-mono leading-none">MED</span>
					</button>
				{:else if midfielders.length === 0}
					<span class="text-[11px] text-white/60 bg-black/40 px-3 py-1 rounded-full border border-white/10">Sin mediocampistas</span>
				{/if}
			</div>
		</div>

		<!-- ÔöÇÔöÇ ZONA 3: DEFENSAS (ZONA DEFENSIVA - 50% a 75%) ÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇ -->
		<!-- Posicionados con holgura por debajo de la l├¡nea central y antes del ├írea penal -->
		<div class="relative z-10 flex-1 flex flex-col items-center justify-center py-2">
			<div class="flex items-center justify-center flex-wrap gap-4 sm:gap-6 w-full px-4">
				{#each defenders as p}
					<div class="flex flex-col items-center group transition-transform hover:scale-110">
						<div class="relative">
							<button
								type="button"
								class="w-12 h-12 rounded-full flex items-center justify-center text-sm font-black text-white shadow-2xl border-2 border-white/90 cursor-pointer"
								style="background: {teamColor};"
								onclick={() => onSelectPlayer?.(p)}
								title="{p.first_name} {p.last_name} (Defensa)"
							>
								{p.shirt_number ?? '­ƒøí´©Å'}
							</button>
							{#if interactive && onRemovePlayer}
								<button
									type="button"
									onclick={() => onRemovePlayer(p)}
									title="Quitar de la cancha"
									class="absolute -top-1.5 -right-1.5 w-5 h-5 bg-red-600 hover:bg-red-500 text-white rounded-full text-xs font-black flex items-center justify-center shadow-lg z-20 cursor-pointer"
								>
									Ô£ò
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
						onclick={() => onAddPlayer('defender')}
						title="Agregar defensa"
						class="w-11 h-11 rounded-full border-2 border-dashed border-blue-300/80 bg-blue-500/20 hover:bg-blue-500/40 text-blue-200 flex flex-col items-center justify-center text-xs font-bold transition shadow cursor-pointer"
					>
						<span>+</span>
						<span class="text-[9px] font-mono leading-none">DEF</span>
					</button>
				{:else if defenders.length === 0}
					<span class="text-[11px] text-white/60 bg-black/40 px-3 py-1 rounded-full border border-white/10">Sin defensas</span>
				{/if}
			</div>
		</div>

		<!-- ÔöÇÔöÇ ZONA 4: PORTERO / ARQUERO (PORTER├ìA - 75% a 100%) ÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇ -->
		<!-- Posicionado estrictamente en la porter├¡a; SOLO SE PERMITE 1 ARQUERO -->
		<div class="relative z-10 flex-1 flex flex-col items-center justify-center pb-2">
			<div class="flex items-center justify-center flex-wrap gap-4 sm:gap-6 w-full px-4">
				{#each goalkeepers as p}
					<div class="flex flex-col items-center group transition-transform hover:scale-110">
						<div class="relative">
							<button
								type="button"
								class="w-12 h-12 rounded-full flex items-center justify-center text-sm font-black text-slate-950 bg-amber-400 shadow-2xl border-2 border-white/90 cursor-pointer"
								onclick={() => onSelectPlayer?.(p)}
								title="{p.first_name} {p.last_name} (Arquero Oficial)"
							>
								{p.shirt_number ?? '1'}
							</button>
							{#if interactive && onRemovePlayer}
								<button
									type="button"
									onclick={() => onRemovePlayer(p)}
									title="Quitar arquero"
									class="absolute -top-1.5 -right-1.5 w-5 h-5 bg-red-600 hover:bg-red-500 text-white rounded-full text-xs font-black flex items-center justify-center shadow-lg z-20 cursor-pointer"
								>
									Ô£ò
								</button>
							{/if}
						</div>
						<span class="mt-1 px-2 py-0.5 rounded-md text-[11px] font-bold text-amber-300 bg-slate-950/90 border border-amber-400/30 truncate max-w-[90px] text-center shadow">
							{getShortDisplayName(p)}
						</span>
					</div>
				{/each}

				<!-- SOLO PERMITIR AGREGAR SI NO HAY NING├ÜN ARQUERO REGISTRADO A├ÜN -->
				{#if interactive && onAddPlayer && goalkeepers.length === 0}
					<button
						type="button"
						onclick={() => onAddPlayer('goalkeeper')}
						title="Agregar ├║nico arquero"
						class="w-11 h-11 rounded-full border-2 border-dashed border-emerald-300/80 bg-emerald-500/20 hover:bg-emerald-500/40 text-emerald-200 flex flex-col items-center justify-center text-xs font-bold transition shadow cursor-pointer"
					>
						<span>+</span>
						<span class="text-[9px] font-mono leading-none">POR</span>
					</button>
				{:else if goalkeepers.length === 0}
					<span class="text-[11px] text-white/60 bg-black/40 px-3 py-1 rounded-full border border-white/10">Sin arquero (1 requerido)</span>
				{/if}
			</div>
		</div>
	</div>

	<!-- ÔöÇÔöÇ BANCA DE SUPLENTES / RESERVA ÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇÔöÇ -->
	{#if benchPlayers.length > 0}
		<div class="p-3 rounded-xl bg-slate-900/70 border border-slate-800">
			<div class="flex items-center justify-between mb-2">
				<span class="text-xs font-bold text-slate-400 flex items-center gap-1.5">
					­ƒ¬æ Reserva / Suplentes ({benchPlayers.length})
				</span>
			</div>
			<div class="flex items-center gap-2 overflow-x-auto pb-1">
				{#each benchPlayers as p}
					<div
						class="flex items-center gap-1.5 px-2.5 py-1 rounded-lg bg-slate-800/80 border border-slate-700 text-xs shrink-0"
					>
						<span class="font-mono font-black text-amber-400">#{p.shirt_number ?? '?'}</span>
						<span class="text-white font-medium">{getShortDisplayName(p)}</span>
						{#if interactive && onRemovePlayer}
							<button
								type="button"
								onclick={() => onRemovePlayer(p)}
								class="text-red-400 hover:text-red-300 ml-1 font-bold cursor-pointer"
								title="Eliminar de la banca"
							>
								Ô£ò
							</button>
						{/if}
					</div>
				{/each}
			</div>
		</div>
	{/if}
</div>
