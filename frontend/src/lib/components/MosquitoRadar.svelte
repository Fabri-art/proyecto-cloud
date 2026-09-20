<script>
	/**
	 * @typedef {Object} Player
	 * @property {number} [id]
	 * @property {string} first_name
	 * @property {string} last_name
	 * @property {number|null} [shirt_number]
	 * @property {string} [position]
	 * @property {string} [nationality]
	 */

	/** @type {{ players: Player[], interactive?: boolean, teamName?: string, teamColor?: string, onAddPlayer?: (pos: string) => void, onRemovePlayer?: (player: Player) => void }} */
	let {
		players = [],
		interactive = false,
		teamName = 'Escuadrón Zancudo',
		teamColor = '#84cc16',
		onAddPlayer = () => {},
		onRemovePlayer = () => {}
	} = $props();

	const lanes = [
		{ id: 'mosquito_pic',  title: 'PIC (Aguijón)',  desc: 'Ataque frontal de picaduras',   icon: '🎯', glow: '#a3e635' },
		{ id: 'mosquito_zum',  title: 'ZUM (Zumbador)', desc: 'Sonido y zumbido constante',    icon: '🔊', glow: '#facc15' },
		{ id: 'mosquito_evas', title: 'EVAS (Evasor)',  desc: 'Maniobra y esquiva rápida',     icon: '💨', glow: '#38bdf8' }
	];

	function getPlayerInLane(laneId) {
		return players.find((p) => p.position === laneId);
	}
</script>

<div class="mosquito-track-container tactical-court-scope relative w-full max-w-xl mx-auto rounded-2xl overflow-hidden shadow-2xl border-2 border-lime-500/40 select-none">
	<!-- Pista Nocturna de Vuelo de Mosquitos -->
	<div class="absolute inset-0 bg-gradient-to-r from-[#031505] via-[#08240a] to-[#041205]"></div>

	<!-- Farolas / luces nocturnas en la meta -->
	<div class="absolute right-0 top-0 bottom-0 w-24 bg-gradient-to-l from-yellow-300/15 to-transparent pointer-events-none"></div>

	<!-- Líneas de vuelo fluorescentes verdes -->
	<svg class="absolute inset-0 w-full h-full pointer-events-none opacity-40" viewBox="0 0 100 100" preserveAspectRatio="none">
		<line x1="0" y1="33" x2="100" y2="33" stroke="#84cc16" stroke-width="0.8" stroke-dasharray="3 3" />
		<line x1="0" y1="66" x2="100" y2="66" stroke="#84cc16" stroke-width="0.8" stroke-dasharray="3 3" />
		<circle cx="95" cy="50" r="18" fill="rgba(234, 179, 8, 0.1)" stroke="#eab308" stroke-width="1" />
	</svg>

	<!-- Standardized Header de la Pista de Mosquitos -->
	<div class="court-header-bar relative z-10 flex items-center justify-between px-4 py-2.5 sm:px-5 sm:py-3 border-b border-lime-500/30 bg-black/75 backdrop-blur-md">
		<div class="flex items-center gap-2.5 min-w-0">
			<span class="text-2xl shrink-0 animate-pulse">🦟</span>
			<div class="min-w-0">
				<h4 class="text-xs sm:text-sm font-black text-white uppercase tracking-wider leading-none truncate" style="color: #ffffff !important;">
					Pista de Vuelo — Maratón de Mosquitos
				</h4>
				<span class="text-[10px] text-lime-300 font-mono block truncate mt-0.5" style="color: #bef264 !important;">
					3 Carriles Aéreos Nocturnos · PIC / ZUM / EVAS
				</span>
			</div>
		</div>
		<div class="px-2.5 py-1 rounded-full text-[11px] font-black bg-lime-950 text-lime-300 border border-lime-500/40 shrink-0 ml-2 truncate max-w-[130px]" style="color: #bef264 !important;">
			{teamName}
		</div>
	</div>

	<!-- 3 Carriles de Vuelo con Selección Clara de Posiciones -->
	<div class="relative z-10 w-full flex flex-col divide-y divide-lime-500/30">
		{#each lanes as lane}
			{@const p = getPlayerInLane(lane.id)}
			<div class="flex items-center justify-between px-4 py-2.5 min-h-[64px] sm:min-h-[72px]">
				<!-- Rol y Descripción protegidos con fondo oscuro -->
				<div class="flex items-center gap-2.5 w-44 sm:w-48 shrink-0 bg-black/70 px-2.5 py-1.5 rounded-lg border border-lime-500/30 shadow-md">
					<div
						class="w-8 h-8 rounded-lg flex items-center justify-center text-lg font-bold border shrink-0"
						style="background: rgba(132, 204, 22, 0.2); border-color: {lane.glow}; color: {lane.glow};"
					>
						{lane.icon}
					</div>
					<div class="min-w-0">
						<span class="text-xs font-black text-white block leading-tight truncate" style="color: #ffffff !important;">{lane.title}</span>
						<span class="text-[10px] text-lime-300 font-mono block truncate" style="color: #bef264 !important;">{lane.desc}</span>
					</div>
				</div>

				<!-- Zancudo / Posición Asignada o Botón Vacío -->
				<div class="flex-1 flex justify-center pl-2">
					{#if p}
						<div class="group relative flex items-center gap-3 cursor-pointer court-player-badge px-3.5 py-2 rounded-xl border border-lime-400 shadow-xl" style="background: rgba(15, 23, 42, 0.94) !important;">
							<span class="text-2xl shrink-0">🦟</span>
							<div class="text-left min-w-0 max-w-[140px] sm:max-w-[170px]">
								<span class="text-xs sm:text-sm font-bold text-white block truncate" style="color: #ffffff !important;">
									{p.first_name} {p.last_name}
								</span>
								{#if p.shirt_number !== null && p.shirt_number !== undefined}
									<span class="text-[10px] text-lime-300 font-mono font-bold block" style="color: #bef264 !important;">Dorsal #{p.shirt_number}</span>
								{/if}
							</div>

							{#if interactive}
								<button
									type="button"
									onclick={() => onRemovePlayer(p)}
									class="ml-2 w-6 h-6 rounded-full bg-red-600 hover:bg-red-500 text-white text-xs font-bold flex items-center justify-center shadow transition hover:scale-115 cursor-pointer shrink-0"
									title="Retirar zancudo"
								>
									✕
								</button>
							{/if}
						</div>
					{:else}
						<button
							type="button"
							disabled={!interactive}
							onclick={() => interactive && onAddPlayer(lane.id)}
							class="px-3.5 py-2 rounded-xl border-2 border-dashed border-lime-400/50 bg-black/60 hover:bg-black/80 text-white flex items-center gap-2 transition hover:scale-105 shadow-md {interactive ? 'cursor-pointer' : ''}"
						>
							{#if interactive}
								<span class="text-base font-black text-lime-300">+</span>
								<span class="text-xs font-bold text-lime-200" style="color: #d9f99d !important;">Asignar {lane.title}</span>
							{:else}
								<span class="text-xs text-lime-400/80 font-mono" style="color: #bef264 !important;">Posición Vacía</span>
							{/if}
						</button>
					{/if}
				</div>
			</div>
		{/each}
	</div>
</div>
