<script>
	/**
	 * routes/equipos/nuevo/+page.svelte — Formulario de Registro de Club y Plantilla (NOM-11)
	 *
	 * Características:
	 * 1. Formulario del Club: Nombre, sigla, delegado, teléfono, ciudad, país.
	 * 2. Tabla dinámica de jugadores: agregar en vivo con nombre, apellido, DNI, dorsal y posición.
	 * 3. Validación robusta: sigla (2-5 chars, alfanumérico), teléfono (≥7 dígitos), DNI (5-20, alfanumérico).
	 * 4. Mínimo 5 jugadores requeridos antes de habilitar el botón "Registrar Club".
	 * 5. Feedback visual inline: bordes rojos + mensajes de error bajo cada campo.
	 * 6. Envío secuencial: POST /api/v1/teams y luego POST /api/v1/teams/{id}/players.
	 */
	import { goto } from '$app/navigation';
	import { teamsApi } from '$lib/api/client';
	import { toast } from '$lib/stores/toast';
	import { auth } from '$lib/stores/auth';
	import AdminPinModal from '$lib/components/AdminPinModal.svelte';
	import { onDestroy, onMount } from 'svelte';

	let isAdmin = $state(false);
	let showPinModal = $state(false);
	const unsub = auth.subscribe((val) => {
		isAdmin = val;
		if (!val) showPinModal = true;
	});
	onDestroy(unsub);

	const TOURNAMENT_ID = 1;
	/** Mínimo de jugadores exigidos para poder enviar el formulario */
	const MIN_PLAYERS = 5;

	/** Lista de equipos ya registrados en el torneo para validar duplicados en vivo */
	let existingTeams = $state([]);

	onMount(async () => {
		try {
			existingTeams = await teamsApi.list(TOURNAMENT_ID);
		} catch {
			// Si falla la consulta previa, el backend validará en el submit
		}
	});

	// ── Estado del Club ────────────────────────────────────────────────────────
	let teamData = $state({
		name: '',
		short_name: '',
		delegate_name: '',
		delegate_phone: '',
		city: '',
		country: ''
	});

	/** Errores de validación por campo (vacío = sin error) */
	let errors = $state({
		name: '',
		short_name: '',
		delegate_name: '',
		delegate_phone: '',
		players_count: ''
	});

	// ── Estado para nuevo jugador en borrador ──────────────────────────────────
	let newPlayer = $state({
		first_name: '',
		last_name: '',
		dni: '',
		shirt_number: '',
		position: 'midfielder'
	});

	/** Errores de validación del formulario de jugador actual */
	let playerErrors = $state({
		first_name: '',
		last_name: '',
		dni: '',
		shirt_number: ''
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

	// ── Helpers de validación ─────────────────────────────────────────────────

	function validatePhone(phone) {
		if (!phone || !phone.trim()) return 'El teléfono de contacto es obligatorio.';
		const digits = phone.replace(/[^\d]/g, '');
		if (digits.length < 9) return 'El teléfono debe tener al menos 9 dígitos.';
		if (!/^\+?[\d\s\-(). ]{9,30}$/.test(phone.trim()))
			return 'Formato inválido. Usa dígitos, espacios, guiones o paréntesis (mín. 9 dígitos).';
		return '';
	}

	function validateTeamName(v) {
		const n = v.trim();
		if (!n) return 'El nombre del club es obligatorio.';
		if (n.length < 2) return 'El nombre debe tener al menos 2 caracteres.';
		if (n.length > 100) return 'El nombre no puede superar 100 caracteres.';
		if (existingTeams.some((t) => t.name?.trim().toLowerCase() === n.toLowerCase())) {
			return `Ya existe un club registrado con el nombre "${n}" en este torneo.`;
		}
		return '';
	}

	function validateShortName(v) {
		const s = v.trim().toUpperCase();
		if (!s) return 'La sigla es obligatoria.';
		if (s.length < 2) return 'La sigla debe tener al menos 2 caracteres.';
		if (s.length > 5) return 'La sigla no puede superar 5 caracteres.';
		if (!/^[A-Z0-9]+$/.test(s)) return 'Solo letras mayúsculas y números.';
		if (existingTeams.some((t) => t.short_name?.trim().toUpperCase() === s)) {
			return `La sigla "${s}" ya está asignada a otro equipo en este torneo.`;
		}
		return '';
	}

	function validateDni(v) {
		const d = v.trim();
		if (!d) return 'El DNI es obligatorio.';
		if (!/^\d{8}$/.test(d)) return 'El DNI debe tener obligatoriamente 8 dígitos numéricos.';
		return '';
	}

	// ── Auto-uppercase y validaciones en tiempo real para club ───────────────
	function handleNameInput(e) {
		teamData.name = e.target.value;
		errors.name = validateTeamName(teamData.name);
	}

	function handleShortNameInput(e) {
		teamData.short_name = e.target.value.toUpperCase().replace(/[^A-Z0-9]/g, '');
		errors.short_name = validateShortName(teamData.short_name);
	}

	// ── Validación y adición de jugador a la lista local ─────────────────────
	function handleAddPlayer(e) {
		e.preventDefault();

		const first_name = newPlayer.first_name.trim();
		const last_name = newPlayer.last_name.trim();
		const dni = newPlayer.dni.trim();
		const shirt_number =
			newPlayer.shirt_number !== '' && newPlayer.shirt_number !== null && newPlayer.shirt_number !== undefined
				? parseInt(newPlayer.shirt_number, 10)
				: null;
		const position = newPlayer.position;

		// Limpiar errores previos
		playerErrors = { first_name: '', last_name: '', dni: '', shirt_number: '' };
		let hasError = false;

		if (!first_name) {
			playerErrors.first_name = 'El nombre es obligatorio.';
			hasError = true;
		}
		if (!last_name) {
			playerErrors.last_name = 'El apellido es obligatorio.';
			hasError = true;
		}

		const dniError = validateDni(dni);
		if (dniError) {
			playerErrors.dni = dniError;
			hasError = true;
		} else {
			// Validar DNI único en la lista en memoria
			const dniExists = players.some((p) => p.dni === dni);
			if (dniExists) {
				playerErrors.dni = `El DNI '${dni}' ya está en la plantilla.`;
				hasError = true;
			}
		}

		if (shirt_number !== null) {
			if (isNaN(shirt_number) || !Number.isInteger(shirt_number) || shirt_number < 0 || shirt_number > 99) {
				playerErrors.shirt_number = 'El dorsal debe ser un número entero entre 0 y 99.';
				hasError = true;
			} else {
				const numberExists = players.some((p) => p.shirt_number === shirt_number);
				if (numberExists) {
					playerErrors.shirt_number = `El dorsal #${shirt_number} ya está asignado.`;
					hasError = true;
				}
			}
		}

		if (hasError) return;

		// Agregar a la lista
		players = [
			...players,
			{ first_name, last_name, dni, shirt_number, position }
		];

		// Limpiar campos del jugador
		newPlayer.first_name = '';
		newPlayer.last_name = '';
		newPlayer.dni = '';
		newPlayer.shirt_number = '';
		newPlayer.position = 'midfielder';

		// Limpiar error de mínimo si ya se alcanzó
		if (players.length >= MIN_PLAYERS) errors.players_count = '';

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

		// Reiniciar errores
		errors = { name: '', short_name: '', delegate_name: '', delegate_phone: '', players_count: '' };
		let hasError = false;

		const nameError = validateTeamName(teamData.name);
		if (nameError) {
			errors.name = nameError;
			hasError = true;
		}

		const snError = validateShortName(teamData.short_name);
		if (snError) {
			errors.short_name = snError;
			hasError = true;
		}

		if (!teamData.delegate_name.trim()) {
			errors.delegate_name = 'El nombre del delegado es obligatorio.';
			hasError = true;
		}

		const phoneError = validatePhone(teamData.delegate_phone);
		if (phoneError) {
			errors.delegate_phone = phoneError;
			hasError = true;
		}

		if (players.length < MIN_PLAYERS) {
			errors.players_count = `Debes agregar al menos ${MIN_PLAYERS} jugadores antes de registrar el club.`;
			hasError = true;
		}

		if (hasError) return;

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
			const msg = err.message || '';
			if (msg.toLowerCase().includes('nombre')) {
				errors.name = msg;
			} else if (msg.toLowerCase().includes('sigla') || msg.toLowerCase().includes('abreviatura')) {
				errors.short_name = msg;
			}
			toast.error(msg || 'Ocurrió un error al registrar el equipo.');
		} finally {
			isSubmitting = false;
		}
	}

	/** Computed: el botón Registrar se deshabilita si faltan jugadores o está enviando */
	let canSubmit = $derived(players.length >= MIN_PLAYERS && !isSubmitting);
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
						oninput={handleNameInput}
						placeholder="Ej. Deportivo Los Tigres"
						required
						class="w-full px-4 py-2.5 rounded-lg bg-slate-900/80 border text-white placeholder-slate-500 focus:outline-none transition {errors.name ? 'border-red-500 focus:border-red-400' : 'border-slate-700 focus:border-emerald-500'}"
					/>
					{#if errors.name}
						<p class="mt-1 text-xs text-red-400">{errors.name}</p>
					{/if}
				</div>

				<!-- Abreviatura -->
				<div>
					<label for="team-short-name" class="block text-sm font-semibold text-slate-300 mb-1.5">
						Sigla / Abreviatura <span class="text-emerald-400">*</span>
						<span class="text-xs font-normal text-slate-500">(2-5 caracteres, solo letras/números)</span>
					</label>
					<input
						id="team-short-name"
						type="text"
						maxlength="5"
						bind:value={teamData.short_name}
						oninput={handleShortNameInput}
						placeholder="Ej. TIG"
						required
						class="w-full px-4 py-2.5 rounded-lg bg-slate-900/80 border text-white placeholder-slate-500 uppercase font-mono font-bold tracking-widest focus:outline-none transition {errors.short_name ? 'border-red-500 focus:border-red-400' : 'border-slate-700 focus:border-emerald-500'}"
					/>
					{#if errors.short_name}
						<p class="mt-1 text-xs text-red-400">{errors.short_name}</p>
					{:else}
						<p class="mt-1 text-xs text-slate-500">{teamData.short_name.length}/5 caracteres</p>
					{/if}
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
						class="w-full px-4 py-2.5 rounded-lg bg-slate-900/80 border text-white placeholder-slate-500 focus:outline-none transition {errors.delegate_name ? 'border-red-500 focus:border-red-400' : 'border-slate-700 focus:border-emerald-500'}"
					/>
					{#if errors.delegate_name}
						<p class="mt-1 text-xs text-red-400">{errors.delegate_name}</p>
					{/if}
				</div>

				<!-- Teléfono -->
				<div>
					<label for="delegate-phone" class="block text-sm font-semibold text-slate-300 mb-1.5">
						Teléfono de Contacto <span class="text-emerald-400">*</span>
						<span class="text-xs font-normal text-slate-500">(mín. 9 dígitos)</span>
					</label>
					<input
						id="delegate-phone"
						type="tel"
						bind:value={teamData.delegate_phone}
						oninput={() => { errors.delegate_phone = validatePhone(teamData.delegate_phone); }}
						placeholder="Ej. 987654321 o +51 987 654 321"
						required
						class="w-full px-4 py-2.5 rounded-lg bg-slate-900/80 border text-white placeholder-slate-500 focus:outline-none transition {errors.delegate_phone ? 'border-red-500 focus:border-red-400' : 'border-slate-700 focus:border-emerald-500'}"
					/>
					{#if errors.delegate_phone}
						<p class="mt-1 text-xs text-red-400">{errors.delegate_phone}</p>
					{/if}
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
			<!-- Sección de jugadores con contador y barra de progreso -->
			<div class="flex items-center justify-between border-b pb-3" style="border-color: var(--border-color);">
				<div class="flex items-center gap-2">
					<span class="text-2xl">👥</span>
					<h2 class="text-xl font-bold text-white">Plantilla de Jugadores</h2>
				</div>
				<div class="flex flex-col items-end gap-1">
					<span class="text-xs px-2.5 py-1 rounded-full font-semibold {players.length >= MIN_PLAYERS ? 'bg-emerald-500/20 text-emerald-300' : 'bg-amber-500/15 text-amber-400'}">
						{players.length}/{MIN_PLAYERS} mínimo
					</span>
					<!-- Barra de progreso hacia el mínimo -->
					<div class="w-24 h-1.5 rounded-full bg-slate-700 overflow-hidden">
						<div
							class="h-full rounded-full transition-all duration-300 {players.length >= MIN_PLAYERS ? 'bg-emerald-500' : 'bg-amber-500'}"
							style="width: {Math.min(100, (players.length / MIN_PLAYERS) * 100)}%"
						></div>
					</div>
				</div>
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
							class="w-full px-3 py-2 text-sm rounded border text-white focus:outline-none transition {playerErrors.first_name ? 'bg-red-950/30 border-red-500/60' : 'bg-slate-950 border-slate-700 focus:border-emerald-500'}"
						/>
						{#if playerErrors.first_name}<p class="mt-0.5 text-xs text-red-400">{playerErrors.first_name}</p>{/if}
					</div>

					<!-- Apellido -->
					<div>
						<label for="p-lastname" class="block text-xs text-slate-400 mb-1">Apellido *</label>
						<input
							id="p-lastname"
							type="text"
							bind:value={newPlayer.last_name}
							placeholder="Gómez"
							class="w-full px-3 py-2 text-sm rounded border text-white focus:outline-none transition {playerErrors.last_name ? 'bg-red-950/30 border-red-500/60' : 'bg-slate-950 border-slate-700 focus:border-emerald-500'}"
						/>
						{#if playerErrors.last_name}<p class="mt-0.5 text-xs text-red-400">{playerErrors.last_name}</p>{/if}
					</div>

					<!-- DNI -->
					<div>
						<label for="p-dni" class="block text-xs text-slate-400 mb-1">DNI / Doc * <span class="text-slate-500">(8 dígitos)</span></label>
						<input
							id="p-dni"
							type="text"
							maxlength="8"
							bind:value={newPlayer.dni}
							oninput={(e) => {
								newPlayer.dni = e.target.value.replace(/\D/g, '').slice(0, 8);
								if (playerErrors.dni) playerErrors.dni = validateDni(newPlayer.dni);
							}}
							placeholder="74859612"
							class="w-full px-3 py-2 text-sm rounded border text-white focus:outline-none transition {playerErrors.dni ? 'bg-red-950/30 border-red-500/60' : 'bg-slate-950 border-slate-700 focus:border-emerald-500'}"
						/>
						{#if playerErrors.dni}<p class="mt-0.5 text-xs text-red-400">{playerErrors.dni}</p>{/if}
					</div>

					<!-- Dorsal -->
					<div>
						<label for="p-shirt" class="block text-xs text-slate-400 mb-1">Dorsal (0-99)</label>
						<input
							id="p-shirt"
							type="number"
							min="0"
							max="99"
							step="1"
							bind:value={newPlayer.shirt_number}
							placeholder="0"
							class="w-full px-3 py-2 text-sm rounded border text-white focus:outline-none transition {playerErrors.shirt_number ? 'bg-red-950/30 border-red-500/60' : 'bg-slate-950 border-slate-700 focus:border-emerald-500'}"
						/>
						{#if playerErrors.shirt_number}<p class="mt-0.5 text-xs text-red-400">{playerErrors.shirt_number}</p>{/if}
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
										{#if p.shirt_number !== null && p.shirt_number !== undefined && p.shirt_number !== ''}
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
		<div class="flex flex-col gap-3 pt-2">
			<!-- Error de mínimo de jugadores -->
			{#if errors.players_count}
				<div class="flex items-center gap-2.5 p-3 rounded-lg bg-amber-500/10 border border-amber-500/30 text-sm text-amber-300">
					<span>⚠️</span>
					<span>{errors.players_count}</span>
				</div>
			{/if}
			<div class="flex items-center justify-end gap-4">
				<a
					href="/equipos"
					class="px-5 py-2.5 rounded-lg text-sm font-semibold text-slate-400 hover:text-white transition"
				>
					Cancelar
				</a>

				<button
					type="submit"
					disabled={!canSubmit}
					title={players.length < MIN_PLAYERS ? `Faltan ${MIN_PLAYERS - players.length} jugador(es) para poder registrar el club` : ''}
					class="px-6 py-3 rounded-lg font-bold text-white shadow-lg transition flex items-center gap-2 {!canSubmit
						? 'bg-slate-700 cursor-not-allowed opacity-60'
						: 'bg-emerald-600 hover:bg-emerald-500 shadow-emerald-950'}"
				>
					{#if isSubmitting}
						<span class="w-4 h-4 border-2 border-white border-t-transparent rounded-full animate-spin"></span>
						<span>Guardando club y plantilla...</span>
					{:else}
						<span>💾 Registrar Club y Plantilla</span>
						{#if players.length < MIN_PLAYERS}
							<span class="text-xs font-normal opacity-70">({players.length}/{MIN_PLAYERS} jug.)</span>
						{/if}
					{/if}
				</button>
			</div>
		</div>
	</form>
</div>
