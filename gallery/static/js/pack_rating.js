document.addEventListener('DOMContentLoaded', function() {
    const form = document.querySelector('.rating-form');
    if (!form) return;

    form.addEventListener('submit', function(e) {
        e.preventDefault();
        
        const formData = new FormData();
        const score = form.querySelector('input[name="rating"]:checked')?.value;
        
        if (!score) {
            return;
        }

        formData.append('score', score);
        formData.append('csrfmiddlewaretoken', form.querySelector('[name=csrfmiddlewaretoken]').value);

        const appLabel = form.dataset.appLabel;
        const modelName = form.dataset.modelName;
        const slug = form.dataset.slug;

        fetch(`/rate/${appLabel}/${modelName}/${slug}/`, {
            method: 'POST',
            body: formData,
            headers: {
                'X-Requested-With': 'XMLHttpRequest'
            }
        })
        .then(response => response.json())
        .then(data => {
            // Обновляем рейтинг и количество оценок
            const averageRating = document.querySelector('.average-rating');
            const totalRatings = document.querySelector('.total-ratings');
            
            if (averageRating) {
                averageRating.textContent = `Средняя оценка: ${data.average_rating}`;
            }
            if (totalRatings) {
                totalRatings.textContent = `Количество оценок: ${data.total_ratings}`;
            }

            // Сбрасываем выбранную звезду
            const checkedStar = form.querySelector('input[name="rating"]:checked');
            if (checkedStar) {
                checkedStar.checked = false;
            }
        });
    });
});