document.addEventListener('DOMContentLoaded', function () {
    // Бургер-меню
    const burger = document.getElementById('burger');
    const nav = document.getElementById('nav');
    if (burger && nav) {
        burger.addEventListener('click', function () {
            const opened = nav.classList.toggle('active');
            burger.classList.toggle('active', opened);
            burger.setAttribute('aria-expanded', String(opened));
        });
    }

    // Мобильные фильтры
    const filterToggle = document.getElementById('filterToggle');
    const filters = document.getElementById('filters');
    if (filterToggle && filters) {
        filterToggle.addEventListener('click', function () {
            filters.classList.toggle('active');
        });
    }

    // Поиск и избранное в каталоге
    const searchInput = document.getElementById('carSearch');
    const cards = Array.from(document.querySelectorAll('.catalog-card'));
    const visibleCount = document.getElementById('visibleCount');
    const dynamicEmpty = document.getElementById('dynamicEmpty');
    const searchStatus = document.getElementById('catalogSearchStatus');
    const favoritesToggle = document.getElementById('favoritesToggle');
    const favoritesCount = document.getElementById('favoritesCount');
    const classSelect = document.getElementById('class');
    const maxPriceSelect = document.getElementById('max_price');

    if (!searchInput || cards.length === 0) return;

    let favorites = [];
    let favoritesOnly = false;
    let apiTimer = null;
    let apiController = null;

    try {
        const saved = JSON.parse(localStorage.getItem('autorentFavorites') || '[]');
        favorites = Array.isArray(saved) ? saved.map(String) : [];
    } catch (error) {
        favorites = [];
    }

    function applySearch() {
        const query = searchInput.value.trim().toLocaleLowerCase('ru');
        let count = 0;

        cards.forEach(function (card) {
            const name = (card.dataset.name || card.querySelector('h3')?.textContent || '')
                .trim().toLocaleLowerCase('ru');
            const id = String(card.dataset.carId || '');
            const nameMatches = !query || name.includes(query);
            const favoriteMatches = !favoritesOnly || favorites.includes(id);
            const show = nameMatches && favoriteMatches;

            card.classList.toggle('hidden-by-filter', !show);
            if (show) count++;

            const button = card.querySelector('.favorite-button');
            if (button) {
                const selected = favorites.includes(id);
                button.textContent = selected ? '♥' : '♡';
                button.classList.toggle('selected', selected);
                button.title = selected ? 'Удалить из избранного' : 'Добавить в избранное';
                button.setAttribute('aria-label', button.title);
            }
        });

        if (visibleCount) visibleCount.textContent = String(count);
        if (dynamicEmpty) dynamicEmpty.style.display = count === 0 ? 'block' : 'none';
        if (favoritesCount) favoritesCount.textContent = String(favorites.length);
    }

    // Собственный Django API вызывается через fetch. Поиск на странице не зависит
    // от ответа API и поэтому продолжает работать даже при временной ошибке сервера.
    async function requestCatalogAPI() {
        if (apiController) apiController.abort();
        apiController = new AbortController();

        const params = new URLSearchParams();
        params.set('q', searchInput.value.trim());
        if (classSelect && classSelect.value) params.set('class', classSelect.value);
        if (maxPriceSelect && maxPriceSelect.value) params.set('max_price', maxPriceSelect.value);

        try {
            const response = await fetch('/api/catalog/?' + params.toString(), {
                method: 'GET',
                headers: { 'X-Requested-With': 'XMLHttpRequest' },
                signal: apiController.signal
            });
            if (!response.ok) throw new Error('HTTP ' + response.status);
            const data = await response.json();
            if (!Array.isArray(data.cars)) throw new Error('Неверный формат ответа API');
            if (searchStatus) searchStatus.textContent = 'Поиск выполнен. Найдено в базе: ' + data.count;
        } catch (error) {
            if (error.name === 'AbortError') return;
            if (searchStatus) searchStatus.textContent = 'Поиск по названию работает на странице.';
            console.error('Ошибка API каталога:', error);
        }
    }

    function onSearchChanged() {
        applySearch();
        window.clearTimeout(apiTimer);
        apiTimer = window.setTimeout(requestCatalogAPI, 250);
    }

    searchInput.addEventListener('input', onSearchChanged);

    cards.forEach(function (card) {
        const button = card.querySelector('.favorite-button');
        if (!button) return;
        button.addEventListener('click', function () {
            const id = String(card.dataset.carId || '');
            favorites = favorites.includes(id)
                ? favorites.filter(function (item) { return item !== id; })
                : favorites.concat(id);
            try {
                localStorage.setItem('autorentFavorites', JSON.stringify(favorites));
            } catch (error) {
                console.warn('Не удалось сохранить избранное.', error);
            }
            applySearch();
        });
    });

    if (favoritesToggle) {
        favoritesToggle.addEventListener('click', function () {
            favoritesOnly = !favoritesOnly;
            favoritesToggle.classList.toggle('active', favoritesOnly);
            applySearch();
        });
    }

    if (classSelect) classSelect.addEventListener('change', requestCatalogAPI);
    if (maxPriceSelect) maxPriceSelect.addEventListener('change', requestCatalogAPI);

    applySearch();
    requestCatalogAPI();
});
