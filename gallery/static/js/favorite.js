document.addEventListener('DOMContentLoaded', function () {
    const favoriteForms = document.querySelectorAll('.favorite-form');

    if (!favoriteForms.length) return;

    favoriteForms.forEach(form => {
        form.addEventListener('submit', function (e) {
            e.preventDefault();

            const url = form.action;
            const formData = new FormData(form);

            fetch(url, {
                method: 'POST',
                body: formData,
                headers: {
                    'X-Requested-With': 'XMLHttpRequest'
                }
            })
                .then(response => response.json())
                .then(data => {
                    if (data.success) {
                        toggleFavoriteButton(form, data.is_favorite, data.new_action_url);
                    }
                })
                .catch(error => {
                    console.error('Ошибка:', error);
                });
        });
    });

    function toggleFavoriteButton(form, isFavorite, newActionUrl) {
        const button = form.querySelector('button[type="submit"]');
        form.action = newActionUrl;

        button.classList.toggle('btn-success', !isFavorite);
        button.classList.toggle('btn-danger', isFavorite);
        button.textContent = isFavorite ? 'Удалить из избранного' : 'Добавить в избранное';
    }
});
