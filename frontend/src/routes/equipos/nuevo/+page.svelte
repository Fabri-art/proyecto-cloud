<script>
	/**
	 * routes/equipos/nuevo/+page.svelte — Formulario de Registro de Club y Plantilla (NOM-11)
	 *
	 * Características:
	 * 1. Formulario del Club: Nombre, sigla, delegado, teléfono, ciudad, país.
	 * 2. Tabla dinámica de jugadores: agregar en vivo con nombre, apellido, DNI, dorsal y posición.
	 * 3. Validación local: impide duplicados de DNI o dorsales en la lista antes de enviar.
	 * 4. Envío secuencial: crea el equipo en POST /api/v1/teams y luego registra a los jugadores en POST /api/v1/teams/{id}/players.
	 */
	import { goto } from '$app/navigation';
	import { teamsApi } from '$lib/api/client';
	import { toast } from '$lib/stores/toast';
	import { auth } from '$lib/stores/auth';
	import AdminPinModal from '$lib/components/AdminPinModal.svelte';
	import { onDestroy } from 'svelte';

	let isAdmin = $state(false);
	let showPinModal = $state(false);
	const unsub = auth.subscribe((val) => {
		isAdmin = val;
		if (!val) showPinModal = true;
	});
	onDestroy(unsub);

	const TOURNAMENT_ID = 1;

	// ── Estado del Club ────────────────────────────────────────────────────────
	let teamData = $state({
		name: '',
		short_name: '',
		delegate_name: '',
		delegate_phone: '',
		city: '',
		country: ''
	});

	// ── Estado para nuevo jugador en borrador ──────────────────────────────────
	let newPlayer = $state({
		first_name: '',
		last_name: '',
		dni: '',
		shirt_number: '',
		position: 'midfielder'
	});

	// ── Lista dinámica de jugadores en plantilla ──────────────────────────────
	let players = $state([]);
	let isSubmitting = $state(false);

	// Posiciones disponibles con etiquetas amigables
	const positions = [
		{ value: 'goalkeeper', label: 'Arquero / Portero', icon: '🧤' },
		{ value: 'defender',   label: 'Defensa',           icon: '🛡️' },
		{ value: 'midfielder', label: 'Mediocampista',     icon: '⚙️' },
		{ value: 'forward',    label: 'Delantero',         icon: '⚽' }
	];

	// ── Validación y adición de jugador a la lista local ─────────────────────
	function handleAddPlayer(e) {
		e.preventDefault();

		const first_name = newPlayer.first_name.trim();
		const last_name = newPlayer.last_name.trim();
		const dni = newPlayer.dni.trim().toUpperCase();
		const shirt_number = newPlayer.shirt_number ? parseInt(newPlayer.shirt_number, 10) : null;
		const position = newPlayer.position;

		// Validaciones obligatorias de jugador
		if (!first_name || !last_name) {
			toast.error('Nombre y apellido del jugador son requeridos.');
			return;
		}

		if (!dni) {
			toast.error('El DNI o documento del jugador es obligatorio.');
			return;
		}

		// Validar DNI único en la lista en memoria
		const dniExists = players.some((p) => p.dni.toUpperCase() === dni);
		if (dniExists) {
			toast.error(`El DNI '${dni}' ya está registrado en la plantilla actual.`);
			return;
		}

		// Validar dorsal único en la lista (si se especificó)
		if (shirt_number !== null) {
			if (shirt_number < 1 || shirt_number > 99) {
				toast.error('El número de dorsal debe estar entre 1 y 99.');
				return;
			}
			const numberExists = players.some((p) => p.shirt_number === shirt_number);
			if (numberExists) {
				toast.error(`El dorsal #${shirt_number} ya fue asignado a otro jugador.`);
				return;
			}
		}

		// Agregar a la lista
		players = [
			...players,
			{
				first_name,
				last_name,
				dni,
				shirt_number,
				position
			}
		];

		// Limpiar campos del jugador
		newPlayer.first_name = '';
		newPlayer.last_name = '';
		newPlayer.dni = '';
		newPlayer.shirt_number = '';
		newPlayer.position = 'midfielder';

		toast.success(`Jugador ${first_name} ${last_name} agregado a la lista.`);
	}

	// Quitar jugador de la lista
	function removePlayer(index) {
		const removed = players[index];
		players = players.filter((_, i) => i !== index);
		toast.info(`Se quitó a ${removed.first_name} ${removed.last_name}.`);
	}

	// ── Envío final a la API ──────────────────────────────────────────────────
	async function handleSubmit(e) {
		e.preventDefault();

		if (!teamData.name.trim()) {
			toast.error('El nombre del club es obligatorio.');
			return;
		}

		if (!teamData.short_name.trim()) {
			toast.error('La sigla/abreviatura es obligatoria (ej: BOC, RIV).');
			return;
		}

		if (!teamData.delegate_name.trim()) {
			toast.error('El nombre del delegado es obligatorio.');
			return;
		}

		isSubmitting = true;

		try {
			// 1. Crear el Club
			const payload = {
				tournament_id: TOURNAMENT_ID,
				name: teamData.name.trim(),
				short_name: teamData.short_name.trim().toUpperCase(),
				delegate_name: teamData.delegate_name.trim(),
				delegate_phone: teamData.delegate_phone.trim() || null,
				city: teamData.city.trim() || null,
				country: teamData.country.trim() || null
			};

			const createdTeam = await teamsApi.create(payload);

			// 2. Registrar jugadores en el club creado
			let registeredPlayers = 0;
			if (players.length > 0) {
				for (const p of players) {
					await teamsApi.addPlayer(createdTeam.id, {
						first_name: p.first_name,
						last_name: p.last_name,
						dni: p.dni,
						shirt_number: p.shirt_number,
						position: p.position
					});
					registeredPlayers++;
				}
			}

			toast.success(
				`¡Club '${createdTeam.name}' registrado con ${registeredPlayers} jugador(es)! Si el fixture ya fue generado, ve a Mesa de Control y presiona "Regenerar Fixture" para incluir este equipo.`
			);

			// Redirigir a la lista de equipos
			goto('/equipos');
		} catch (err) {
			toast.error(err.message || 'Ocurrió un error al registrar el equipo.');
		} finally {
			isSubmitting = false;
		}
	}
