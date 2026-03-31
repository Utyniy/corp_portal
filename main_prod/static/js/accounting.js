/**
 * Бухгалтерия - визуальные эффекты, уведомления (без реальных расчётов)
 */

class AccountingPage {
    constructor() {
        this.notifications = [];
    }

    init() {
        console.log('Страница бухгалтерии загружена');
        this.initButtons();
        this.initFormListeners();
        this.updateDateTime();
        setInterval(() => this.updateDateTime(), 1000);
    }

    initButtons() {
        // Все кнопки "Рассчитать"
        document.querySelectorAll('.btn-primary, .btn-secondary').forEach(btn => {
            btn.addEventListener('click', (e) => {
                e.preventDefault();
                const text = btn.textContent.trim();
                this.showNotification(`✅ ${text}: данные обработаны (демо)`, 'success');
            });
        });

        // Ссылки на отчёты
        document.querySelectorAll('.report-link').forEach(link => {
            link.addEventListener('click', (e) => {
                e.preventDefault();
                const reportName = link.textContent.trim();
                this.showNotification(`📄 Формирование отчёта: ${reportName}`, 'info');
            });
        });

        // Кнопка "Скачать все отчёты"
        const downloadAll = document.querySelector('.btn-secondary .fa-download')?.parentElement;
        if (downloadAll) {
            downloadAll.addEventListener('click', (e) => {
                e.preventDefault();
                this.showNotification('📦 Подготовка архива отчётов...', 'info');
                setTimeout(() => {
                    this.showNotification('✅ Архив готов к скачиванию', 'success');
                }, 2000);
            });
        }
    }

    initFormListeners() {
        // Имитация расчёта при изменении полей (просто меняем итоговую сумму)
        const forms = document.querySelectorAll('.accounting-form');
        forms.forEach(form => {
            const inputs = form.querySelectorAll('input[type="number"]:not([disabled])');
            const resultSpan = form.querySelector('.form-result strong');
            
            if (inputs.length && resultSpan) {
                inputs.forEach(input => {
                    input.addEventListener('input', () => {
                        // Простейший демо-расчёт
                        let total = 0;
                        inputs.forEach(inp => {
                            total += Number(inp.value) || 0;
                        });
                        // Примерная логика: оклад + премии - вычеты
                        const formType = form.closest('.accounting-card')?.querySelector('h2')?.textContent;
                        if (formType?.includes('Зарплаты')) {
                            const okrug = Math.round(total * 0.87); // -13%
                            resultSpan.textContent = `${okrug.toLocaleString()} ₽`;
                        } else if (formType?.includes('отпуск')) {
                            resultSpan.textContent = `${Math.round(total * 14).toLocaleString()} ₽`;
                        }
                    });
                });
            }
        });
    }

    // Уведомления
    showNotification(message, type = 'info') {
        let container = document.querySelector('.notifications-container');
        if (!container) {
            container = document.createElement('div');
            container.className = 'notifications-container';
            document.body.appendChild(container);
        }

        const notification = document.createElement('div');
        notification.className = `notification ${type}`;

        const icons = {
            info: 'info-circle',
            success: 'check-circle',
            warning: 'exclamation-triangle',
            error: 'times-circle'
        };

        notification.innerHTML = `
            <div style="color: var(--${type === 'info' ? 'primary' : type}); font-size: 1.2rem;">
                <i class="fas fa-${icons[type]}"></i>
            </div>
            <div style="flex: 1;">${message}</div>
            <button class="close-notif" style="background: none; border: none; color: var(--text-light); cursor: pointer;">
                <i class="fas fa-times"></i>
            </button>
        `;

        container.appendChild(notification);
        setTimeout(() => notification.classList.add('show'), 10);

        notification.querySelector('.close-notif').addEventListener('click', () => {
            notification.classList.remove('show');
            setTimeout(() => notification.remove(), 300);
        });

        setTimeout(() => {
            notification.classList.remove('show');
            setTimeout(() => notification.remove(), 300);
        }, 4000);
    }

    // Обновление даты/времени в футере
    updateDateTime() {
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
}

// Инициализация
document.addEventListener('DOMContentLoaded', () => {
    const accounting = new AccountingPage();
    accounting.init();
    window.accounting = accounting;
});

class AccountingPage {
    constructor() {
        this.notifications = [];
    }

    init() {
        console.log('Страница бухгалтерии загружена');
        this.initButtons();
        this.initFormListeners();
        this.initSickLeaveCalculator();
        this.initPayslipGenerator();
        this.updateDateTime();
        setInterval(() => this.updateDateTime(), 1000);
    }

