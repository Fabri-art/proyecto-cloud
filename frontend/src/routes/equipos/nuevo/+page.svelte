<script>
	/**
	 * routes/equipos/nuevo/+page.svelte â€” Formulario de Registro de Club y Plantilla (NOM-11)
	 *
	 * CaracterÃ­sticas:
	 * 1. Formulario del Club: Nombre, sigla, delegado, telÃ©fono, ciudad, paÃ­s (Selector SudamÃ©rica).
	 * 2. Restricciones estrictas de caracteres:
	 *    - Nombres, delegado, ciudad: Sin nÃºmeros.
	 *    - TelÃ©fono: Sin letras.
	 *    - DNI: Solo 8 nÃºmeros, sin letras.
	 *    - Dorsal: Solo nÃºmeros 0-99.
	 * 3. ValidaciÃ³n de DNI duplicado: En plantilla actual y en todos los equipos del torneo.
	 * 4. Selector de paÃ­ses de SudamÃ©rica tanto para el club como para cada jugador.
	 * 5. Cancha/pista tÃ¡ctica interactiva + Vista formulario clÃ¡sico.
	 */
	import { goto } from '$app/navigation';
	import { teamsApi, tournamentsApi } from '$lib/api/client';
	import { toast } from '$lib/stores/toast';
	import { auth } from '$lib/stores/auth';
	import AdminPinModal from '$lib/components/AdminPinModal.svelte';
	import SoccerPitch from '$lib/components/SoccerPitch.svelte';
	import BasketballCourt from '$lib/components/BasketballCourt.svelte';
	import { onDestroy, onMount } from 'svelte';

	let isAdmin = $state(false);
	let showPinModal = $state(false);
	const unsub = auth.subscribe((val) => {
		isAdmin = val;
		if (!val) showPinModal = true;
	});
	onDestroy(unsub);

	const TOURNAMENT_ID = 1;
	/** MÃ­nimo de jugadores exigidos para poder enviar el formulario */
	const MIN_PLAYERS = 5;

	/** Lista oficial de paÃ­ses de SudamÃ©rica */
	const southAmericanCountries = [
		'Argentina',
		'Bolivia',
		'Brasil',
		'Chile',
		'Colombia',
		'Ecuador',
		'Guyana',
		'Paraguay',
		'PerÃº',
		'Surinam',
		'Uruguay',
		'Venezuela'
	];

	let existingTeams = $state([]);
	let tournament = $state(null);
	let loading = $state(true);

	onMount(async () => {
		try {
			tournament = await tournamentsApi.get(TOURNAMENT_ID).catch(() => null);
			existingTeams = await teamsApi.list(TOURNAMENT_ID, true);
		} catch {
			// Si falla la consulta previa, el backend validarÃ¡ en el submit
		} finally {
			loading = false;
		}
	});

	async function createBaseTournament() {
		try {
			loading = true;
			tournament = await tournamentsApi.create({
				name: 'Torneo Oficial',
				slug: 'torneo-oficial',
				season: new Date().getFullYear().toString(),
				sport: 'football'
			});
			toast.success('Â¡Torneo base creado! Ahora puedes registrar equipos.');
			existingTeams = await teamsApi.list(TOURNAMENT_ID, true).catch(() => []);
		} catch (err) {
			toast.error(err.message || 'Error al crear el torneo.');
		} finally {
			loading = false;
		}
	}

	// â”€â”€ Estado del Club â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€
	let teamData = $state({
		name: '',
		short_name: '',
		sport: 'football',
		delegate_name: '',
		delegate_phone: '',
		city: '',
		country: 'PerÃº'
	});

	/** Errores de validaciÃ³n por campo (vacÃ­o = sin error) */
	let errors = $state({
		name: '',
		short_name: '',
		delegate_name: '',
		delegate_phone: '',
		city: '',
		players_count: ''
	});

	// â”€â”€ Estado para nuevo jugador en borrador â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€
	let newPlayer = $state({
		first_name: '',
		last_name: '',
		dni: '',
		shirt_number: '',
		position: 'midfielder',
		nationality: 'PerÃº'
	});

	/** Errores de validaciÃ³n del formulario de jugador actual */
	let playerErrors = $state({
		first_name: '',
		last_name: '',
		dni: '',
		shirt_number: ''
	});

	// â”€â”€ Lista dinÃ¡mica de jugadores en plantilla â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€
	let players = $state([]);
	let isSubmitting = $state(false);
	let editorView = $state('pitch'); // 'pitch' | 'classic'
	let showQuickAddModal = $state(false);
	let quickPosition = $state('forward');

	// Indicador reactivo: ya hay un arquero (solo para fÃºtbol)
	let hasGoalkeeper = $derived(players.some((p) => p.position === 'goalkeeper'));

	function openQuickAdd(position) {
		// Bloquear segundo arquero en fÃºtbol
		if (teamData.sport !== 'basketball' && teamData.sport !== 'volleyball' && position === 'goalkeeper' && hasGoalkeeper) {
			toast.warning('El equipo ya tiene 1 arquero. Solo se permite un arquero.');
			return;
		}
		quickPosition = position || (teamData.sport === 'basketball' ? 'point_guard' : teamData.sport === 'volleyball' ? 'setter' : 'forward');
		newPlayer.position = quickPosition;
		newPlayer.nationality = teamData.country || 'PerÃº';
		playerErrors = { first_name: '', last_name: '', dni: '', shirt_number: '' };
		showQuickAddModal = true;
	}

	function closeQuickAdd() {
		showQuickAddModal = false;
		playerErrors = { first_name: '', last_name: '', dni: '', shirt_number: '' };
	}

	function handleRemovePlayerFromPitch(player) {
		const idx = players.findIndex(
			(p) => p.dni === player.dni ||
				(p.shirt_number === player.shirt_number && p.first_name === player.first_name)
		);
		if (idx !== -1) removePlayer(idx);
	}

	// Posiciones disponibles con etiquetas amigables
	const footballPositions = [
		{ value: 'goalkeeper', label: 'Arquero / Portero', icon: 'ðŸ§¤' },
		{ value: 'defender',   label: 'Defensa',           icon: 'ðŸ›¡ï¸' },
		{ value: 'midfielder', label: 'Mediocampista',     icon: 'âš¡' },
		{ value: 'forward',    label: 'Delantero',         icon: 'âš½' }
	];
	const basketballPositions = [
		{ value: 'point_guard',    label: 'Base',          icon: 'ðŸ€' },
		{ value: 'shooting_guard', label: 'Escolta',       icon: 'ðŸŽ¯' },
		{ value: 'small_forward',  label: 'Alero',         icon: 'ðŸš€' },
		{ value: 'power_forward',  label: 'Ala-PÃ­vot',     icon: 'ðŸ’ª' },
		{ value: 'center',         label: 'PÃ­vot',         icon: 'ðŸ›¡ï¸' }
	];
	const volleyballPositions = [
		{ value: 'setter',         label: 'Armador',   icon: '🎯' },
		{ value: 'libero',          label: 'Líbero',    icon: '🛡' },
		{ value: 'outside_hitter',  label: 'Punta',     icon: '⚡' },
		{ value: 'opposite',        label: 'Opuesto',   icon: '🏐' },
		{ value: 'middle_blocker',  label: 'Central',   icon: '🧱' }
	];
	
	let positions = $derived(teamData.sport === 'basketball' ? basketballPositions : footballPositions);

	// â”€â”€ Helpers de validaciÃ³n y sanitizaciÃ³n estricta â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€

	function validatePhone(phone) {
		if (!phone || !phone.trim()) return 'El telÃ©fono de contacto es obligatorio.';
		if (/[a-zA-Z]/.test(phone)) return 'El telÃ©fono no puede contener letras.';
		const digits = phone.replace(/[^\d]/g, '');
		if (digits.length < 9) return 'El telÃ©fono debe tener al menos 9 dÃ­gitos.';
		if (!/^\+?[\d\s\-().]{9,30}$/.test(phone.trim())) {
			return 'Formato invÃ¡lido. Usa solo dÃ­gitos y signos (+ - ()).';
		}
		return '';
	}

	function validateTeamName(v) {
		const n = v.trim();
		if (!n) return 'El nombre del club es obligatorio.';
		if (/\d/.test(n)) return 'El nombre del club no puede contener nÃºmeros.';
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
		if (!/^[A-Z0-9]+$/.test(s)) return 'Solo letras mayÃºsculas y nÃºmeros.';
		if (existingTeams.some((t) => t.short_name?.trim().toUpperCase() === s)) {
			return `La sigla "${s}" ya estÃ¡ asignada a otro equipo en este torneo.`;
		}
		return '';
	}

	/**
	 * Valida DNI:
	 * 1. No letras
	 * 2. Exactamente 8 dÃ­gitos
	 * 3. No duplicado en la plantilla actual
	 * 4. No duplicado en otros clubes del torneo
	 */
	function validateDni(v) {
		const d = (v || '').trim();
		if (!d) return 'El DNI es obligatorio.';
		if (/[a-zA-Z]/.test(d)) return 'El DNI no puede contener letras. Solo nÃºmeros.';
		if (!/^\d{8}$/.test(d)) return 'El DNI debe tener obligatoriamente 8 dÃ­gitos numÃ©ricos.';

		// 1. Validar contra la plantilla actual en borrador
		if (players.some((p) => p.dni === d)) {
			return `El DNI '${d}' ya estÃ¡ registrado en la plantilla de este equipo.`;
		}
		
		// 2. Validar contra jugadores ya registrados en otros equipos del torneo
		const conflictTeam = existingTeams.find(
			(team) => team.players && team.players.some((p) => p.dni === d)
		);
		if (conflictTeam) {
			return `El DNI '${d}' ya se encuentra registrado en el equipo "${conflictTeam.name}" del torneo.`;
		}
		
		return '';
	}

	// â”€â”€ Event handlers con sanitizaciÃ³n en tiempo real â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€

	function handleNameInput(e) {
		// Restringir nÃºmeros en tiempo real
		teamData.name = e.target.value.replace(/[0-9]/g, '');
		errors.name = validateTeamName(teamData.name);
	}

	function handleShortNameInput(e) {
		teamData.short_name = e.target.value.toUpperCase().replace(/[^A-Z0-9]/g, '').slice(0, 5);
		errors.short_name = validateShortName(teamData.short_name);
	}

	function handleDelegateNameInput(e) {
		// Restringir nÃºmeros en tiempo real
		teamData.delegate_name = e.target.value.replace(/[0-9]/g, '');
		if (!teamData.delegate_name.trim()) {
			errors.delegate_name = 'El nombre del delegado es obligatorio.';
		} else {
			errors.delegate_name = '';
		}
	}

	function handlePhoneInput(e) {
		// Restringir letras en tiempo real
		teamData.delegate_phone = e.target.value.replace(/[a-zA-Z]/g, '');
		errors.delegate_phone = validatePhone(teamData.delegate_phone);
	}

	function handleCityInput(e) {
		// Restringir nÃºmeros en tiempo real
		teamData.city = e.target.value.replace(/[0-9]/g, '');
	}

	function handlePlayerFirstNameInput(e) {
		newPlayer.first_name = e.target.value.replace(/[0-9]/g, '');
		if (playerErrors.first_name && newPlayer.first_name.trim()) {
			playerErrors.first_name = '';
		}
	}

	function handlePlayerLastNameInput(e) {
		newPlayer.last_name = e.target.value.replace(/[0-9]/g, '');
		if (playerErrors.last_name && newPlayer.last_name.trim()) {
			playerErrors.last_name = '';
		}
	}

	function handlePlayerDniInput(e) {
		// Solo nÃºmeros, max 8 dÃ­gitos
		newPlayer.dni = e.target.value.replace(/\D/g, '').slice(0, 8);
		if (newPlayer.dni.length === 8) {
			playerErrors.dni = validateDni(newPlayer.dni);
		} else if (playerErrors.dni) {
			playerErrors.dni = validateDni(newPlayer.dni);
		}
	}

	function handlePlayerShirtInput(e) {
		// Solo nÃºmeros, max 2 dÃ­gitos
		const clean = e.target.value.replace(/\D/g, '').slice(0, 2);
		newPlayer.shirt_number = clean;
		if (clean !== '') {
			const num = parseInt(clean, 10);
			if (players.some((p) => p.shirt_number === num)) {
				playerErrors.shirt_number = `El dorsal #${num} ya estÃ¡ asignado.`;
			} else {
				playerErrors.shirt_number = '';
			}
		} else {
			playerErrors.shirt_number = '';
		}
	}

	// â”€â”€ Agregar jugador desde la Cancha (Quick Add) â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€
	function handleQuickAddSubmit(e) {
		if (e) e.preventDefault();
		const first_name = newPlayer.first_name.trim();
		const last_name = newPlayer.last_name.trim();
		const dni = newPlayer.dni.trim();
		const shirt_number =
			newPlayer.shirt_number !== '' && newPlayer.shirt_number !== null && newPlayer.shirt_number !== undefined
				? parseInt(newPlayer.shirt_number, 10)
				: null;
		const position = newPlayer.position;
		const nationality = newPlayer.nationality || teamData.country || 'PerÃº';

		playerErrors = { first_name: '', last_name: '', dni: '', shirt_number: '' };
		let hasError = false;

		// Bloquear segundo arquero en fÃºtbol
		if (teamData.sport !== 'basketball' && teamData.sport !== 'volleyball' && position === 'goalkeeper' && hasGoalkeeper) {
			toast.error('Solo se permite registrar 1 arquero por equipo.');
			return;
		}

		if (!first_name) { playerErrors.first_name = 'El nombre es obligatorio.'; hasError = true; }
		if (!last_name) { playerErrors.last_name = 'El apellido es obligatorio.'; hasError = true; }

		const dniError = validateDni(dni);
		if (dniError) {
			playerErrors.dni = dniError;
			toast.error(dniError);
			hasError = true;
		}

		if (shirt_number !== null) {
			if (isNaN(shirt_number) || !Number.isInteger(shirt_number) || shirt_number < 0 || shirt_number > 99) {
				playerErrors.shirt_number = 'El dorsal debe ser entre 0 y 99.';
				hasError = true;
			} else if (players.some((p) => p.shirt_number === shirt_number)) {
				playerErrors.shirt_number = `El dorsal #${shirt_number} ya estÃ¡ asignado.`;
				toast.error(`El dorsal #${shirt_number} ya estÃ¡ asignado.`);
				hasError = true;
			}
		}

		if (hasError) return;

		players = [...players, { first_name, last_name, dni, shirt_number, position, nationality }];
		newPlayer.first_name = '';
		newPlayer.last_name = '';
		newPlayer.dni = '';
		newPlayer.shirt_number = '';
		newPlayer.position = teamData.sport === 'basketball' ? 'point_guard' : teamData.sport === 'volleyball' ? 'setter' : (position === 'goalkeeper' ? 'forward' : position);
		if (players.length >= MIN_PLAYERS) errors.players_count = '';
		toast.success(`Jugador ${first_name} ${last_name} (${nationality}) agregado.`);
		showQuickAddModal = false;
	}

	// â”€â”€ Agregar jugador desde la Vista ClÃ¡sica â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€
	function handleAddPlayer(e) {
		if (e) e.preventDefault();

		const first_name = newPlayer.first_name.trim();
		const last_name = newPlayer.last_name.trim();
		const dni = newPlayer.dni.trim();
		const shirt_number =
			newPlayer.shirt_number !== '' && newPlayer.shirt_number !== null && newPlayer.shirt_number !== undefined
				? parseInt(newPlayer.shirt_number, 10)
				: null;
		const position = newPlayer.position;
		const nationality = newPlayer.nationality || teamData.country || 'PerÃº';

		playerErrors = { first_name: '', last_name: '', dni: '', shirt_number: '' };
		let hasError = false;

		// Bloquear segundo arquero en fÃºtbol
		if (teamData.sport !== 'basketball' && teamData.sport !== 'volleyball' && position === 'goalkeeper' && hasGoalkeeper) {
			toast.error('Solo se permite registrar 1 arquero por equipo.');
			return;
		}

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
			toast.error(dniError);
			hasError = true;
		}

		if (shirt_number !== null) {
			if (isNaN(shirt_number) || !Number.isInteger(shirt_number) || shirt_number < 0 || shirt_number > 99) {
				playerErrors.shirt_number = 'El dorsal debe ser un nÃºmero entero entre 0 y 99.';
				hasError = true;
			} else {
				const numberExists = players.some((p) => p.shirt_number === shirt_number);
				if (numberExists) {
					playerErrors.shirt_number = `El dorsal #${shirt_number} ya estÃ¡ asignado.`;
					toast.error(`El dorsal #${shirt_number} ya estÃ¡ asignado.`);
					hasError = true;
				}
			}
		}

		if (hasError) return;

		players = [
			...players,
			{ first_name, last_name, dni, shirt_number, position, nationality }
		];

		newPlayer.first_name = '';
		newPlayer.last_name = '';
		newPlayer.dni = '';
		newPlayer.shirt_number = '';
		newPlayer.position = teamData.sport === 'basketball' ? 'point_guard' : teamData.sport === 'volleyball' ? 'setter' : 'midfielder';

		if (players.length >= MIN_PLAYERS) errors.players_count = '';
		toast.success(`Jugador ${first_name} ${last_name} (${nationality}) agregado.`);
	}

	function removePlayer(index) {
		const removed = players[index];
		players = players.filter((_, i) => i !== index);
		toast.info(`Se retirÃ³ a ${removed.first_name} ${removed.last_name}.`);
	}

	// â”€â”€ EnvÃ­o final a la API â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€
	async function handleSubmit(e) {
		e.preventDefault();

		errors = { name: '', short_name: '', delegate_name: '', delegate_phone: '', city: '', players_count: '' };
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
		} else if (/\d/.test(teamData.delegate_name)) {
			errors.delegate_name = 'El nombre del delegado no puede contener nÃºmeros.';
			hasError = true;
		}

		const phoneError = validatePhone(teamData.delegate_phone);
		if (phoneError) {
			errors.delegate_phone = phoneError;
			hasError = true;
		}

		if (teamData.city && /\d/.test(teamData.city)) {
			errors.city = 'La ciudad no puede contener nÃºmeros.';
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
				sport: teamData.sport,
				delegate_name: teamData.delegate_name.trim(),
				delegate_phone: teamData.delegate_phone.trim() || null,
				city: teamData.city.trim() || null,
				country: teamData.country.trim() || 'PerÃº'
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
						position: p.position,
						nationality: p.nationality || teamData.country || 'PerÃº'
					});
					registeredPlayers++;
				}
			}

			toast.success(
				`Â¡Club '${createdTeam.name}' registrado con Ã©xito con ${registeredPlayers} jugador(es)!`
			);

			goto('/equipos');
		} catch (err) {
			const msg = err.message || '';
			if (msg.toLowerCase().includes('nombre')) {
				errors.name = msg;
			} else if (msg.toLowerCase().includes('sigla') || msg.toLowerCase().includes('abreviatura')) {
				errors.short_name = msg;
			} else if (msg.toLowerCase().includes('dni')) {
				toast.error(msg);
			}
			toast.error(msg || 'OcurriÃ³ un error al registrar el equipo.');
		} finally {
			isSubmitting = false;
		}
	}

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
	<title>Registrar Club y Plantilla â€” TORNEO HUB</title>
