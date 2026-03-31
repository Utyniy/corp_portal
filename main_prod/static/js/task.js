/**
 * Корпоративный портал - Планировщик задач
 * Полностью переработанная версия с исправленными багами
 */

class TasksManager {
    constructor() {
        this.isInitialized = false;
        this.notifications = [];
        this.archiveData = [];
        this.docsData = [];
        this.currentArchivePage = 1;
        this.archiveTotalPages = 5;
    }

    /**
     * Инициализация страницы
     */
    init() {
        if (this.isInitialized) return;
        
        console.log('Инициализация планировщика задач...');
        
        this.loadMockData();
        this.renderArchiveGrid();
        this.renderDocsGrid();
        this.renderPagination();
        this.initEventListeners();
        this.updateDateTime();
        
        setInterval(() => this.updateDateTime(), 1000);
        
        this.isInitialized = true;
        console.log('Планировщик задач инициализирован');
    }

    /**
     * Загрузка тестовых данных
     */
    loadMockData() {
        // Данные для архива задач
        this.archiveData = [
            {
                id: 1,
                category: 'project',
                categoryText: 'Проект',
                date: '05.02.2026',
                title: 'Разработка лендинга для нового продукта',
                description: 'Создание посадочной страницы для запуска CRM-системы. Завершено досрочно с высоким качеством.',
                time: '3 дня',
                participants: '2',
                status: 'completed'
            },
            {
                id: 2,
                category: 'meeting',
                categoryText: 'Встреча',
                date: '03.02.2026',
                title: 'Планирование спринта #12',
                description: 'Определение целей и распределение задач на следующий спринт разработки.',
                time: '2 часа',
                participants: '8',
                status: 'completed'
            },
            {
                id: 3,
                category: 'development',
                categoryText: 'Разработка',
                date: '01.02.2026',
                title: 'Исправление критического бага #1234',
                description: 'Ошибка в авторизации пользователей через корпоративный SSO.',
                time: '4 часа',
                participants: '1',
                status: 'completed'
            },
            {
                id: 4,
                category: 'analytics',
                categoryText: 'Аналитика',
                date: '30.01.2026',
                title: 'Анализ производительности БД',
                description: 'Исследование узких мест и оптимизация запросов к базе данных.',
                time: '2 дня',
                participants: '1',
                status: 'completed'
            }
        ];

        // Данные для документации
        this.docsData = [
            {
                id: 1,
                icon: 'api',
                iconClass: 'fa-code',
                title: 'API Документация',
                description: 'Полная спецификация REST API корпоративного портала с примерами запросов и ответов.',
                format: 'PDF, 2.4 МБ',
                date: '12.02.2026'
            },
            {
                id: 2,
                icon: 'guide',
                iconClass: 'fa-book-open',
                title: 'Руководство разработчика',
                description: 'Стандарты кодирования, настройка окружения и процесс CI/CD.',
                format: 'DOCX, 3.1 МБ',
                date: '10.02.2026'
            },
            {
                id: 3,
                icon: 'spec',
                iconClass: 'fa-cogs',
                title: 'Технические спецификации',
                description: 'Требования к системе, архитектура и используемые технологии.',
                format: 'PDF, 4.2 МБ',
                date: '08.02.2026'
            },
            {
                id: 4,
                icon: 'manual',
                iconClass: 'fa-user-cog',
                title: 'Инструкция по развертыванию',
                description: 'Пошаговое руководство по установке и настройке системы.',
                format: 'MD, 1.8 МБ',
                date: '05.02.2026'
            }
        ];
    }

