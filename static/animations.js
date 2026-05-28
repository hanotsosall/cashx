// Эффект конфетти при большом выигрыше (>1000)
function showConfetti() {
    const colors = ['#ffaa33', '#ff6600', '#ffcc00', '#ffffff'];
    for (let i = 0; i < 100; i++) {
        const conf = document.createElement('div');
        conf.style.position = 'fixed';
        conf.style.width = '10px';
        conf.style.height = '10px';
        conf.style.backgroundColor = colors[Math.floor(Math.random() * colors.length)];
        conf.style.left = Math.random() * window.innerWidth + 'px';
        conf.style.top = '-10px';
        conf.style.zIndex = '10000';
        conf.style.pointerEvents = 'none';
        conf.style.borderRadius = '50%';
        conf.style.animation = `fall ${Math.random() * 2 + 1}s linear forwards`;
        document.body.appendChild(conf);
        setTimeout(() => conf.remove(), 3000);
    }
}

// Добавляем ключевые кадры анимации
const style = document.createElement('style');
style.textContent = `
    @keyframes fall {
        0% { transform: translateY(0) rotate(0deg); opacity: 1; }
        100% { transform: translateY(100vh) rotate(360deg); opacity: 0; }
    }
    @keyframes shake {
        0% { transform: translate(1px, 1px); }
        100% { transform: translate(-1px, -1px); }
    }
    .win-effect {
        animation: shake 0.2s ease-in-out 0s 2;
    }
`;
document.head.appendChild(style);

// Функция для показа вспышки на весь экран при джекпоте
function flashScreen() {
    const flash = document.createElement('div');
    flash.style.position = 'fixed';
    flash.style.top = 0;
    flash.style.left = 0;
    flash.style.width = '100%';
    flash.style.height = '100%';
    flash.style.backgroundColor = 'rgba(255, 215, 0, 0.3)';
    flash.style.zIndex = '9999';
    flash.style.pointerEvents = 'none';
    flash.style.animation = 'fadeOut 0.5s forwards';
    document.body.appendChild(flash);
    setTimeout(() => flash.remove(), 500);
}

// Вешаем глобально, чтобы можно было вызывать из игр
window.showConfetti = showConfetti;
window.flashScreen = flashScreen;
