/**
 * lib/stores/auth.js
 *
 * Store simple de autenticación para el panel de administrador.
 * Usa localStorage para persistir la sesión hasta 8 horas.
 *
 * PIN por defecto: 1234  (configurable en ADMIN_PIN)
 *
 * Uso:
 *   import { auth } from '$lib/stores/auth';
 *   $auth.isAdmin  → true/false
 *   auth.login('1234')  → true si PIN correcto
 *   auth.logout()
 */

const ADMIN_PIN =
	(typeof import.meta !== 'undefined' &&
		(import.meta.env?.PUBLIC_ADMIN_PIN || import.meta.env?.VITE_ADMIN_PIN)) ||
	'1234';
const SESSION_KEY = 'nc_admin_session';
const SESSION_HOURS = 8;

function createAuthStore() {
	// ── Inicializar estado desde localStorage ──────────────────────────────────
	function loadSession() {
		if (typeof window === 'undefined') return false; // SSR guard
		try {
			const raw = localStorage.getItem(SESSION_KEY);
			if (!raw) return false;
			const { expiresAt } = JSON.parse(raw);
			return Date.now() < expiresAt;
		} catch {
			return false;
		}
	}

	// ── Estado reactivo con Svelte 5 runes (pero exportado como objeto) ────────
	// Como este archivo puede cargarse fuera de un componente, usamos un patrón
	// de suscripción manual compatible con Svelte 4 stores (writable-like).
	let _subscribers = [];
	let _isAdmin = loadSession();

	function notify() {
		for (const fn of _subscribers) fn(_isAdmin);
	}

	function login(pin) {
		if (pin === ADMIN_PIN) {
			const expiresAt = Date.now() + SESSION_HOURS * 60 * 60 * 1000;
			localStorage.setItem(SESSION_KEY, JSON.stringify({ expiresAt }));
			_isAdmin = true;
			notify();
			return true;
		}
		return false;
	}

	function logout() {
		localStorage.removeItem(SESSION_KEY);
		_isAdmin = false;
		notify();
	}

	function checkSession() {
		const valid = loadSession();
		if (_isAdmin !== valid) {
			_isAdmin = valid;
			notify();
		}
		return valid;
	}

	// Svelte store interface (subscribe / set / update)
	function subscribe(fn) {
		_subscribers.push(fn);
		fn(_isAdmin); // immediate call with current value
		return () => {
			_subscribers = _subscribers.filter((s) => s !== fn);
		};
	}

	return {
		subscribe,
		login,
		logout,
		checkSession,
		get isAdmin() {
			return _isAdmin;
		}
	};
}

export const auth = createAuthStore();
