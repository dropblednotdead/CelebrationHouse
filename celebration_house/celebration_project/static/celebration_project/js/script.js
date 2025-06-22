    document.addEventListener('DOMContentLoaded', function() {
        const menuToggle = document.querySelector('.menu-toggle');
        const header = document.querySelector('.header');

        menuToggle.addEventListener('click', function() {
            header.classList.toggle('active');
            document.body.style.overflow = header.classList.contains('active') ? 'hidden' : '';
        });

        // Закрытие меню при клике на ссылку
        document.querySelectorAll('.mobile-menu a').forEach(link => {
            link.addEventListener('click', function() {
                header.classList.remove('active');
                document.body.style.overflow = '';
            });
        });
    });