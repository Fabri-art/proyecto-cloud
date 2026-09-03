<script>
	/**
	 * AdminPinModal.svelte
	 *
	 * Modal que solicita el PIN de administrador.
	 * Se muestra cuando el usuario intenta acceder a rutas protegidas.
	 *
	 * Props:
	 *   onSuccess — callback a ejecutar si el PIN es correcto
	 *   onCancel  — callback al cancelar (ej: volver a /publico)
	 */
	import { auth } from '$lib/stores/auth';

	let { onSuccess, onCancel } = $props();

	let pin = $state('');
	let error = $state('');
	let loading = $state(false);
	let inputRef = $state(null);

	function handleSubmit() {
		loading = true;
		error = '';

		// Pequeño delay para evitar timing attacks obvios
		setTimeout(() => {
			const ok = auth.login(pin);
			loading = false;
			if (ok) {
				pin = '';
				onSuccess?.();
			} else {
				error = 'PIN incorrecto. Inténtalo de nuevo.';
				pin = '';
				inputRef?.focus();
			}
		}, 300);
	}

	function handleKeydown(e) {
		if (e.key === 'Enter') handleSubmit();
		if (e.key === 'Escape') onCancel?.();
	}
</script>

<!-- Overlay -->
<div
	class="fixed inset-0 z-50 flex items-center justify-center p-4 bg-slate-950/90"
	role="dialog"
	aria-modal="true"
	aria-label="Acceso de administrador"
>
	<div class="w-full max-w-sm bg-slate-900 border border-slate-700 rounded-2xl shadow-2xl overflow-hidden">
		<!-- Encabezado -->
		<div class="px-6 py-5 border-b border-slate-800 flex items-center gap-3">
			<div class="w-10 h-10 rounded-xl bg-emerald-600/20 border border-emerald-600/30 flex items-center justify-center text-xl">
				🔐
			</div>
			<div>
				<h2 class="font-black text-white text-lg leading-tight">Área de Administrador</h2>
				<p class="text-slate-400 text-xs mt-0.5">Ingresa el PIN para continuar</p>
			</div>
		</div>

		<!-- Cuerpo -->
		<div class="px-6 py-6 space-y-4">
			<div>
				<label for="admin-pin" class="block text-xs font-semibold text-slate-400 mb-1.5 uppercase tracking-wider">
					PIN de Acceso
				</label>
				<input
					id="admin-pin"
					bind:this={inputRef}
					bind:value={pin}
					type="password"
					inputmode="numeric"
					maxlength="8"
					placeholder="••••"
					onkeydown={handleKeydown}
					class="w-full px-4 py-3 rounded-xl bg-slate-800 border text-white text-lg font-mono text-center tracking-widest placeholder:text-slate-600 outline-none transition {error
						? 'border-red-500 focus:border-red-400'
						: 'border-slate-700 focus:border-emerald-500'}"
					autocomplete="off"
				/>
				{#if error}
					<p class="text-red-400 text-xs mt-2 flex items-center gap-1.5">
						<span>⚠️</span> {error}
					</p>
				{/if}
			</div>

			<div class="flex gap-3 pt-1">
				<button
					type="button"
					onclick={onCancel}
					class="flex-1 py-2.5 rounded-xl text-sm font-semibold text-slate-400 hover:text-white bg-slate-800 hover:bg-slate-700 transition"
				>
					Cancelar
				</button>
				<button
					type="button"
					onclick={handleSubmit}
					disabled={!pin || loading}
					class="flex-1 py-2.5 rounded-xl text-sm font-bold text-white bg-emerald-600 hover:bg-emerald-500 shadow-lg shadow-emerald-950 transition disabled:opacity-40 disabled:cursor-not-allowed flex items-center justify-center gap-2"
				>
					{#if loading}
						<span class="w-4 h-4 border-2 border-white border-t-transparent rounded-full animate-spin"></span>
					{:else}
						Entrar
					{/if}
				</button>
			</div>
		</div>

		<!-- Pie -->
		<div class="px-6 py-3 bg-slate-950/40 border-t border-slate-800 text-center">
			<p class="text-xs text-slate-600">
				Solo para delegados y árbitros del torneo
			</p>
		</div>
	</div>
</div>