    /**
     * Инициализация обработчиков событий
     */
    initEventListeners() {
        // Чекбоксы задач
        this.initTaskCheckboxes();

        // Кнопка добавления задачи
        const addTaskBtn = document.getElementById('add-task-btn');
        if (addTaskBtn) {
            addTaskBtn.addEventListener('click', (e) => {
                e.preventDefault();
                this.showAddTaskModal();
            });
        }

        // Кнопка фильтров
        const filterBtn = document.getElementById('filter-tasks-btn');
        if (filterBtn) {
            filterBtn.addEventListener('click', (e) => {
                e.preventDefault();
                this.showFiltersModal();
            });
        }

        // Кнопка экспорта
        const exportBtn = document.getElementById('export-tasks-btn');
        if (exportBtn) {
            exportBtn.addEventListener('click', (e) => {
                e.preventDefault();
                this.exportTasks();
            });
        }

        // Кнопка продолжения отчета
        const continueReportBtn = document.getElementById('continue-report-btn');
        if (continueReportBtn) {
            continueReportBtn.addEventListener('click', (e) => {
                e.preventDefault();
                this.continueReport();
            });
        }

        // Кнопки действий с задачами
        document.querySelectorAll('.task-btn.edit-btn, .task-btn.details-btn').forEach(btn => {
            btn.addEventListener('click', (e) => {
                e.preventDefault();
                e.stopPropagation();
                this.handleTaskAction(btn);
            });
        });

        // Фильтры архива
        const archiveSearch = document.getElementById('archive-search-input');
        if (archiveSearch) {
            let timeout;
            archiveSearch.addEventListener('input', () => {
                clearTimeout(timeout);
                timeout = setTimeout(() => {
                    this.searchArchive(archiveSearch.value);
                }, 500);
            });
        }

        // Селекты фильтров
        document.querySelectorAll('#archive-category-filter, #archive-sort-filter').forEach(select => {
            select.addEventListener('change', () => {
                this.filterArchive();
            });
        });

        // Кнопка фильтров архива
        const archiveFilterBtn = document.getElementById('archive-filter-btn');
        if (archiveFilterBtn) {
            archiveFilterBtn.addEventListener('click', (e) => {
                e.preventDefault();
                this.showFiltersModal();
            });
        }

        // Кнопка скачивания всех документов
        const downloadAllBtn = document.getElementById('download-all-docs');
        if (downloadAllBtn) {
            downloadAllBtn.addEventListener('click', (e) => {
                e.preventDefault();
                this.downloadAllDocs();
            });
        }
    }

    /**
     * Инициализация чекбоксов задач
     */
    initTaskCheckboxes() {
        const checkboxes = document.querySelectorAll('.task-item .task-checkbox input[type="checkbox"]');
        
        checkboxes.forEach(checkbox => {
            // Удаляем старые обработчики
            const newCheckbox = checkbox.cloneNode(true);
            checkbox.parentNode.replaceChild(newCheckbox, checkbox);
            
            newCheckbox.addEventListener('change', (e) => {
                this.handleTaskComplete(e);
            });
        });
    }

    /**
     * Обработка завершения задачи
     */
    handleTaskComplete(e) {
        const checkbox = e.target;
        const taskItem = checkbox.closest('.task-item');
        
        if (!taskItem) return;
        
        const taskTitle = taskItem.querySelector('.task-content h4')?.textContent || 'Задача';
        
        if (checkbox.checked) {
            // Показываем уведомление
            this.showNotification(`Задача выполнена: ${taskTitle}`, 'success');
            
            // Добавляем класс для анимации удаления
            taskItem.classList.add('removing');
            
            // Удаляем элемент после завершения анимации
            setTimeout(() => {
                if (taskItem && taskItem.parentNode) {
                    taskItem.remove();
                    this.updateTaskCounter();
                    this.checkEmptyTasks();
                }
            }, 400);
        }
    }

    /**
     * Обновление счетчика задач
     */
    updateTaskCounter() {
        const taskItems = document.querySelectorAll('.task-item');
        const counter = document.getElementById('task-counter');
        
        if (counter) {
            const count = taskItems.length;
            
            if (count === 0) {
                counter.textContent = 'Нет задач';
                counter.style.background = 'var(--text-light)';
            } else {
                counter.textContent = `${count} активных`;
                counter.style.background = 'var(--warning)';
            }
        }
    }