</script>

<!-- Modal de PIN si no es admin -->
{#if showPinModal && !isAdmin}
	<AdminPinModal
		onSuccess={() => { showPinModal = false; }}
		onCancel={() => goto('/publico')}
	/>
{/if}

<svelte:head>
	<title>Registrar Club y Plantilla — Nombre-Creativo</title>
</svelte:head>

<div class="max-w-4xl mx-auto animate-fade-in-up pb-12">
	<!-- Encabezado con navegación de retorno -->
	<div class="flex items-center gap-3 mb-6">
		<a
			href="/equipos"
			class="px-3 py-1.5 rounded-lg text-sm text-slate-400 hover:text-white bg-slate-800/60 hover:bg-slate-800 transition"
		>
			← Volver a Equipos
		</a>
	</div>

	<div class="mb-8">
		<h1 class="text-3xl font-black text-white flex items-center gap-3">
			📝 Registro de Club y Plantilla
		</h1>
		<p class="text-slate-400 mt-1">
			Ingresa la información oficial del equipo y agrega los jugadores habilitados.
		</p>
	</div>

	<form onsubmit={handleSubmit} class="flex flex-col gap-8">
		<!-- ── SECCIÓN 1: DATOS DEL CLUB ──────────────────────────────────────── -->
		<div class="glass-card p-6 md:p-8 flex flex-col gap-5">
			<div class="flex items-center gap-2 border-b pb-3" style="border-color: var(--border-color);">
				<span class="text-2xl">🛡️</span>
				<h2 class="text-xl font-bold text-white">Información del Club</h2>
			</div>

			<div class="grid grid-cols-1 md:grid-cols-2 gap-5">
				<!-- Nombre del Club -->
				<div>
					<label for="team-name" class="block text-sm font-semibold text-slate-300 mb-1.5">
						Nombre del Club <span class="text-emerald-400">*</span>
					</label>
					<input
						id="team-name"
						type="text"
						bind:value={teamData.name}
						placeholder="Ej. Deportivo Los Tigres"
						required
						class="w-full px-4 py-2.5 rounded-lg bg-slate-900/80 border border-slate-700 text-white placeholder-slate-500 focus:outline-none focus:border-emerald-500 transition"
					/>
				</div>

				<!-- Abreviatura -->
				<div>
					<label for="team-short-name" class="block text-sm font-semibold text-slate-300 mb-1.5">
						Sigla / Abreviatura <span class="text-emerald-400">*</span>
					</label>
					<input
						id="team-short-name"
						type="text"
						maxlength="5"
						bind:value={teamData.short_name}
						placeholder="Ej. TIG (máx. 5 letras)"
						required
						class="w-full px-4 py-2.5 rounded-lg bg-slate-900/80 border border-slate-700 text-white placeholder-slate-500 uppercase focus:outline-none focus:border-emerald-500 transition"
					/>
				</div>

				<!-- Delegado -->
				<div>
					<label for="delegate-name" class="block text-sm font-semibold text-slate-300 mb-1.5">
						Nombre del Delegado Responsable <span class="text-emerald-400">*</span>
					</label>
					<input
						id="delegate-name"
						type="text"
						bind:value={teamData.delegate_name}
						placeholder="Ej. Juan Pérez"
						required
						class="w-full px-4 py-2.5 rounded-lg bg-slate-900/80 border border-slate-700 text-white placeholder-slate-500 focus:outline-none focus:border-emerald-500 transition"
					/>
				</div>

				<!-- Teléfono -->
				<div>
					<label for="delegate-phone" class="block text-sm font-semibold text-slate-300 mb-1.5">
						Teléfono de Contacto
					</label>
					<input
						id="delegate-phone"
						type="tel"
						bind:value={teamData.delegate_phone}
						placeholder="Ej. +51 987 654 321"
						class="w-full px-4 py-2.5 rounded-lg bg-slate-900/80 border border-slate-700 text-white placeholder-slate-500 focus:outline-none focus:border-emerald-500 transition"
					/>
				</div>

				<!-- Ciudad -->
				<div>
					<label for="team-city" class="block text-sm font-semibold text-slate-300 mb-1.5">
						Ciudad
					</label>
					<input
						id="team-city"
						type="text"
						bind:value={teamData.city}
						placeholder="Ej. Lima"
						class="w-full px-4 py-2.5 rounded-lg bg-slate-900/80 border border-slate-700 text-white placeholder-slate-500 focus:outline-none focus:border-emerald-500 transition"
					/>
				</div>

				<!-- País -->
				<div>
					<label for="team-country" class="block text-sm font-semibold text-slate-300 mb-1.5">
						País
					</label>
					<input
						id="team-country"
						type="text"
						bind:value={teamData.country}
						placeholder="Ej. Perú"
						class="w-full px-4 py-2.5 rounded-lg bg-slate-900/80 border border-slate-700 text-white placeholder-slate-500 focus:outline-none focus:border-emerald-500 transition"
					/>
				</div>
			</div>
		</div>

		<!-- ── SECCIÓN 2: CARGA DE PLANTILLA (JUGADORES) ───────────────────────── -->
		<div class="glass-card p-6 md:p-8 flex flex-col gap-6">
			<div class="flex items-center justify-between border-b pb-3" style="border-color: var(--border-color);">
				<div class="flex items-center gap-2">
					<span class="text-2xl">👥</span>
					<h2 class="text-xl font-bold text-white">Plantilla de Jugadores</h2>
				</div>
				<span class="text-xs px-2.5 py-1 rounded-full bg-emerald-500/20 text-emerald-300 font-semibold">
					{players.length} {players.length === 1 ? 'jugador' : 'jugadores'} en lista
				</span>
			</div>

			<!-- Mini formulario para añadir jugador a la lista -->
			<div class="bg-slate-900/60 p-4 rounded-xl border border-slate-800">
				<h3 class="text-sm font-bold text-slate-300 mb-3 flex items-center gap-2">
					<span>➕</span> Añadir Jugador a la Plantilla
				</h3>

				<div class="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-5 gap-3">
					<!-- Nombre -->
					<div>
						<label for="p-firstname" class="block text-xs text-slate-400 mb-1">Nombre *</label>
						<input
							id="p-firstname"
							type="text"
							bind:value={newPlayer.first_name}
							placeholder="Carlos"
							class="w-full px-3 py-2 text-sm rounded bg-slate-950 border border-slate-700 text-white focus:outline-none focus:border-emerald-500"
						/>
					</div>

					<!-- Apellido -->
					<div>
						<label for="p-lastname" class="block text-xs text-slate-400 mb-1">Apellido *</label>
						<input
							id="p-lastname"
							type="text"
							bind:value={newPlayer.last_name}
							placeholder="Gómez"
							class="w-full px-3 py-2 text-sm rounded bg-slate-950 border border-slate-700 text-white focus:outline-none focus:border-emerald-500"
						/>
					</div>

					<!-- DNI -->
					<div>
						<label for="p-dni" class="block text-xs text-slate-400 mb-1">DNI / Doc *</label>
						<input
							id="p-dni"
							type="text"
							bind:value={newPlayer.dni}
							placeholder="74859612"
							class="w-full px-3 py-2 text-sm rounded bg-slate-950 border border-slate-700 text-white focus:outline-none focus:border-emerald-500 uppercase"
						/>
					</div>

					<!-- Dorsal -->
					<div>
						<label for="p-shirt" class="block text-xs text-slate-400 mb-1">Dorsal (1-99)</label>
						<input
							id="p-shirt"
							type="number"
							min="1"
							max="99"
							bind:value={newPlayer.shirt_number}
							placeholder="10"
							class="w-full px-3 py-2 text-sm rounded bg-slate-950 border border-slate-700 text-white focus:outline-none focus:border-emerald-500"
						/>
					</div>

					<!-- Posición -->
					<div>
						<label for="p-position" class="block text-xs text-slate-400 mb-1">Posición</label>
						<select
							id="p-position"
							bind:value={newPlayer.position}
							class="w-full px-3 py-2 text-sm rounded bg-slate-950 border border-slate-700 text-white focus:outline-none focus:border-emerald-500"
						>
							{#each positions as pos}
								<option value={pos.value}>{pos.icon} {pos.label}</option>
							{/each}
						</select>
					</div>
				</div>

				<div class="mt-3 flex justify-end">
					<button
						type="button"
						onclick={handleAddPlayer}
						class="px-4 py-2 text-sm font-semibold rounded-lg bg-emerald-600 hover:bg-emerald-500 text-white transition flex items-center gap-1.5 shadow-md shadow-emerald-950"
					>
						<span>➕</span> Agregar a la lista
					</button>
				</div>
			</div>

			<!-- Tabla de jugadores agregados -->
			{#if players.length === 0}
				<div class="p-8 text-center text-slate-500 border border-dashed border-slate-800 rounded-xl">
					<p class="text-sm">Aún no has agregado jugadores a la lista.</p>
					<p class="text-xs text-slate-600 mt-1">Completa los campos arriba y haz clic en "Agregar a la lista".</p>
				</div>
			{:else}
				<div class="overflow-x-auto rounded-xl border border-slate-800">
					<table class="w-full text-sm">
						<thead class="bg-slate-900/90 text-xs text-slate-400 uppercase tracking-wider">
							<tr>
								<th class="px-4 py-3 text-center w-12">#</th>
								<th class="px-4 py-3 text-left">Jugador</th>
								<th class="px-4 py-3 text-left">DNI</th>
								<th class="px-4 py-3 text-left">Posición</th>
								<th class="px-4 py-3 text-center w-16">Acción</th>
							</tr>
						</thead>
						<tbody class="divide-y divide-slate-800">
							{#each players as p, idx}
								<tr class="hover:bg-slate-800/40 transition">
									<!-- Dorsal -->
									<td class="px-4 py-3 text-center">
										{#if p.shirt_number}
											<span class="inline-block px-2 py-0.5 rounded bg-slate-800 font-mono font-bold text-emerald-400 text-xs">
												{p.shirt_number}
											</span>
										{:else}
											<span class="text-slate-600">-</span>
										{/if}
									</td>

									<!-- Nombre completo -->
									<td class="px-4 py-3 font-semibold text-white">
										{p.first_name} {p.last_name}
									</td>

									<!-- DNI -->
									<td class="px-4 py-3 font-mono text-slate-300">
										{p.dni}
									</td>

									<!-- Posición -->
									<td class="px-4 py-3 text-slate-300 text-xs">
										{positions.find((pos) => pos.value === p.position)?.icon}
										{positions.find((pos) => pos.value === p.position)?.label}
									</td>

									<!-- Quitar de la lista -->
									<td class="px-4 py-3 text-center">
										<button
											type="button"
											onclick={() => removePlayer(idx)}
											class="text-red-400 hover:text-red-300 p-1 rounded hover:bg-red-500/10 transition"
											title="Eliminar de la lista"
										>
											🗑️
										</button>
									</td>
								</tr>
							{/each}
						</tbody>
					</table>
				</div>
			{/if}
		</div>

		<!-- ── BOTÓN DE GUARDADO FINAL ─────────────────────────────────────────── -->
		<div class="flex items-center justify-end gap-4 pt-2">
			<a
				href="/equipos"
				class="px-5 py-2.5 rounded-lg text-sm font-semibold text-slate-400 hover:text-white transition"
			>
				Cancelar
			</a>

			<button
				type="submit"
				disabled={isSubmitting}
				class="px-6 py-3 rounded-lg font-bold text-white shadow-lg transition flex items-center gap-2 {isSubmitting
					? 'bg-slate-700 cursor-not-allowed'
					: 'bg-emerald-600 hover:bg-emerald-500 shadow-emerald-950'}"
			>
				{#if isSubmitting}
					<span class="w-4 h-4 border-2 border-white border-t-transparent rounded-full animate-spin"></span>
					<span>Guardando club y plantilla...</span>
				{:else}
					<span>💾 Registrar Club y Plantilla</span>
				{/if}
			</button>
		</div>
	</form>
</div>
