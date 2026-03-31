// onescript.js – без таймера
document.addEventListener('DOMContentLoaded', function() {
    console.log('Корпоративный портал загружен');

    initDropdown();
    initCalendar();
    initTaskCheckboxes();
    updateDateTime();
    initHoverEffects();

    setInterval(updateDateTime, 60000);
});

function initDropdown() {
    const dropdownToggle = document.querySelector('.dropdown-toggle');
    const dropdown = document.querySelector('.dropdown');
    const dropdownMenu = document.querySelector('.dropdown-menu');

    if (!dropdownToggle || !dropdown || !dropdownMenu) return;

    dropdownToggle.addEventListener('click', function(e) {
        e.preventDefault();
        e.stopPropagation();
        dropdown.classList.toggle('active');
    });

    document.addEventListener('click', function(e) {
        if (!dropdown.contains(e.target)) {
            dropdown.classList.remove('active');
        }
    });

    dropdownMenu.querySelectorAll('.dropdown-item').forEach(item => {
        item.addEventListener('click', function(e) {
            e.preventDefault();
            dropdown.classList.remove('active');
        });
    });
}

function initCalendar() {
    const prevBtn = document.querySelector('.calendar-nav button:nth-child(1)');
    const nextBtn = document.querySelector('.calendar-nav button:nth-child(3)');
    const todayBtn = document.querySelector('.today-btn');
    const dates = document.querySelectorAll('.calendar-grid .date:not(.inactive)');

    if (prevBtn) prevBtn.addEventListener('click', function() {});
    if (nextBtn) nextBtn.addEventListener('click', function() {});
    if (todayBtn) todayBtn.addEventListener('click', function() {});

    dates.forEach(date => {
        date.addEventListener('click', function() {
            dates.forEach(d => d.classList.remove('selected'));
            this.classList.add('selected');
        });
    });
}

function initTaskCheckboxes() {
    document.querySelectorAll('.task-checkbox input[type="checkbox"]').forEach(checkbox => {
        checkbox.addEventListener('change', function() {
            if (!this.checked) return;
            const taskItem = this.closest('.task-item');
            if (!taskItem) return;

            taskItem.style.transition = 'all 0.3s';
            taskItem.style.opacity = '0.6';
            setTimeout(() => {
                taskItem.style.transform = 'translateX(100px)';
                taskItem.style.opacity = '0';
                setTimeout(() => {
                    taskItem.remove();
                    updateTaskCounter();
                }, 300);
            }, 500);
        });
    });
}

function updateTaskCounter() {
    const taskItems = document.querySelectorAll('.task-item');
    const taskLink = document.querySelector('.card-link');
    if (taskLink && taskLink.textContent.includes('+')) {
        taskLink.textContent = `+${taskItems.length}`;
    }
}

function updateDateTime() {
    const now = new Date();
    const dateEl = document.getElementById('current-date');
    const timeEl = document.getElementById('current-time');

    if (dateEl) {
        dateEl.textContent = now.toLocaleDateString('ru-RU', {
            weekday: 'long',
            year: 'numeric',
            month: 'long',
            day: 'numeric'
        });
    }
    if (timeEl) {
        timeEl.textContent = now.toLocaleTimeString('ru-RU', {
            hour: '2-digit',
            minute: '2-digit',
            second: '2-digit'
        });
    }
}

function initHoverEffects() {
    document.querySelectorAll('.card').forEach(card => {
        card.addEventListener('mouseenter', () => card.style.zIndex = '10');
        card.addEventListener('mouseleave', () => card.style.zIndex = '1');
    });
}