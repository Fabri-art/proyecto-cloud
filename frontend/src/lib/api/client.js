/**
 * lib/api/client.js
 *
 * Cliente HTTP centralizado para comunicarse con el backend FastAPI.
 * URL base: http://localhost:8001/api/v1
 *
 * USO:
 *   import { api } from '$lib/api/client';
 *   const teams = await api.get('/teams');
 *   const team  = await api.post('/teams', { name: 'Boca', ... });
 */

const BASE_URL =
	(typeof import.meta !== 'undefined' &&
		(import.meta.env?.PUBLIC_API_BASE_URL || import.meta.env?.VITE_API_BASE_URL)) ||
	'/api/v1';

/**
 * Realiza una petición al backend.
 * @param {string} path - Ruta relativa, ej: '/teams', '/tournaments/1/fixture'
 * @param {RequestInit} options - Opciones fetch (method, body, headers, etc.)
 * @returns {Promise<any>} - Datos JSON de la respuesta
 * @throws {Error} - Con mensaje del backend si hay error HTTP
 */
async function request(path, options = {}) {
	const url = `${BASE_URL}${path}`;

	const response = await fetch(url, {
		headers: {
			'Content-Type': 'application/json',
			...options.headers
		},
		...options
	});

	// Si la respuesta no es exitosa (2xx), lanzamos un error con el mensaje del backend
	if (!response.ok) {
		let message = `Error ${response.status}: ${response.statusText}`;
		try {
			const errorBody = await response.json();
			message = errorBody.detail || message;
		} catch {
			// Si el body no es JSON lo ignoramos
		}
		throw new Error(message);
	}

	// Si la respuesta está vacía (204 No Content), retornamos null
	if (response.status === 204) return null;

	return response.json();
}

/** Objeto con métodos GET, POST, PATCH, DELETE */
export const api = {
	/** GET /path */
	get: (path) => request(path),

	/** POST /path con body JSON */
	post: (path, body) =>
		request(path, {
			method: 'POST',
			body: JSON.stringify(body)
		}),

	/** PATCH /path con body JSON parcial */
	patch: (path, body) =>
		request(path, {
			method: 'PATCH',
			body: JSON.stringify(body)
		}),

	/** DELETE /path */
	delete: (path) =>
		request(path, {
			method: 'DELETE'
		})
};

// ── Helpers específicos por dominio ─────────────────────────────────────────

/** Equipos */
export const teamsApi = {
	list: (tournamentId, includePlayers = false) => {
		const params = new URLSearchParams();
		if (tournamentId) params.set('tournament_id', tournamentId);
		if (includePlayers) params.set('include_players', 'true');
		const qs = params.toString() ? `?${params.toString()}` : '';
		return api.get(`/teams${qs}`);
	},
	get: (teamId) => api.get(`/teams/${teamId}`),
	create: (body) => api.post('/teams', body),
	addPlayer: (teamId, body) => api.post(`/teams/${teamId}/players`, body)
};

/** Fixture (calendario de partidos) */
export const fixtureApi = {
	/** GET /tournaments/{id}/fixture → FixtureRead agrupado por jornada */
	get: (tournamentId) => api.get(`/tournaments/${tournamentId}/fixture`),

	/** POST /tournaments/{id}/fixture/generate — Primera generación (falla si ya existe) */
	generate: (tournamentId) => api.post(`/tournaments/${tournamentId}/fixture/generate`),

	/**
	 * POST /tournaments/{id}/fixture/generate con force=true.
	 * Elimina el fixture existente (incluyendo partidos jugados) y genera uno nuevo
	 * en una sola transacción atómica.
	 */
	generateForce: (tournamentId) =>
		api.post(`/tournaments/${tournamentId}/fixture/generate`, { force: true }),

	/**
	 * DELETE /tournaments/{id}/fixture
	 * @param {boolean} force - Si true, elimina aunque haya partidos jugados/finalizados.
	 *   Por defecto false (retorna 409 si hay partidos con resultados).
	 */
	deleteFixture: (tournamentId, force = false) =>
		api.delete(`/tournaments/${tournamentId}/fixture?force=${force}`)
};

/** Partidos */
export const matchesApi = {
	list: (tournamentId, matchday) => {
		const params = new URLSearchParams();
		if (tournamentId) params.append('tournament_id', tournamentId);
		if (matchday) params.append('matchday', matchday);
		const qs = params.toString() ? `?${params.toString()}` : '';
		return api.get(`/matches${qs}`);
	},
	get: (matchId) => api.get(`/matches/${matchId}`),
	updateStatus: (matchId, status) => api.patch(`/matches/${matchId}/status`, { status }),
	/** Update live score without finishing the match */
	updateScore: (matchId, homeScore, awayScore) =>
		api.patch(`/matches/${matchId}/score`, { home_score: homeScore, away_score: awayScore }),
	registerResult: (matchId, body) => api.patch(`/matches/${matchId}/result`, body)
};

/** Tabla de posiciones */
export const standingsApi = {
	get: (tournamentId) => api.get(`/tournaments/${tournamentId}/standings`)
};

/** Health check del backend */
export const healthApi = {
	check: () => api.get('/health')
};
