<script>
	/**
	 * @typedef {Object} Player
	 * @property {number} [id]
	 * @property {string} first_name
	 * @property {string} last_name
	 * @property {number|null} [shirt_number]
	 * @property {string} [position]
	 * @property {string} [dni]
	 * @property {string} [nationality]
	 */

	/** @type {{ players: Player[], interactive?: boolean, teamName?: string, teamColor?: string, onAddPlayer?: (pos: string) => void, onRemovePlayer?: (player: Player) => void }} */
	let {
		players = [],
		interactive = false,
		teamName = 'Nadadores Celulares',
		teamColor = '#06b6d4',
		onAddPlayer = () => {},
		onRemovePlayer = () => {}
	} = $props();

	const p = $derived(players.find((item) => item.position === 'sperm_main') || players[0]);
</script>

<div class="sperm-track-container tactical-court-scope relative w-full max-w-xl mx-auto rounded-2xl overflow-hidden shadow-2xl border-2 border-cyan-500/40 select-none">
	<!-- Pista de Triatlón Celular dividida en 3 etapas -->
	<div class="absolute inset-0 bg-gradient-to-r from-[#032029] via-[#063847] to-[#041e26]"></div>
	
	<!-- 3 Etapas del Triatlón coloreadas -->
	<div class="absolute inset-0 flex">
		<!-- Etapa 1: Natación en Fluido -->
		<div class="flex-1 bg-cyan-950/50 border-r border-dashed border-cyan-400/30 flex flex-col justify-end p-2 sm:p-2.5">
			<span class="text-[9px] sm:text-[10px] font-mono font-bold text-cyan-300 uppercase bg-black/80 px-1.5 py-0.5 rounded self-start border border-cyan-500/40" style="color: #67e8f9 !important;">
				Etapa 1: Nado (0 - 300 µm)
			</span>
		</div>
		<!-- Etapa 2: Impulso Flagelar -->
		<div class="flex-1 bg-emerald-950/40 border-r border-dashed border-emerald-400/30 flex flex-col justify-end p-2 sm:p-2.5">
			<span class="text-[9px] sm:text-[10px] font-mono font-bold text-emerald-300 uppercase bg-black/80 px-1.5 py-0.5 rounded self-start border border-emerald-500/40" style="color: #6ee7b7 !important;">
				Etapa 2: Corriente (300 - 700 µm)
			</span>
		</div>
		<!-- Etapa 3: Recta a Meta -->
		<div class="flex-1 bg-pink-950/40 flex flex-col justify-end p-2 sm:p-2.5">
			<span class="text-[9px] sm:text-[10px] font-mono font-bold text-pink-300 uppercase bg-black/80 px-1.5 py-0.5 rounded self-start border border-pink-500/40" style="color: #f472b6 !important;">
				Etapa 3: Fecundación (700 - 1000 µm)
			</span>
		</div>
	</div>

	<!-- Carril de nado y boyas olímpicas microscópicas -->
	<svg class="absolute inset-0 w-full h-full pointer-events-none opacity-50" viewBox="0 0 100 100" preserveAspectRatio="none">
		<!-- Carriles superior e inferior de boyas -->
		<line x1="0" y1="25" x2="100" y2="25" stroke="rgba(6, 182, 212, 0.4)" stroke-width="0.8" stroke-dasharray="2 3" />
		<line x1="0" y1="75" x2="100" y2="75" stroke="rgba(6, 182, 212, 0.4)" stroke-width="0.8" stroke-dasharray="2 3" />
		<!-- Meta: Óvulo -->
		<circle cx="92" cy="50" r="16" fill="rgba(244, 114, 182, 0.15)" stroke="rgba(244, 114, 182, 0.8)" stroke-width="1.2" />
		<circle cx="92" cy="50" r="8" fill="rgba(244, 114, 182, 0.3)" stroke="rgba(244, 114, 182, 0.9)" stroke-width="0.8" />
	</svg>

	<!-- Standardized Header del Triatlón -->
	<div class="court-header-bar relative z-10 flex items-center justify-between px-4 py-2.5 sm:px-5 sm:py-3 border-b border-cyan-500/30 bg-black/75 backdrop-blur-md">
		<div class="flex items-center gap-2.5 min-w-0">
			<span class="text-2xl shrink-0 animate-bounce">🧬</span>
			<div class="min-w-0">
				<h4 class="text-xs sm:text-sm font-black text-white uppercase tracking-wider leading-none truncate" style="color: #ffffff !important;">
					Circuito de Triatlón de Espermatozoide
				</h4>
				<span class="text-[10px] text-cyan-300 font-mono block truncate mt-0.5" style="color: #67e8f9 !important;">
					Carril Celular de 1000 µm · 1 Nadador Titular
				</span>
			</div>
		</div>
		<div class="px-2.5 py-1 rounded-full text-[11px] font-bold bg-cyan-950/90 text-cyan-300 border border-cyan-500/40 shrink-0 ml-2 truncate max-w-[130px]" style="color: #67e8f9 !important;">
			{teamName}
		</div>
	</div>

	<!-- Zona de Nadador en la Pista -->
	<div class="relative z-10 w-full p-4 flex items-center justify-center" style="min-height: 320px;">
		<!-- Slot Único de Nadador -->
		<div class="relative flex flex-col items-center">
			{#if p}
				<div class="group relative flex flex-col items-center cursor-pointer">
					<div class="flex items-center gap-2">
						<div
							class="w-14 h-14 sm:w-16 sm:h-16 rounded-full flex items-center justify-center shadow-2xl transition transform group-hover:scale-110 border-2 border-cyan-300"
							style="background: radial-gradient(circle, #22d3ee 0%, #083344 85%); box-shadow: 0 0 25px rgba(6, 182, 212, 0.7);"
						>
							<span class="text-3xl sm:text-4xl">🧬</span>
						</div>
						<span class="text-cyan-300 font-mono text-2xl animate-pulse">〰️🏊‍♂️</span>
					</div>

					<div class="mt-2 flex flex-col items-center max-w-[180px]">
						<span class="text-[9px] font-mono font-bold px-2 py-0.5 rounded bg-black/90 text-cyan-300 border border-cyan-500/50 uppercase tracking-wide" style="color: #67e8f9 !important;">
							ESPERMATOZOIDE PRINCIPAL
						</span>
						<div class="court-player-badge mt-1 px-3 py-1 rounded-lg flex flex-col items-center w-full shadow-xl" style="background: rgba(15, 23, 42, 0.94) !important; border: 1px solid rgba(6, 182, 212, 0.5) !important;">
							<span class="text-xs sm:text-sm font-bold text-white text-center truncate w-full" style="color: #ffffff !important;">
								{p.first_name} {p.last_name}
							</span>
							{#if p.dni}
								<span class="text-[10px] text-cyan-300 font-mono font-bold" style="color: #67e8f9 !important;">DNI: {p.dni}</span>
							{:else if p.shirt_number !== null && p.shirt_number !== undefined}
								<span class="text-[10px] text-cyan-300 font-mono font-bold" style="color: #67e8f9 !important;">Dorsal #{p.shirt_number}</span>
							{/if}
						</div>
					</div>

					{#if interactive}
						<button
							type="button"
							onclick={() => onRemovePlayer(p)}
							class="absolute -top-1.5 -right-1.5 w-6 h-6 rounded-full bg-red-600 hover:bg-red-500 text-white text-xs font-bold flex items-center justify-center shadow-md transition transform hover:scale-115 cursor-pointer"
							title="Retirar nadador"
						>
							✕
						</button>
					{/if}
				</div>
			{:else}
				<div class="flex flex-col items-center">
					<button
						type="button"
						disabled={!interactive}
						onclick={() => interactive && onAddPlayer('sperm_main')}
						class="w-16 h-16 sm:w-20 sm:h-20 rounded-full border-2 border-dashed border-cyan-400 bg-cyan-950/70 flex items-center justify-center transition group hover:scale-105 hover:border-cyan-300 shadow-lg {interactive ? 'cursor-pointer' : ''}"
					>
						{#if interactive}
							<span class="text-2xl text-cyan-300 group-hover:text-white font-black group-hover:scale-125 transition">+</span>
						{:else}
							<span class="text-xs text-cyan-400 font-mono font-bold" style="color: #67e8f9 !important;">Vacío</span>
						{/if}
					</button>
					<div class="mt-2 text-center px-3 py-1 rounded bg-black/85 border border-cyan-500/30">
						<span class="text-xs font-bold text-cyan-200 block" style="color: #a5f3fc !important;">Espermatozoide Principal</span>
						{#if interactive}
							<span class="text-[10px] text-cyan-300 font-mono" style="color: #67e8f9 !important;">Clic para registrar nadador</span>
						{/if}
					</div>
				</div>
			{/if}
		</div>
	</div>
</div>
