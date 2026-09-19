<script>
	/**
	 * routes/equipos/nuevo/+page.svelte — Registro de Club y Carga de Plantilla
	 * Incluye modo formulario clásico y modo Cancha Táctica Interactiva para ubicar jugadores.
	 * Regla: Mínimo 5 jugadores, sin límite máximo de jugadores, pero MÁXIMO 1 ARQUERO por equipo.
	 */
	import { onMount, onDestroy } from 'svelte';
	import { goto } from '$app/navigation';
	import { teamsApi, tournamentsApi } from '$lib/api/client';
	import { toast } from '$lib/stores/toast';
	import { auth } from '$lib/stores/auth';
	import AdminPinModal from '$lib/components/AdminPinModal.svelte';
	import SoccerPitch from '$lib/components/SoccerPitch.svelte';

	const TOURNAMENT_ID = 1;
	const MIN_PLAYERS = 5;

	// Control de acceso de administrador
	let isAdmin = $state(auth.isAdmin);
	let showPinModal = $state(!auth.isAdmin);

	const unsub = auth.subscribe((val) => {
		isAdmin = val;
		if (!val) showPinModal = true;
	});
	onDestroy(unsub);

	/** Lista de equipos ya registrados en el torneo para validar duplicados en vivo */
	let existingTeams = $state([]);
	let tournament = $state(null);

	onMount(async () => {
		try {
			tournament = await tournamentsApi.get(TOURNAMENT_ID).catch(() => null);
			existingTeams = await teamsApi.list(TOURNAMENT_ID, true);
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

	// Errores de validación a nivel de club
	let errors = $state({
		name: '',
		short_name: '',
		delegate_name: '',
		delegate_phone: '',
		players_count: ''
	});

	// ── Jugador temporal para el formulario ──────────────────────────────────
	let newPlayer = $state({
		first_name: '',
		last_name: '',
		dni: '',
		shirt_number: '',
		position: 'forward'
	});

	let playerErrors = $state({
		first_name: '',
		last_name: '',
		dni: '',
		shirt_number: ''
	});

	// ── Lista dinámica de jugadores en plantilla ──────────────────────────────
	let players = $state([]);
	let isSubmitting = $state(false);
	let editorView = $state('pitch'); // 'pitch' | 'classic'
	let showQuickAddModal = $state(false);
	let quickPosition = $state('forward');

	// Indicador reactivo si ya hay un arquero registrado
	let hasGoalkeeper = $derived(players.some((p) => (p.position ?? '').toLowerCase() === 'goalkeeper'));

	function openQuickAdd(position) {
		if (position === 'goalkeeper' && hasGoalkeeper) {
			toast.warning('El equipo ya tiene 1 arquero asignado. Solo se permite un arquero.');
			return;
		}
		quickPosition = position || 'forward';
		newPlayer.position = quickPosition;
		playerErrors = { first_name: '', last_name: '', dni: '', shirt_number: '' };
		showQuickAddModal = true;
	}

	function closeQuickAdd() {
		showQuickAddModal = false;
		playerErrors = { first_name: '', last_name: '', dni: '', shirt_number: '' };
	}

	function handleRemovePlayerFromPitch(player) {
		const idx = players.findIndex((p) => p.dni === player.dni || (p.shirt_number === player.shirt_number && p.first_name === player.first_name));
		if (idx !== -1) {
			removePlayer(idx);
		}
	}

	// Posiciones disponibles con etiquetas amigables
	const footballPositions = [
		{ value: 'goalkeeper', label: 'Arquero / Portero', icon: '🧤' },
		{ value: 'defender',   label: 'Defensa',           icon: '🛡️' },
		{ value: 'midfielder', label: 'Mediocampista',     icon: '⚙️' },
		{ value: 'forward',    label: 'Delantero',         icon: '⚽' }
	];
	const basketballPositions = [
		{ value: 'point_guard',    label: 'Base',          icon: '🏀' },
		{ value: 'shooting_guard', label: 'Escolta',       icon: '🎯' },
		{ value: 'small_forward',  label: 'Alero',         icon: '🏃' },
		{ value: 'power_forward',  label: 'Ala-Pívot',     icon: '💪' },
		{ value: 'center',         label: 'Pívot',         icon: '🛡️' }
	];
	
	let positions = $derived(tournament?.sport === 'basketball' ? basketballPositions : footballPositions);

	// ── Helpers de validación ─────────────────────────────────────────────────

	function validatePhone(phone) {
		if (!phone || !phone.trim()) return 'El teléfono de contacto es obligatorio.';
		const digits = phone.replace(/[^\d]/g, '');
		if (digits.length < 9) return 'El teléfono debe tener al menos 9 dígitos.';
		if (!/^\+?[\d\s\-(). ]{9,30}$/.test(phone.trim()))
			return 'Formato inválido. Usa dígitos, espacios, guiones o paréntesis (mín. 9 dígitos).';
		return '';
	}

	function validateTeamName(name) {
		if (!name || !name.trim()) return 'El nombre del club es obligatorio.';
		if (name.trim().length < 2) return 'El nombre debe tener al menos 2 caracteres.';
		if (name.trim().length > 60) return 'El nombre no puede exceder 60 caracteres.';
		return '';
	}

	function validatePlayerName(name, fieldName) {
		if (!name || !name.trim()) return `El ${fieldName} es obligatorio.`;
		if (name.trim().length < 2) return `El ${fieldName} debe tener al menos 2 caracteres.`;
		if (name.trim().length > 40) return `El ${fieldName} no puede superar 40 caracteres.`;
		return '';
	}

	function validateShortName(v) {
		const s = (v || '').trim().toUpperCase();
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
		const d = (v || '').trim();
		if (!d) return 'El DNI es obligatorio.';
		if (!/^\d{8}$/.test(d)) return 'El DNI debe tener obligatoriamente 8 dígitos numéricos.';
		
		// Validar contra jugadores ya registrados en el backend
		const dniExistsInBackend = existingTeams.some(
			(team) => team.players && team.players.some((p) => p.dni === d)
		);
		if (dniExistsInBackend) {
			return `El DNI '${d}' ya se encuentra registrado en otro equipo del torneo.`;
		}
		
		return '';
	}

	// ── Auto-uppercase y validaciones en tiempo real para club ───────────────
	function handleNameInput(e) {
		teamData.name = e ? e.target.value : teamData.name;
		errors.name = validateTeamName(teamData.name);
		if (!teamData.short_name || teamData.short_name.length <= 3) {
			const words = teamData.name.trim().split(/\s+/).filter(Boolean);
			if (words.length >= 3) {
				teamData.short_name = words.slice(0, 3).map((w) => w[0]).join('').toUpperCase();
			} else if (words.length === 2) {
				teamData.short_name = (words[0].slice(0, 2) + words[1][0]).toUpperCase();
			} else if (words.length === 1 && words[0].length >= 3) {
				teamData.short_name = words[0].slice(0, 3).toUpperCase();
			}
		}
	}

	function handleShortNameInput(e) {
		teamData.short_name = e.target.value.toUpperCase().replace(/[^A-Z0-9]/g, '');
		if (errors.short_name) errors.short_name = validateShortName(teamData.short_name);
	}

	// ── Agregar jugador a la lista local ──────────────────────────────────────
	function handleAddPlayer() {
		playerErrors = { first_name: '', last_name: '', dni: '', shirt_number: '' };
		let hasError = false;

		// Validación de arquero único
		if (newPlayer.position === 'goalkeeper' && hasGoalkeeper) {
			toast.error('Solo se permite registrar 1 arquero por equipo.');
			hasError = true;
			return false;
		}

		const fnErr = validatePlayerName(newPlayer.first_name, 'nombre');
		if (fnErr) { playerErrors.first_name = fnErr; hasError = true; }

		const lnErr = validatePlayerName(newPlayer.last_name, 'apellido');
		if (lnErr) { playerErrors.last_name = lnErr; hasError = true; }

		const dniErr = validateDni(newPlayer.dni);
		if (dniErr) {
			playerErrors.dni = dniErr;
			hasError = true;
		} else {
			const cleanDni = newPlayer.dni.trim();
			const exists = players.some((p) => p.dni === cleanDni);
			if (exists) {
				playerErrors.dni = 'Ya existe un jugador con este DNI en la lista.';
				hasError = true;
			}
		}

		const first_name = newPlayer.first_name.trim();
		const last_name = newPlayer.last_name.trim();
		const dni = newPlayer.dni.trim();
		const position = newPlayer.position;
		let shirt_number = null;

		if (newPlayer.shirt_number !== '' && newPlayer.shirt_number !== null && newPlayer.shirt_number !== undefined) {
			const num = parseInt(newPlayer.shirt_number, 10);
			if (isNaN(num) || num < 0 || num > 99) {
				playerErrors.shirt_number = 'El dorsal debe ser un número entero entre 0 y 99.';
				hasError = true;
			} else {
				const numberExists = players.some((p) => p.shirt_number === num);
				if (numberExists) {
					playerErrors.shirt_number = `El dorsal #${num} ya está asignado.`;
					hasError = true;
				} else {
					shirt_number = num;
				}
			}
		}

		if (hasError) return false;

		// Agregar a la lista
		players = [
			...players,
			{ first_name, last_name, dni, shirt_number, position }
		];

		// Limpiar campos del jugador (si ya hay arquero, default a delantera o mediocampo)
		newPlayer.first_name = '';
		newPlayer.last_name = '';
		newPlayer.dni = '';
		newPlayer.shirt_number = '';
		newPlayer.position = tournament?.sport === 'basketball' ? 'point_guard' : (position === 'goalkeeper' ? 'forward' : position);

		// Limpiar error de mínimo si ya se alcanzó
		if (players.length >= MIN_PLAYERS) errors.players_count = '';

		toast.success(`Jugador ${first_name} ${last_name} agregado a la plantilla.`);
		return true;
	}

	function handleQuickAddSubmit(e) {
		if (e) e.preventDefault();
		const success = handleAddPlayer();
		if (success) {
			showQuickAddModal = false;
		}
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
			errors.players_count = `Debes agregar al menos ${MIN_PLAYERS} jugadores antes de registrar el club. Actualmente tienes ${players.length}.`;
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
				`¡Club '${createdTeam.name}' registrado con éxito con ${registeredPlayers} jugadores! Si el fixture ya fue generado, ve a Mesa de Control y presiona "Regenerar Fixture" para incluir este equipo.`
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
	<title>Registrar Club y Plantilla — Torneo Hub</title>
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
			📋 Registro de Club y Plantilla
		</h1>
		<p class="text-slate-400 mt-1">
			Ingresa la información oficial del club y configura la plantilla en la cancha interactiva o en el formulario.
		</p>
	</div>

	<form onsubmit={handleSubmit} class="flex flex-col gap-8">
		<!-- ── SECCIÓN 1: DATOS DEL CLUB ─────────────────────────────────────────── -->
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
						<span class="text-xs font-normal text-slate-500">(2-5 caracteres, letras/números)</span>
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
					{/if}
				</div>

				<!-- Delegado Responsable -->
				<div>
					<label for="delegate-name" class="block text-sm font-semibold text-slate-300 mb-1.5">
						Delegado Responsable <span class="text-emerald-400">*</span>
					</label>
					<input
						id="delegate-name"
						type="text"
						bind:value={teamData.delegate_name}
						oninput={() => { if (errors.delegate_name) errors.delegate_name = ''; }}
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

		<!-- ── SECCIÓN 2: CARGA DE PLANTILLA (JUGADORES) ─────────────────────────── -->
		<div class="glass-card p-6 md:p-8 flex flex-col gap-6">
			<!-- Header de sección con controles de vista y contador -->
			<div class="flex flex-col sm:flex-row sm:items-center justify-between gap-4 border-b pb-4" style="border-color: var(--border-color);">
				<div class="flex items-center gap-2">
					<span class="text-2xl">👥</span>
					<div>
						<h2 class="text-xl font-bold text-white">Plantilla de Jugadores</h2>
						<p class="text-xs text-slate-400">Agrega todos los jugadores que desees (mínimo 5 requeridos, máximo 1 arquero).</p>
					</div>
				</div>

				<div class="flex items-center gap-3">
					<!-- Switcher de Vistas: Cancha vs Lista -->
					<div class="flex items-center bg-slate-950 p-1 rounded-xl border border-slate-800">
						<button
							type="button"
							onclick={() => editorView = 'pitch'}
							class="px-3 py-1.5 text-xs font-bold rounded-lg transition flex items-center gap-1.5 {editorView === 'pitch' ? 'bg-emerald-600 text-white shadow' : 'text-slate-400 hover:text-white'}"
						>
							<span>🏟️</span> Cancha Táctica
						</button>
						<button
							type="button"
							onclick={() => editorView = 'classic'}
							class="px-3 py-1.5 text-xs font-bold rounded-lg transition flex items-center gap-1.5 {editorView === 'classic' ? 'bg-emerald-600 text-white shadow' : 'text-slate-400 hover:text-white'}"
						>
							<span>📋</span> Lista Clásica
						</button>
					</div>

					<!-- Contador y barra de progreso -->
					<div class="flex flex-col items-end gap-1">
						<span class="text-xs px-2.5 py-1 rounded-full font-semibold {players.length >= MIN_PLAYERS ? 'bg-emerald-500/20 text-emerald-300' : 'bg-amber-500/15 text-amber-400'}">
							{players.length}/{MIN_PLAYERS} mín.
						</span>
						<div class="w-20 h-1.5 rounded-full bg-slate-700 overflow-hidden">
							<div
								class="h-full rounded-full transition-all duration-300 {players.length >= MIN_PLAYERS ? 'bg-emerald-500' : 'bg-amber-500'}"
								style="width: {Math.min(100, (players.length / MIN_PLAYERS) * 100)}%"
							></div>
						</div>
					</div>
				</div>
			</div>

			<!-- Regla informativa explícita -->
			<div class="flex flex-col sm:flex-row sm:items-center justify-between gap-2 px-4 py-2.5 rounded-xl bg-slate-900/70 border border-slate-800 text-xs text-slate-300">
				<div class="flex items-center gap-2">
					<span class="text-emerald-400 font-bold">💡 Regla del Torneo:</span>
					<span>Puedes registrar <strong>cualquier cantidad de jugadores</strong> (mínimo 5), con <strong>un único arquero</strong> (máximo 1 arquero por equipo).</span>
				</div>
				<div class="flex items-center gap-2 self-end sm:self-auto">
					<span class="px-2 py-0.5 rounded font-mono text-xs {hasGoalkeeper ? 'bg-emerald-950 text-emerald-300 border border-emerald-800/50' : 'bg-amber-950 text-amber-300 border border-amber-800/50'}">
						{hasGoalkeeper ? '🧤 Arquero registrado' : '🧤 Falta arquero'}
					</span>
					<span class="font-mono text-emerald-400 font-bold text-sm shrink-0">
						{players.length} totales
					</span>
				</div>
			</div>

			<!-- VISTA 1: CANCHA TÁCTICA INTERACTIVA -->
			{#if editorView === 'pitch'}
				<div class="flex flex-col gap-4">
					<div class="flex flex-wrap items-center justify-between gap-2 px-1">
						<span class="text-xs text-slate-400">
							Haz clic en los botones <strong>(+)</strong> de cada línea para ubicar jugadores en su posición táctica:
						</span>
						<button
							type="button"
							onclick={() => openQuickAdd('forward')}
							class="px-3 py-1.5 text-xs font-bold rounded-lg bg-emerald-600 hover:bg-emerald-500 text-white transition flex items-center gap-1.5 shadow"
						>
							<span>+</span> Agregar Jugador
						</button>
					</div>

					<!-- Componente de Cancha de Fútbol -->
					<SoccerPitch
						{players}
						interactive={true}
						teamName={teamData.name || 'Nuevo Club'}
						teamColor="#10b981"
						onAddPlayer={(pos) => openQuickAdd(pos)}
						onRemovePlayer={(p) => handleRemovePlayerFromPitch(p)}
					/>

					<!-- Resumen rápido de la plantilla debajo de la cancha -->
					{#if players.length > 0}
						<div class="mt-3 p-4 rounded-xl bg-slate-900/50 border border-slate-800">
							<div class="flex items-center justify-between mb-2">
								<h4 class="text-xs font-bold text-slate-300 uppercase tracking-wider">
									Jugadores en Plantilla ({players.length})
								</h4>
								<span class="text-[11px] text-slate-400">Haz clic en ✕ para retirar a un jugador</span>
							</div>
							<div class="flex flex-wrap gap-2">
								{#each players as p, idx}
									<div class="flex items-center gap-2 px-3 py-1.5 rounded-lg bg-slate-800/80 border border-slate-700 text-xs">
										<span class="font-mono font-black text-emerald-400">
											{p.shirt_number !== null && p.shirt_number !== undefined ? '#' + p.shirt_number : '—'}
										</span>
										<span class="text-white font-medium">{p.first_name} {p.last_name}</span>
										<span class="text-[10px] text-slate-400">
											({positions.find((pos) => pos.value === p.position)?.label || p.position})
										</span>
										<button
											type="button"
											onclick={() => removePlayer(idx)}
											class="text-red-400 hover:text-red-300 ml-1 font-bold transition"
											title="Eliminar jugador"
										>
											✕
										</button>
									</div>
								{/each}
							</div>
						</div>
					{/if}
				</div>
			{:else}
				<!-- VISTA 2: FORMULARIO Y LISTA CLÁSICA -->
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
								oninput={() => {
									newPlayer.dni = newPlayer.dni.replace(/[^0-9]/g, '');
									if (playerErrors.dni) playerErrors.dni = validateDni(newPlayer.dni);
								}}
								placeholder="74859612"
								class="w-full px-3 py-2 text-sm rounded border text-white focus:outline-none transition {playerErrors.dni ? 'bg-red-950/30 border-red-500/60' : 'bg-slate-950 border-slate-700 focus:border-emerald-500'}"
							/>
							{#if playerErrors.dni}<p class="mt-0.5 text-xs text-red-400">{playerErrors.dni}</p>{/if}
						</div>

						<!-- Dorsal -->
						<div>
							<label for="p-shirt" class="block text-xs text-slate-400 mb-1">Dorsal <span class="text-slate-500">(0-99)</span></label>
							<input
								id="p-shirt"
								type="number"
								min="0"
								max="99"
								bind:value={newPlayer.shirt_number}
								placeholder="10"
								class="w-full px-3 py-2 text-sm rounded border text-white focus:outline-none transition {playerErrors.shirt_number ? 'bg-red-950/30 border-red-500/60' : 'bg-slate-950 border-slate-700 focus:border-emerald-500'}"
							/>
							{#if playerErrors.shirt_number}<p class="mt-0.5 text-xs text-red-400">{playerErrors.shirt_number}</p>{/if}
						</div>

						<!-- Posición (con bloqueo si ya hay 1 arquero) -->
						<div>
							<label for="p-position" class="block text-xs text-slate-400 mb-1">Posición</label>
							<select
								id="p-position"
								bind:value={newPlayer.position}
								class="w-full px-3 py-2 text-sm rounded bg-slate-950 border border-slate-700 text-white focus:outline-none focus:border-emerald-500"
							>
								{#each positions as pos}
									{#if pos.value === 'goalkeeper'}
										<option value="goalkeeper" disabled={hasGoalkeeper}>
											{pos.icon} {pos.label} {hasGoalkeeper ? '(Máx. 1 asignado)' : ''}
										</option>
									{:else}
										<option value={pos.value}>{pos.icon} {pos.label}</option>
									{/if}
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

				<!-- Tabla clásica de jugadores agregados -->
				{#if players.length === 0}
					<div class="p-8 text-center text-slate-500 border border-dashed border-slate-800 rounded-xl">
						<p class="text-sm">Aún no has agregado jugadores a la lista.</p>
						<p class="text-xs text-slate-600 mt-1">Completa los campos arriba y haz clic en "Agregar a la lista".</p>
					</div>
				{:else}
					<div class="overflow-x-auto rounded-xl border border-slate-800">
						<table class="w-full text-left border-collapse text-sm">
							<thead>
								<tr class="bg-slate-900/80 border-b border-slate-800 text-slate-400 text-xs uppercase tracking-wider">
									<th class="px-4 py-3 text-center w-12">#</th>
									<th class="px-4 py-3">Nombre Completo</th>
									<th class="px-4 py-3">DNI / Documento</th>
									<th class="px-4 py-3">Posición</th>
									<th class="px-4 py-3 text-center w-16">Acción</th>
								</tr>
							</thead>
							<tbody class="divide-y divide-slate-800/60">
								{#each players as p, idx}
									<tr class="hover:bg-slate-800/40 transition">
										<td class="px-4 py-3 text-center">
											{#if p.shirt_number !== null && p.shirt_number !== undefined && p.shirt_number !== ''}
												<span class="inline-block px-2 py-0.5 rounded bg-slate-800 font-mono font-bold text-emerald-400 text-xs">
													{p.shirt_number}
												</span>
											{:else}
												<span class="text-slate-600">—</span>
											{/if}
										</td>
										<td class="px-4 py-3 font-medium text-white">
											{p.first_name} {p.last_name}
										</td>
										<td class="px-4 py-3 text-slate-400 font-mono text-xs">
											{p.dni}
										</td>
										<td class="px-4 py-3 text-slate-300 text-xs">
											{positions.find((pos) => pos.value === p.position)?.label || p.position}
										</td>
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

<!-- ── MODAL QUICK-ADD DESDE LA CANCHA TÁCTICA ────────────────────────────── -->
{#if showQuickAddModal}
	<div class="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/70 backdrop-blur-sm animate-fade-in">
		<div class="glass-card w-full max-w-md p-6 rounded-2xl border border-slate-700 shadow-2xl flex flex-col gap-5">
			<div class="flex items-center justify-between border-b pb-3 border-slate-800">
				<div class="flex items-center gap-2">
					<span class="text-xl">🏟️</span>
					<h3 class="text-lg font-bold text-white">Ubicar Jugador en la Cancha</h3>
				</div>
				<button
					type="button"
					onclick={closeQuickAdd}
					class="text-slate-400 hover:text-white text-xl leading-none"
				>
					✕
				</button>
			</div>

			<div class="flex flex-col gap-4">
				<!-- Selector de Posición (con deshabilitación de arquero si ya hay 1) -->
				<div>
					<label for="qa-pos" class="block text-xs font-semibold text-slate-300 mb-1">Posición en el campo</label>
					<select
						id="qa-pos"
						bind:value={newPlayer.position}
						class="w-full px-3 py-2 text-sm rounded-lg bg-slate-900 border border-slate-700 text-white focus:outline-none focus:border-emerald-500"
					>
						{#each positions as pos}
							{#if pos.value === 'goalkeeper'}
								<option value="goalkeeper" disabled={hasGoalkeeper}>
									{pos.icon} {pos.label} {hasGoalkeeper ? '(Máx. 1 arquero ya asignado)' : ''}
								</option>
							{:else}
								<option value={pos.value}>{pos.icon} {pos.label}</option>
							{/if}
						{/each}
					</select>
				</div>

				<div class="grid grid-cols-2 gap-3">
					<!-- Nombre -->
					<div>
						<label for="qa-fn" class="block text-xs font-semibold text-slate-300 mb-1">Nombre *</label>
						<input
							id="qa-fn"
							type="text"
							bind:value={newPlayer.first_name}
							placeholder="Ej. Lucas"
							class="w-full px-3 py-2 text-sm rounded-lg bg-slate-900 border text-white focus:outline-none transition {playerErrors.first_name ? 'border-red-500' : 'border-slate-700 focus:border-emerald-500'}"
						/>
						{#if playerErrors.first_name}
							<p class="mt-0.5 text-xs text-red-400">{playerErrors.first_name}</p>
						{/if}
					</div>

					<!-- Apellido -->
					<div>
						<label for="qa-ln" class="block text-xs font-semibold text-slate-300 mb-1">Apellido *</label>
						<input
							id="qa-ln"
							type="text"
							bind:value={newPlayer.last_name}
							placeholder="Ej. Díaz"
							class="w-full px-3 py-2 text-sm rounded-lg bg-slate-900 border text-white focus:outline-none transition {playerErrors.last_name ? 'border-red-500' : 'border-slate-700 focus:border-emerald-500'}"
						/>
						{#if playerErrors.last_name}
							<p class="mt-0.5 text-xs text-red-400">{playerErrors.last_name}</p>
						{/if}
					</div>
				</div>

				<div class="grid grid-cols-2 gap-3">
					<!-- DNI -->
					<div>
						<label for="qa-dni" class="block text-xs font-semibold text-slate-300 mb-1">DNI (8 dígitos) *</label>
						<input
							id="qa-dni"
							type="text"
							maxlength="8"
							bind:value={newPlayer.dni}
							oninput={() => {
								newPlayer.dni = newPlayer.dni.replace(/[^0-9]/g, '');
								if (playerErrors.dni) playerErrors.dni = validateDni(newPlayer.dni);
							}}
							placeholder="71234567"
							class="w-full px-3 py-2 text-sm rounded-lg bg-slate-900 border text-white focus:outline-none transition {playerErrors.dni ? 'border-red-500' : 'border-slate-700 focus:border-emerald-500'}"
						/>
						{#if playerErrors.dni}
							<p class="mt-0.5 text-xs text-red-400">{playerErrors.dni}</p>
						{/if}
					</div>

					<!-- Dorsal -->
					<div>
						<label for="qa-shirt" class="block text-xs font-semibold text-slate-300 mb-1">Dorsal (0-99)</label>
						<input
							id="qa-shirt"
							type="number"
							min="0"
							max="99"
							bind:value={newPlayer.shirt_number}
							placeholder="9"
							class="w-full px-3 py-2 text-sm rounded-lg bg-slate-900 border text-white focus:outline-none transition {playerErrors.shirt_number ? 'border-red-500' : 'border-slate-700 focus:border-emerald-500'}"
						/>
						{#if playerErrors.shirt_number}
							<p class="mt-0.5 text-xs text-red-400">{playerErrors.shirt_number}</p>
						{/if}
					</div>
				</div>
			</div>

			<div class="flex items-center justify-end gap-3 pt-2 border-t border-slate-800">
				<button
					type="button"
					onclick={closeQuickAdd}
					class="px-4 py-2 text-sm rounded-lg text-slate-400 hover:text-white transition"
				>
					Cancelar
				</button>
				<button
					type="button"
					onclick={handleQuickAddSubmit}
					class="px-5 py-2 text-sm font-bold rounded-lg bg-emerald-600 hover:bg-emerald-500 text-white shadow-lg transition flex items-center gap-1.5 cursor-pointer"
				>
					<span>⚽</span> Agregar a la Cancha
				</button>
			</div>
		</div>
	</div>
{/if}
