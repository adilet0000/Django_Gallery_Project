const searchInput = document.getElementById('search-input');
const suggestionsList = document.getElementById('search-suggestions');

searchInput.addEventListener('input', function () {
   const query = this.value.trim();

   if (query.length > 0) {
      fetch(`/autocomplete/?q=${encodeURIComponent(query)}`)
         .then(response => response.json())
         .then(data => {
            suggestionsList.innerHTML = '';

            data.results.forEach(item => {
               const suggestionItem = document.createElement('li');
               suggestionItem.classList.add('suggestion-item');

               suggestionItem.innerHTML = `
                        <a href="${item.url}" class="suggestion-link">
                            ${item.type === 'model' ? 'Модель: ' : 'Пак: '} ${item.name}
                        </a>
                    `;

               suggestionsList.appendChild(suggestionItem);
            });

            suggestionsList.style.display = 'block';
         });
   } else {
      suggestionsList.innerHTML = '';
      suggestionsList.style.display = 'none';
   }
});

document.addEventListener('click', function (e) {
   if (!searchInput.contains(e.target) && !suggestionsList.contains(e.target)) {
      suggestionsList.style.display = 'none';
   }
});
