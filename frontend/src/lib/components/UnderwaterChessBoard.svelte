<script>
	/**
	 * UnderwaterChessBoard.svelte
	 * Tablero de Ajedrez Bajo el Agua (8x8 con ambientación subacuática)
	 *
	 * Props:
	 *   players        — array de jugadores (en ajedrez: 1 o 2 competidores)
	 *   interactive    — si es true, permite agregar/quitar ajedrecistas
	 *   teamName       — nombre del club o jugador
	 *   teamColor      — color temático
	 *   onSelectPlayer — callback al hacer clic en un jugador
	 *   onAddPlayer    — callback para registrar ajedrecista
	 *   onRemovePlayer — callback para retirar ajedrecista
	 */

	let {
		players = [],
		interactive = false,
		teamName = '',
		teamColor = '#06b6d4',
		onSelectPlayer = null,
		onAddPlayer = null,
		onRemovePlayer = null
	} = $props();

	const ranks = [8, 7, 6, 5, 4, 3, 2, 1];
	const files = ['a', 'b', 'c', 'd', 'e', 'f', 'g', 'h'];

	// Piezas iniciales estándar (estética de tablero listo)
	const initialPieces = {
		'a8': '♜', 'b8': '♞', 'c8': '♝', 'd8': '♛', 'e8': '♚', 'f8': '♝', 'g8': '♞', 'h8': '♜',
		'a7': '♟', 'b7': '♟', 'c7': '♟', 'd7': '♟', 'e7': '♟', 'f7': '♟', 'g7': '♟', 'h7': '♟',
		'a2': '♙', 'b2': '♙', 'c2': '♙', 'd2': '♙', 'e2': '♙', 'f2': '♙', 'g2': '♙', 'h2': '♙',
		'a1': '♖', 'b1': '♘', 'c1': '♗', 'd1': '♕', 'e1': '♔', 'f1': '♗', 'g1': '♘', 'h1': '♖'
	};

	function isDarkSquare(fileIdx, rank) {
		return (fileIdx + rank) % 2 === 0;
	}

	const mainPlayer = $derived(players[0] ?? null);
	const subPlayer = $derived(players[1] ?? null);
</script>

