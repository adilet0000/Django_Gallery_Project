// static/js/subscription.js
document.addEventListener('DOMContentLoaded', function() {
    const subscriptionButtons = document.querySelector('.subscription-buttons');
    if (!subscriptionButtons) return;

    const handleSubscription = async (e) => {
        const button = e.target;
        if (!button.matches('button')) return;
        
        e.preventDefault();
        
        const form = button.closest('form');
        const url = form.action;
        const csrfToken = document.querySelector('[name=csrfmiddlewaretoken]').value;

        try {
            const response = await fetch(url, {
                method: 'POST',
                headers: {
                    'X-CSRFToken': csrfToken,
                    'X-Requested-With': 'XMLHttpRequest'
                },
                credentials: 'same-origin'
            });

            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }

            const data = await response.json();

            // Обновляем количество подписчиков
            const subscribersCount = document.querySelector('.packs-subscribers');
            if (subscribersCount) {
                subscribersCount.textContent = `Подписчиков: ${data.subscribers_count}`;
            }

            // Обновляем кнопки
            subscriptionButtons.innerHTML = data.button_html;

        } catch (error) {
            console.error('Error:', error);
            alert(`Произошла ошибка: ${error.message}`);
        }
    };

    subscriptionButtons.addEventListener('click', handleSubscription);
});