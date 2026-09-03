/**
 * lib/stores/toast.js
 *
 * Sistema global de notificaciones tipo "toast" (popup de éxito/error).
 * Las páginas lo importan para mostrar mensajes al usuario sin recargar.
 *
 * USO:
 *   import { toast } from '$lib/stores/toast';
 *   toast.success('¡Equipo registrado!');
 *   toast.error('No se pudo conectar con el servidor');
 *   toast.info('Cargando datos...');
 */

import { writable } from 'svelte/store';

/**
 * Store reactivo que guarda la lista de toasts activos.
 * Cada toast tiene: { id, type, message }
 */
const { subscribe, update } = writable([]);

let nextId = 0;

/**
 * Agrega un toast y lo elimina automáticamente después de `duration` ms.
 * @param {'success'|'error'|'info'} type
 * @param {string} message
 * @param {number} duration - milisegundos antes de desaparecer
 */
function addToast(type, message, duration = 3500) {
	const id = ++nextId;

	update((list) => [...list, { id, type, message }]);

	setTimeout(() => {
		update((list) => list.filter((t) => t.id !== id));
	}, duration);
}

export const toasts = { subscribe };

export const toast = {
	success: (msg, duration) => addToast('success', msg, duration),
	error: (msg, duration) => addToast('error', msg, duration),
	info: (msg, duration) => addToast('info', msg, duration)
};
