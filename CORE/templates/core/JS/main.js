document.addEventListener('DOMContentLoaded', function() {
    const indicadorSelect = document.getElementById('indicador');
    const obtenerBtn = document.querySelector('.btn-primary');

    if (indicadorSelect && obtenerBtn) {
        indicadorSelect.addEventListener('change', function() {
            const selectedOption = this.value;
            obtenerBtn.textContent = `Obtener datos de ${selectedOption.toUpperCase()}`;
        });
    }
});