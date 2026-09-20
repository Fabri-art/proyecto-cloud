<script>
	/**
	 * routes/publico/+page.svelte — Vista Pública para Hinchas y Jugadores (/publico)
	 * Rediseñada con estética deportiva profesional al estilo Sofascore/ESPN.
	 */
	import { onMount, onDestroy } from 'svelte';
	import { fixtureApi, standingsApi, teamsApi } from '$lib/api/client';
	import SoccerPitch from '$lib/components/SoccerPitch.svelte';
	import BasketballCourt from '$lib/components/BasketballCourt.svelte';
	import VolleyballCourt from '$lib/components/VolleyballCourt.svelte';
	import UnderwaterChessBoard from '$lib/components/UnderwaterChessBoard.svelte';
	import AuraBattleArena from '$lib/components/AuraBattleArena.svelte';
	import SpermTriathlonTrack from '$lib/components/SpermTriathlonTrack.svelte';
	import TireRaceTrack from '$lib/components/TireRaceTrack.svelte';
	import MosquitoRadar from '$lib/components/MosquitoRadar.svelte';

	const TOURNAMENT_ID = 1;
	const REFRESH_INTERVAL_MS = 30_000;
	const LIVE_REFRESH_INTERVAL_MS = 10_000;

	let activeTab = $state('fixture');
	let rounds = $state([]);
	let standings = $state([]);
	let teamsMap = $state({});
	let selectedRound = $state(1);
	let loading = $state(true);
	let pitchModalTeam = $state(null);
	let selectedSport = $state('all'); // 'all' | 'football' | 'basketball' | 'volleyball'
	function getMatchSport(match) {
		return match.sport || teamsMap[match.home_team_id]?.sport || teamsMap[match.away_team_id]?.sport || 'football';
	}

	function getSportBadge(sport) {
		switch (sport) {
			case 'aura_battle':
				return {
					name: 'BATALLA DE AURA',
					icon: '🕺',
					bg: 'rgba(234, 179, 8, 0.2)',
					text: '#facc15',
					border: 'rgba(234, 179, 8, 0.45)',
					accent: '#eab308',
					bgLight: '#fefce8',
					textLight: '#a16207',
					borderLight: '#fef08a'
				};
			case 'sperm_triathlon':
				return {
					name: 'TRIATLÓN ESPERM.',
					icon: '🧬',
					bg: 'rgba(6, 182, 212, 0.2)',
					text: '#22d3ee',
					border: 'rgba(6, 182, 212, 0.45)',
					accent: '#06b6d4',
					bgLight: '#ecfeff',
					textLight: '#0e7490',
					borderLight: '#a5f3fc'
				};
			case 'tire_race':
				return {
					name: 'CARRERA DE LLANTAS',
					icon: '🛞',
					bg: 'rgba(234, 88, 12, 0.2)',
					text: '#fb923c',
					border: 'rgba(234, 88, 12, 0.45)',
					accent: '#ea580c',
					bgLight: '#fff7ed',
					textLight: '#c2410c',
					borderLight: '#fed7aa'
				};
			case 'mosquito_marathon':
				return {
					name: 'MARATÓN MOSQUITOS',
					icon: '🦟',
					bg: 'rgba(132, 204, 22, 0.2)',
					text: '#a3e635',
					border: 'rgba(132, 204, 22, 0.45)',
					accent: '#84cc16',
					bgLight: '#f7fee7',
					textLight: '#4d7c0f',
					borderLight: '#d9f99d'
				};
			case 'basketball':
				return {
					name: 'BÁSQUETBOL',
					icon: '🏀',
					bg: 'rgba(245, 158, 11, 0.16)',
					text: '#fbbf24',
					border: 'rgba(245, 158, 11, 0.35)',
					accent: '#f59e0b',
					bgLight: '#fffbeb',
					textLight: '#b45309',
					borderLight: '#fde68a'
				};
			case 'volleyball':
				return {
					name: 'VOLEIBOL',
					icon: '🏐',
					bg: 'rgba(56, 189, 248, 0.16)',
					text: '#38bdf8',
					border: 'rgba(56, 189, 248, 0.35)',
					accent: '#0284c7',
					bgLight: '#f0f9ff',
					textLight: '#0369a1',
					borderLight: '#bae6fd'
				};
			case 'underwater_chess':
				return {
					name: 'AJEDREZ SUBACUÁTICO',
					icon: '🌊♟️',
					bg: 'rgba(168, 85, 247, 0.2)',
					text: '#c084fc',
					border: 'rgba(168, 85, 247, 0.45)',
					accent: '#a855f7',
					bgLight: '#faf5ff',
					textLight: '#7e22ce',
					borderLight: '#e9d5ff'
				};
			case 'football':
			default:
				return {
					name: 'FÚTBOL',
					icon: '⚽',
					bg: 'rgba(16, 185, 129, 0.16)',
					text: '#34d399',
					border: 'rgba(16, 185, 129, 0.35)',
					accent: '#10b981',
					bgLight: '#ecfdf5',
					textLight: '#047857',
					borderLight: '#a7f3d0'
				};
		}
	}
	let filteredMatches = $derived(
		selectedSport === 'all'
			? sortedMatches
			: sortedMatches.filter((m) => getMatchSport(m) === selectedSport)
	);
	function getSportStandings(sport) {
		const sportTeams = Object.values(teamsMap).filter((t) => (t.sport || 'football') === sport);
		const existingMap = new Map((standings || []).map((s) => [s.team_id, s]));

		const list = sportTeams.map((t) => {
			const s = existingMap.get(t.id);
			if (s) return s;
			return {
				team_id: t.id,
				played: 0,
				won: 0,
				drawn: 0,
				lost: 0,
				goals_for: 0,
				goals_against: 0,
				goal_difference: 0,
				points: 0
			};
		});

		for (const s of (standings || [])) {
			const t = teamsMap[s.team_id];
			if (t && (t.sport || 'football') === sport && !sportTeams.some((team) => team.id === s.team_id)) {
				list.push(s);
			}
		}

		return list.sort((a, b) => {
			if ((b.points ?? 0) !== (a.points ?? 0)) return (b.points ?? 0) - (a.points ?? 0);
			const diffB = (b.goals_for ?? 0) - (b.goals_against ?? 0);
			const diffA = (a.goals_for ?? 0) - (a.goals_against ?? 0);
			if (diffB !== diffA) return diffB - diffA;
			return (b.goals_for ?? 0) - (a.goals_for ?? 0);
		});
	}

	let footballStandings = $derived(getSportStandings('football'));
	let basketballStandings = $derived(getSportStandings('basketball'));
	let volleyballStandings = $derived(getSportStandings('volleyball'));
	let chessStandings = $derived(getSportStandings('underwater_chess'));
	let auraStandings = $derived(getSportStandings('aura_battle'));
	let spermStandings = $derived(getSportStandings('sperm_triathlon'));
	let tireStandings = $derived(getSportStandings('tire_race'));
	let mosquitoStandings = $derived(getSportStandings('mosquito_marathon'));

	async function showTeamPitch(teamId) {
		let t = teamsMap[teamId];
		if (!t) return;
		if (!t.players || t.players.length === 0) {
			try {
				const full = await teamsApi.get(teamId);
				teamsMap[teamId] = full;
				t = full;
			} catch (_) {}
		}
		pitchModalTeam = t;
	}
	let now = $state(Date.now());
	function getMatchTimer(match, _tick) {
		const s = (match.status ?? '').toLowerCase();
		if (s === 'paused') {
			const totalSec = match.elapsed_seconds || 0;
			const m = Math.floor(totalSec / 60);
			const sec = totalSec % 60;
			return `${String(m).padStart(2, '0')}:${String(sec).padStart(2, '0')}`;
		}
		if (s !== 'live') return null;
		if (!match.started_at) return '00:00';
		const iso = match.started_at.endsWith('Z') ? match.started_at : match.started_at + 'Z';
		const startedMs = new Date(iso).getTime();
		const current = now || Date.now();
		const totalSec = Math.max(0, Math.floor((current - startedMs) / 1000));
		const m = Math.floor(totalSec / 60);
		const sec = totalSec % 60;
		return `${String(m).padStart(2, '0')}:${String(s).padStart(2, '0')}`;
	}
	let lastUpdated = $state(null);
	let secondsSince = $state(0);
	let refreshTimer = null;
	let clockTimer = null;

	let currentMatches = $derived(
		rounds.find((r) => (r.matchday ?? r.round) === selectedRound)?.matches ?? []
	);

	let sortedMatches = $derived(
		[...currentMatches].sort((a, b) => {
			const rank = { live: 0, paused: 1, finished: 2, scheduled: 3 };
			const aR = rank[(a.status ?? '').toLowerCase()] ?? 2;
			const bR = rank[(b.status ?? '').toLowerCase()] ?? 2;
			return aR - bR;
		})
	);

	let hasLiveMatch = $derived(
		rounds.some((r) =>
			(r.matches ?? []).some((m) => (m.status ?? '').toLowerCase() === 'live')
		)
	);

	// Colores únicos por equipo (basado en hash del ID)
	const teamColors = ['#10b981','#3b82f6','#f59e0b','#8b5cf6','#ef4444','#06b6d4','#f97316','#ec4899'];
	function teamColor(id) { return teamColors[(id ?? 0) % teamColors.length]; }

	const statusConfig = {
		scheduled: { label: 'Programado', cls: 'badge-scheduled', icon: null },
		live:      { label: 'EN VIVO',    cls: 'badge-live',      icon: 'live' },
		paused:    { label: 'PAUSADO',    cls: 'badge-scheduled text-amber-300 border-amber-500/40 bg-amber-500/15', icon: null },
		finished:  { label: 'Finalizado', cls: 'badge-finished',  icon: null },
		cancelled: { label: 'Cancelado',  cls: 'badge-cancelled', icon: null },
		postponed: { label: 'Pospuesto',  cls: 'badge-scheduled', icon: null }
	};

	function getStatus(raw) {
		const key = (raw ?? 'scheduled').toLowerCase();
		return statusConfig[key] ?? statusConfig.scheduled;
	}

	function formatDate(dateStr) {
		if (!dateStr) return null;
		return new Date(dateStr).toLocaleDateString('es', {
			weekday: 'short', day: 'numeric', month: 'short',
			hour: '2-digit', minute: '2-digit'
		});
	}

	function goalDiff(s) {
		const d = (s.goals_for ?? 0) - (s.goals_against ?? 0);
		return d > 0 ? `+${d}` : `${d}`;
	}

	async function fetchAll() {
		try {
			const [fixtureData, standingsData, teamsList] = await Promise.all([
				fixtureApi.get(TOURNAMENT_ID).catch(() => ({ rounds: [] })),
				standingsApi.get(TOURNAMENT_ID).catch(() => []),
				teamsApi.list(TOURNAMENT_ID, false).catch(() => [])
			]);
			const map = {};
			for (const t of teamsList) map[t.id] = t;
			teamsMap = map;
			rounds = fixtureData.rounds ?? [];
			standings = standingsData;

			const liveRound = rounds.find((r) =>
				(r.matches ?? []).some((m) => (m.status ?? '').toLowerCase() === 'live')
			);
			if (liveRound) {
				selectedRound = liveRound.matchday ?? liveRound.round ?? 1;
			} else if (rounds.length > 0 && !rounds.some((r) => (r.matchday ?? r.round) === selectedRound)) {
				selectedRound = rounds[0].matchday ?? rounds[0].round ?? 1;
			}

			lastUpdated = new Date();
			secondsSince = 0;
		} catch (_) {}
		finally { loading = false; }
	}

	let syncChannel = null;
	let storageListener = null;

	function handleLiveScoreSync(eventData) {
		if (!eventData || !eventData.matchId) return;
		let matchFound = false;
		for (const r of rounds) {
			const m = (r.matches || []).find((x) => x.id === eventData.matchId);
			if (m) {
				m.home_score = eventData.home_score;
				m.away_score = eventData.away_score;
				if (eventData.status) m.status = eventData.status;
				matchFound = true;
			}
		}
		if (matchFound) {
			rounds = [...rounds];
		}
		// Refrescar en background para sincronizar posiciones y estadísticas
		fetchAll();
	}

	onMount(() => {
		fetchAll();
		refreshTimer = setInterval(() => {
			fetchAll();
		}, hasLiveMatch ? 4000 : REFRESH_INTERVAL_MS);
		clockTimer = setInterval(() => {
			secondsSince++;
			if (hasLiveMatch) {
				now = Date.now();
			}
		}, 1000);

		// Escuchar sincronización en tiempo real desde Mesa de Control
		if (typeof window !== 'undefined') {
			if ('BroadcastChannel' in window) {
				syncChannel = new BroadcastChannel('torneo_live_sync');
				syncChannel.onmessage = (e) => handleLiveScoreSync(e.data);
			}
			storageListener = (e) => {
				if (e.key === 'torneo_score_sync' && e.newValue) {
					try {
						handleLiveScoreSync(JSON.parse(e.newValue));
					} catch (_) {}
				}
			};
			window.addEventListener('storage', storageListener);
		}
	});

	onDestroy(() => {
		if (refreshTimer) clearInterval(refreshTimer);
		if (clockTimer) clearInterval(clockTimer);
		if (syncChannel) syncChannel.close();
		if (typeof window !== 'undefined' && storageListener) {
			window.removeEventListener('storage', storageListener);
		}
	});

	function teamName(id) { return teamsMap[id]?.name ?? `Equipo #${id}`; }
	function teamShort(id) { return teamsMap[id]?.short_name ?? '???'; }
	function teamInitial(id) { return teamsMap[id]?.name?.[0]?.toUpperCase() ?? '?'; }

	// Porcentaje de progreso del refresh (para la barra)
	let refreshInterval = $derived(hasLiveMatch ? LIVE_REFRESH_INTERVAL_MS : REFRESH_INTERVAL_MS);
	let refreshProgress = $derived(Math.min(100, (secondsSince / (refreshInterval / 1000)) * 100));
