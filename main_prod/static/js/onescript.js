document.addEventListener('DOMContentLoaded', function () {
    initDropdowns();
    initCalendar();
    initTaskCheckboxes();
    updateDateTime();
    initHoverEffects();

    if (window.portalDateTimeInterval) {
        clearInterval(window.portalDateTimeInterval);
    }
    window.portalDateTimeInterval = setInterval(updateDateTime, 60000);
});

function initDropdowns() {
    const dropdowns = document.querySelectorAll('.dropdown');
    if (!dropdowns.length) return;

    dropdowns.forEach((dropdown) => {
        const toggle = dropdown.querySelector('.dropdown-toggle');
        if (!toggle) return;

        toggle.addEventListener('click', function (e) {
            e.preventDefault();
            e.stopPropagation();

            const isOpen = dropdown.classList.contains('active');

            dropdowns.forEach((item) => {
                item.classList.remove('active');
                const itemToggle = item.querySelector('.dropdown-toggle');
                if (itemToggle) itemToggle.setAttribute('aria-expanded', 'false');
            });

            if (!isOpen) {
                dropdown.classList.add('active');
                toggle.setAttribute('aria-expanded', 'true');
            }
        });
    });

    document.addEventListener('click', function (e) {
        dropdowns.forEach((dropdown) => {
            if (!dropdown.contains(e.target)) {
                dropdown.classList.remove('active');
                const toggle = dropdown.querySelector('.dropdown-toggle');
                if (toggle) toggle.setAttribute('aria-expanded', 'false');
            }
        });
    });

    document.addEventListener('keydown', function (e) {
        if (e.key === 'Escape') {
            dropdowns.forEach((dropdown) => {
                dropdown.classList.remove('active');
                const toggle = dropdown.querySelector('.dropdown-toggle');
                if (toggle) toggle.setAttribute('aria-expanded', 'false');
            });
        }
    });
}

function initCalendar() {
    const dates = document.querySelectorAll('.calendar-grid .date:not(.inactive)');
    dates.forEach((date) => {
        date.addEventListener('click', function () {
            dates.forEach((d) => d.classList.remove('selected'));
            this.classList.add('selected');
        });
    });
}

function initTaskCheckboxes() {
    document.querySelectorAll('.task-checkbox input[type="checkbox"]').forEach((checkbox) => {
        checkbox.addEventListener('change', function () {
            if (!this.checked) return;

            const taskItem = this.closest('.task-item');
            if (!taskItem) return;

            taskItem.style.transition = 'all 0.3s ease';
            taskItem.style.opacity = '0.6';

            setTimeout(() => {
                taskItem.style.transform = 'translateX(100px)';
                taskItem.style.opacity = '0';

                setTimeout(() => {
                    if (taskItem.parentNode) {
                        taskItem.remove();
                        updateTaskCounter();
                    }
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
    document.querySelectorAll('.card').forEach((card) => {
        card.addEventListener('mouseenter', () => {
            card.style.zIndex = '10';
        });
        card.addEventListener('mouseleave', () => {
            card.style.zIndex = '1';
        });
    });
}