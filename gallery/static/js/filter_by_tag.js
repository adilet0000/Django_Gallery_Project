document.addEventListener('DOMContentLoaded', function() {
    const filterForm = document.querySelector('.filter-form');
    if (!filterForm) return;

    filterForm.addEventListener('submit', function(e) {
        e.preventDefault();
        
        const formData = new FormData(this);
        const params = new URLSearchParams(formData);

        fetch(`${window.location.pathname}?${params}`, {
            headers: {
                'X-Requested-With': 'XMLHttpRequest'
            }
        })
        .then(response => response.text())
        .then(html => {
            const parser = new DOMParser();
            const doc = parser.parseFromString(html, 'text/html');
            const newContent = doc.querySelector('.models-flex-container');  // Замените на ваш класс с контентом
            if (newContent) {
                document.querySelector('.models-flex-container').innerHTML = newContent.innerHTML;
            }
        });
    });
});