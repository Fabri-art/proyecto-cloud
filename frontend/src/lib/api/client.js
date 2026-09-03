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

const BASE_URL = 'http://localhost:8001/api/v1';

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
	list: (tournamentId) => {
		const qs = tournamentId ? `?tournament_id=${tournamentId}` : '';
		return api.get(`/teams${qs}`);
	},
	get: (teamId) => api.get(`/teams/${teamId}`),
	create: (body) => api.post('/teams', body),
	addPlayer: (teamId, body) => api.post(`/teams/${teamId}/players`, body)
};

/** Fixture (calendario de partidos) */
export const fixtureApi = {
	generate: (tournamentId) => api.post(`/tournaments/${tournamentId}/fixture/generate`),
	get: (tournamentId) => api.get(`/tournaments/${tournamentId}/fixture`)
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