    initButtons() {
        // Все кнопки .btn-primary и .btn-secondary (кроме специальных)
        document.querySelectorAll('.btn-primary, .btn-secondary').forEach(btn => {
            // Избегаем двойного навешивания
            if (btn.dataset.listener) return;
            btn.dataset.listener = 'true';
            
            btn.addEventListener('click', (e) => {
                e.preventDefault();
                const text = btn.textContent.trim();
                // Специальные кнопки обрабатываются отдельно
                if (btn.id === 'calc-sick-btn' || btn.id === 'generate-payslip-btn') return;
                this.showNotification(`✅ ${text}: данные обработаны (демо)`, 'success');
            });
        });

        // Ссылки на отчёты
        document.querySelectorAll('.report-link').forEach(link => {
            link.addEventListener('click', (e) => {
                e.preventDefault();
                const reportName = link.textContent.trim();
                this.showNotification(`📄 Формирование отчёта: ${reportName}`, 'info');
            });
        });

        // Кнопка "Скачать все отчёты"
        const downloadAll = document.querySelector('.btn-secondary .fa-download')?.parentElement;
        if (downloadAll) {
            downloadAll.addEventListener('click', (e) => {
                e.preventDefault();
                this.showNotification('📦 Подготовка архива отчётов...', 'info');
                setTimeout(() => {
                    this.showNotification('✅ Архив готов к скачиванию', 'success');
                }, 2000);
            });
        }
    }

    initFormListeners() {
        // Имитация расчёта зарплаты и отпусков (как было)
        const forms = document.querySelectorAll('.accounting-form');
        forms.forEach(form => {
            const inputs = form.querySelectorAll('input[type="number"]:not([disabled]):not([readonly])');
            const resultSpan = form.querySelector('.form-result strong');
            
            if (inputs.length && resultSpan) {
                inputs.forEach(input => {
                    input.addEventListener('input', () => {
                        let total = 0;
                        inputs.forEach(inp => {
                            total += Number(inp.value) || 0;
                        });
                        const formType = form.closest('.accounting-card')?.querySelector('h2')?.textContent;
                        if (formType?.includes('Зарплаты')) {
                            const okrug = Math.round(total * 0.87);
                            resultSpan.textContent = `${okrug.toLocaleString()} ₽`;
                        } else if (formType?.includes('отпуск')) {
                            resultSpan.textContent = `${Math.round(total * 14).toLocaleString()} ₽`;
                        }
                    });
                });
            }
        });
    }

    // Расчёт больничного
    initSickLeaveCalculator() {
        const startInput = document.getElementById('sick-start');
        const endInput = document.getElementById('sick-end');
        const daysInput = document.getElementById('sick-days');
        const dailyInput = document.getElementById('sick-daily');
        const expSelect = document.getElementById('sick-experience');
        const resultSpan = document.getElementById('sick-result');
        const calcBtn = document.getElementById('calc-sick-btn');

        if (!startInput || !endInput || !daysInput || !dailyInput || !expSelect || !resultSpan || !calcBtn) return;

        // Функция пересчёта дней
        const updateDays = () => {
            const start = new Date(startInput.value);
            const end = new Date(endInput.value);
            if (start && end && end >= start) {
                const diffTime = end - start;
                const diffDays = Math.ceil(diffTime / (1000 * 60 * 60 * 24)) + 1; // включая оба дня
                daysInput.value = diffDays;
            } else {
                daysInput.value = 0;
            }
        };

        startInput.addEventListener('change', updateDays);
        endInput.addEventListener('change', updateDays);
        updateDays(); // при загрузке

        // Функция расчёта суммы
        const calculateSick = () => {
            const days = parseInt(daysInput.value) || 0;
            const daily = parseFloat(dailyInput.value) || 0;
            const coeff = parseFloat(expSelect.value) || 0.8;
            const total = days * daily * coeff;
            resultSpan.textContent = `${Math.round(total).toLocaleString()} ₽`;
        };

        // События для пересчёта
        [dailyInput, expSelect, daysInput].forEach(el => {
            el.addEventListener('input', calculateSick);
            el.addEventListener('change', calculateSick);
        });

        // Кнопка "Рассчитать" – просто уведомление
        calcBtn.addEventListener('click', (e) => {
            e.preventDefault();
            this.showNotification('🧮 Больничный рассчитан (демо)', 'success');
            calculateSick(); // обновим сумму
        });

        // Первоначальный расчёт
        calculateSick();
    }

    // Формирование расчётного листа
    initPayslipGenerator() {
        const generateBtn = document.getElementById('generate-payslip-btn');
        const downloadDiv = document.getElementById('payslip-download');
        const employeeSelect = document.getElementById('payslip-employee');
        const monthInput = document.getElementById('payslip-month');
        const formatSelect = document.getElementById('payslip-format');

        if (!generateBtn || !downloadDiv) return;

        generateBtn.addEventListener('click', (e) => {
            e.preventDefault();
            
            const employee = employeeSelect?.value || 'Сотрудник';
            const month = monthInput?.value || '2026-02';
            const format = formatSelect?.value || 'PDF';

            this.showNotification(`📄 Формирование расчётного листа для ${employee} за ${month} в формате ${format}...`, 'info');

            // Показываем ссылку на скачивание через 1 секунду
            setTimeout(() => {
                downloadDiv.style.display = 'flex';
                // Обновляем ссылку (можно подставить параметры)
                const link = downloadDiv.querySelector('.download-link');
                if (link) {
                    link.href = '#'; // здесь мог бы быть реальный URL
                    link.setAttribute('download', `payslip_${employee}_${month}.${format.toLowerCase()}`);
                }
                this.showNotification('✅ Расчётный лист готов к скачиванию', 'success');
            }, 1000);
        });

        // Ссылка на скачивание – просто уведомление
        downloadDiv.querySelector('.download-link')?.addEventListener('click', (e) => {
            e.preventDefault();
            this.showNotification('⬇️ Скачивание начато (демо)', 'info');
        });
    }
}