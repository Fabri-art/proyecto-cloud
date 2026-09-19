<script>
	/**
	 * VolleyballCourt.svelte — Cancha táctica de Vóley (6 zonas reglamentarias)
	 *
	 * Disposición:
	 *   Zona Delantera (frente a la red): Opuesto | Central Del. | Punta Del.
	 *   Zona Trasera  (fondo de cancha): Armador  | Líbero      | Punta Tras.
	 *
	 * Props:
	 *   players        — array de jugadores
	 *   interactive    — si es true, muestra botones de agregar/quitar
	 *   teamName       — nombre del equipo
	 *   teamColor      — color base del equipo
	 *   onSelectPlayer — callback al hacer click en un jugador
	 *   onAddPlayer    — callback para agregar jugador en una posición
	 *   onRemovePlayer — callback para quitar jugador de la cancha
	 */

	let {
		players = [],
		interactive = false,
		teamName = '',
		teamColor = '#7c3aed',
		onSelectPlayer = null,
		onAddPlayer = null,
		onRemovePlayer = null
	} = $props();

	// Agrupar jugadores por posición
	const setters        = $derived(players.filter((p) => p.position === 'setter'));
	const liberos        = $derived(players.filter((p) => p.position === 'libero'));
	const outsideHitters = $derived(players.filter((p) => p.position === 'outside_hitter'));
	const opposites      = $derived(players.filter((p) => p.position === 'opposite'));
	const middleBlockers = $derived(players.filter((p) => p.position === 'middle_blocker'));
	const benchPlayers   = $derived(
		players.filter(
			(p) =>
				!['setter', 'libero', 'outside_hitter', 'opposite', 'middle_blocker'].includes(
					p.position ?? ''
				)
		)
	);

	function getShortDisplayName(p) {
		if (!p) return '?';
		const first = p.first_name?.[0]?.toUpperCase() ?? '';
		const last = p.last_name ? p.last_name.split(' ')[0] : '';
		return last ? `${first}. ${last}` : p.first_name ?? '?';
	}
</script>