</svelte:head>

<div class="max-w-4xl mx-auto animate-fade-in-up pb-12">
	<!-- Encabezado con navegaciÃ³n de retorno -->
	<div class="flex items-center gap-3 mb-6">
		<a
			href="/equipos"
			class="px-3 py-1.5 rounded-lg text-sm text-slate-400 hover:text-white bg-slate-800/60 hover:bg-slate-800 transition"
		>
			â† Volver a Equipos
		</a>
	</div>

	<div class="mb-8">
		<h1 class="text-3xl font-black text-white flex items-center gap-3">
			ðŸ“ Registro de Club y Plantilla
		</h1>
		<p class="text-slate-400 mt-1">
			Ingresa la informaciÃ³n oficial del equipo y agrega los jugadores habilitados con sus paÃ­ses de SudamÃ©rica.
		</p>
	</div>

	{#if loading}
		<div class="flex flex-col items-center justify-center p-12 glass-card rounded-xl border border-slate-700">
			<span class="w-8 h-8 border-4 border-emerald-500 border-t-transparent rounded-full animate-spin mb-4"></span>
			<p class="text-slate-400 font-medium">Cargando informaciÃ³n del torneo...</p>
		</div>
	{:else if !tournament}
		<!-- EMPTY STATE: No hay torneo creado -->
		<div class="flex flex-col items-center justify-center p-12 glass-card rounded-xl border border-slate-700 text-center animate-fade-in-up">
			<div class="text-6xl mb-4">ðŸ†</div>
			<h2 class="text-2xl font-bold text-white mb-2">AÃºn no existe un Torneo</h2>
			<p class="text-slate-400 max-w-md mx-auto mb-6">
				Para registrar un equipo y su plantilla, primero debes crear la base del torneo. 
				Haz clic abajo para crear un torneo por defecto y comenzar.
			</p>
			<button
				type="button"
				onclick={createBaseTournament}
				class="px-6 py-3 rounded-lg font-bold bg-emerald-600 hover:bg-emerald-500 text-white shadow-lg transition flex items-center gap-2"
			>
				<span>âž•</span> Crear Torneo Inicial
			</button>
		</div>
	{:else}
	<form onsubmit={handleSubmit} class="flex flex-col gap-8">
		<!-- â”€â”€ SECCIÃ“N 1: DATOS DEL CLUB â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€ -->
		<div class="glass-card p-6 md:p-8 flex flex-col gap-5">
			<div class="flex items-center gap-2 border-b pb-3" style="border-color: var(--border-color);">
				<span class="text-2xl">ðŸ›¡ï¸</span>
				<h2 class="text-xl font-bold text-white">InformaciÃ³n del Club</h2>
			</div>

			<div class="grid grid-cols-1 md:grid-cols-2 gap-6">
				<!-- Selector de Deporte -->
				<div class="bg-slate-800/40 p-5 rounded-xl border border-slate-700/50 shadow-inner">
					<h3 class="text-sm font-semibold text-slate-300 mb-4 flex items-center gap-2">
						<span class="text-emerald-400">ðŸ…</span> Disciplina Deportiva
					</h3>
					<div class="flex gap-4">
						<label class="flex items-center gap-2 cursor-pointer">
							<input type="radio" bind:group={teamData.sport} value="football" class="accent-emerald-500" />
							<span class="text-white">âš½ FÃºtbol</span>
						</label>
						<label class="flex items-center gap-2 cursor-pointer">
							<input type="radio" bind:group={teamData.sport} value="basketball" class="accent-orange-500" />
							<span class="text-white">ðŸ€ BÃ¡squet</span>
						</label>
					</div>
				</div>

				<!-- Nombre del Club (RestricciÃ³n: Sin nÃºmeros) -->
				<div class="bg-slate-800/40 p-5 rounded-xl border border-slate-700/50 shadow-inner">
					<label for="team-name" class="block text-sm font-semibold text-slate-300 mb-1.5">
						Nombre del Club <span class="text-emerald-400">*</span>
						<span class="text-xs font-normal text-slate-400">(Solo letras, sin nÃºmeros)</span>
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
						<span class="text-xs font-normal text-slate-500">(2-5 letras o nÃºmeros)</span>
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

				<!-- Delegado (RestricciÃ³n: Sin nÃºmeros) -->
				<div>
					<label for="delegate-name" class="block text-sm font-semibold text-slate-300 mb-1.5">
						Nombre del Delegado Responsable <span class="text-emerald-400">*</span>
						<span class="text-xs font-normal text-slate-400">(Solo letras)</span>
					</label>
					<input
						id="delegate-name"
						type="text"
						bind:value={teamData.delegate_name}
						oninput={handleDelegateNameInput}
						placeholder="Ej. Juan PÃ©rez"
						required
						class="w-full px-4 py-2.5 rounded-lg bg-slate-900/80 border text-white placeholder-slate-500 focus:outline-none transition {errors.delegate_name ? 'border-red-500 focus:border-red-400' : 'border-slate-700 focus:border-emerald-500'}"
					/>
					{#if errors.delegate_name}
						<p class="mt-1 text-xs text-red-400">{errors.delegate_name}</p>
					{/if}
				</div>

				<!-- TelÃ©fono (RestricciÃ³n: Sin letras) -->
				<div>
					<label for="delegate-phone" class="block text-sm font-semibold text-slate-300 mb-1.5">
						TelÃ©fono de Contacto <span class="text-emerald-400">*</span>
						<span class="text-xs font-normal text-slate-400">(Solo nÃºmeros, mÃ­n. 9 dÃ­gitos)</span>
					</label>
					<input
						id="delegate-phone"
						type="tel"
						bind:value={teamData.delegate_phone}
						oninput={handlePhoneInput}
						placeholder="Ej. 987654321 o +51 987 654 321"
						required
						class="w-full px-4 py-2.5 rounded-lg bg-slate-900/80 border text-white placeholder-slate-500 focus:outline-none transition {errors.delegate_phone ? 'border-red-500 focus:border-red-400' : 'border-slate-700 focus:border-emerald-500'}"
					/>
					{#if errors.delegate_phone}
						<p class="mt-1 text-xs text-red-400">{errors.delegate_phone}</p>
					{/if}
				</div>

				<!-- Ciudad (RestricciÃ³n: Sin nÃºmeros) -->
				<div>
					<label for="team-city" class="block text-sm font-semibold text-slate-300 mb-1.5">
						Ciudad
						<span class="text-xs font-normal text-slate-400">(Solo letras)</span>
					</label>
					<input
						id="team-city"
						type="text"
						bind:value={teamData.city}
						oninput={handleCityInput}
						placeholder="Ej. Lima"
						class="w-full px-4 py-2.5 rounded-lg bg-slate-900/80 border text-white placeholder-slate-500 focus:outline-none transition {errors.city ? 'border-red-500' : 'border-slate-700 focus:border-emerald-500'}"
					/>
					{#if errors.city}
						<p class="mt-1 text-xs text-red-400">{errors.city}</p>
					{/if}
				</div>

				<!-- Selector de PaÃ­ses de SudamÃ©rica para el Club -->
				<div>
					<label for="team-country" class="block text-sm font-semibold text-slate-300 mb-1.5">
						PaÃ­s de Origen (SudamÃ©rica) <span class="text-emerald-400">*</span>
					</label>
					<select
						id="team-country"
						bind:value={teamData.country}
						class="w-full px-4 py-2.5 rounded-lg bg-slate-900/80 border border-slate-700 text-white focus:outline-none focus:border-emerald-500 transition cursor-pointer"
					>
						{#each southAmericanCountries as country}
							<option value={country}>{country}</option>
						{/each}
					</select>
				</div>
			</div>
		</div>

		<!-- â”€â”€ SECCIÃ“N 2: CARGA DE PLANTILLA (JUGADORES) â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€ -->
		<div class="glass-card p-6 md:p-8 flex flex-col gap-6">
			<!-- Header de secciÃ³n con selector de vista y contador -->
			<div class="flex flex-col sm:flex-row sm:items-center justify-between gap-4 border-b pb-4" style="border-color: var(--border-color);">
				<div class="flex items-center gap-2">
					<span class="text-2xl">{teamData.sport === 'basketball' ? 'ðŸ€' : 'âš½'}</span>
					<div>
						<h2 class="text-xl font-bold text-white">Plantilla de Jugadores</h2>
						<p class="text-xs text-slate-400">
							{teamData.sport === 'basketball'
								? 'Ubica a tus jugadores en la pista de bÃ¡squetbol (mÃ­n. 5).'
								: 'Ubica a tus jugadores en la cancha tÃ¡ctica (mÃ­n. 5, mÃ¡x. 1 arquero).'}
						</p>
					</div>
				</div>

				<div class="flex items-center gap-3">
					<!-- Switcher de vistas -->
					<div class="flex items-center bg-slate-950 p-1 rounded-xl border border-slate-800">
						<button
							type="button"
							onclick={() => editorView = 'pitch'}
							class="px-3 py-1.5 text-xs font-bold rounded-lg transition flex items-center gap-1.5 {editorView === 'pitch' ? 'bg-emerald-600 text-white shadow' : 'text-slate-400 hover:text-white'}"
						>
							<span>{teamData.sport === 'basketball' ? 'ðŸ€' : 'ðŸŸï¸'}</span>
							{teamData.sport === 'basketball' ? 'Pista' : 'Cancha'}
						</button>
						<button
							type="button"
							onclick={() => editorView = 'classic'}
							class="px-3 py-1.5 text-xs font-bold rounded-lg transition flex items-center gap-1.5 {editorView === 'classic' ? 'bg-emerald-600 text-white shadow' : 'text-slate-400 hover:text-white'}"
						>
							<span>ðŸ“‹</span> Formulario
						</button>
					</div>

					<!-- Contador y barra de progreso -->
					<div class="flex flex-col items-end gap-1">
						<span class="text-xs px-2.5 py-1 rounded-full font-semibold {players.length >= MIN_PLAYERS ? 'bg-emerald-500/20 text-emerald-300' : 'bg-amber-500/15 text-amber-400'}">
							{players.length}/{MIN_PLAYERS} mÃ­n.
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

			<!-- VISTA 1: CANCHA / PISTA TÃCTICA INTERACTIVA -->
			{#if editorView === 'pitch'}
				<div class="flex flex-col gap-4">
					<div class="flex flex-wrap items-center justify-between gap-2 px-1">
						<span class="text-xs text-slate-400">
							Haz clic en los botones <strong>(+)</strong> de la formaciÃ³n para ubicar jugadores:
						</span>
						<button
							type="button"
							onclick={() => openQuickAdd(teamData.sport === 'basketball' ? 'point_guard' : 'forward')}
							class="px-3 py-1.5 text-xs font-bold rounded-lg bg-emerald-600 hover:bg-emerald-500 text-white transition flex items-center gap-1.5 shadow"
						>
							<span>+</span> Agregar Jugador
						</button>
					</div>

					<!-- Cancha segÃºn deporte -->
					{#if teamData.sport === 'basketball'}
						<BasketballCourt
							{players}
							interactive={true}
							teamName={teamData.name || 'Nuevo Club'}
							teamColor="#f59e0b"
							onAddPlayer={(pos) => openQuickAdd(pos)}
							onRemovePlayer={(p) => handleRemovePlayerFromPitch(p)}
						/>
					{:else}
						<SoccerPitch
							{players}
							interactive={true}
							teamName={teamData.name || 'Nuevo Club'}
							teamColor="#10b981"
							onAddPlayer={(pos) => openQuickAdd(pos)}
							onRemovePlayer={(p) => handleRemovePlayerFromPitch(p)}
						/>
					{/if}

					<!-- Resumen de plantilla debajo de la cancha -->
					{#if players.length > 0}
						<div class="mt-1 p-4 rounded-xl bg-slate-900/50 border border-slate-800">
							<div class="flex items-center justify-between mb-2">
								<h4 class="text-xs font-bold text-slate-300 uppercase tracking-wider">
									Jugadores en Plantilla ({players.length})
								</h4>
								<span class="text-[11px] text-slate-400">Clic en âœ• para retirar</span>
							</div>
							<div class="flex flex-wrap gap-2">
								{#each players as p, idx}
									<div class="flex items-center gap-2 px-3 py-1.5 rounded-lg bg-slate-800/80 border border-slate-700 text-xs">
										<span class="font-mono font-black text-emerald-400">
											{p.shirt_number !== null && p.shirt_number !== undefined && p.shirt_number !== '' ? '#' + p.shirt_number : 'â€”'}
										</span>
										<span class="text-white font-medium">{p.first_name} {p.last_name}</span>
										<span class="text-[10px] text-emerald-400/90 font-medium">({p.nationality || teamData.country})</span>
										<span class="text-[10px] text-slate-400">
											({positions.find((pos) => pos.value === p.position)?.label || p.position})
										</span>
										<button
											type="button"
											onclick={() => removePlayer(idx)}
											class="text-red-400 hover:text-red-300 ml-1 font-bold transition"
											title="Eliminar jugador"
										>âœ•</button>
									</div>
								{/each}
							</div>
						</div>
					{/if}
				</div>
			{:else}
				<!-- VISTA 2: FORMULARIO CLÃSICO -->
				<div class="bg-slate-900/60 p-4 rounded-xl border border-slate-800">
					<h3 class="text-sm font-bold text-slate-300 mb-3 flex items-center gap-2">
						<span>âž•</span> AÃ±adir Jugador a la Plantilla
					</h3>

					<div class="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-3 lg:grid-cols-6 gap-3">
						<!-- Nombre (Sin nÃºmeros) -->
						<div>
							<label for="p-firstname" class="block text-xs text-slate-400 mb-1">Nombre * <span class="text-[10px] text-slate-500">(Letras)</span></label>
							<input
								id="p-firstname"
								type="text"
								bind:value={newPlayer.first_name}
								oninput={handlePlayerFirstNameInput}
								placeholder="Carlos"
								class="w-full px-3 py-2 text-sm rounded border text-white focus:outline-none transition {playerErrors.first_name ? 'bg-red-950/30 border-red-500/60' : 'bg-slate-950 border-slate-700 focus:border-emerald-500'}"
							/>
							{#if playerErrors.first_name}<p class="mt-0.5 text-xs text-red-400">{playerErrors.first_name}</p>{/if}
						</div>

						<!-- Apellido (Sin nÃºmeros) -->
						<div>
							<label for="p-lastname" class="block text-xs text-slate-400 mb-1">Apellido * <span class="text-[10px] text-slate-500">(Letras)</span></label>
							<input
								id="p-lastname"
								type="text"
								bind:value={newPlayer.last_name}
								oninput={handlePlayerLastNameInput}
								placeholder="GÃ³mez"
								class="w-full px-3 py-2 text-sm rounded border text-white focus:outline-none transition {playerErrors.last_name ? 'bg-red-950/30 border-red-500/60' : 'bg-slate-950 border-slate-700 focus:border-emerald-500'}"
							/>
							{#if playerErrors.last_name}<p class="mt-0.5 text-xs text-red-400">{playerErrors.last_name}</p>{/if}
						</div>

						<!-- DNI (Solo nÃºmeros, 8 dÃ­gitos, sin duplicados) -->
						<div>
							<label for="p-dni" class="block text-xs text-slate-400 mb-1">DNI (8 dÃ­gitos) *</label>
							<input
								id="p-dni"
								type="text"
								maxlength="8"
								bind:value={newPlayer.dni}
								oninput={handlePlayerDniInput}
								placeholder="74859612"
								class="w-full px-3 py-2 text-sm rounded border text-white focus:outline-none transition {playerErrors.dni ? 'bg-red-950/30 border-red-500/60' : 'bg-slate-950 border-slate-700 focus:border-emerald-500'}"
							/>
							{#if playerErrors.dni}<p class="mt-0.5 text-xs text-red-400">{playerErrors.dni}</p>{/if}
						</div>

						<!-- Dorsal (Solo nÃºmeros 0-99) -->
						<div>
							<label for="p-shirt" class="block text-xs text-slate-400 mb-1">Dorsal (0-99)</label>
							<input
								id="p-shirt"
								type="text"
								maxlength="2"
								bind:value={newPlayer.shirt_number}
								oninput={handlePlayerShirtInput}
								placeholder="10"
								class="w-full px-3 py-2 text-sm rounded border text-white focus:outline-none transition {playerErrors.shirt_number ? 'bg-red-950/30 border-red-500/60' : 'bg-slate-950 border-slate-700 focus:border-emerald-500'}"
							/>
							{#if playerErrors.shirt_number}<p class="mt-0.5 text-xs text-red-400">{playerErrors.shirt_number}</p>{/if}
						</div>

						<!-- PosiciÃ³n -->
						<div>
							<label for="p-position" class="block text-xs text-slate-400 mb-1">PosiciÃ³n</label>
							<select
								id="p-position"
								bind:value={newPlayer.position}
								class="w-full px-3 py-2 text-sm rounded bg-slate-950 border border-slate-700 text-white focus:outline-none focus:border-emerald-500"
							>
								{#each positions as pos}
									{#if pos.value === 'goalkeeper' && hasGoalkeeper}
										<option value="goalkeeper" disabled>{pos.icon} {pos.label} (MÃ¡x. 1)</option>
									{:else}
										<option value={pos.value}>{pos.icon} {pos.label}</option>
									{/if}
								{/each}
							</select>
						</div>

						<!-- Selector de PaÃ­s de SudamÃ©rica para Jugador -->
						<div>
							<label for="p-nationality" class="block text-xs text-slate-400 mb-1">PaÃ­s (SudamÃ©rica)</label>
							<select
								id="p-nationality"
								bind:value={newPlayer.nationality}
								class="w-full px-3 py-2 text-sm rounded bg-slate-950 border border-slate-700 text-white focus:outline-none focus:border-emerald-500"
							>
								{#each southAmericanCountries as country}
									<option value={country}>{country}</option>
								{/each}
							</select>
						</div>
					</div>

					<div class="mt-3 flex justify-end">
						<button
							type="button"
							onclick={handleAddPlayer}
							class="px-4 py-2 text-sm font-semibold rounded-lg bg-emerald-600 hover:bg-emerald-500 text-white transition flex items-center gap-1.5 shadow-md shadow-emerald-950 cursor-pointer"
						>
							<span>âž•</span> Agregar a la lista
						</button>
					</div>
				</div>

				<!-- Tabla de jugadores agregados -->
				{#if players.length === 0}
					<div class="p-8 text-center text-slate-500 border border-dashed border-slate-800 rounded-xl">
						<p class="text-sm">AÃºn no has agregado jugadores a la lista.</p>
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
									<th class="px-4 py-3 text-left">PaÃ­s</th>
									<th class="px-4 py-3 text-left">PosiciÃ³n</th>
									<th class="px-4 py-3 text-center w-16">AcciÃ³n</th>
								</tr>
							</thead>
							<tbody class="divide-y divide-slate-800">
								{#each players as p, idx}
									<tr class="hover:bg-slate-800/40 transition">
										<td class="px-4 py-3 text-center">
											{#if p.shirt_number !== null && p.shirt_number !== undefined && p.shirt_number !== ''}
												<span class="inline-block px-2 py-0.5 rounded bg-slate-800 font-mono font-bold text-emerald-400 text-xs">
													{p.shirt_number}
												</span>
											{:else}
												<span class="text-slate-600">-</span>
											{/if}
										</td>
										<td class="px-4 py-3 font-semibold text-white">
											{p.first_name} {p.last_name}
										</td>
										<td class="px-4 py-3 font-mono text-slate-300">
											{p.dni}
										</td>
										<td class="px-4 py-3 text-emerald-400 font-medium text-xs">
											{p.nationality || teamData.country || 'PerÃº'}
										</td>
										<td class="px-4 py-3 text-slate-300 text-xs">
											{positions.find((pos) => pos.value === p.position)?.icon}
											{positions.find((pos) => pos.value === p.position)?.label}
										</td>
										<td class="px-4 py-3 text-center">
											<button
												type="button"
												onclick={() => removePlayer(idx)}
												class="text-red-400 hover:text-red-300 p-1 rounded hover:bg-red-500/10 transition"
												title="Eliminar de la lista"
											>
												ðŸ—‘ï¸
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

		<!-- â”€â”€ BOTÃ“N DE GUARDADO FINAL â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€ -->
		<div class="flex flex-col gap-3 pt-2">
			{#if errors.players_count}
				<div class="flex items-center gap-2.5 p-3 rounded-lg bg-amber-500/10 border border-amber-500/30 text-sm text-amber-300">
					<span>âš ï¸</span>
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
						: 'bg-emerald-600 hover:bg-emerald-500 shadow-emerald-950 cursor-pointer'}"
				>
					{#if isSubmitting}
						<span class="w-4 h-4 border-2 border-white border-t-transparent rounded-full animate-spin"></span>
						<span>Guardando club y plantilla...</span>
					{:else}
						<span>ðŸ’¾ Registrar Club y Plantilla</span>
						{#if players.length < MIN_PLAYERS}
							<span class="text-xs font-normal opacity-70">({players.length}/{MIN_PLAYERS} jug.)</span>
						{/if}
					{/if}
				</button>
			</div>
		</div>
	</form>
	{/if}
</div>

<!-- â”€â”€ MODAL QUICK-ADD DESDE LA CANCHA TÃCTICA â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€ -->
{#if showQuickAddModal}
	<div class="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/70 backdrop-blur-sm animate-fade-in">
		<div class="glass-card w-full max-w-md p-6 rounded-2xl border border-slate-700 shadow-2xl flex flex-col gap-5">
			<div class="flex items-center justify-between border-b pb-3 border-slate-800">
				<div class="flex items-center gap-2">
					<span class="text-xl">{teamData.sport === 'basketball' ? 'ðŸ€' : 'ðŸŸï¸'}</span>
					<h3 class="text-lg font-bold text-white">
						{teamData.sport === 'basketball' ? 'Ubicar en la Pista' : 'Ubicar en la Cancha'}
					</h3>
				</div>
				<button
					type="button"
					onclick={closeQuickAdd}
					class="text-slate-400 hover:text-white text-xl leading-none"
				>âœ•</button>
			</div>

			<div class="flex flex-col gap-4">
				<!-- PosiciÃ³n -->
				<div>
					<label for="qa-pos" class="block text-xs font-semibold text-slate-300 mb-1">PosiciÃ³n en el campo</label>
					<select
						id="qa-pos"
						bind:value={newPlayer.position}
						class="w-full px-3 py-2 text-sm rounded-lg bg-slate-900 border border-slate-700 text-white focus:outline-none focus:border-emerald-500"
					>
						{#each positions as pos}
							{#if pos.value === 'goalkeeper' && hasGoalkeeper}
								<option value="goalkeeper" disabled>{pos.icon} {pos.label} (MÃ¡x. 1 arquero ya asignado)</option>
							{:else}
								<option value={pos.value}>{pos.icon} {pos.label}</option>
							{/if}
						{/each}
					</select>
				</div>

				<div class="grid grid-cols-2 gap-3">
					<!-- Nombre (Sin nÃºmeros) -->
					<div>
						<label for="qa-fn" class="block text-xs font-semibold text-slate-300 mb-1">
							Nombre * <span class="text-[10px] text-slate-400">(Letras)</span>
						</label>
						<input
							id="qa-fn"
							type="text"
							bind:value={newPlayer.first_name}
							oninput={handlePlayerFirstNameInput}
							placeholder="Lucas"
							class="w-full px-3 py-2 text-sm rounded-lg bg-slate-900 border text-white focus:outline-none transition {playerErrors.first_name ? 'border-red-500' : 'border-slate-700 focus:border-emerald-500'}"
						/>
						{#if playerErrors.first_name}
							<p class="mt-0.5 text-xs text-red-400">{playerErrors.first_name}</p>
						{/if}
					</div>
					<!-- Apellido (Sin nÃºmeros) -->
					<div>
						<label for="qa-ln" class="block text-xs font-semibold text-slate-300 mb-1">
							Apellido * <span class="text-[10px] text-slate-400">(Letras)</span>
						</label>
						<input
							id="qa-ln"
							type="text"
							bind:value={newPlayer.last_name}
							oninput={handlePlayerLastNameInput}
							placeholder="DÃ­az"
							class="w-full px-3 py-2 text-sm rounded-lg bg-slate-900 border text-white focus:outline-none transition {playerErrors.last_name ? 'border-red-500' : 'border-slate-700 focus:border-emerald-500'}"
						/>
						{#if playerErrors.last_name}
							<p class="mt-0.5 text-xs text-red-400">{playerErrors.last_name}</p>
						{/if}
					</div>
				</div>

				<div class="grid grid-cols-2 gap-3">
					<!-- DNI (Solo nÃºmeros, 8 dÃ­gitos, sin duplicados) -->
					<div>
						<label for="qa-dni" class="block text-xs font-semibold text-slate-300 mb-1">DNI (8 dÃ­gitos) *</label>
						<input
							id="qa-dni"
							type="text"
							maxlength="8"
							bind:value={newPlayer.dni}
							oninput={handlePlayerDniInput}
							placeholder="71234567"
							class="w-full px-3 py-2 text-sm rounded-lg bg-slate-900 border text-white focus:outline-none transition {playerErrors.dni ? 'border-red-500' : 'border-slate-700 focus:border-emerald-500'}"
						/>
						{#if playerErrors.dni}
							<p class="mt-0.5 text-xs text-red-400">{playerErrors.dni}</p>
						{/if}
					</div>
					<!-- Dorsal (Solo nÃºmeros 0-99) -->
					<div>
						<label for="qa-shirt" class="block text-xs font-semibold text-slate-300 mb-1">Dorsal (0-99)</label>
						<input
							id="qa-shirt"
							type="text"
							maxlength="2"
							bind:value={newPlayer.shirt_number}
							oninput={handlePlayerShirtInput}
							placeholder="9"
							class="w-full px-3 py-2 text-sm rounded-lg bg-slate-900 border text-white focus:outline-none transition {playerErrors.shirt_number ? 'border-red-500' : 'border-slate-700 focus:border-emerald-500'}"
						/>
						{#if playerErrors.shirt_number}
							<p class="mt-0.5 text-xs text-red-400">{playerErrors.shirt_number}</p>
						{/if}
					</div>
				</div>

				<!-- PaÃ­s / Nacionalidad (SudamÃ©rica) -->
				<div>
					<label for="qa-nationality" class="block text-xs font-semibold text-slate-300 mb-1">PaÃ­s de Origen (SudamÃ©rica)</label>
					<select
						id="qa-nationality"
						bind:value={newPlayer.nationality}
						class="w-full px-3 py-2 text-sm rounded-lg bg-slate-900 border border-slate-700 text-white focus:outline-none focus:border-emerald-500 cursor-pointer"
					>
						{#each southAmericanCountries as country}
							<option value={country}>{country}</option>
						{/each}
					</select>
				</div>
			</div>

			<div class="flex items-center justify-end gap-3 pt-2 border-t border-slate-800">
				<button
					type="button"
					onclick={closeQuickAdd}
					class="px-4 py-2 text-sm rounded-lg text-slate-400 hover:text-white transition"
				>Cancelar</button>
				<button
					type="button"
					onclick={handleQuickAddSubmit}
					class="px-5 py-2 text-sm font-bold rounded-lg bg-emerald-600 hover:bg-emerald-500 text-white shadow-lg transition flex items-center gap-1.5 cursor-pointer"
				>
					<span>{teamData.sport === 'basketball' ? 'ðŸ€' : 'âš½'}</span>
					Agregar a la {teamData.sport === 'basketball' ? 'Pista' : 'Cancha'}
				</button>
			</div>
		</div>
	</div>
{/if}


