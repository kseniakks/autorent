document.addEventListener('DOMContentLoaded', function () {
    const burger = document.getElementById('burger');
    const nav = document.getElementById('nav');

    if (burger && nav) {
        burger.addEventListener('click', function () {
            const isOpen = nav.classList.toggle('active');
            burger.classList.toggle('active', isOpen);
            burger.setAttribute('aria-expanded', isOpen);
        });
    }

    const filterToggle = document.getElementById('filterToggle');
    const filters = document.getElementById('filters');

    if (filterToggle && filters) {
        filterToggle.addEventListener('click', function () {
            filters.classList.toggle('active');
        });
    }
});