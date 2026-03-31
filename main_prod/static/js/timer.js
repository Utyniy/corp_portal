// timer.js – простой и понятный код таймера
(function() {
    // Функция форматирования времени
    function formatTime(seconds) {
        const h = Math.floor(seconds / 3600);
        const m = Math.floor((seconds % 3600) / 60);
        const s = seconds % 60;
        return `${h.toString().padStart(2, '0')}:${m.toString().padStart(2, '0')}:${s.toString().padStart(2, '0')}`;
    }

    // Обновление времени на странице
    function updateWorkTime() {
        fetch(window.workUrls.time)
            .then(response => response.json())
            .then(data => {
                if (data.status === 'success') {
                    const formatted = data.worked_today.formatted;
                    const totalSec = data.worked_today.total_seconds;
                    const workedTimeEl = document.getElementById('worked-time');
                    const workProgressEl = document.getElementById('work-progress');
                    const workPercentEl = document.getElementById('work-percent');
                    if (workedTimeEl) workedTimeEl.textContent = formatted;
                    if (workProgressEl && workPercentEl) {
                        const maxWorkSeconds = 8 * 3600;
                        let percent = Math.min(100, Math.floor((totalSec / maxWorkSeconds) * 100));
                        workProgressEl.style.width = percent + '%';
                        workPercentEl.textContent = percent + '%';
                    }
                } else {
                    console.error('Ошибка получения времени:', data);
                }
            })
            .catch(error => console.error('Ошибка загрузки времени:', error));
    }

    // Начать день
    function startWork() {
        fetch(window.workUrls.start, {
            method: 'POST',
            headers: {
                'X-CSRFToken': document.querySelector('[name=csrf-token]').content,
            },
        })
        .then(response => response.json())
        .then(data => {
            const msgDiv = document.getElementById('work-message');
            if (msgDiv) {
                msgDiv.style.display = 'block';
                if (data.status === 'success') {
                    msgDiv.style.color = 'green';
                    msgDiv.textContent = data.message;
                    // Запускаем интервал обновления (каждую секунду)
                    if (window.workInterval) clearInterval(window.workInterval);
                    window.workInterval = setInterval(updateWorkTime, 1000);
                    updateWorkTime();
                } else {
                    msgDiv.style.color = 'red';
                    msgDiv.textContent = data.message;
                }
                setTimeout(() => msgDiv.style.display = 'none', 3000);
            }
        })
        .catch(error => console.error('Ошибка:', error));
    }

    // Завершить день
    function endWork() {
        fetch(window.workUrls.end, {
            method: 'POST',
            headers: {
                'X-CSRFToken': document.querySelector('[name=csrf-token]').content,
            },
        })
        .then(response => response.json())
        .then(data => {
            const msgDiv = document.getElementById('work-message');
            if (msgDiv) {
                msgDiv.style.display = 'block';
                if (data.status === 'success') {
                    msgDiv.style.color = 'green';
                    msgDiv.textContent = data.message;
                    if (window.workInterval) {
                        clearInterval(window.workInterval);
                        window.workInterval = null;
                    }
                    updateWorkTime();
                } else {
                    msgDiv.style.color = 'red';
                    msgDiv.textContent = data.message;
                }
                setTimeout(() => msgDiv.style.display = 'none', 3000);
            }
        })
        .catch(error => console.error('Ошибка:', error));
    }

    // Инициализация
    function init() {
        const startBtn = document.getElementById('start-work-btn');
        const endBtn = document.getElementById('end-work-btn');
        if (startBtn) startBtn.addEventListener('click', startWork);
        if (endBtn) endBtn.addEventListener('click', endWork);

        // Начать обновление времени
        if (window.workUrls && window.workUrls.time) {
            if (window.workInterval) clearInterval(window.workInterval);
            window.workInterval = setInterval(updateWorkTime, 1000);
            updateWorkTime();
        }
    }

    // Запускаем после загрузки DOM
    document.addEventListener('DOMContentLoaded', init);
})();