    /**
     * Проверка на пустой список задач
     */
    checkEmptyTasks() {
        const taskList = document.getElementById('tasks-list-container');
        const taskItems = taskList.querySelectorAll('.task-item');
        
        if (taskItems.length === 0) {
            const emptyMessage = document.createElement('div');
            emptyMessage.className = 'empty-tasks';
            emptyMessage.id = 'empty-tasks-message';
            emptyMessage.innerHTML = `
                <i class="fas fa-check-circle"></i>
                <h3>Все задачи выполнены!</h3>
                <p>Отличная работа! У вас нет активных задач.</p>
                <button class="btn-primary" id="empty-add-task-btn">
                    <i class="fas fa-plus"></i> Добавить задачу
                </button>
            `;
            taskList.appendChild(emptyMessage);
            
            // Обработчик для кнопки в пустом состоянии
            const emptyAddBtn = document.getElementById('empty-add-task-btn');
            if (emptyAddBtn) {
                emptyAddBtn.addEventListener('click', () => {
                    this.showAddTaskModal();
                });
            }
        } else {
            const emptyMessage = document.getElementById('empty-tasks-message');
            if (emptyMessage) {
                emptyMessage.remove();
            }
        }
    }

    /**
     * Показать модальное окно добавления задачи
     */
    showAddTaskModal() {
        const modalHTML = `
            <div class="tasks-modal">
                <div class="tasks-modal-content">
                    <div class="tasks-modal-header">
                        <h3><i class="fas fa-plus-circle"></i> Добавление новой задачи</h3>
                        <button class="tasks-modal-close">&times;</button>
                    </div>
                    <div class="tasks-modal-body">
                        <form id="add-task-form">
                            <div class="form-group">
                                <label class="form-label">
                                    <i class="fas fa-heading"></i>
                                    Название задачи
                                </label>
                                <input type="text" class="form-control" placeholder="Введите название задачи..." id="task-title-input" required>
                            </div>
                            
                            <div class="form-row">
                                <div class="form-group">
                                    <label class="form-label">
                                        <i class="fas fa-flag"></i>
                                        Приоритет
                                    </label>
                                    <select class="form-control" id="task-priority-select">
                                        <option value="high">Высокий</option>
                                        <option value="medium" selected>Средний</option>
                                        <option value="low">Низкий</option>
                                    </select>
                                </div>
                                
                                <div class="form-group">
                                    <label class="form-label">
                                        <i class="fas fa-calendar"></i>
                                        Дедлайн
                                    </label>
                                    <input type="date" class="form-control" id="task-deadline-input">
                                </div>
                            </div>
                            
                            <div class="form-group">
                                <label class="form-label">
                                    <i class="fas fa-user"></i>
                                    Исполнитель
                                </label>
                                <select class="form-control" id="task-assignee-select">
                                    <option value="me">Я (Алексей Смирнов)</option>
                                    <option value="ivan">Иван Петров</option>
                                    <option value="elena">Елена Ковалева</option>
                                    <option value="sergey">Сергей Козлов</option>
                                </select>
                            </div>
                            
                            <div class="form-group">
                                <label class="form-label">
                                    <i class="fas fa-align-left"></i>
                                    Описание
                                </label>
                                <textarea class="form-control" rows="3" placeholder="Добавьте описание задачи..." id="task-description-input"></textarea>
                            </div>
                        </form>
                    </div>
                    <div class="tasks-modal-footer">
                        <button class="btn-secondary modal-cancel-btn">Отмена</button>
                        <button class="btn-primary modal-save-btn" id="save-task-btn">
                            <i class="fas fa-plus"></i> Создать задачу
                        </button>
                    </div>
                </div>
            </div>
        `;
        
        this.showModal(modalHTML, (modal) => {
            // Обработчик сохранения задачи
            const saveBtn = modal.querySelector('#save-task-btn');
            saveBtn.addEventListener('click', () => {
                this.createNewTask();
                this.closeModal(modal);
            });
        });
    }

    /**
     * Создание новой задачи
     */
    createNewTask() {
        const title = document.getElementById('task-title-input')?.value;
        
        if (!title) {
            this.showNotification('Введите название задачи', 'warning');
            return;
        }
        
        // Здесь должна быть логика добавления задачи
        this.showNotification('Новая задача создана!', 'success');
        
        // В реальном приложении здесь добавлялась бы задача в DOM
        setTimeout(() => {
            location.reload(); // Для демонстрации просто перезагружаем
        }, 1500);
    }

