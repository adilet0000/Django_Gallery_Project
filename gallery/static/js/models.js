document.addEventListener('DOMContentLoaded', function() {
    const filterForm = document.querySelector('.filter-form');
    const modelsContainer = document.querySelector('.models-flex-container');
    const paginationContainer = document.querySelector('.pagination')?.parentNode;
    
    // Обработчик для формы фильтрации
    if (filterForm) {
        filterForm.addEventListener('submit', function(e) {
            e.preventDefault();
            
            const formData = new FormData(this);
            const params = new URLSearchParams(formData);
            
            // Сбрасываем страницу на первую при смене сортировки
            params.set('page', '1');
            
            loadContentWithRefresh(params);
        });
    }
    
    // Обработчик для пагинации
    document.addEventListener('click', function(e) {
        if (e.target.closest('.pagination a')) {
            e.preventDefault();
            
            const link = e.target.closest('.pagination a');
            const url = new URL(link.href);
            const params = url.searchParams;
            
            // Добавляем параметр сортировки, если он существует в URL
            const currentParams = new URLSearchParams(window.location.search);
            if (currentParams.has('sort_by')) {
                params.set('sort_by', currentParams.get('sort_by'));
            }
            
            loadContentWithRefresh(params);
        }
    });
    
    // Функция для загрузки контента с обновлением URL
    function loadContentWithRefresh(params) {
        // Обновляем URL без перезагрузки страницы
        history.pushState(null, '', `${window.location.pathname}?${params}`);
        
        // Загружаем страницу
        window.location.reload();
    }
});