<div class="flex flex-col gap-4 w-full select-none">
	<!-- ══ TABLERO DE AJEDREZ SUBMARINO ════════════════════════════════ -->
	<div
		class="relative w-full rounded-2xl overflow-hidden shadow-2xl border border-cyan-500/40 p-5 flex flex-col items-center gap-4"
		style="background: radial-gradient(ellipse at 50% 0%, #0d3b66 0%, #08203e 50%, #030d1a 100%);"
	>
		<!-- Efecto de burbujas y rayos de luz subacuáticos -->
		<div class="absolute inset-0 pointer-events-none opacity-30 overflow-hidden" aria-hidden="true">
			<div class="absolute -top-10 left-1/4 w-32 h-64 bg-cyan-400/20 blur-3xl transform -rotate-12"></div>
			<div class="absolute -top-10 right-1/4 w-40 h-64 bg-teal-300/20 blur-3xl transform rotate-12"></div>
			<div class="absolute bottom-4 left-10 text-cyan-300/20 text-xs font-mono">🫧 15m de profundidad submarina</div>
		</div>

		<!-- Cabecera del tablero -->
		<div class="relative z-10 flex flex-wrap items-center justify-between w-full max-w-md border-b border-cyan-500/30 pb-2.5">
			<div class="flex items-center gap-2">
				<span class="text-2xl">🌊♟️</span>
				<div>
					<h3 class="text-sm font-black text-white tracking-wide flex items-center gap-1.5">
						Ajedrez Bajo el Agua
						<span class="text-[10px] px-2 py-0.5 rounded-full bg-cyan-500/20 text-cyan-300 font-normal border border-cyan-500/30">1 vs 1</span>
					</h3>
					<p class="text-[11px] text-cyan-300/70 font-mono">
						{teamName ? teamName : 'Duelo Submarino'} &bull; Sin posiciones tácticas fijas
					</p>
				</div>
			</div>

			{#if interactive && onAddPlayer && players.length === 0}
				<button
					type="button"
					onclick={() => onAddPlayer('chess_player')}
					class="px-3 py-1 text-xs font-bold rounded-lg bg-cyan-600 hover:bg-cyan-500 text-white shadow-lg transition flex items-center gap-1"
				>
					<span>+</span> Inscribir Ajedrecista
				</button>
			{/if}
		</div>

		<!-- Cuadrícula del tablero 8x8 con coordenadas -->
		<div class="relative z-10 flex flex-col items-center">
			<div class="p-2 rounded-xl bg-slate-950/80 border-2 border-cyan-600/60 shadow-[0_0_30px_rgba(6,182,212,0.25)]">
				<div class="grid grid-cols-8 grid-rows-8 w-64 h-64 sm:w-80 sm:h-80 md:w-96 md:h-96 rounded-lg overflow-hidden border border-cyan-800">
					{#each ranks as rank}
						{#each files as file, fileIdx}
							{@const coord = file + rank}
							{@const piece = initialPieces[coord]}
							{@const isDark = isDarkSquare(fileIdx, rank)}
							<div
								class="relative flex items-center justify-center font-serif text-lg sm:text-2xl transition-colors {isDark ? 'bg-cyan-950/80 text-cyan-100' : 'bg-cyan-600/30 text-cyan-200'}"
								title="{coord.toUpperCase()}"
							>
								<!-- Coordenadas en las esquinas de los bordes -->
								{#if file === 'a'}
									<span class="absolute top-0.5 left-1 text-[8px] font-mono opacity-50">{rank}</span>
								{/if}
								{#if rank === 1}
									<span class="absolute bottom-0.5 right-1 text-[8px] font-mono opacity-50 uppercase">{file}</span>
								{/if}

								<!-- Pieza de ajedrez -->
								{#if piece}
									<span class="drop-shadow-[0_2px_4px_rgba(0,0,0,0.8)] filter transition-transform hover:scale-110 cursor-default">
										{piece}
									</span>
								{/if}
							</div>
						{/each}
					{/each}
				</div>
			</div>
		</div>

		<!-- Tarjeta de competidor(es) registrado(s) -->
		<div class="relative z-10 w-full max-w-md bg-slate-900/80 rounded-xl p-3 border border-cyan-900/60 backdrop-blur-md">
			<div class="flex items-center justify-between mb-2">
				<span class="text-xs font-bold text-cyan-300 uppercase tracking-wider flex items-center gap-1.5">
					<span>♟️</span> {players.length === 0 ? 'Sin ajedrecista registrado' : 'Competidor Habilitado'}
				</span>
				<span class="text-[11px] text-slate-400 font-mono">
					{players.length}/1 titular
				</span>
			</div>

			{#if players.length === 0}
				<div class="text-center py-3 text-slate-400 text-xs">
					{#if interactive && onAddPlayer}
						<button
							type="button"
							onclick={() => onAddPlayer('chess_player')}
							class="text-cyan-400 hover:text-cyan-300 font-semibold underline underline-offset-2"
						>
							Haz clic aquí para agregar al jugador de ajedrez
						</button>
					{:else}
						No hay jugador inscrito para este tablero.
					{/if}
				</div>
			{:else}
				<div class="flex flex-col gap-2">
					{#each players as p, idx}
						<div class="flex items-center justify-between p-2 rounded-lg bg-cyan-950/40 border border-cyan-800/40 text-xs">
							<div class="flex items-center gap-2.5">
								<span class="text-lg">♟️</span>
								<div>
									<div class="font-bold text-white flex items-center gap-1.5">
										{p.first_name} {p.last_name}
										{#if idx === 0}
											<span class="text-[9px] px-1.5 py-0.2 rounded bg-cyan-500/20 text-cyan-300 font-mono">Titular</span>
										{:else}
											<span class="text-[9px] px-1.5 py-0.2 rounded bg-slate-700 text-slate-300 font-mono">Suplente</span>
										{/if}
									</div>
									<div class="text-[11px] text-slate-400 font-mono">
										DNI: {p.dni} &bull; {p.nationality || 'Perú'}
									</div>
								</div>
							</div>

							{#if interactive && onRemovePlayer}
								<button
									type="button"
									onclick={() => onRemovePlayer(p)}
									class="text-red-400 hover:text-red-300 p-1 rounded hover:bg-red-500/10 transition"
									title="Retirar jugador"
								>
									✕
								</button>
							{/if}
						</div>
					{/each}
				</div>
			{/if}
		</div>
	</div>
</div>