    /**
     * Показать модальное окно фильтров
     */
    showFiltersModal() {
        const modalHTML = `
            <div class="tasks-modal">
                <div class="tasks-modal-content" style="max-width: 500px;">
                    <div class="tasks-modal-header">
                        <h3><i class="fas fa-filter"></i> Фильтры задач</h3>
                        <button class="tasks-modal-close">&times;</button>
                    </div>
                    <div class="tasks-modal-body">
                        <div class="form-group">
                            <label class="form-label">Статус</label>
                            <select class="form-control">
                                <option value="all">Все задачи</option>
                                <option value="active">Активные</option>
                                <option value="completed">Выполненные</option>
                                <option value="overdue">Просроченные</option>
                            </select>
                        </div>
                        
                        <div class="form-group">
                            <label class="form-label">Приоритет</label>
                            <select class="form-control">
                                <option value="all">Все приоритеты</option>
                                <option value="high">Высокий</option>
                                <option value="medium">Средний</option>
                                <option value="low">Низкий</option>
                            </select>
                        </div>
                        
                        <div class="form-group">
                            <label class="form-label">Исполнитель</label>
                            <select class="form-control">
                                <option value="all">Все исполнители</option>
                                <option value="me">Я</option>
                                <option value="team">Моя команда</option>
                            </select>
                        </div>
                        
                        <div class="form-group">
                            <label class="form-label">Период</label>
                            <div style="display: flex; gap: 10px;">
                                <input type="date" class="form-control" placeholder="От">
                                <input type="date" class="form-control" placeholder="До">
                            </div>
                        </div>
                    </div>
                    <div class="tasks-modal-footer">
                        <button class="btn-secondary modal-cancel-btn">Сбросить</button>
                        <button class="btn-primary modal-save-btn">
                            <i class="fas fa-check"></i> Применить
                        </button>
                    </div>
                </div>
            </div>
        `;
        
        this.showModal(modalHTML);
    }

    /**
     * Отображение модального окна
     */
    showModal(html, callback = null) {
        // Удаляем предыдущее модальное окно
        const existingModal = document.querySelector('.tasks-modal');
        if (existingModal) {
            existingModal.remove();
        }
        
        const modalContainer = document.createElement('div');
        modalContainer.innerHTML = html;
        const modal = modalContainer.firstElementChild;
        
        document.body.appendChild(modal);
        
        // Анимация появления
        setTimeout(() => {
            modal.classList.add('show');
        }, 10);
        
        // Закрытие модального окна
        const closeModal = () => this.closeModal(modal);
        
        modal.querySelector('.tasks-modal-close')?.addEventListener('click', closeModal);
        modal.querySelector('.modal-cancel-btn')?.addEventListener('click', closeModal);
        
        modal.addEventListener('click', (e) => {
            if (e.target === modal) {
                closeModal();
            }
        });
        
        // Вызов колбэка
        if (callback) {
            callback(modal);
        }
    }

    /**
     * Закрытие модального окна
     */
    closeModal(modal) {
        modal.classList.remove('show');
        setTimeout(() => {
            if (modal.parentNode) {
                modal.parentNode.removeChild(modal);
            }
        }, 300);
    }

    /**
     * Экспорт задач
     */
    exportTasks() {
        this.showNotification('Экспорт задач начат...', 'info');
        
        setTimeout(() => {
            this.showNotification('Задачи экспортированы в Excel', 'success');
        }, 1500);
    }

    /**
     * Продолжить создание отчета
     */
    continueReport() {
        this.showNotification('Продолжение создания отчета...', 'info');
        
        const progressFill = document.getElementById('report-progress-fill');
        const progressPercent = document.getElementById('report-progress-percent');
        const reportStatus = document.getElementById('report-status');
        
        if (progressFill && progressPercent) {
            let width = parseInt(progressFill.style.width) || 65;
            
            if (width < 100) {
                width += 5;
                progressFill.style.width = `${width}%`;
                progressPercent.textContent = `${width}%`;
                
                if (width >= 100) {
                    reportStatus.textContent = 'Готов';
                    reportStatus.style.background = 'var(--success)';
                    this.showNotification('Отчет готов к скачиванию!', 'success');
                } else {
                    this.showNotification(`Прогресс отчета: ${width}%`, 'info');
                }
            }
        }
    }

