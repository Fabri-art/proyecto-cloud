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
		teamName = 'Escudería de Llantas',
		teamColor = '#f97316',
		onAddPlayer = () => {},
		onRemovePlayer = () => {}
	} = $props();

	const lanes = [
		{ id: 'tire_dir',  laneNum: 1, title: 'DIR (Dirección)', desc: 'Control de trayectoria y volante' },
		{ id: 'tire_rod',  laneNum: 2, title: 'ROD (Rodado)',    desc: 'Empuje y tracción en la recta' },
		{ id: 'tire_fren', laneNum: 3, title: 'FREN (Frenado)',  desc: 'Punto de frenado y estabilidad' }
	];

	function getPlayerInLane(laneId) {
		return players.find((p) => p.position === laneId);
	}
</script>

<div class="tire-olympic-container tactical-court-scope relative w-full max-w-xl mx-auto rounded-2xl overflow-hidden shadow-2xl border-2 border-orange-500/50 select-none">
	<!-- Pista Olímpica de Tartán Naranja -->
	<div class="absolute inset-0 bg-[#c2410c]"></div>
	
	<!-- Textura de tartán de atletismo -->
	<div class="absolute inset-0 opacity-15 bg-[radial-gradient(#ffffff_1px,transparent_1px)] [background-size:12px_12px]"></div>

	<!-- 3 Carriles Olímpicos delimitados por líneas blancas -->
	<div class="absolute inset-0 flex flex-col pointer-events-none">
		<div class="flex-1 border-b-2 border-white/80 relative flex items-center px-4">
			<span class="text-white/30 font-black text-2xl font-mono">1</span>
		</div>
		<div class="flex-1 border-b-2 border-white/80 relative flex items-center px-4">
			<span class="text-white/30 font-black text-2xl font-mono">2</span>
		</div>
		<div class="flex-1 relative flex items-center px-4">
			<span class="text-white/30 font-black text-2xl font-mono">3</span>
		</div>
	</div>

	<!-- Standardized Header de la Carrera de Llantas -->
	<div class="court-header-bar relative z-10 flex items-center justify-between px-4 py-2.5 sm:px-5 sm:py-3 border-b border-orange-500/40 bg-black/75 backdrop-blur-md">
		<div class="flex items-center gap-2.5 min-w-0">
			<span class="text-2xl shrink-0">🛞</span>
			<div class="min-w-0">
				<h4 class="text-xs sm:text-sm font-black text-white uppercase tracking-wider leading-none truncate" style="color: #ffffff !important;">
					Pista Olímpica — Carrera de Llantas
				</h4>
				<span class="text-[10px] text-orange-300 font-mono block truncate mt-0.5" style="color: #fdba74 !important;">
					3 Carriles de Tartán Naranja · DIR / ROD / FREN
				</span>
			</div>
		</div>
		<div class="px-2.5 py-1 rounded-full text-[11px] font-bold bg-orange-950/90 text-orange-300 border border-orange-500/50 shrink-0 ml-2 truncate max-w-[130px]" style="color: #fdba74 !important;">
			{teamName}
		</div>
	</div>

	<!-- 3 Carriles con sus slots horizontales -->
	<div class="relative z-10 w-full flex flex-col divide-y divide-white/40">
		{#each lanes as lane}
			{@const p = getPlayerInLane(lane.id)}
			<div class="flex items-center justify-between px-4 py-2.5 min-h-[64px] sm:min-h-[72px]">
				<!-- Número de carril y título con fondo oscuro protector -->
				<div class="flex items-center gap-2.5 w-44 sm:w-48 shrink-0 bg-black/70 px-2.5 py-1.5 rounded-lg border border-white/20 shadow-md">
					<div class="w-7 h-7 rounded-full bg-white/20 border border-white text-white font-black text-xs flex items-center justify-center font-mono shrink-0" style="color: #ffffff !important;">
						{lane.laneNum}
					</div>
					<div class="min-w-0">
						<span class="text-xs font-black text-white block leading-tight truncate" style="color: #ffffff !important;">{lane.title}</span>
						<span class="text-[10px] text-orange-200 font-mono block truncate" style="color: #fed7aa !important;">{lane.desc}</span>
					</div>
				</div>

				<!-- Llanta / Jugador Asignado o Botón Vacío -->
				<div class="flex-1 flex justify-center pl-2">
					{#if p}
						<div class="group relative flex items-center gap-3 cursor-pointer court-player-badge px-3.5 py-2 rounded-xl border border-orange-400 shadow-xl" style="background: rgba(15, 23, 42, 0.94) !important;">
							<div class="w-9 h-9 rounded-xl bg-orange-600 text-white flex items-center justify-center text-lg font-bold shadow shrink-0">
								🛞
							</div>
							<div class="text-left min-w-0 max-w-[140px] sm:max-w-[170px]">
								<span class="text-xs sm:text-sm font-bold text-white block truncate" style="color: #ffffff !important;">
									{p.first_name} {p.last_name}
								</span>
								{#if p.shirt_number !== null && p.shirt_number !== undefined}
									<span class="text-[10px] text-orange-300 font-mono font-bold block" style="color: #fdba74 !important;">Dorsal #{p.shirt_number}</span>
								{/if}
							</div>

							{#if interactive}
								<button
									type="button"
									onclick={() => onRemovePlayer(p)}
									class="ml-2 w-6 h-6 rounded-full bg-red-600 hover:bg-red-500 text-white text-xs font-bold flex items-center justify-center shadow transition hover:scale-115 cursor-pointer shrink-0"
									title="Quitar piloto"
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
							class="px-3.5 py-2 rounded-xl border-2 border-dashed border-white/60 bg-black/60 hover:bg-black/80 text-white flex items-center gap-2 transition hover:scale-105 shadow-md {interactive ? 'cursor-pointer' : ''}"
						>
							{#if interactive}
								<span class="text-base font-black text-orange-300">+</span>
								<span class="text-xs font-bold text-white" style="color: #ffffff !important;">Asignar a Carril {lane.laneNum}</span>
							{:else}
								<span class="text-xs text-orange-200/80 font-mono" style="color: #fed7aa !important;">Carril Vacío</span>
							{/if}
						</button>
					{/if}
				</div>
			</div>
		{/each}
	</div>
</div>
