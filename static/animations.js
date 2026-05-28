// ========== ЭФФЕКТЫ ДЛЯ ПОБЕД И ДЖЕКПОТОВ ==========
(function() {
    // Конфетти (ремейк с частицами)
    function createConfetti() {
        const colors = ['#f5b042', '#ffd966', '#ff8800', '#ffffff', '#2ecc71'];
        for (let i = 0; i < 120; i++) {
            const conf = document.createElement('div');
            conf.style.position = 'fixed';
            conf.style.width = Math.random() * 10 + 4 + 'px';
            conf.style.height = Math.random() * 6 + 4 + 'px';
            conf.style.backgroundColor = colors[Math.floor(Math.random() * colors.length)];
            conf.style.left = Math.random() * window.innerWidth + 'px';
            conf.style.top = '-20px';
            conf.style.zIndex = '10000';
            conf.style.pointerEvents = 'none';
            conf.style.borderRadius = Math.random() > 0.5 ? '50%' : '0';
            conf.style.opacity = Math.random() * 0.8 + 0.5;
            conf.style.animation = `fallConfetti ${Math.random() * 2 + 1.5}s linear forwards`;
            document.body.appendChild(conf);
            setTimeout(() => conf.remove(), 3000);
        }
    }

    // Вспышка на весь экран
    function flashScreen(color = '#f5b042') {
        const flash = document.createElement('div');
        flash.style.position = 'fixed';
        flash.style.top = 0;
        flash.style.left = 0;
        flash.style.width = '100%';
        flash.style.height = '100%';
        flash.style.backgroundColor = color;
        flash.style.zIndex = '9999';
        flash.style.pointerEvents = 'none';
        flash.style.opacity = '0.6';
        flash.style.transition = 'opacity 0.3s ease';
        document.body.appendChild(flash);
        setTimeout(() => {
            flash.style.opacity = '0';
            setTimeout(() => flash.remove(), 300);
        }, 100);
    }

    // Анимация цифр (счётчик выигрыша)
    function animateNumber(element, start, end, duration = 800) {
        if (!element) return;
        let startTime = null;
        const step = (timestamp) => {
            if (!startTime) startTime = timestamp;
            const progress = Math.min((timestamp - startTime) / duration, 1);
            const current = Math.floor(progress * (end - start) + start);
            element.innerText = current;
            if (progress < 1) {
                requestAnimationFrame(step);
            } else {
                element.innerText = end;
            }
        };
        requestAnimationFrame(step);
    }

    // Эффект "встряски" элемента
    function shakeElement(el) {
        if (!el) return;
        el.classList.add('shake-effect');
        setTimeout(() => el.classList.remove('shake-effect'), 500);
    }

    // Добавляем стили для анимаций
    const style = document.createElement('style');
    style.textContent = `
        @keyframes fallConfetti {
            0% { transform: translateY(0) rotate(0deg); opacity: 1; }
            100% { transform: translateY(100vh) rotate(720deg); opacity: 0; }
        }
        .shake-effect {
            animation: shakeAnim 0.3s ease-in-out 0s 2;
        }
        @keyframes shakeAnim {
            0% { transform: translate(1px, 1px); }
            50% { transform: translate(-2px, 0); }
            100% { transform: translate(0, 0); }
        }
        .pulse-gold {
            animation: pulseGold 0.5s ease-out;
        }
        @keyframes pulseGold {
            0% { text-shadow: 0 0 0 gold; transform: scale(1); }
            50% { text-shadow: 0 0 20px gold; transform: scale(1.05); }
            100% { text-shadow: 0 0 0 gold; transform: scale(1); }
        }
    `;
    document.head.appendChild(style);

    // Глобальный доступ
    window.createConfetti = createConfetti;
    window.flashScreen = flashScreen;
    window.animateNumber = animateNumber;
    window.shakeElement = shakeElement;

    // Автоматический перехват больших выигрышей (можно вызвать из игр)
    console.log('Анимации загружены: конфетти, вспышки, счётчики');
})();