    /**
     * Обработка действий с задачами
     */
    handleTaskAction(btn) {
        const taskItem = btn.closest('.task-item');
        const taskTitle = taskItem?.querySelector('.task-content h4')?.textContent || 'Задача';
        
        if (btn.classList.contains('edit-btn')) {
            this.showNotification(`Редактирование: ${taskTitle}`, 'info');
        } else if (btn.classList.contains('details-btn')) {
            this.showNotification(`Детали задачи: ${taskTitle}`, 'info');
        }
    }

    /**
     * Рендеринг сетки архива
     */
    renderArchiveGrid() {
        const grid = document.getElementById('archive-tasks-grid');
        if (!grid) return;
        
        grid.innerHTML = '';
        
        this.archiveData.forEach(task => {
            const template = document.getElementById('archive-task-template');
            const clone = template.content.cloneNode(true);
            
            const card = clone.querySelector('.archive-task-card');
            card.dataset.taskId = task.id;
            card.dataset.category = task.category;
            
            clone.querySelector('.archive-task-category').textContent = task.categoryText;
            clone.querySelector('.archive-task-category').classList.add(task.category);
            clone.querySelector('.archive-task-date').innerHTML = `<i class="far fa-calendar-alt"></i> ${task.date}`;
            clone.querySelector('h3').textContent = task.title;
            clone.querySelector('p').textContent = task.description;
            clone.querySelector('.archive-task-time').innerHTML = `<i class="far fa-clock"></i> ${task.time}`;
            clone.querySelector('.archive-task-participants').innerHTML = `<i class="fas fa-users"></i> ${task.participants}`;
            
            card.addEventListener('click', () => {
                this.showNotification(`Открытие архивной задачи: "${task.title}"`, 'info');
            });
            
            grid.appendChild(clone);
        });
    }

    /**
     * Рендеринг сетки документации
     */
    renderDocsGrid() {
        const grid = document.getElementById('docs-grid');
        if (!grid) return;
        
        grid.innerHTML = '';
        
        this.docsData.forEach(doc => {
            const template = document.getElementById('doc-template');
            const clone = template.content.cloneNode(true);
            
            const iconDiv = clone.querySelector('.doc-icon');
            iconDiv.classList.add(doc.icon);
            iconDiv.innerHTML = `<i class="fas ${doc.iconClass}"></i>`;
            
            clone.querySelector('h3').textContent = doc.title;
            clone.querySelector('p').textContent = doc.description;
            clone.querySelector('.doc-format').innerHTML = `<i class="fas fa-file-alt"></i> ${doc.format}`;
            clone.querySelector('.doc-date').innerHTML = `<i class="far fa-clock"></i> ${doc.date}`;
            
            const link = clone.querySelector('.doc-link');
            link.addEventListener('click', (e) => {
                e.preventDefault();
                this.showNotification(`Открытие документа: ${doc.title}`, 'info');
            });
            
            grid.appendChild(clone);
        });
    }

    /**
     * Рендеринг пагинации
     */
    renderPagination() {
        const pagination = document.getElementById('archive-pagination');
        if (!pagination) return;
        
        pagination.innerHTML = '';
        
        // Кнопка "Предыдущая"
        const prevBtn = document.createElement('button');
        prevBtn.className = 'archive-pagination-btn';
        prevBtn.disabled = this.currentArchivePage === 1;
        prevBtn.innerHTML = '<i class="fas fa-chevron-left"></i>';
        prevBtn.addEventListener('click', () => {
            if (this.currentArchivePage > 1) {
                this.currentArchivePage--;
                this.renderPagination();
                this.showNotification(`Страница ${this.currentArchivePage}`, 'info');
            }
        });
        pagination.appendChild(prevBtn);
        
        // Кнопки страниц
        for (let i = 1; i <= this.archiveTotalPages; i++) {
            const btn = document.createElement('button');
            btn.className = `archive-pagination-btn ${this.currentArchivePage === i ? 'active' : ''}`;
            btn.textContent = i;
            btn.addEventListener('click', () => {
                this.currentArchivePage = i;
                this.renderPagination();
                this.showNotification(`Страница ${i}`, 'info');
            });
            pagination.appendChild(btn);
        }
        
        // Кнопка "Следующая"
        const nextBtn = document.createElement('button');
        nextBtn.className = 'archive-pagination-btn next';
        nextBtn.innerHTML = '<i class="fas fa-chevron-right"></i>';
        nextBtn.disabled = this.currentArchivePage === this.archiveTotalPages;
        nextBtn.addEventListener('click', () => {
            if (this.currentArchivePage < this.archiveTotalPages) {
                this.currentArchivePage++;
                this.renderPagination();
                this.showNotification(`Страница ${this.currentArchivePage}`, 'info');
            }
        });
        pagination.appendChild(nextBtn);
    }

