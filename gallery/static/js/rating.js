document.addEventListener('DOMContentLoaded', function() {
    const form = document.querySelector('.rating-form');
    if (!form) return;

    form.addEventListener('submit', function(e) {
        e.preventDefault();
        
        const formData = new FormData();
        const score = form.querySelector('input[name="rating"]:checked')?.value;
        
        if (!score) {
            alert('Пожалуйста, выберите оценку');
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
            // Обновляем информацию о рейтинге
            const ratingElement = document.querySelector('.packs-rating');
            const ratingCountElement = document.querySelector('.rating-count');
            
            if (ratingElement) {
                ratingElement.textContent = `Средний рейтинг: ${data.average_rating}`;
            }
            if (ratingCountElement) {
                ratingCountElement.textContent = `Количество оценок: ${data.total_ratings}`;
            }

            // Сбрасываем выбранную звезду
            const checkedStar = form.querySelector('input[name="rating"]:checked');
            if (checkedStar) {
                checkedStar.checked = false;
            }
        })
        .catch(error => {
            console.error('Error:', error);
            alert('Произошла ошибка при отправке оценки');
        });
    });
});