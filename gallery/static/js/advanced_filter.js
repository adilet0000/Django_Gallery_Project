document.addEventListener('DOMContentLoaded', function() {
    const filterForm = document.querySelector('.filter-form');
    if (!filterForm) return;

    const updateResults = () => {
        const formData = new FormData(filterForm);
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
            const newContent = doc.querySelector('.filtered-results');
            if (newContent) {
                document.querySelector('.filtered-results').innerHTML = newContent.innerHTML;
            }
        });
    };

    filterForm.addEventListener('submit', function(e) {
        e.preventDefault();
        updateResults();
    });

    filterForm.querySelector('select[name="sort_by"]').addEventListener('change', function() {
        updateResults();
    });
});