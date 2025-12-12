// Fonction pour basculer entre livre physique et numérique
function toggleBookType() {
    const physicalRadio = document.querySelector('input[name="book_type"][value="physical"]');
    const digitalRadio = document.querySelector('input[name="book_type"][value="digital"]');
    const physicalFields = document.getElementById('physical-fields');
    const digitalFields = document.getElementById('digital-fields');
    // IMPORTANT: Cibler spécifiquement le champ file (PDF/EPUB) par son nom
    // et NON par type="file" pour ne pas affecter cover_image
    const fileInput = document.querySelector('input[name="file"]');

    if (physicalRadio.checked) {
        physicalFields.style.display = 'block';
        digitalFields.style.display = 'none';
        if (fileInput) {
            fileInput.removeAttribute('required');
            fileInput.disabled = true;
        }
    } else {
        physicalFields.style.display = 'none';
        digitalFields.style.display = 'block';
        if (fileInput) {
            fileInput.setAttribute('required', 'required');
            fileInput.disabled = false;
        }
    }
}

// Initialiser au chargement
document.addEventListener('DOMContentLoaded', function() {
    toggleBookType();
});
