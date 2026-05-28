// ========== ПЛАВНОЕ МОБИЛЬНОЕ МЕНЮ + ПОДСВЕТКА ==========
document.addEventListener('DOMContentLoaded', () => {
    // Мобильное меню с анимацией
    const toggle = document.getElementById('mobileMenuToggle');
    const sidebar = document.getElementById('sidebar');
    if (toggle && sidebar) {
        toggle.addEventListener('click', () => {
            sidebar.classList.toggle('open');
            toggle.innerHTML = sidebar.classList.contains('open') ? '✕' : '☰';
        });
        // Закрытие при клике на ссылку
        document.querySelectorAll('.nav-link').forEach(link => {
            link.addEventListener('click', () => {
                if (window.innerWidth <= 768) {
                    sidebar.classList.remove('open');
                    toggle.innerHTML = '☰';
                }
            });
        });
    }

    // Эффект наведения на игровые карточки (звук - заглушка)
    document.querySelectorAll('.game-card').forEach(card => {
        card.addEventListener('mouseenter', () => {
            card.style.transition = 'transform 0.2s, box-shadow 0.2s';
        });
    });

    // Анимированное появление контента
    const observer = new IntersectionObserver((entries) => {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                entry.target.style.opacity = '1';
                entry.target.style.transform = 'translateY(0)';
            }
        });
    }, { threshold: 0.1 });
    document.querySelectorAll('.game-card, .hero, .feature').forEach(el => {
        el.style.opacity = '0';
        el.style.transform = 'translateY(20px)';
        el.style.transition = 'all 0.5s ease-out';
        observer.observe(el);
    });
});
