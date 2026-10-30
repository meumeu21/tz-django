const TOAST_DELAY_MS = 5000;
const COPY_FEEDBACK_MS = 2000;

document.querySelectorAll('.toast').forEach((element) => {
  element.addEventListener('hidden.bs.toast', () => element.remove());
  bootstrap.Toast.getOrCreateInstance(element, { delay: TOAST_DELAY_MS }).show();
});

document.addEventListener('focusin', (event) => {
  if (event.target.matches('[data-select-on-focus]')) {
    event.target.select();
  }
});

document.addEventListener('click', async (event) => {
  const button = event.target.closest('[data-copy]');
  if (!button) {
    return;
  }
  button.dataset.label ??= button.textContent;
  clearTimeout(button.resetTimer);
  try {
    await navigator.clipboard.writeText(button.dataset.copy);
    button.textContent = 'Скопировано';
  } catch {
    button.textContent = 'Не удалось';
  }
  button.resetTimer = setTimeout(() => {
    button.textContent = button.dataset.label;
  }, COPY_FEEDBACK_MS);
});
