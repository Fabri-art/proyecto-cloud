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
		teamName = 'Los Farmeadores',
		teamColor = '#eab308',
		onAddPlayer = () => {},
		onRemovePlayer = () => {}
	} = $props();

	// 3 Nodos en el asfalto callejero (Pelea de Baile)
	const auraSpots = [
		{ id: 'aura_main',  title: 'FARMEADOR PRINCIPAL',  subtitle: 'Rey del Aura / Breakdance', icon: '👑', x: 50, y: 44, glow: '#eab308' },
		{ id: 'aura_sub_1', title: 'FARMEADOR SUPLENTE 1', subtitle: 'Paso Lunar / Free Flow',   icon: '🕺', x: 26, y: 68, glow: '#a855f7' },
		{ id: 'aura_sub_2', title: 'FARMEADOR SUPLENTE 2', subtitle: 'Onda Eléctrica / Flex',    icon: '⚡', x: 74, y: 68, glow: '#06b6d4' }
	];

	function getPlayerInSpot(spotId) {
		return players.find((p) => p.position === spotId);
	}
</script>

<div class="aura-street-container tactical-court-scope relative w-full max-w-xl mx-auto rounded-2xl overflow-hidden shadow-2xl border-2 border-yellow-500/40 select-none">
	<!-- Cuadrado Asfaltado Callejero -->
	<div class="absolute inset-0 bg-[#1e1e24]"></div>
	
	<!-- Textura de asfalto y grietas urbanas -->
	<div class="absolute inset-0 opacity-20 bg-[radial-gradient(#ffffff_1px,transparent_1px)] [background-size:16px_16px]"></div>

	<!-- Círculo y Cuadrado de Batalla de Baile pintado con tiza / spray amarillo y blanco -->
	<svg class="absolute inset-0 w-full h-full pointer-events-none opacity-60" viewBox="0 0 100 100" preserveAspectRatio="none">
		<!-- Cuadrado exterior de asfalto delimitado -->
		<rect x="10" y="12" width="80" height="76" rx="4" fill="none" stroke="#facc15" stroke-width="1" stroke-dasharray="6 3" />
		<!-- Círculo central de pista de baile -->
		<circle cx="50" cy="48" r="26" fill="rgba(250, 204, 21, 0.04)" stroke="#ffffff" stroke-width="0.8" stroke-dasharray="4 2" />
		<circle cx="50" cy="48" r="14" fill="rgba(234, 179, 8, 0.08)" stroke="#facc15" stroke-width="0.6" />
		<!-- Marcas de spray urbano -->
		<line x1="20" y1="12" x2="20" y2="88" stroke="rgba(255,255,255,0.15)" stroke-width="0.5" />
		<line x1="80" y1="12" x2="80" y2="88" stroke="rgba(255,255,255,0.15)" stroke-width="0.5" />
		<line x1="10" y1="50" x2="90" y2="50" stroke="rgba(255,255,255,0.15)" stroke-width="0.5" stroke-dasharray="2 4" />
	</svg>

	<!-- Standardized Header de la Batalla Callejera -->
	<div class="court-header-bar relative z-10 flex items-center justify-between px-4 py-2.5 sm:px-5 sm:py-3 border-b border-yellow-500/30 bg-black/75 backdrop-blur-md">
		<div class="flex items-center gap-2.5 min-w-0">
			<span class="text-2xl shrink-0 animate-bounce">🕺</span>
			<div class="min-w-0">
				<h4 class="text-xs sm:text-sm font-black text-white uppercase tracking-wider leading-none truncate" style="color: #ffffff !important;">
					Cuadrilátero de Asfalto — Batalla de Aura
				</h4>
				<span class="text-[10px] text-yellow-300 font-mono block truncate mt-0.5" style="color: #fde047 !important;">
					Duelo de Baile y Farmear Aura · 3 Puestos
				</span>
			</div>
		</div>
		<div class="px-2.5 py-1 rounded-full text-[11px] font-bold bg-yellow-950/90 text-yellow-300 border border-yellow-500/40 shrink-0 ml-2 truncate max-w-[130px]" style="color: #fde047 !important;">
			{teamName}
		</div>
	</div>

	<!-- Pista de baile de asfalto -->
	<div class="relative z-10 w-full p-3 flex items-center justify-center" style="min-height: 380px;">
		{#each auraSpots as spot}
			{@const p = getPlayerInSpot(spot.id)}
			<div
				class="absolute -translate-x-1/2 -translate-y-1/2 flex flex-col items-center transition-all duration-300"
				style="left: {spot.x}%; top: {spot.y}%;"
			>
				{#if p}
					<!-- Bailarín / Farmeador Asignado -->
					<div class="group relative flex flex-col items-center cursor-pointer">
						<div
							class="w-12 h-12 sm:w-14 sm:h-14 rounded-2xl flex items-center justify-center shadow-2xl transition-transform duration-300 group-hover:scale-110 border-2"
							style="background: radial-gradient(circle, {spot.glow} 0%, #17171c 80%); border-color: {spot.glow}; box-shadow: 0 0 20px {spot.glow}88;"
						>
							<span class="text-2xl sm:text-3xl animate-pulse">{spot.icon}</span>
						</div>

						<div class="mt-1.5 flex flex-col items-center max-w-[130px]">
							<span class="text-[9px] font-mono font-bold px-1.5 py-0.5 rounded bg-black/90 text-yellow-300 border border-yellow-500/50 whitespace-nowrap" style="color: #fde047 !important;">
								{spot.title}
							</span>
							<div class="court-player-badge mt-1 px-2.5 py-1 rounded-lg flex flex-col items-center w-full shadow-lg" style="background: rgba(15, 23, 42, 0.94) !important; border: 1px solid rgba(250, 204, 21, 0.5) !important;">
								<span class="text-xs font-bold text-white text-center truncate w-full" style="color: #ffffff !important;">
									{p.first_name} {p.last_name}
								</span>
								{#if p.shirt_number !== null && p.shirt_number !== undefined}
									<span class="text-[9px] font-mono text-yellow-300/90 font-bold" style="color: #fde047 !important;">
										Dorsal #{p.shirt_number}
									</span>
								{/if}
							</div>
						</div>

						{#if interactive}
							<button
								type="button"
								onclick={() => onRemovePlayer(p)}
								class="absolute -top-1.5 -right-1.5 w-6 h-6 rounded-full bg-red-600 hover:bg-red-500 text-white text-xs font-bold flex items-center justify-center shadow-md transition transform hover:scale-115 cursor-pointer"
								title="Bajar de la pista"
							>
								✕
							</button>
						{/if}
					</div>
				{:else}
					<!-- Espacio de baile libre -->
					<div class="flex flex-col items-center">
						<button
							type="button"
							disabled={!interactive}
							onclick={() => interactive && onAddPlayer(spot.id)}
							class="w-12 h-12 sm:w-14 sm:h-14 rounded-2xl border-2 border-dashed flex items-center justify-center transition duration-300 group hover:scale-105 {interactive ? 'cursor-pointer' : ''}"
							style="border-color: {spot.glow}99; background: rgba(0, 0, 0, 0.7); box-shadow: 0 0 14px {spot.glow}33;"
						>
							{#if interactive}
								<span class="text-xl text-yellow-300 group-hover:text-white font-black group-hover:scale-125 transition">+</span>
							{:else}
								<span class="text-xs text-yellow-400 font-mono font-bold" style="color: #facc15 !important;">Libre</span>
							{/if}
						</button>
						<div class="mt-1.5 flex flex-col items-center px-2 py-1 rounded bg-black/85 border border-yellow-500/30 max-w-[125px]">
							<span class="text-[10px] font-bold text-yellow-300 block leading-tight text-center truncate w-full" style="color: #fde047 !important;">{spot.title}</span>
							<span class="text-[9px] text-slate-300 block font-mono text-center truncate w-full" style="color: #cbd5e1 !important;">{spot.subtitle}</span>
							{#if interactive}
								<span class="text-[8px] text-yellow-400/90 font-mono" style="color: #facc15 !important;">Clic para colocar</span>
							{/if}
						</div>
					</div>
				{/if}
			</div>
		{/each}
	</div>
</div>