</script>

<svelte:head>
	<title>Torneo Hub — Fixture & Posiciones</title>
	<meta name="description" content="Fixture y tabla de posiciones del torneo en tiempo real." />
</svelte:head>

<!-- ── ENCABEZADO ─────────────────────────────────────────────────────────── -->
<div class="mb-7 animate-fade-in-up">
	<div class="flex flex-col sm:flex-row sm:items-center justify-between gap-3">
		<div>
			<div class="flex items-center gap-3 mb-1">
				<h1 class="text-2xl sm:text-3xl font-black text-white tracking-tight font-display">
					Vista Pública
				</h1>
				{#if hasLiveMatch}
					<span class="live-badge-pill">
						<span class="live-dot"></span> EN VIVO
					</span>
				{/if}
			</div>
			<p class="text-slate-500 text-sm">Torneo Hub · Fixture y clasificación en tiempo real</p>
		</div>

		<!-- Refresh indicator -->
		{#if lastUpdated}
			<div class="flex flex-col items-end gap-1.5">
				<div class="flex items-center gap-2 text-xs text-slate-500">
					<span class="w-1.5 h-1.5 rounded-full {hasLiveMatch ? 'bg-emerald-400' : 'bg-slate-600'}"></span>
					{secondsSince < 5 ? 'Actualizado ahora' : `Hace ${secondsSince}s`}
				</div>
				<!-- Barra de progreso de refresh -->
				<div class="w-24 h-0.5 rounded-full overflow-hidden" style="background: rgba(148,163,184,0.12);">
					<div class="h-full rounded-full transition-all duration-1000 ease-linear"
						style="width: {refreshProgress}%; background: {hasLiveMatch ? '#10b981' : '#475569'};"></div>
				</div>
			</div>
		{/if}
	</div>
</div>

<!-- ── PESTAÑAS Y SELECTOR DE DEPORTE ── -->
<div class="flex flex-wrap items-center justify-between gap-3 mb-7">
	<!-- Pestañas Fixture / Posiciones -->
	<div class="flex gap-0 p-1 bg-slate-900 rounded-xl border border-slate-800/80 w-fit">
		<button
			onclick={() => (activeTab = 'fixture')}
			class="tab-pill {activeTab === 'fixture' ? 'tab-pill-active' : 'tab-pill-inactive'}"
		>
			<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 20 20" fill="currentColor" class="w-4 h-4 shrink-0">
				<path fill-rule="evenodd" d="M5.75 2a.75.75 0 0 1 .75.75V4h7V2.75a.75.75 0 0 1 1.5 0V4h.25A2.75 2.75 0 0 1 18 6.75v8.5A2.75 2.75 0 0 1 15.25 18H4.75A2.75 2.75 0 0 1 2 15.25v-8.5A2.75 2.75 0 0 1 4.75 4H5V2.75A.75.75 0 0 1 5.75 2Z" clip-rule="evenodd"/>
			</svg>
			Fixture
		</button>
		<button
			onclick={() => (activeTab = 'posiciones')}
			class="tab-pill {activeTab === 'posiciones' ? 'tab-pill-active' : 'tab-pill-inactive'}"
		>
			<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 20 20" fill="currentColor" class="w-4 h-4 shrink-0">
				<path d="M15.5 2A1.5 1.5 0 0 0 14 3.5v13a1.5 1.5 0 0 0 3 0v-13A1.5 1.5 0 0 0 15.5 2ZM9.5 6A1.5 1.5 0 0 0 8 7.5v9a1.5 1.5 0 0 0 3 0v-9A1.5 1.5 0 0 0 9.5 6ZM3.5 10A1.5 1.5 0 0 0 2 11.5v5a1.5 1.5 0 0 0 3 0v-5A1.5 1.5 0 0 0 3.5 10Z"/>
			</svg>
			Posiciones
		</button>
	</div>

	<!-- Selector de Deporte -->
	<div class="flex flex-wrap items-center gap-1.5 p-1.5 bg-slate-900 rounded-xl border border-slate-800/80 max-w-full">
		<button
			type="button"
			onclick={() => (selectedSport = 'all')}
			class="px-3 py-1.5 rounded-lg text-xs font-bold transition {selectedSport === 'all' ? 'bg-slate-700 text-white shadow' : 'text-slate-400 hover:text-white'}"
		>
			🌐 Todos
		</button>
		<button
			type="button"
			onclick={() => (selectedSport = 'football')}
			class="px-3 py-1.5 rounded-lg text-xs font-bold transition {selectedSport === 'football' ? 'bg-emerald-600 text-white shadow' : 'text-slate-400 hover:text-white'}"
		>
			⚽ Fútbol
		</button>
		<button
			type="button"
			onclick={() => (selectedSport = 'basketball')}
			class="px-3 py-1.5 rounded-lg text-xs font-bold transition {selectedSport === 'basketball' ? 'bg-amber-600 text-white shadow' : 'text-slate-400 hover:text-white'}"
		>
			🏀 Básquetbol
		</button>
		<button
			type="button"
			onclick={() => (selectedSport = 'volleyball')}
			class="px-3 py-1.5 rounded-lg text-xs font-bold transition {selectedSport === 'volleyball' ? 'bg-violet-600 text-white shadow' : 'text-slate-400 hover:text-white'}"
		>
			🏐 Vóley
		</button>
		<button
			type="button"
			onclick={() => (selectedSport = 'underwater_chess')}
			class="px-3 py-1.5 rounded-lg text-xs font-bold transition {selectedSport === 'underwater_chess' ? 'bg-cyan-600 text-white shadow' : 'text-slate-400 hover:text-white'}"
		>
			♟️ Ajedrez acuático
		</button>
		<button
			type="button"
			onclick={() => (selectedSport = 'aura_battle')}
			class="px-3 py-1.5 rounded-lg text-xs font-bold transition {selectedSport === 'aura_battle' ? 'bg-yellow-500 text-black shadow' : 'text-slate-400 hover:text-white'}"
		>
			🕺 Batalla de aura
		</button>
		<button
			type="button"
			onclick={() => (selectedSport = 'sperm_triathlon')}
			class="px-3 py-1.5 rounded-lg text-xs font-bold transition {selectedSport === 'sperm_triathlon' ? 'bg-cyan-500 text-black shadow' : 'text-slate-400 hover:text-white'}"
		>
			🧬 Triatlón esperm.
		</button>
		<button
			type="button"
			onclick={() => (selectedSport = 'tire_race')}
			class="px-3 py-1.5 rounded-lg text-xs font-bold transition {selectedSport === 'tire_race' ? 'bg-orange-600 text-white shadow' : 'text-slate-400 hover:text-white'}"
		>
			🛞 Carrera llantas
		</button>
		<button
			type="button"
			onclick={() => (selectedSport = 'mosquito_marathon')}
			class="px-3 py-1.5 rounded-lg text-xs font-bold transition {selectedSport === 'mosquito_marathon' ? 'bg-lime-600 text-white shadow' : 'text-slate-400 hover:text-white'}"
		>
			🦟 Maratón mosquitos
		</button>
	</div>
</div>

<!-- ── CARGANDO ────────────────────────────────────────────────────────────── -->
{#if loading}
	<div class="space-y-3">
		<div class="flex gap-2 mb-5">
			{#each Array(3) as _}
				<div class="skeleton h-9 w-28 rounded-lg"></div>
			{/each}
		</div>
		{#each Array(3) as _}
			<div class="skeleton h-28 w-full rounded-2xl"></div>
		{/each}
	</div>

{:else}

<!-- ════════ PESTAÑA: FIXTURE ══════════════════════════════════════════════════ -->
{#if activeTab === 'fixture'}
	{#if rounds.length === 0}
		<div class="glass-card p-16 text-center">
			<div class="text-5xl mb-4 opacity-30">📅</div>
			<h2 class="text-lg font-bold text-white mb-2">Fixture no disponible</h2>
			<p class="text-slate-500 text-sm">El fixture del torneo se publicará próximamente.</p>
		</div>
	{:else}
		<!-- Selector de jornadas tipo pill-scroll -->
		<div class="flex gap-2 mb-6 overflow-x-auto pb-1 scrollbar-hide">
			{#each rounds as r}
				{@const mday = r.matchday ?? r.round ?? 1}
				{@const hasLive = (r.matches ?? []).some((m) => (m.status ?? '').toLowerCase() === 'live')}
				<button
					onclick={() => (selectedRound = mday)}
					class="round-btn {selectedRound === mday ? 'round-btn-active' : 'round-btn-inactive'} flex-shrink-0"
				>
					{#if hasLive}<span class="live-dot"></span>{/if}
					J{mday}
				</button>
			{/each}
		</div>

		<!-- Tarjetas de partidos -->
		<div class="flex flex-col gap-3">
			{#if filteredMatches.length === 0}
			<div class="glass-card p-10 text-center">
				<p class="text-slate-400 text-sm">No hay partidos de {selectedSport === 'all' ? 'las disciplinas seleccionadas' : getSportBadge(selectedSport).name.toLowerCase()} en esta jornada.</p>
			</div>
		{/if}
		{#each filteredMatches as match, i}
			{@const mSport = getMatchSport(match)}
			{@const sportBadge = getSportBadge(mSport)}
			{@const status = getStatus(match.status)}
			{@const isLive = (match.status ?? '').toLowerCase() === 'live'}
			{@const isFinished = (match.status ?? '').toLowerCase() === 'finished'}
			{@const hColor = teamColor(match.home_team_id)}
			{@const aColor = teamColor(match.away_team_id)}

			<div class="match-card-new {isLive ? 'match-card-live-border' : ''} animate-fade-in-up flex-col"
				style="animation-delay: {i * 0.04}s; border-top: 3px solid {sportBadge.accent};">

				<!-- Franja superior destacada de la disciplina -->
				<div class="match-card-top-bar px-4 py-2.5 flex items-center justify-between border-b border-slate-800/80"
					style="--sport-bg: {sportBadge.bg}; --sport-bg-light: {sportBadge.bgLight};">
					<div class="flex items-center gap-2">
						<span class="sport-badge-pill inline-flex items-center gap-1.5 px-2.5 py-1 rounded-lg text-xs font-black tracking-wider uppercase shadow-sm"
							style="--badge-bg: {sportBadge.bg}; --badge-text: {sportBadge.text}; --badge-border: {sportBadge.border}; --badge-bg-light: {sportBadge.bgLight}; --badge-text-light: {sportBadge.textLight}; --badge-border-light: {sportBadge.borderLight};">
							<span class="text-sm leading-none">{sportBadge.icon}</span>
							<span>{sportBadge.name}</span>
						</span>
						<span class="match-id-pill text-xs font-mono font-bold px-2 py-0.5 rounded border">
							#{match.id}
						</span>
					</div>
					<div class="flex items-center gap-2">
						<span class="status-pill {status.cls}">
							{#if isLive}<span class="live-dot"></span>{/if}
							{status.label}
						</span>
						{#if match.scheduled_at}
							<span class="text-xs text-slate-400 font-mono hidden sm:inline">{formatDate(match.scheduled_at)}</span>
						{/if}
					</div>
				</div>

				<div class="match-inner">

						<!-- Equipos y marcador -->
						<div class="flex items-center justify-between gap-2">
							<!-- Local -->
							<div class="flex-1 flex flex-col sm:flex-row items-center sm:justify-end gap-2.5 text-center sm:text-right min-w-0">
								<div class="min-w-0">
									<p class="font-bold text-white text-sm sm:text-base leading-tight truncate">
										{teamName(match.home_team_id)}
									</p>
									<p class="text-xs font-mono" style="color: {hColor}; opacity: 0.8;">
										{teamShort(match.home_team_id)}
									</p>
								</div>
								<div class="team-shield" style="background: linear-gradient(135deg, {hColor}22, {hColor}44); border-color: {hColor}55; color: {hColor};">
									{teamInitial(match.home_team_id)}
								</div>
							</div>

							<!-- Marcador central con timer encima -->
							<div class="flex flex-col items-center gap-1.5 flex-shrink-0">
								{#if isLive}
									<div class="inline-flex items-center gap-1 px-3 py-0.5 rounded-full bg-emerald-950/90 border border-emerald-500/50 text-emerald-300 font-mono font-black text-xs shadow-md animate-pulse tracking-wider">
										<span class="w-1.5 h-1.5 rounded-full bg-emerald-400"></span>
										<span>⏱️ {getMatchTimer(match, now)}</span>
									</div>
								{:else if (match.status ?? '').toLowerCase() === 'paused'}
									<div class="inline-flex items-center gap-1 px-3 py-0.5 rounded-full bg-amber-950/90 border border-amber-500/50 text-amber-300 font-mono font-black text-xs shadow-md tracking-wider">
										<span>⏸️ {getMatchTimer(match, now)}</span>
									</div>
								{/if}
								<div class="score-center {isLive ? 'score-live' : isFinished ? 'score-done' : 'score-upcoming'}">
									{#if match.home_score !== null && match.away_score !== null}
										<span class="font-score text-2xl sm:text-3xl font-bold tabular-nums">
											{match.home_score}:{match.away_score}
										</span>
									{:else}
										<span class="text-slate-600 font-bold text-sm">VS</span>
									{/if}
								</div>
							</div>

							<!-- Visitante -->
							<div class="flex-1 flex flex-col sm:flex-row items-center sm:justify-start gap-2.5 text-center sm:text-left min-w-0">
								<div class="team-shield" style="background: linear-gradient(135deg, {aColor}22, {aColor}44); border-color: {aColor}55; color: {aColor};">
									{teamInitial(match.away_team_id)}
								</div>
								<div class="min-w-0">
									<p class="font-bold text-white text-sm sm:text-base leading-tight truncate">
										{teamName(match.away_team_id)}
									</p>
									<p class="text-xs font-mono" style="color: {aColor}; opacity: 0.8;">
										{teamShort(match.away_team_id)}
									</p>
								</div>
							</div>
						</div>
						<!-- Botones de Alineación Táctica en Cancha -->
						<div class="mt-3 pt-2.5 border-t border-slate-800/60 flex items-center justify-between text-xs">
							<button type="button" onclick={() => showTeamPitch(match.home_team_id)} class="text-slate-400 hover:text-emerald-400 flex items-center gap-1 transition" title="Ver formación en cancha">
								<span>🏟️</span> Ver alineación {teamShort(match.home_team_id)}
							</button>
							<span class="text-slate-700">•</span>
							<button type="button" onclick={() => showTeamPitch(match.away_team_id)} class="text-slate-400 hover:text-emerald-400 flex items-center gap-1 transition" title="Ver formación en cancha">
								<span>🏟️</span> Ver alineación {teamShort(match.away_team_id)}
							</button>
						</div>
					</div>
				</div>
			{/each}
		</div>
	{/if}
{/if}

<!-- ════════ PESTAÑA: POSICIONES ══════════════════════════════════════════════ -->
{#if activeTab === 'posiciones'}
	{#if footballStandings.length === 0 && basketballStandings.length === 0 && volleyballStandings.length === 0 && chessStandings.length === 0 && auraStandings.length === 0 && spermStandings.length === 0 && tireStandings.length === 0 && mosquitoStandings.length === 0}
		<div class="glass-card p-16 text-center">
			<div class="text-5xl mb-4 opacity-30">📊</div>
			<h2 class="text-lg font-bold text-white mb-2">Sin datos todavía</h2>
			<p class="text-slate-500 text-sm">La tabla se completa automáticamente al registrar clubes y finalizar partidos.</p>
		</div>
	{:else}
		<div class="space-y-10">
			<!-- TABLA DE FÚTBOL -->
			{#if (selectedSport === 'all' || selectedSport === 'football') && (footballStandings.length > 0 || selectedSport === 'football')}
				<div class="space-y-3">
					<div class="flex items-center justify-between">
						<div class="flex items-center gap-2">
							<span class="text-2xl">⚽</span>
							<div>
								<h3 class="text-lg font-black text-white">Tabla de Posiciones — Fútbol</h3>
								<p class="text-xs text-slate-400">Torneo oficial de fútbol 11</p>
							</div>
						</div>
						<span class="text-xs px-2.5 py-1 rounded-full font-bold bg-emerald-500/15 text-emerald-300 border border-emerald-500/30">
							{footballStandings.length} clubes
						</span>
					</div>

					<div class="standings-box rounded-2xl overflow-hidden border shadow-xl">
						<div class="overflow-x-auto -mx-1 sm:mx-0">
					<table class="w-full text-sm min-w-[520px]">
								<thead>
									<tr class="standings-head-row">
										<th class="px-4 py-3 text-left text-xs section-label w-10">#</th>
										<th class="px-4 py-3 text-left text-xs section-label">Club</th>
										<th class="px-3 py-3 text-center text-xs section-label" title="Partidos Jugados">PJ</th>
										<th class="px-3 py-3 text-center text-xs section-label" title="Ganados">PG</th>
										<th class="px-3 py-3 text-center text-xs section-label" title="Empates">PE</th>
										<th class="px-3 py-3 text-center text-xs section-label" title="Perdidos">PP</th>
										<th class="px-3 py-3 text-center text-xs section-label hidden sm:table-cell" title="Goles Favor">GF</th>
										<th class="px-3 py-3 text-center text-xs section-label hidden sm:table-cell" title="Goles Contra">GC</th>
										<th class="px-3 py-3 text-center text-xs section-label hidden sm:table-cell" title="Diferencia">DG</th>
										<th class="px-4 py-3 text-center text-xs section-label text-emerald-400">PTS</th>
									</tr>
								</thead>
								<tbody>
									{#if footballStandings.length === 0}
										<tr><td colspan="10" class="text-center py-6 text-slate-500 text-xs">No hay clubes registrados en fútbol</td></tr>
									{/if}
									{#each footballStandings as s, i}
										{@const accentLeft = i === 0 ? '#10b981' : i === 1 ? '#38bdf8' : i === 2 ? '#f59e0b' : 'transparent'}
										{@const tColor = teamColor(s.team_id)}
										<tr class="standings-row border-b border-slate-800/50 transition-colors"
											style="border-left: 3px solid {accentLeft};">
											<td class="px-4 py-3 text-center">
												{#if i === 0}<span class="text-base">🥇</span>
												{:else if i === 1}<span class="text-base">🥈</span>
												{:else if i === 2}<span class="text-base">🥉</span>
												{:else}<span class="text-xs text-slate-500 font-mono">{i + 1}</span>{/if}
											</td>
											<td class="px-4 py-3">
												<div class="flex items-center gap-3">
													<div class="w-8 h-8 rounded-lg flex items-center justify-center text-xs font-black shrink-0"
														style="background: {tColor}20; border: 1px solid {tColor}40; color: {tColor};">
														{teamInitial(s.team_id)}
													</div>
													<div class="flex-1 min-w-0">
														<p class="font-bold text-white text-sm leading-tight truncate">{teamName(s.team_id)}</p>
														<span class="text-xs font-mono text-slate-500">{teamShort(s.team_id)}</span>
													</div>
													<button type="button" onclick={() => showTeamPitch(s.team_id)} class="standings-btn-pitch text-xs px-2.5 py-1 rounded transition hidden sm:inline-flex items-center gap-1 font-semibold">
														<span>🏟️</span> Ver posiciones
													</button>
												</div>
											</td>
											<td class="px-3 py-3 text-center font-mono text-slate-300">{s.played ?? 0}</td>
											<td class="px-3 py-3 text-center font-mono text-emerald-400 font-semibold">{s.won ?? 0}</td>
											<td class="px-3 py-3 text-center font-mono text-slate-400">{s.drawn ?? 0}</td>
											<td class="px-3 py-3 text-center font-mono text-red-400/80">{s.lost ?? 0}</td>
											<td class="px-3 py-3 text-center font-mono text-slate-400 hidden sm:table-cell">{s.goals_for ?? 0}</td>
											<td class="px-3 py-3 text-center font-mono text-slate-400 hidden sm:table-cell">{s.goals_against ?? 0}</td>
											<td class="px-3 py-3 text-center font-mono font-bold hidden sm:table-cell {(s.goals_for - s.goals_against) > 0 ? 'text-emerald-400' : (s.goals_for - s.goals_against) < 0 ? 'text-red-400' : 'text-slate-400'}">
												{(s.goals_for ?? 0) - (s.goals_against ?? 0) > 0 ? '+' : ''}{(s.goals_for ?? 0) - (s.goals_against ?? 0)}
											</td>
											<td class="px-4 py-3 text-center font-score font-bold text-emerald-400 text-base">{s.points ?? 0}</td>
										</tr>
									{/each}
								</tbody>
							</table>
						</div>
						<div class="standings-footer px-4 py-2.5 border-t text-xs">
							PJ = Jugados · PG = Ganados · PE = Empates · PP = Perdidos · GF = Goles Favor · GC = Goles Contra · DG = Dif. Goles · PTS = Puntos
						</div>
					</div>
				</div>
			{/if}

			<!-- TABLA DE BÁSQUETBOL -->
			{#if (selectedSport === 'all' || selectedSport === 'basketball') && (basketballStandings.length > 0 || selectedSport === 'basketball')}
				<div class="space-y-3">
					<div class="flex items-center justify-between">
						<div class="flex items-center gap-2">
							<span class="text-2xl">🏀</span>
							<div>
								<h3 class="text-lg font-black text-white">Tabla de Posiciones — Básquetbol</h3>
								<p class="text-xs text-slate-400">Torneo oficial de básquetbol 5x5</p>
							</div>
						</div>
						<span class="text-xs px-2.5 py-1 rounded-full font-bold bg-amber-500/15 text-amber-300 border border-amber-500/30">
							{basketballStandings.length} clubes
						</span>
					</div>

					<div class="standings-box rounded-2xl overflow-hidden border shadow-xl">
						<div class="overflow-x-auto -mx-1 sm:mx-0">
					<table class="w-full text-sm min-w-[520px]">
								<thead>
									<tr class="standings-head-row">
										<th class="px-4 py-3 text-left text-xs section-label w-10">#</th>
										<th class="px-4 py-3 text-left text-xs section-label">Club</th>
										<th class="px-3 py-3 text-center text-xs section-label" title="Partidos Jugados">PJ</th>
										<th class="px-3 py-3 text-center text-xs section-label" title="Ganados">PG</th>
										<th class="px-3 py-3 text-center text-xs section-label" title="Perdidos">PP</th>
										<th class="px-3 py-3 text-center text-xs section-label hidden sm:table-cell" title="Puntos a Favor">PF</th>
										<th class="px-3 py-3 text-center text-xs section-label hidden sm:table-cell" title="Puntos en Contra">PC</th>
										<th class="px-3 py-3 text-center text-xs section-label hidden sm:table-cell" title="Diferencia de Puntos">DP</th>
										<th class="px-4 py-3 text-center text-xs section-label text-amber-400">PTS</th>
									</tr>
								</thead>
								<tbody>
									{#if basketballStandings.length === 0}
										<tr><td colspan="9" class="text-center py-6 text-slate-500 text-xs">No hay clubes registrados en básquetbol</td></tr>
									{/if}
									{#each basketballStandings as s, i}
										{@const accentLeft = i === 0 ? '#f59e0b' : i === 1 ? '#38bdf8' : '#64748b'}
										{@const tColor = teamColor(s.team_id)}
										<tr class="standings-row border-b border-slate-800/50 transition-colors"
											style="border-left: 3px solid {accentLeft};">
											<td class="px-4 py-3 text-center">
												{#if i === 0}<span class="text-base">🥇</span>
												{:else if i === 1}<span class="text-base">🥈</span>
												{:else if i === 2}<span class="text-base">🥉</span>
												{:else}<span class="text-xs text-slate-500 font-mono">{i + 1}</span>{/if}
											</td>
											<td class="px-4 py-3">
												<div class="flex items-center gap-3">
													<div class="w-8 h-8 rounded-lg flex items-center justify-center text-xs font-black shrink-0"
														style="background: {tColor}20; border: 1px solid {tColor}40; color: {tColor};">
														{teamInitial(s.team_id)}
													</div>
													<div class="flex-1 min-w-0">
														<p class="font-bold text-white text-sm leading-tight truncate">{teamName(s.team_id)}</p>
														<span class="text-xs font-mono text-slate-500">{teamShort(s.team_id)}</span>
													</div>
													<button type="button" onclick={() => showTeamPitch(s.team_id)} class="standings-btn-pitch text-xs px-2.5 py-1 rounded transition hidden sm:inline-flex items-center gap-1 font-semibold">
														<span>🏀</span> Ver posiciones
													</button>
												</div>
											</td>
											<td class="px-3 py-3 text-center font-mono text-slate-300">{s.played ?? 0}</td>
											<td class="px-3 py-3 text-center font-mono text-emerald-400 font-semibold">{s.won ?? 0}</td>
											<td class="px-3 py-3 text-center font-mono text-red-400/80">{s.lost ?? 0}</td>
											<td class="px-3 py-3 text-center font-mono text-slate-400 hidden sm:table-cell">{s.goals_for ?? 0}</td>
											<td class="px-3 py-3 text-center font-mono text-slate-400 hidden sm:table-cell">{s.goals_against ?? 0}</td>
											<td class="px-3 py-3 text-center font-mono font-bold hidden sm:table-cell {(s.goals_for - s.goals_against) > 0 ? 'text-amber-400' : (s.goals_for - s.goals_against) < 0 ? 'text-red-400' : 'text-slate-400'}">
												{(s.goals_for ?? 0) - (s.goals_against ?? 0) > 0 ? '+' : ''}{(s.goals_for ?? 0) - (s.goals_against ?? 0)}
											</td>
											<td class="px-4 py-3 text-center font-score font-bold text-amber-400 text-base">{s.points ?? 0}</td>
										</tr>
									{/each}
								</tbody>
							</table>
						</div>
						<div class="standings-footer px-4 py-2.5 border-t text-xs">
							PJ = Jugados · PG = Ganados · PP = Perdidos · PF = Puntos Favor · PC = Puntos Contra · DP = Dif. Puntos · PTS = Puntos
						</div>
					</div>
				</div>
			{/if}

			<!-- TABLA VÓLEY -->
			{#if (selectedSport === 'all' || selectedSport === 'volleyball') && (volleyballStandings.length > 0 || selectedSport === 'volleyball')}
				<div class="space-y-3">
					<div class="flex items-center justify-between">
						<div class="flex items-center gap-2">
							<span class="text-2xl">🏐</span>
							<div>
								<h3 class="text-lg font-black text-white">Tabla de Posiciones — Vóley</h3>
								<p class="text-xs text-slate-400">Torneo oficial de vóley 6x6</p>
							</div>
						</div>
						<span class="text-xs px-2.5 py-1 rounded-full font-bold bg-violet-500/15 text-violet-300 border border-violet-500/30">
							{volleyballStandings.length} clubes
						</span>
					</div>

					<div class="standings-box rounded-2xl overflow-hidden border shadow-xl">
						<div class="overflow-x-auto -mx-1 sm:mx-0">
							<table class="w-full text-sm min-w-[520px]">
								<thead>
									<tr class="standings-head-row">
										<th class="px-4 py-3 text-left text-xs section-label w-10">#</th>
										<th class="px-4 py-3 text-left text-xs section-label">Club</th>
										<th class="px-3 py-3 text-center text-xs section-label" title="Partidos Jugados">PJ</th>
										<th class="px-3 py-3 text-center text-xs section-label" title="Ganados">PG</th>
										<th class="px-3 py-3 text-center text-xs section-label" title="Perdidos">PP</th>
										<th class="px-3 py-3 text-center text-xs section-label hidden sm:table-cell" title="Sets a Favor">SF</th>
										<th class="px-3 py-3 text-center text-xs section-label hidden sm:table-cell" title="Sets en Contra">SC</th>
										<th class="px-3 py-3 text-center text-xs section-label hidden sm:table-cell" title="Diferencia de Sets">DS</th>
										<th class="px-4 py-3 text-center text-xs section-label text-violet-400">PTS</th>
									</tr>
								</thead>
								<tbody>
									{#if volleyballStandings.length === 0}
										<tr><td colspan="9" class="text-center py-6 text-slate-500 text-xs">No hay clubes registrados en vóley todavía</td></tr>
									{/if}
									{#each volleyballStandings as s, i}
										{@const accentLeft = i === 0 ? '#8b5cf6' : i === 1 ? '#a78bfa' : '#64748b'}
										{@const tColor = teamColor(s.team_id)}
										<tr class="standings-row border-b border-slate-800/50 transition-colors"
											style="border-left: 3px solid {accentLeft};">
											<td class="px-4 py-3 text-center">
												{#if i === 0}<span class="text-base">🥇</span>
												{:else if i === 1}<span class="text-base">🥈</span>
												{:else if i === 2}<span class="text-base">🥉</span>
												{:else}<span class="text-xs text-slate-500 font-mono">{i + 1}</span>{/if}
											</td>
											<td class="px-4 py-3">
												<div class="flex items-center gap-3">
													<div class="w-8 h-8 rounded-lg flex items-center justify-center text-xs font-black shrink-0"
														style="background: {tColor}20; border: 1px solid {tColor}40; color: {tColor};">
														{teamInitial(s.team_id)}
													</div>
													<div class="flex-1 min-w-0">
														<p class="font-bold text-white text-sm leading-tight truncate">{teamName(s.team_id)}</p>
														<span class="text-xs font-mono text-slate-500">{teamShort(s.team_id)}</span>
													</div>
													<button type="button" onclick={() => showTeamPitch(s.team_id)} class="standings-btn-pitch text-xs px-2.5 py-1 rounded transition hidden sm:inline-flex items-center gap-1 font-semibold">
														<span>🏐</span> Ver posiciones
													</button>
												</div>
											</td>
											<td class="px-3 py-3 text-center font-mono text-slate-300">{s.played ?? 0}</td>
											<td class="px-3 py-3 text-center font-mono text-emerald-400 font-semibold">{s.won ?? 0}</td>
											<td class="px-3 py-3 text-center font-mono text-red-400/80">{s.lost ?? 0}</td>
											<td class="px-3 py-3 text-center font-mono text-slate-400 hidden sm:table-cell">{s.goals_for ?? 0}</td>
											<td class="px-3 py-3 text-center font-mono text-slate-400 hidden sm:table-cell">{s.goals_against ?? 0}</td>
											<td class="px-3 py-3 text-center font-mono font-bold hidden sm:table-cell {(s.goals_for - s.goals_against) > 0 ? 'text-violet-400' : (s.goals_for - s.goals_against) < 0 ? 'text-red-400' : 'text-slate-400'}">
												{(s.goals_for ?? 0) - (s.goals_against ?? 0) > 0 ? '+' : ''}{(s.goals_for ?? 0) - (s.goals_against ?? 0)}
											</td>
											<td class="px-4 py-3 text-center font-score font-bold text-violet-400 text-base">{s.points ?? 0}</td>
										</tr>
									{/each}
								</tbody>
							</table>
						</div>
						<div class="standings-footer px-4 py-2.5 border-t text-xs">
							PJ = Jugados · PG = Ganados · PP = Perdidos · SF = Sets Favor · SC = Sets Contra · DS = Dif. Sets · PTS = Puntos
						</div>
					</div>
				</div>
			{/if}

			<!-- TABLA AJEDREZ BAJO EL AGUA -->
			{#if (selectedSport === 'all' || selectedSport === 'underwater_chess') && (chessStandings.length > 0 || selectedSport === 'underwater_chess')}
				<div class="space-y-3">
					<div class="flex items-center justify-between">
						<div class="flex items-center gap-2">
							<span class="text-2xl">🌊♟️</span>
							<div>
								<h3 class="text-lg font-black text-white">Tabla de Posiciones — Ajedrez bajo el agua</h3>
								<p class="text-xs text-slate-400">Torneo oficial de duelos 1 vs 1</p>
							</div>
						</div>
						<span class="text-xs px-2.5 py-1 rounded-full font-bold bg-cyan-500/15 text-cyan-300 border border-cyan-500/30">
							{chessStandings.length} competidores
						</span>
					</div>

					<div class="standings-box rounded-2xl overflow-hidden border shadow-xl">
						<div class="overflow-x-auto -mx-1 sm:mx-0">
							<table class="w-full text-sm min-w-[520px]">
								<thead>
									<tr class="standings-head-row">
										<th class="px-4 py-3 text-left text-xs section-label w-10">#</th>
										<th class="px-4 py-3 text-left text-xs section-label">Competidor</th>
										<th class="px-3 py-3 text-center text-xs section-label">PJ</th>
										<th class="px-3 py-3 text-center text-xs section-label">PG</th>
										<th class="px-3 py-3 text-center text-xs section-label">PE</th>
										<th class="px-3 py-3 text-center text-xs section-label">PP</th>
										<th class="px-4 py-3 text-center text-xs section-label text-cyan-400">PTS</th>
									</tr>
								</thead>
								<tbody>
									{#if chessStandings.length === 0}
										<tr><td colspan="7" class="text-center py-6 text-slate-500 text-xs">No hay competidores registrados en ajedrez bajo el agua todavía</td></tr>
									{/if}
									{#each chessStandings as s, i}
										{@const accentLeft = i === 0 ? '#06b6d4' : i === 1 ? '#38bdf8' : '#64748b'}
										{@const tColor = teamColor(s.team_id)}
										<tr class="standings-row border-b border-slate-800/50 transition-colors"
											style="border-left: 3px solid {accentLeft};">
											<td class="px-4 py-3 text-center">
												{#if i === 0}<span class="text-base">🥇</span>
												{:else if i === 1}<span class="text-base">🥈</span>
												{:else if i === 2}<span class="text-base">🥉</span>
												{:else}<span class="text-xs text-slate-500 font-mono">{i + 1}</span>{/if}
											</td>
											<td class="px-4 py-3">
												<div class="flex items-center gap-3">
													<div class="w-8 h-8 rounded-lg flex items-center justify-center text-xs font-black shrink-0"
														style="background: {tColor}20; border: 1px solid {tColor}40; color: {tColor};">
														{teamInitial(s.team_id)}
													</div>
													<div class="flex-1 min-w-0">
														<p class="font-bold text-white text-sm leading-tight truncate">{teamName(s.team_id)}</p>
														<span class="text-xs font-mono text-slate-500">{teamShort(s.team_id)}</span>
													</div>
													<button type="button" onclick={() => showTeamPitch(s.team_id)} class="standings-btn-pitch text-xs px-2.5 py-1 rounded transition hidden sm:inline-flex items-center gap-1 font-semibold">
														<span>♟️</span> Ver posiciones
													</button>
												</div>
											</td>
											<td class="px-3 py-3 text-center font-mono text-slate-300">{s.played ?? 0}</td>
											<td class="px-3 py-3 text-center font-mono text-emerald-400 font-semibold">{s.won ?? 0}</td>
											<td class="px-3 py-3 text-center font-mono text-slate-400">{s.drawn ?? 0}</td>
											<td class="px-3 py-3 text-center font-mono text-red-400/80">{s.lost ?? 0}</td>
											<td class="px-4 py-3 text-center font-score font-bold text-cyan-400 text-base">{s.points ?? 0}</td>
										</tr>
									{/each}
								</tbody>
							</table>
						</div>
						<div class="standings-footer px-4 py-2.5 border-t text-xs">
							PJ = Jugados · PG = Victorias · PE = Tablas · PP = Derrotas · PTS = Puntos (Victoria 1, Tablas 0.5)
						</div>
					</div>
				</div>
			{/if}

			<!-- ── TABLA 5: BATALLA DE AURA ──────────────────────────────────────── -->
			{#if (selectedSport === 'all' || selectedSport === 'aura_battle') && (auraStandings.length > 0 || selectedSport === 'aura_battle')}
				<div class="space-y-3">
					<div class="flex items-center justify-between">
						<div class="flex items-center gap-2">
							<span class="text-2xl">🕺</span>
							<div>
								<h3 class="text-lg font-black text-white">Tabla de Posiciones — Batalla de Aura</h3>
								<p class="text-xs text-slate-400">Duelo callejero de baile y farmeo de aura con pasos prohibidos</p>
							</div>
						</div>
						<span class="text-xs px-2.5 py-1 rounded-full font-bold bg-purple-500/15 text-purple-300 border border-purple-500/30">
							{auraStandings.length} clubes
						</span>
					</div>

					<div class="standings-box rounded-2xl overflow-hidden border shadow-xl">
						<div class="overflow-x-auto -mx-1 sm:mx-0">
							<table class="w-full text-sm min-w-[560px]">
								<thead>
									<tr class="standings-head-row">
										<th class="px-4 py-3 text-left text-xs section-label w-10">#</th>
										<th class="px-4 py-3 text-left text-xs section-label">Orden / Club</th>
										<th class="px-3 py-3 text-center text-xs section-label">PJ</th>
										<th class="px-3 py-3 text-center text-xs section-label">PG</th>
										<th class="px-3 py-3 text-center text-xs section-label">PP</th>
										<th class="px-3 py-3 text-center text-xs section-label">PA Favor</th>
										<th class="px-3 py-3 text-center text-xs section-label">PA Contra</th>
										<th class="px-3 py-3 text-center text-xs section-label">Dif. PA</th>
										<th class="px-4 py-3 text-center text-xs section-label text-purple-400">PTS</th>
									</tr>
								</thead>
								<tbody>
									{#if auraStandings.length === 0}
										<tr><td colspan="9" class="text-center py-6 text-slate-500 text-xs">No hay clubes registrados en Batalla de Aura todavía</td></tr>
									{/if}
									{#each auraStandings as s, i}
										{@const accentLeft = i === 0 ? '#a855f7' : i === 1 ? '#c084fc' : '#64748b'}
										{@const tColor = teamColor(s.team_id)}
										<tr class="standings-row border-b border-slate-800/50 transition-colors"
											style="border-left: 3px solid {accentLeft};">
											<td class="px-4 py-3 text-center">
												{#if i === 0}<span class="text-base">🥇</span>
												{:else if i === 1}<span class="text-base">🥈</span>
												{:else if i === 2}<span class="text-base">🥉</span>
												{:else}<span class="text-xs text-slate-500 font-mono">{i + 1}</span>{/if}
											</td>
											<td class="px-4 py-3">
												<div class="flex items-center gap-3">
													<div class="w-8 h-8 rounded-lg flex items-center justify-center text-xs font-black shrink-0"
														style="background: {tColor}20; border: 1px solid {tColor}40; color: {tColor};">
														{teamInitial(s.team_id)}
													</div>
													<div class="flex-1 min-w-0">
														<p class="font-bold text-white text-sm leading-tight truncate">{teamName(s.team_id)}</p>
														<span class="text-xs font-mono text-slate-500">{teamShort(s.team_id)}</span>
													</div>
													<button type="button" onclick={() => showTeamPitch(s.team_id)} class="standings-btn-pitch text-xs px-2.5 py-1 rounded transition hidden sm:inline-flex items-center gap-1 font-semibold">
														<span>🔮</span> Ver posiciones
													</button>
												</div>
											</td>
											<td class="px-3 py-3 text-center font-mono text-slate-300">{s.played ?? 0}</td>
											<td class="px-3 py-3 text-center font-mono text-emerald-400 font-semibold">{s.won ?? 0}</td>
											<td class="px-3 py-3 text-center font-mono text-red-400/80">{s.lost ?? 0}</td>
											<td class="px-3 py-3 text-center font-mono text-slate-300">{s.goals_for ?? 0}</td>
											<td class="px-3 py-3 text-center font-mono text-slate-400">{s.goals_against ?? 0}</td>
											<td class="px-3 py-3 text-center font-mono font-semibold {(s.goal_difference ?? 0) > 0 ? 'text-emerald-400' : (s.goal_difference ?? 0) < 0 ? 'text-red-400' : 'text-slate-400'}">
												{(s.goal_difference ?? 0) > 0 ? '+' : ''}{s.goal_difference ?? 0}
											</td>
											<td class="px-4 py-3 text-center font-score font-bold text-purple-400 text-base">{s.points ?? 0}</td>
										</tr>
									{/each}
								</tbody>
							</table>
						</div>
						<div class="standings-footer px-4 py-2.5 border-t text-xs">
							PJ = Jugados · PG = Ganados · PP = Perdidos · PA = Puntos de Aura · Dif. PA = Diferencia · PTS = Puntos
						</div>
					</div>
				</div>
			{/if}

			<!-- ── TABLA 6: TRIATLÓN DE ESPERMATOZOIDE ────────────────────────────── -->
			{#if (selectedSport === 'all' || selectedSport === 'sperm_triathlon') && (spermStandings.length > 0 || selectedSport === 'sperm_triathlon')}
				<div class="space-y-3">
					<div class="flex items-center justify-between">
						<div class="flex items-center gap-2">
							<span class="text-2xl">🧬</span>
							<div>
								<h3 class="text-lg font-black text-white">Tabla de Posiciones — Triatlón de Espermatozoide</h3>
								<p class="text-xs text-slate-400">Carrera celular de velocidad y distancia</p>
							</div>
						</div>
						<span class="text-xs px-2.5 py-1 rounded-full font-bold bg-cyan-500/15 text-cyan-300 border border-cyan-500/30">
							{spermStandings.length} competidores
						</span>
					</div>

					<div class="standings-box rounded-2xl overflow-hidden border shadow-xl">
						<div class="overflow-x-auto -mx-1 sm:mx-0">
							<table class="w-full text-sm min-w-[560px]">
								<thead>
									<tr class="standings-head-row">
										<th class="px-4 py-3 text-left text-xs section-label w-10">#</th>
										<th class="px-4 py-3 text-left text-xs section-label">Nadador Celular</th>
										<th class="px-3 py-3 text-center text-xs section-label">PJ</th>
										<th class="px-3 py-3 text-center text-xs section-label">PG</th>
										<th class="px-3 py-3 text-center text-xs section-label">PP</th>
										<th class="px-3 py-3 text-center text-xs section-label">Distancia (µm)</th>
										<th class="px-3 py-3 text-center text-xs section-label">Penaliz. (µm)</th>
										<th class="px-3 py-3 text-center text-xs section-label">Neto (µm)</th>
										<th class="px-4 py-3 text-center text-xs section-label text-cyan-400">PTS</th>
									</tr>
								</thead>
								<tbody>
									{#if spermStandings.length === 0}
										<tr><td colspan="9" class="text-center py-6 text-slate-500 text-xs">No hay nadadores registrados todavía</td></tr>
									{/if}
									{#each spermStandings as s, i}
										{@const accentLeft = i === 0 ? '#06b6d4' : i === 1 ? '#38bdf8' : '#64748b'}
										{@const tColor = teamColor(s.team_id)}
										<tr class="standings-row border-b border-slate-800/50 transition-colors"
											style="border-left: 3px solid {accentLeft};">
											<td class="px-4 py-3 text-center">
												{#if i === 0}<span class="text-base">🥇</span>
												{:else if i === 1}<span class="text-base">🥈</span>
												{:else if i === 2}<span class="text-base">🥉</span>
												{:else}<span class="text-xs text-slate-500 font-mono">{i + 1}</span>{/if}
											</td>
											<td class="px-4 py-3">
												<div class="flex items-center gap-3">
													<div class="w-8 h-8 rounded-lg flex items-center justify-center text-xs font-black shrink-0"
														style="background: {tColor}20; border: 1px solid {tColor}40; color: {tColor};">
														{teamInitial(s.team_id)}
													</div>
													<div class="flex-1 min-w-0">
														<p class="font-bold text-white text-sm leading-tight truncate">{teamName(s.team_id)}</p>
														<span class="text-xs font-mono text-slate-500">{teamShort(s.team_id)}</span>
													</div>
													<button type="button" onclick={() => showTeamPitch(s.team_id)} class="standings-btn-pitch text-xs px-2.5 py-1 rounded transition hidden sm:inline-flex items-center gap-1 font-semibold">
														<span>🧬</span> Ver posiciones
													</button>
												</div>
											</td>
											<td class="px-3 py-3 text-center font-mono text-slate-300">{s.played ?? 0}</td>
											<td class="px-3 py-3 text-center font-mono text-emerald-400 font-semibold">{s.won ?? 0}</td>
											<td class="px-3 py-3 text-center font-mono text-red-400/80">{s.lost ?? 0}</td>
											<td class="px-3 py-3 text-center font-mono text-cyan-300">{s.goals_for ?? 0} µm</td>
											<td class="px-3 py-3 text-center font-mono text-amber-400/80">{s.goals_against ?? 0}</td>
											<td class="px-3 py-3 text-center font-mono font-semibold {(s.goal_difference ?? 0) > 0 ? 'text-emerald-400' : (s.goal_difference ?? 0) < 0 ? 'text-red-400' : 'text-slate-400'}">
												{(s.goal_difference ?? 0) > 0 ? '+' : ''}{s.goal_difference ?? 0}
											</td>
											<td class="px-4 py-3 text-center font-score font-bold text-cyan-400 text-base">{s.points ?? 0}</td>
										</tr>
									{/each}
								</tbody>
							</table>
						</div>
						<div class="standings-footer px-4 py-2.5 border-t text-xs">
							PJ = Pruebas · PG = Ganados · PP = Perdidos · µm = Micrómetros recorridos · PTS = Puntos
						</div>
					</div>
				</div>
			{/if}

			<!-- ── TABLA 7: CARRERA DE LLANTAS ───────────────────────────────────── -->
			{#if (selectedSport === 'all' || selectedSport === 'tire_race') && (tireStandings.length > 0 || selectedSport === 'tire_race')}
				<div class="space-y-3">
					<div class="flex items-center justify-between">
						<div class="flex items-center gap-2">
							<span class="text-2xl">🛞</span>
							<div>
								<h3 class="text-lg font-black text-white">Tabla de Posiciones — Carrera de Llantas</h3>
								<p class="text-xs text-slate-400">Campeonato oficial de rodada en pista</p>
							</div>
						</div>
						<span class="text-xs px-2.5 py-1 rounded-full font-bold bg-amber-500/15 text-amber-300 border border-amber-500/30">
							{tireStandings.length} escuderías
						</span>
					</div>

					<div class="standings-box rounded-2xl overflow-hidden border shadow-xl">
						<div class="overflow-x-auto -mx-1 sm:mx-0">
							<table class="w-full text-sm min-w-[560px]">
								<thead>
									<tr class="standings-head-row">
										<th class="px-4 py-3 text-left text-xs section-label w-10">#</th>
										<th class="px-4 py-3 text-left text-xs section-label">Escudería</th>
										<th class="px-3 py-3 text-center text-xs section-label">PJ</th>
										<th class="px-3 py-3 text-center text-xs section-label">PG</th>
										<th class="px-3 py-3 text-center text-xs section-label">PP</th>
										<th class="px-3 py-3 text-center text-xs section-label">Vueltas (VLT)</th>
										<th class="px-3 py-3 text-center text-xs section-label">VLT Contra</th>
										<th class="px-3 py-3 text-center text-xs section-label">Dif. VLT</th>
										<th class="px-4 py-3 text-center text-xs section-label text-amber-400">PTS</th>
									</tr>
								</thead>
								<tbody>
									{#if tireStandings.length === 0}
										<tr><td colspan="9" class="text-center py-6 text-slate-500 text-xs">No hay escuderías registradas todavía</td></tr>
									{/if}
									{#each tireStandings as s, i}
										{@const accentLeft = i === 0 ? '#f59e0b' : i === 1 ? '#fbbf24' : '#64748b'}
										{@const tColor = teamColor(s.team_id)}
										<tr class="standings-row border-b border-slate-800/50 transition-colors"
											style="border-left: 3px solid {accentLeft};">
											<td class="px-4 py-3 text-center">
												{#if i === 0}<span class="text-base">🥇</span>
												{:else if i === 1}<span class="text-base">🥈</span>
												{:else if i === 2}<span class="text-base">🥉</span>
												{:else}<span class="text-xs text-slate-500 font-mono">{i + 1}</span>{/if}
											</td>
											<td class="px-4 py-3">
												<div class="flex items-center gap-3">
													<div class="w-8 h-8 rounded-lg flex items-center justify-center text-xs font-black shrink-0"
														style="background: {tColor}20; border: 1px solid {tColor}40; color: {tColor};">
														{teamInitial(s.team_id)}
													</div>
													<div class="flex-1 min-w-0">
														<p class="font-bold text-white text-sm leading-tight truncate">{teamName(s.team_id)}</p>
														<span class="text-xs font-mono text-slate-500">{teamShort(s.team_id)}</span>
													</div>
													<button type="button" onclick={() => showTeamPitch(s.team_id)} class="standings-btn-pitch text-xs px-2.5 py-1 rounded transition hidden sm:inline-flex items-center gap-1 font-semibold">
														<span>🛞</span> Ver posiciones
													</button>
												</div>
											</td>
											<td class="px-3 py-3 text-center font-mono text-slate-300">{s.played ?? 0}</td>
											<td class="px-3 py-3 text-center font-mono text-emerald-400 font-semibold">{s.won ?? 0}</td>
											<td class="px-3 py-3 text-center font-mono text-red-400/80">{s.lost ?? 0}</td>
											<td class="px-3 py-3 text-center font-mono text-amber-300 font-semibold">{s.goals_for ?? 0}</td>
											<td class="px-3 py-3 text-center font-mono text-slate-400">{s.goals_against ?? 0}</td>
											<td class="px-3 py-3 text-center font-mono font-semibold {(s.goal_difference ?? 0) > 0 ? 'text-emerald-400' : (s.goal_difference ?? 0) < 0 ? 'text-red-400' : 'text-slate-400'}">
												{(s.goal_difference ?? 0) > 0 ? '+' : ''}{s.goal_difference ?? 0}
											</td>
											<td class="px-4 py-3 text-center font-score font-bold text-amber-400 text-base">{s.points ?? 0}</td>
										</tr>
									{/each}
								</tbody>
							</table>
						</div>
						<div class="standings-footer px-4 py-2.5 border-t text-xs">
							PJ = Carreras · PG = Victorias · PP = Derrotas · VLT = Vueltas completadas · Dif. VLT = Diferencia · PTS = Puntos
						</div>
					</div>
				</div>
			{/if}

			<!-- ── TABLA 8: MARATÓN DE MOSQUITOS ────────────────────────────────── -->
			{#if (selectedSport === 'all' || selectedSport === 'mosquito_marathon') && (mosquitoStandings.length > 0 || selectedSport === 'mosquito_marathon')}
				<div class="space-y-3">
					<div class="flex items-center justify-between">
						<div class="flex items-center gap-2">
							<span class="text-2xl">🦟</span>
							<div>
								<h3 class="text-lg font-black text-white">Tabla de Posiciones — Maratón de Mosquitos</h3>
								<p class="text-xs text-slate-400">Torneo nocturno de sigilo y picaduras</p>
							</div>
						</div>
						<span class="text-xs px-2.5 py-1 rounded-full font-bold bg-lime-500/15 text-lime-300 border border-lime-500/30">
							{mosquitoStandings.length} enjambres
						</span>
					</div>

					<div class="standings-box rounded-2xl overflow-hidden border shadow-xl">
						<div class="overflow-x-auto -mx-1 sm:mx-0">
							<table class="w-full text-sm min-w-[560px]">
								<thead>
									<tr class="standings-head-row">
										<th class="px-4 py-3 text-left text-xs section-label w-10">#</th>
										<th class="px-4 py-3 text-left text-xs section-label">Enjambre</th>
										<th class="px-3 py-3 text-center text-xs section-label">PJ</th>
										<th class="px-3 py-3 text-center text-xs section-label">PG</th>
										<th class="px-3 py-3 text-center text-xs section-label">PP</th>
										<th class="px-3 py-3 text-center text-xs section-label">Picaduras (PC)</th>
										<th class="px-3 py-3 text-center text-xs section-label">Repelente</th>
										<th class="px-3 py-3 text-center text-xs section-label">Dif. PC</th>
										<th class="px-4 py-3 text-center text-xs section-label text-lime-400">PTS</th>
									</tr>
								</thead>
								<tbody>
									{#if mosquitoStandings.length === 0}
										<tr><td colspan="9" class="text-center py-6 text-slate-500 text-xs">No hay enjambres registrados todavía</td></tr>
									{/if}
									{#each mosquitoStandings as s, i}
										{@const accentLeft = i === 0 ? '#84cc16' : i === 1 ? '#a3e635' : '#64748b'}
										{@const tColor = teamColor(s.team_id)}
										<tr class="standings-row border-b border-slate-800/50 transition-colors"
											style="border-left: 3px solid {accentLeft};">
											<td class="px-4 py-3 text-center">
												{#if i === 0}<span class="text-base">🥇</span>
												{:else if i === 1}<span class="text-base">🥈</span>
												{:else if i === 2}<span class="text-base">🥉</span>
												{:else}<span class="text-xs text-slate-500 font-mono">{i + 1}</span>{/if}
											</td>
											<td class="px-4 py-3">
												<div class="flex items-center gap-3">
													<div class="w-8 h-8 rounded-lg flex items-center justify-center text-xs font-black shrink-0"
														style="background: {tColor}20; border: 1px solid {tColor}40; color: {tColor};">
														{teamInitial(s.team_id)}
													</div>
													<div class="flex-1 min-w-0">
														<p class="font-bold text-white text-sm leading-tight truncate">{teamName(s.team_id)}</p>
														<span class="text-xs font-mono text-slate-500">{teamShort(s.team_id)}</span>
													</div>
													<button type="button" onclick={() => showTeamPitch(s.team_id)} class="standings-btn-pitch text-xs px-2.5 py-1 rounded transition hidden sm:inline-flex items-center gap-1 font-semibold">
														<span>🦟</span> Ver posiciones
													</button>
												</div>
											</td>
											<td class="px-3 py-3 text-center font-mono text-slate-300">{s.played ?? 0}</td>
											<td class="px-3 py-3 text-center font-mono text-emerald-400 font-semibold">{s.won ?? 0}</td>
											<td class="px-3 py-3 text-center font-mono text-red-400/80">{s.lost ?? 0}</td>
											<td class="px-3 py-3 text-center font-mono text-lime-300 font-semibold">{s.goals_for ?? 0}</td>
											<td class="px-3 py-3 text-center font-mono text-slate-400">{s.goals_against ?? 0}</td>
											<td class="px-3 py-3 text-center font-mono font-semibold {(s.goal_difference ?? 0) > 0 ? 'text-emerald-400' : (s.goal_difference ?? 0) < 0 ? 'text-red-400' : 'text-slate-400'}">
												{(s.goal_difference ?? 0) > 0 ? '+' : ''}{s.goal_difference ?? 0}
											</td>
											<td class="px-4 py-3 text-center font-score font-bold text-lime-400 text-base">{s.points ?? 0}</td>
										</tr>
									{/each}
								</tbody>
							</table>
						</div>
						<div class="standings-footer px-4 py-2.5 border-t text-xs">
							PJ = Salidas · PG = Ganados · PP = Perdidos · PC = Picaduras válidas · Dif. PC = Diferencia · PTS = Puntos
						</div>
					</div>
				</div>
			{/if}
		</div>
	{/if}
{/if}

{/if}

<!-- MODAL DE CANCHA TÁCTICA PARA PÚBLICO -->
{#if pitchModalTeam}
	<div
		class="fixed inset-0 z-50 flex items-center justify-center p-4 bg-slate-950/85 backdrop-blur-sm animate-fade-in"
		role="dialog"
		aria-modal="true"
		tabindex="-1"
		onclick={(e) => e.target === e.currentTarget && (pitchModalTeam = null)}
		onkeydown={(e) => e.key === 'Escape' && (pitchModalTeam = null)}
	>
		<div class="team-detail-modal-box glass-card w-full max-w-2xl max-h-[90vh] overflow-y-auto p-5 rounded-2xl border border-slate-700 shadow-2xl flex flex-col gap-4">
			<div class="flex items-center justify-between border-b border-slate-800 pb-3">
				<div class="flex items-center gap-3">
					<div class="w-10 h-10 rounded-xl flex items-center justify-center font-black text-lg" style="background: {teamColor(pitchModalTeam.id)}25; color: {teamColor(pitchModalTeam.id)};">
						{teamInitial(pitchModalTeam.id)}
					</div>
					<div>
						<h3 class="text-base font-bold text-white leading-tight">{pitchModalTeam.name}</h3>
						<p class="text-xs text-slate-400 font-mono">Alineación y Plantilla en Cancha</p>
					</div>
				</div>
				<button
					type="button"
					onclick={() => (pitchModalTeam = null)}
					class="text-slate-400 hover:text-white p-1 rounded-lg text-lg"
				>
					✕
				</button>
			</div>

			{#if (pitchModalTeam.sport === 'basketball')}
				<BasketballCourt
					players={pitchModalTeam.players || []}
					interactive={false}
					teamName={pitchModalTeam.name}
					teamColor="#f59e0b"
				/>
			{:else if (pitchModalTeam.sport === 'volleyball')}
				<VolleyballCourt
					players={pitchModalTeam.players || []}
					interactive={false}
					teamName={pitchModalTeam.name}
					teamColor="#8b5cf6"
				/>
			{:else if (pitchModalTeam.sport === 'underwater_chess')}
				<UnderwaterChessBoard
					players={pitchModalTeam.players || []}
					interactive={false}
					teamName={pitchModalTeam.name}
					teamColor="#06b6d4"
				/>
			{:else if (pitchModalTeam.sport === 'aura_battle')}
				<AuraBattleArena
					players={pitchModalTeam.players || []}
					interactive={false}
					teamName={pitchModalTeam.name}
					teamColor="#a855f7"
				/>
			{:else if (pitchModalTeam.sport === 'sperm_triathlon')}
				<SpermTriathlonTrack
					players={pitchModalTeam.players || []}
					interactive={false}
					teamName={pitchModalTeam.name}
					teamColor="#06b6d4"
				/>
			{:else if (pitchModalTeam.sport === 'tire_race')}
				<TireRaceTrack
					players={pitchModalTeam.players || []}
					interactive={false}
					teamName={pitchModalTeam.name}
					teamColor="#f97316"
				/>
			{:else if (pitchModalTeam.sport === 'mosquito_marathon')}
				<MosquitoRadar
					players={pitchModalTeam.players || []}
					interactive={false}
					teamName={pitchModalTeam.name}
					teamColor="#84cc16"
				/>
			{:else}
				<SoccerPitch
					players={pitchModalTeam.players || []}
					interactive={false}
					teamName={pitchModalTeam.name}
					teamColor={teamColor(pitchModalTeam.id)}
				/>
			{/if}

			<div class="flex justify-end pt-2 border-t border-slate-800">
				<button
					type="button"
					onclick={() => (pitchModalTeam = null)}
					class="px-4 py-2 text-xs font-semibold rounded-lg bg-slate-800 text-slate-300 hover:text-white transition"
				>
					Cerrar
				</button>
			</div>
		</div>
	</div>
{/if}
<style>
	/* ── Pestañas ─────────────────────────────────────────────────────────────── */
	.tab-pill {
		display: flex;
		align-items: center;
		gap: 0.4rem;
		padding: 0.5rem 1.1rem;
		border-radius: 0.6rem;
		font-size: 0.85rem;
		font-weight: 600;
		transition: all 0.15s ease;
	}
	.tab-pill-active {
		background: #10b981;
		color: white;
		box-shadow: 0 2px 10px rgba(16,185,129,0.3);
	}
	.tab-pill-inactive { color: #64748b; }
	.tab-pill-inactive:hover { color: #e2e8f0; }

	/* ── Botones de jornada ─────────────────────────────────────────────────── */
	.round-btn {
		display: flex;
		align-items: center;
		gap: 0.4rem;
		padding: 0.4rem 0.85rem;
		border-radius: 0.5rem;
		font-size: 0.8rem;
		font-weight: 700;
		letter-spacing: 0.02em;
		transition: all 0.15s;
		white-space: nowrap;
	}
	.round-btn-active {
		background: #10b981;
		color: white;
		box-shadow: 0 2px 8px rgba(16,185,129,0.35);
	}
	.round-btn-inactive {
		background: #111827;
		color: #64748b;
		border: 1px solid rgba(148,163,184,0.12);
	}
	.round-btn-inactive:hover { color: #e2e8f0; border-color: rgba(148,163,184,0.25); }

	/* ── Tarjetas de partido ────────────────────────────────────────────────── */
	.match-card-new {
		display: flex;
		align-items: stretch;
		background: #111827;
		border: 1px solid rgba(148,163,184,0.08);
		border-radius: 1rem;
		overflow: hidden;
		transition: border-color 0.15s, box-shadow 0.15s;
	}
	.match-card-new:hover {
		border-color: rgba(148,163,184,0.2);
		box-shadow: 0 4px 20px rgba(0,0,0,0.2);
	}
	.match-card-live-border { border-color: rgba(16,185,129,0.3); }
	.match-card-live-border:hover { border-color: rgba(16,185,129,0.5); }

	.match-status-bar { width: 4px; flex-shrink: 0; }
	.match-inner { flex: 1; padding: 1rem 1.25rem; }

	/* Badge de estado en tarjeta de partido */
	.status-pill {
		display: inline-flex;
		align-items: center;
		gap: 0.35rem;
		font-size: 0.65rem;
		font-weight: 800;
		padding: 0.2rem 0.7rem;
		border-radius: 9999px;
		text-transform: uppercase;
		letter-spacing: 0.06em;
	}

	/* Escudo del equipo */
	.team-shield {
		width: 2.25rem;
		height: 2.25rem;
		border-radius: 0.5rem;
		border: 1.5px solid;
		display: flex;
		align-items: center;
		justify-content: center;
		font-size: 0.9rem;
		font-weight: 900;
		flex-shrink: 0;
	}

	/* Marcador central */
	.score-center {
		padding: 0.5rem 1rem;
		border-radius: 0.625rem;
		min-width: 80px;
		display: flex;
		align-items: center;
		justify-content: center;
		flex-shrink: 0;
	}
	.score-live   { background: rgba(16,185,129,0.12); border: 1.5px solid rgba(16,185,129,0.3); color: #34d399; }
	.score-done   { background: rgba(99,102,241,0.1);  border: 1.5px solid rgba(99,102,241,0.25); color: #a5b4fc; }
	.score-upcoming { background: #0b1120; border: 1.5px solid rgba(148,163,184,0.1); }

	/* Píldora LIVE del encabezado */
	.live-badge-pill {
		display: inline-flex;
		align-items: center;
		gap: 0.35rem;
		font-size: 0.65rem;
		font-weight: 800;
		padding: 0.25rem 0.7rem;
		border-radius: 9999px;
		background: rgba(16,185,129,0.15);
		color: #34d399;
		border: 1px solid rgba(16,185,129,0.3);
		letter-spacing: 0.08em;
		text-transform: uppercase;
	}
</style>