<div class="flex flex-col gap-3 w-full select-none">
	<!-- ══ CANCHA DE VÓLEY ══════════════════════════════════════════ -->
	<div
		class="relative w-full rounded-2xl overflow-hidden shadow-2xl border border-violet-800/60"
		style="background: linear-gradient(180deg, #1e1230 0%, #2d1b6e 50%, #1e1230 100%); min-height: 340px;"
	>
		<!-- Líneas de la cancha -->
		<svg
			class="absolute inset-0 w-full h-full"
			viewBox="0 0 400 340"
			preserveAspectRatio="none"
			aria-hidden="true"
		>
			<!-- Borde exterior de la cancha -->
			<rect x="20" y="20" width="360" height="300" fill="none" stroke="rgba(167,139,250,0.35)" stroke-width="2" rx="4"/>
			<!-- Red central (línea de mitad de cancha) -->
			<line x1="20" y1="170" x2="380" y2="170" stroke="rgba(255,255,255,0.65)" stroke-width="3"/>
			<!-- Sombra/grosor de red -->
			<line x1="20" y1="173" x2="380" y2="173" stroke="rgba(0,0,0,0.3)" stroke-width="1"/>
			<!-- Línea de ataque delantera (3m desde la red) -->
			<line x1="20" y1="115" x2="380" y2="115" stroke="rgba(167,139,250,0.4)" stroke-width="1.5" stroke-dasharray="8,4"/>
			<!-- Línea de ataque trasera (3m desde la red) -->
			<line x1="20" y1="225" x2="380" y2="225" stroke="rgba(167,139,250,0.4)" stroke-width="1.5" stroke-dasharray="8,4"/>
			<!-- Divisiones verticales zona delantera -->
			<line x1="153" y1="20" x2="153" y2="170" stroke="rgba(167,139,250,0.2)" stroke-width="1"/>
			<line x1="247" y1="20" x2="247" y2="170" stroke="rgba(167,139,250,0.2)" stroke-width="1"/>
			<!-- Divisiones verticales zona trasera -->
			<line x1="153" y1="170" x2="153" y2="320" stroke="rgba(167,139,250,0.2)" stroke-width="1"/>
			<line x1="247" y1="170" x2="247" y2="320" stroke="rgba(167,139,250,0.2)" stroke-width="1"/>
			<!-- Etiquetas de zonas -->
			<text x="200" y="14" text-anchor="middle" fill="rgba(167,139,250,0.5)" font-size="9" font-family="monospace">ZONA DELANTERA</text>
			<text x="200" y="336" text-anchor="middle" fill="rgba(167,139,250,0.5)" font-size="9" font-family="monospace">ZONA TRASERA</text>
			<!-- Etiqueta red -->
			<text x="390" y="173" text-anchor="start" fill="rgba(255,255,255,0.4)" font-size="8" font-family="monospace">RED</text>
		</svg>

		<!-- ══ ZONA DELANTERA (cerca de la red) ══════════════════════ -->
		<div class="relative z-10 flex items-center justify-around px-4 pt-5 pb-2" style="height: 50%;">
			<!-- Opuesto -->
			<div class="flex flex-col items-center gap-1">
				<span class="text-[9px] font-bold text-violet-300/70 uppercase tracking-widest">Opuesto</span>
				{#each opposites as p}
					<div class="flex flex-col items-center group transition-transform hover:scale-110">
						<div class="relative">
							<button
								type="button"
								class="w-12 h-12 rounded-full flex items-center justify-center text-sm font-black text-white shadow-2xl border-2 border-white/90 cursor-pointer bg-violet-700"
								onclick={() => onSelectPlayer?.(p)}
								title="{p.first_name} {p.last_name} (Opuesto)"
							>
								{p.shirt_number ?? '1'}
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
						<span class="mt-1 px-2 py-0.5 rounded-md text-[10px] font-bold text-white bg-slate-950/85 border border-white/20 truncate max-w-[80px] text-center shadow">
							{getShortDisplayName(p)}
						</span>
					</div>
				{/each}
				{#if interactive && onAddPlayer}
					<button
						type="button"
						onclick={() => onAddPlayer('opposite')}
						title="Agregar Opuesto"
						class="w-11 h-11 rounded-full border-2 border-dashed border-violet-300/80 bg-violet-500/20 hover:bg-violet-500/40 text-violet-200 flex flex-col items-center justify-center text-xs font-bold transition shadow cursor-pointer"
					>
						<span>+</span>
						<span class="text-[9px] font-mono leading-none">OPU</span>
					</button>
				{:else if opposites.length === 0}
					<span class="text-[10px] text-white/50 bg-black/30 px-2 py-0.5 rounded-full border border-white/10">Sin opuesto</span>
				{/if}
			</div>

			<!-- Central Delantero -->
			<div class="flex flex-col items-center gap-1">
				<span class="text-[9px] font-bold text-fuchsia-300/70 uppercase tracking-widest">Central</span>
				{#each middleBlockers.slice(0, Math.ceil(middleBlockers.length / 2)) as p}
					<div class="flex flex-col items-center group transition-transform hover:scale-110">
						<div class="relative">
							<button
								type="button"
								class="w-12 h-12 rounded-full flex items-center justify-center text-sm font-black text-white shadow-2xl border-2 border-white/90 cursor-pointer bg-fuchsia-700"
								onclick={() => onSelectPlayer?.(p)}
								title="{p.first_name} {p.last_name} (Central)"
							>
								{p.shirt_number ?? '2'}
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
						<span class="mt-1 px-2 py-0.5 rounded-md text-[10px] font-bold text-white bg-slate-950/85 border border-white/20 truncate max-w-[80px] text-center shadow">
							{getShortDisplayName(p)}
						</span>
					</div>
				{/each}
				{#if interactive && onAddPlayer}
					<button
						type="button"
						onclick={() => onAddPlayer('middle_blocker')}
						title="Agregar Central"
						class="w-11 h-11 rounded-full border-2 border-dashed border-fuchsia-300/80 bg-fuchsia-500/20 hover:bg-fuchsia-500/40 text-fuchsia-200 flex flex-col items-center justify-center text-xs font-bold transition shadow cursor-pointer"
					>
						<span>+</span>
						<span class="text-[9px] font-mono leading-none">CEN</span>
					</button>
				{:else if middleBlockers.length === 0}
					<span class="text-[10px] text-white/50 bg-black/30 px-2 py-0.5 rounded-full border border-white/10">Sin centrales</span>
				{/if}
			</div>

			<!-- Punta Delantero (Outside Hitter delantero) -->
			<div class="flex flex-col items-center gap-1">
				<span class="text-[9px] font-bold text-indigo-300/70 uppercase tracking-widest">Punta Del.</span>
				{#each outsideHitters.slice(0, Math.ceil(outsideHitters.length / 2)) as p}
					<div class="flex flex-col items-center group transition-transform hover:scale-110">
						<div class="relative">
							<button
								type="button"
								class="w-12 h-12 rounded-full flex items-center justify-center text-sm font-black text-white shadow-2xl border-2 border-white/90 cursor-pointer bg-indigo-600"
								onclick={() => onSelectPlayer?.(p)}
								title="{p.first_name} {p.last_name} (Punta)"
							>
								{p.shirt_number ?? '6'}
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
						<span class="mt-1 px-2 py-0.5 rounded-md text-[10px] font-bold text-white bg-slate-950/85 border border-white/20 truncate max-w-[80px] text-center shadow">
							{getShortDisplayName(p)}
						</span>
					</div>
				{/each}
				{#if interactive && onAddPlayer}
					<button
						type="button"
						onclick={() => onAddPlayer('outside_hitter')}
						title="Agregar Punta"
						class="w-11 h-11 rounded-full border-2 border-dashed border-indigo-300/80 bg-indigo-500/20 hover:bg-indigo-500/40 text-indigo-200 flex flex-col items-center justify-center text-xs font-bold transition shadow cursor-pointer"
					>
						<span>+</span>
						<span class="text-[9px] font-mono leading-none">PUN</span>
					</button>
				{:else if outsideHitters.length === 0}
					<span class="text-[10px] text-white/50 bg-black/30 px-2 py-0.5 rounded-full border border-white/10">Sin puntas</span>
				{/if}
			</div>
		</div>

		<!-- ══ RED (separador visual) ══════════════════════════════════ -->
		<div class="relative z-10 flex items-center gap-2 px-4">
			<div class="flex-1 h-px bg-white/30"></div>
			<span class="text-[10px] font-black text-white/60 tracking-widest uppercase px-2">RED</span>
			<div class="flex-1 h-px bg-white/30"></div>
		</div>

		<!-- ══ ZONA TRASERA (fondo de cancha) ════════════════════════ -->
		<div class="relative z-10 flex items-center justify-around px-4 pt-2 pb-5" style="height: 50%;">
			<!-- Armador -->
			<div class="flex flex-col items-center gap-1">
				<span class="text-[9px] font-bold text-cyan-300/70 uppercase tracking-widest">Armador</span>
				{#each setters as p}
					<div class="flex flex-col items-center group transition-transform hover:scale-110">
						<div class="relative">
							<button
								type="button"
								class="w-12 h-12 rounded-full flex items-center justify-center text-sm font-black text-white shadow-2xl border-2 border-white/90 cursor-pointer bg-cyan-700"
								onclick={() => onSelectPlayer?.(p)}
								title="{p.first_name} {p.last_name} (Armador)"
							>
								{p.shirt_number ?? '11'}
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
						<span class="mt-1 px-2 py-0.5 rounded-md text-[10px] font-bold text-cyan-300 bg-slate-950/90 border border-cyan-400/30 truncate max-w-[80px] text-center shadow">
							{getShortDisplayName(p)}
						</span>
					</div>
				{/each}
				{#if interactive && onAddPlayer}
					<button
						type="button"
						onclick={() => onAddPlayer('setter')}
						title="Agregar Armador"
						class="w-11 h-11 rounded-full border-2 border-dashed border-cyan-300/80 bg-cyan-500/20 hover:bg-cyan-500/40 text-cyan-200 flex flex-col items-center justify-center text-xs font-bold transition shadow cursor-pointer"
					>
						<span>+</span>
						<span class="text-[9px] font-mono leading-none">ARM</span>
					</button>
				{:else if setters.length === 0}
					<span class="text-[10px] text-white/50 bg-black/30 px-2 py-0.5 rounded-full border border-white/10">Sin armador</span>
				{/if}
			</div>

			<!-- Líbero -->
			<div class="flex flex-col items-center gap-1">
				<span class="text-[9px] font-bold text-yellow-300/70 uppercase tracking-widest">Líbero</span>
				{#each liberos as p}
					<div class="flex flex-col items-center group transition-transform hover:scale-110">
						<div class="relative">
							<button
								type="button"
								class="w-12 h-12 rounded-full flex items-center justify-center text-sm font-black text-white shadow-2xl border-2 border-yellow-300/80 cursor-pointer bg-yellow-700"
								onclick={() => onSelectPlayer?.(p)}
								title="{p.first_name} {p.last_name} (Líbero)"
							>
								{p.shirt_number ?? 'L'}
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
						<span class="mt-1 px-2 py-0.5 rounded-md text-[10px] font-bold text-yellow-300 bg-slate-950/90 border border-yellow-400/30 truncate max-w-[80px] text-center shadow">
							{getShortDisplayName(p)}
						</span>
					</div>
				{/each}
				{#if interactive && onAddPlayer}
					<button
						type="button"
						onclick={() => onAddPlayer('libero')}
						title="Agregar Líbero"
						class="w-11 h-11 rounded-full border-2 border-dashed border-yellow-300/80 bg-yellow-500/20 hover:bg-yellow-500/40 text-yellow-200 flex flex-col items-center justify-center text-xs font-bold transition shadow cursor-pointer"
					>
						<span>+</span>
						<span class="text-[9px] font-mono leading-none">LIB</span>
					</button>
				{:else if liberos.length === 0}
					<span class="text-[10px] text-white/50 bg-black/30 px-2 py-0.5 rounded-full border border-white/10">Sin líbero</span>
				{/if}
			</div>

			<!-- Punta Trasero -->
			<div class="flex flex-col items-center gap-1">
				<span class="text-[9px] font-bold text-indigo-300/70 uppercase tracking-widest">Punta Tras.</span>
				{#each outsideHitters.slice(Math.ceil(outsideHitters.length / 2)) as p}
					<div class="flex flex-col items-center group transition-transform hover:scale-110">
						<div class="relative">
							<button
								type="button"
								class="w-12 h-12 rounded-full flex items-center justify-center text-sm font-black text-white shadow-2xl border-2 border-white/90 cursor-pointer bg-indigo-600"
								onclick={() => onSelectPlayer?.(p)}
								title="{p.first_name} {p.last_name} (Punta)"
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
						<span class="mt-1 px-2 py-0.5 rounded-md text-[10px] font-bold text-white bg-slate-950/85 border border-white/20 truncate max-w-[80px] text-center shadow">
							{getShortDisplayName(p)}
						</span>
					</div>
				{/each}
				{#if interactive && onAddPlayer && outsideHitters.length < 2}
					<button
						type="button"
						onclick={() => onAddPlayer('outside_hitter')}
						title="Agregar Punta Trasero"
						class="w-11 h-11 rounded-full border-2 border-dashed border-indigo-300/80 bg-indigo-500/20 hover:bg-indigo-500/40 text-indigo-200 flex flex-col items-center justify-center text-xs font-bold transition shadow cursor-pointer"
					>
						<span>+</span>
						<span class="text-[9px] font-mono leading-none">PUN</span>
					</button>
				{:else if outsideHitters.length < 2 && !interactive}
					<span class="text-[10px] text-white/50 bg-black/30 px-2 py-0.5 rounded-full border border-white/10">—</span>
				{/if}
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