    /**
     * Поиск по архиву
     */
    searchArchive(query) {
        if (query.trim()) {
            this.showNotification(`Поиск: "${query}"`, 'info');
        }
    }

    /**
     * Фильтрация архива
     */
    filterArchive() {
        this.showNotification('Фильтры применены', 'success');
    }

    /**
     * Скачивание всех документов
     */
    downloadAllDocs() {
        this.showNotification('Подготовка архива документов...', 'info');
        
        setTimeout(() => {
            this.showNotification('Архив готов к скачиванию', 'success');
        }, 2000);
    }

    /**
     * Показать уведомление
     */
    showNotification(message, type = 'info') {
        let container = document.querySelector('.notifications-container');
        
        if (!container) {
            container = document.createElement('div');
            container.className = 'notifications-container';
            document.body.appendChild(container);
        }
        
        const notification = document.createElement('div');
        notification.className = `news-notification ${type}`;
        
        const icons = {
            'info': 'info-circle',
            'success': 'check-circle',
            'warning': 'exclamation-triangle',
            'error': 'times-circle'
        };
        
        notification.innerHTML = `
            <div class="notification-icon">
                <i class="fas fa-${icons[type] || 'info-circle'}"></i>
            </div>
            <div class="notification-message">${message}</div>
            <button class="notification-close-btn">
                <i class="fas fa-times"></i>
            </button>
        `;
        
        container.appendChild(notification);
        
        setTimeout(() => notification.classList.add('show'), 10);
        
        const closeBtn = notification.querySelector('.notification-close-btn');
        closeBtn.addEventListener('click', () => {
            this.closeNotification(notification);
        });
        
        setTimeout(() => {
            this.closeNotification(notification);
        }, 4000);
        
        this.notifications.push(notification);
    }

    /**
     * Закрыть уведомление
     */
    closeNotification(notification) {
        notification.classList.remove('show');
        
        setTimeout(() => {
            if (notification.parentNode) {
                notification.parentNode.removeChild(notification);
            }
            
            const index = this.notifications.indexOf(notification);
            if (index > -1) {
                this.notifications.splice(index, 1);
            }
        }, 300);
    }

    /**
     * Обновление даты и времени
     */
    updateDateTime() {
        const now = new Date();
        
        const dateOptions = {
            weekday: 'long',
            year: 'numeric',
            month: 'long',
            day: 'numeric'
        };
        
        const timeOptions = {
            hour: '2-digit',
            minute: '2-digit',
            second: '2-digit'
        };
        
        const dateElement = document.getElementById('current-date');
        const timeElement = document.getElementById('current-time');
        
        if (dateElement) {
            dateElement.textContent = now.toLocaleDateString('ru-RU', dateOptions);
        }
        
        if (timeElement) {
            timeElement.textContent = now.toLocaleTimeString('ru-RU', timeOptions);
        }
    }
}

// Инициализация при загрузке страницы
document.addEventListener('DOMContentLoaded', () => {
    const tasksManager = new TasksManager();
    tasksManager.init();
    
    // Экспортируем для отладки
    window.tasksManager = tasksManager;
});

// Предотвращение дублирования инициализации
if (!window.tasksPageInitialized) {
    window.tasksPageInitialized = true;
}

