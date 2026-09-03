<script>
	/**
	 * Toast.svelte — Contenedor visual de notificaciones.
	 * Se coloca UNA SOLA VEZ en el +layout.svelte y muestra los toasts globales.
	 * Los toasts desaparecen solos después de unos segundos.
	 */
	import { toasts } from '$lib/stores/toast';

	const iconMap = {
		success: '✅',
		error: '❌',
		info: 'ℹ️'
	};
</script>

<!-- Contenedor fijo en la esquina inferior derecha -->
<div class="fixed bottom-6 right-6 z-50 flex flex-col gap-3 pointer-events-none" aria-live="polite">
	{#each $toasts as t (t.id)}
		<div
			class="toast-{t.type} flex items-center gap-3 px-4 py-3 rounded-lg shadow-2xl text-white text-sm font-medium pointer-events-auto animate-fade-in-up max-w-xs"
			role="alert"
		>
			<span class="text-base shrink-0">{iconMap[t.type]}</span>
			<span>{t.message}</span>
		</div>
	{/each}
</div>
