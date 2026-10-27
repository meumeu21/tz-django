document.querySelectorAll('.toast').forEach((element) => {
  element.addEventListener('hidden.bs.toast', () => element.remove());
  bootstrap.Toast.getOrCreateInstance(element, { delay: 5000 }).show();
});
