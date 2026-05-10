/**
 * UI Controller for Coach Everything Dashboard
 * Handles DOM manipulation and user interactions
 */

class DashboardUI {
    constructor() {
        this.currentProjectId = null;
        this.chatHistory = [];
        this.pomodoroWebSocket = null;
        this.timerInterval = null;
        this.timeRemaining = 25 * 60; // 25 minutes in seconds
        this.isTimerRunning = false;
        this.currentPhase = 'work'; // 'work' or 'break'
        this.pomodorosCompleted = 0;

        this.initializeElements();
        this.attachEventListeners();
    }

    // ========== Initialization ==========

    initializeElements() {
        // Navbar
        this.elements = {
            projectSelector: document.getElementById('projectSelector'),
            settingsBtn: document.getElementById('settingsBtn'),
            helpBtn: document.getElementById('helpBtn'),

            // Main content
            leftPanel: document.getElementById('leftPanel'),
            centerPanel: document.getElementById('centerPanel'),
            rightPanel: document.getElementById('rightPanel'),

            // Center tabs
            tabTasksBtn: document.getElementById('tabTasksBtn'),
            tabChatBtn: document.getElementById('tabChatBtn'),
            tasksView: document.getElementById('tasksView'),
            chatView: document.getElementById('chatView'),

            // Chat
            chatProviderSelect: document.getElementById('chatProviderSelect'),
            chatModelInput: document.getElementById('chatModelInput'),
            chatModeSelect: document.getElementById('chatModeSelect'),
            chatSystemPromptInput: document.getElementById('chatSystemPromptInput'),
            chatContextLimit: document.getElementById('chatContextLimit'),
            chatSettingsBtn: document.getElementById('chatSettingsBtn'),
            chatSettingsPanel: document.getElementById('chatSettingsPanel'),
            chatModelSummary: document.getElementById('chatModelSummary'),
            chatClearBtn: document.getElementById('chatClearBtn'),
            chatMessages: document.getElementById('chatMessages'),
            chatInput: document.getElementById('chatInput'),
            chatSendBtn: document.getElementById('chatSendBtn'),
            chatContextPreview: document.getElementById('chatContextPreview'),

            // Timer
            timerDisplay: document.getElementById('timerDisplay'),
            timerStatus: document.getElementById('timerStatus'),
            startBtn: document.getElementById('startBtn'),
            pauseBtn: document.getElementById('pauseBtn'),
            resetBtn: document.getElementById('resetBtn'),
            expandLeftBtn: document.getElementById('expandLeftBtn'),

            // Stats
            todayPomodoros: document.getElementById('todayPomodoros'),
            totalHours: document.getElementById('totalHours'),
            viewAnalyticsBtn: document.getElementById('viewAnalyticsBtn'),

            // Project content
            emptyState: document.getElementById('emptyState'),
            projectContent: document.getElementById('projectContent'),
            projectName: document.getElementById('projectName'),
            projectDomain: document.getElementById('projectDomain'),
            progressFill: document.getElementById('progressFill'),

            // Tasks
            taskList: document.getElementById('taskList'),
            taskFilters: document.querySelectorAll('.filter-btn'),

            // Coaching
            coachingNotes: document.getElementById('coachingNotes'),

            // Resources
            resourcesList: document.getElementById('resourcesList'),

            // File browser
            workspaceBrowser: document.getElementById('workspaceBrowser'),
            expandRightBtn: document.getElementById('expandRightBtn'),

            // Modals
            settingsModal: document.getElementById('settingsModal'),
            analyticsModal: document.getElementById('analyticsModal'),
            closeSettingsBtn: document.getElementById('closeSettingsBtn'),
            closeAnalyticsBtn: document.getElementById('closeAnalyticsBtn'),
            cancelSettingsBtn: document.getElementById('cancelSettingsBtn'),
            saveSettingsBtn: document.getElementById('saveSettingsBtn'),

            // Settings
            themeToggle: document.getElementById('themeToggle'),
            fontSizeSlider: document.getElementById('fontSizeSlider'),
            fontSizeValue: document.getElementById('fontSizeValue'),
            languageSelect: document.getElementById('languageSelect'),
            llmProviderSelect: document.getElementById('llmProviderSelect'),
            llmModelSelect: document.getElementById('llmModelSelect'),
            llmBaseUrlInput: document.getElementById('llmBaseUrlInput'),
            llmApiKeyInput: document.getElementById('llmApiKeyInput'),
            cliClaudeCommandInput: document.getElementById('cliClaudeCommandInput'),
            cliCodexCommandInput: document.getElementById('cliCodexCommandInput'),
            cliTimeoutInput: document.getElementById('cliTimeoutInput'),
            mcpStatus: document.getElementById('mcpStatus'),
            mcpStatusText: document.getElementById('mcpStatusText'),

            // Analytics
            ganttChart: document.getElementById('ganttChart'),
            pieChartCanvas: document.getElementById('pieChartCanvas'),
            statsTableBody: document.getElementById('statsTableBody'),
        };
    }

    attachEventListeners() {
        // Project selector
        this.elements.projectSelector.addEventListener('change', (e) => {
            const projectId = e.target.value;
            if (projectId) {
                this.loadProject(projectId);
            }
        });

        if (this.elements.tabTasksBtn && this.elements.tabChatBtn) {
            this.elements.tabTasksBtn.addEventListener('click', () => this.showTasksTab());
            this.elements.tabChatBtn.addEventListener('click', () => this.showChatTab());
        }

        if (this.elements.chatSendBtn) {
            this.elements.chatSendBtn.addEventListener('click', () => this.sendChat());
        }
        if (this.elements.chatClearBtn) {
            this.elements.chatClearBtn.addEventListener('click', () => this.clearChat());
        }
        if (this.elements.chatSettingsBtn) {
            this.elements.chatSettingsBtn.addEventListener('click', () => this.toggleChatSettings());
        }
        if (this.elements.chatInput) {
            this.elements.chatInput.addEventListener('keydown', (e) => {
                if ((e.ctrlKey || e.metaKey) && e.key === 'Enter') {
                    e.preventDefault();
                    this.sendChat();
                }
            });
        }
        if (this.elements.chatProviderSelect) {
            this.elements.chatProviderSelect.addEventListener('change', () => {
                this.updateChatModelSummary();
                this.updateChatContextPreview();
            });
        }
        if (this.elements.chatModelInput) {
            this.elements.chatModelInput.addEventListener('input', () => {
                this.updateChatModelSummary();
                this.updateChatContextPreview();
            });
        }
        if (this.elements.chatModeSelect) {
            this.elements.chatModeSelect.addEventListener('change', () => {
                this.updateChatModelSummary();
                this.updateChatContextPreview();
            });
        }
        if (this.elements.chatSystemPromptInput) {
            this.elements.chatSystemPromptInput.addEventListener('input', () => this.updateChatContextPreview());
        }
        if (this.elements.chatContextLimit) {
            this.elements.chatContextLimit.addEventListener('input', () => this.updateChatContextPreview());
        }

        // Timer controls
        this.elements.startBtn.addEventListener('click', () => this.startTimer());
        this.elements.pauseBtn.addEventListener('click', () => this.pauseTimer());
        this.elements.resetBtn.addEventListener('click', () => this.resetTimer());

        // Panel expansion
        this.elements.expandLeftBtn.addEventListener('click', () => this.toggleLeftPanelExpand());
        this.elements.expandRightBtn.addEventListener('click', () => this.toggleRightPanelExpand());

        // Analytics
        this.elements.viewAnalyticsBtn.addEventListener('click', () => this.showAnalytics());

        // Task filters
        this.elements.taskFilters.forEach((btn) => {
            btn.addEventListener('click', (e) => {
                this.elements.taskFilters.forEach((b) => b.classList.remove('active'));
                e.target.classList.add('active');
                this.filterTasks(e.target.dataset.filter);
            });
        });

        // Settings
        this.elements.settingsBtn.addEventListener('click', () => this.showSettings());
        this.elements.closeSettingsBtn.addEventListener('click', () => this.closeSettings());
        this.elements.cancelSettingsBtn.addEventListener('click', () => this.closeSettings());
        this.elements.saveSettingsBtn.addEventListener('click', () => this.saveSettings());

        // Close analytics modal
        this.elements.closeAnalyticsBtn.addEventListener('click', () => this.closeAnalytics());

        // Settings controls
        this.elements.themeToggle.addEventListener('change', (e) => {
            this.toggleTheme(e.target.checked);
        });

        this.elements.fontSizeSlider.addEventListener('input', (e) => {
            this.changeFontSize(parseInt(e.target.value));
        });

        // Load initial data
        this.loadProjects();
        this.loadSettings();
    }

    // ========== Project Management ==========

    async loadProjects() {
        try {
            const projects = await api.getProjects();
            this.populateProjectSelector(projects);
        } catch (error) {
            console.error('Failed to load projects:', error);
            this.showNotification('Failed to load projects', 'error');
        }
    }

    populateProjectSelector(projects) {
        const selector = this.elements.projectSelector;
        selector.innerHTML = '<option value="">选择项目 (Select Project)</option>';

        projects.forEach((project) => {
            const option = document.createElement('option');
            option.value = project.id;
            option.textContent = project.name;
            selector.appendChild(option);
        });
    }

    async loadProject(projectId) {
        try {
            this.currentProjectId = projectId;
            const dashboardData = await api.getProjectDashboard(projectId);

            // Update project overview
            this.elements.projectName.textContent = dashboardData.project.name;
            this.elements.projectDomain.textContent = dashboardData.project.domain;

            // Calculate progress
            const completedTasks = dashboardData.tasks.filter((t) => t.status === 'completed').length;
            const progress = (completedTasks / dashboardData.tasks.length) * 100 || 0;
            this.elements.progressFill.style.width = `${progress}%`;

            // Update stats
            this.elements.totalHours.textContent = `${dashboardData.time_stats.total_hours.toFixed(1)}h`;
            this.elements.todayPomodoros.textContent = dashboardData.time_stats.pomodoros_count;

            // Render tasks
            this.renderTasks(dashboardData.tasks);

            // Render coaching notes
            this.renderCoachingNotes(dashboardData.recent_coaching_notes);

            // Render file browser
            this.renderFileTree(dashboardData.project);

            // Show project content
            this.elements.emptyState.style.display = 'none';
            this.elements.projectContent.style.display = 'block';

            // Connect to WebSocket for real-time updates
            if (this.pomodoroWebSocket) {
                this.pomodoroWebSocket.close();
            }
            this.connectPomodoroWebSocket(projectId);

            // Store dashboard data for analytics
            this.currentDashboardData = dashboardData;
        } catch (error) {
            console.error('Failed to load project:', error);
            this.showNotification('Failed to load project', 'error');
        }
    }

    showTasksTab() {
        if (!this.elements.tasksView || !this.elements.chatView) return;
        this.elements.tasksView.style.display = 'block';
        this.elements.chatView.style.display = 'none';
        if (this.elements.tabTasksBtn && this.elements.tabChatBtn) {
            this.elements.tabTasksBtn.classList.add('active');
            this.elements.tabChatBtn.classList.remove('active');
            this.elements.tabTasksBtn.setAttribute('aria-selected', 'true');
            this.elements.tabChatBtn.setAttribute('aria-selected', 'false');
        }
    }

    showChatTab() {
        if (!this.elements.tasksView || !this.elements.chatView) return;
        this.elements.tasksView.style.display = 'none';
        this.elements.chatView.style.display = 'block';
        if (this.elements.tabTasksBtn && this.elements.tabChatBtn) {
            this.elements.tabChatBtn.classList.add('active');
            this.elements.tabTasksBtn.classList.remove('active');
            this.elements.tabChatBtn.setAttribute('aria-selected', 'true');
            this.elements.tabTasksBtn.setAttribute('aria-selected', 'false');
        }
        this.updateChatContextPreview();
        if (this.elements.chatInput) {
            this.elements.chatInput.focus();
        }
    }

    clearChat() {
        this.chatHistory = [];
        if (this.elements.chatMessages) {
            this.elements.chatMessages.innerHTML = '';
        }
        this.updateChatContextPreview();
    }

    toggleChatSettings() {
        if (!this.elements.chatSettingsPanel || !this.elements.chatSettingsBtn) return;
        const shouldOpen = this.elements.chatSettingsPanel.hidden;
        this.elements.chatSettingsPanel.hidden = !shouldOpen;
        this.elements.chatSettingsBtn.classList.toggle('active', shouldOpen);
        this.elements.chatSettingsBtn.setAttribute('aria-expanded', String(shouldOpen));
    }

    escapeHtml(value) {
        return String(value || '')
            .replace(/&/g, '&amp;')
            .replace(/</g, '&lt;')
            .replace(/>/g, '&gt;')
            .replace(/"/g, '&quot;')
            .replace(/'/g, '&#39;');
    }

    renderMarkdownInline(text) {
        return this.escapeHtml(text)
            .replace(/`([^`]+)`/g, '<code>$1</code>')
            .replace(/\*\*([^*]+)\*\*/g, '<strong>$1</strong>')
            .replace(/__([^_]+)__/g, '<strong>$1</strong>')
            .replace(/~~(.+?)~~/g, '<del>$1</del>')
            .replace(/\*([^*]+)\*/g, '<em>$1</em>');
    }

    renderMarkdown(content) {
        const lines = String(content || '').replace(/\r\n/g, '\n').split('\n');
        const html = [];
        let listType = null;
        let listClass = '';

        const closeList = () => {
            if (!listType) return;
            html.push(`</${listType}>`);
            listType = null;
            listClass = '';
        };

        const openList = (type, className = '') => {
            if (listType === type && listClass === className) return;
            closeList();
            html.push(`<${type}${className ? ` class="${className}"` : ''}>`);
            listType = type;
            listClass = className;
        };

        lines.forEach((line) => {
            const trimmed = line.trim();
            if (!trimmed) {
                closeList();
                return;
            }

            const headingMatch = trimmed.match(/^(#{1,3})\s+(.+)$/);
            if (headingMatch) {
                closeList();
                const level = Math.min(headingMatch[1].length + 3, 6);
                html.push(`<h${level}>${this.renderMarkdownInline(headingMatch[2])}</h${level}>`);
                return;
            }

            const checkboxMatch = trimmed.match(/^[-*]\s+\[([ xX])\]\s+(.+)$/);
            if (checkboxMatch) {
                openList('ul', 'markdown-checklist');
                const checked = checkboxMatch[1].toLowerCase() === 'x' ? ' checked' : '';
                html.push(`<li><input type="checkbox" disabled${checked}> <span>${this.renderMarkdownInline(checkboxMatch[2])}</span></li>`);
                return;
            }

            const orderedMatch = trimmed.match(/^\d+\.\s+(.+)$/);
            if (orderedMatch) {
                openList('ol');
                html.push(`<li>${this.renderMarkdownInline(orderedMatch[1])}</li>`);
                return;
            }

            const unorderedMatch = trimmed.match(/^[-*]\s+(.+)$/);
            if (unorderedMatch) {
                openList('ul');
                html.push(`<li>${this.renderMarkdownInline(unorderedMatch[1])}</li>`);
                return;
            }

            const quoteMatch = trimmed.match(/^>\s+(.+)$/);
            if (quoteMatch) {
                closeList();
                html.push(`<blockquote>${this.renderMarkdownInline(quoteMatch[1])}</blockquote>`);
                return;
            }

            closeList();
            html.push(`<p>${this.renderMarkdownInline(trimmed)}</p>`);
        });

        closeList();
        return html.join('');
    }

    appendChatMessage(role, content) {
        this.chatHistory.push({ role, content });
        if (!this.elements.chatMessages) return;
        const el = document.createElement('div');
        el.className = `chat-message ${role}`;
        if (role === 'assistant') {
            el.innerHTML = this.renderMarkdown(content);
        } else {
            el.textContent = content;
        }
        this.elements.chatMessages.appendChild(el);
        this.elements.chatMessages.scrollTop = this.elements.chatMessages.scrollHeight;
    }

    buildChatPayload() {
        const provider = this.elements.chatProviderSelect?.value || this.elements.llmProviderSelect?.value || 'claude_code';
        const modelInput = (this.elements.chatModelInput?.value || '').trim();
        const model = modelInput || this.elements.llmModelSelect?.value || null;
        const mode = this.elements.chatModeSelect?.value || 'task_breakdown';
        const system_prompt = (this.elements.chatSystemPromptInput?.value || '').trim() || null;
        const limit = parseInt(this.elements.chatContextLimit?.value || '8000', 10) || 8000;

        let total = 0;
        const selected = [];
        for (let i = this.chatHistory.length - 1; i >= 0; i--) {
            const m = this.chatHistory[i];
            const size = (m.content || '').length;
            if (selected.length > 0 && total + size > limit) break;
            selected.unshift({ role: m.role, content: m.content });
            total += size;
        }

        return { provider, model, mode, system_prompt, messages: selected };
    }

    updateChatContextPreview() {
        if (!this.elements.chatContextPreview) return;
        const payload = this.buildChatPayload();
        this.elements.chatContextPreview.textContent = JSON.stringify(payload, null, 2);
    }

    updateChatModelSummary() {
        if (!this.elements.chatModelSummary) return;
        const providerLabel = this.elements.chatProviderSelect
            ? this.elements.chatProviderSelect.options[this.elements.chatProviderSelect.selectedIndex]?.textContent || 'Claude Code'
            : 'Claude Code';
        const model = (this.elements.chatModelInput?.value || this.elements.llmModelSelect?.value || 'sonnet').trim();
        const modeLabel = this.elements.chatModeSelect
            ? this.elements.chatModeSelect.options[this.elements.chatModeSelect.selectedIndex]?.textContent || '任务拆分'
            : '任务拆分';
        this.elements.chatModelSummary.textContent = `${providerLabel} · ${model || '默认模型'} · ${modeLabel}`;
    }

    async sendChat() {
        if (!this.elements.chatInput) return;
        const text = (this.elements.chatInput.value || '').trim();
        if (!text) return;
        this.elements.chatInput.value = '';
        this.appendChatMessage('user', text);
        this.updateChatContextPreview();

        try {
            const payload = this.buildChatPayload();
            const res = await api.chat(payload);
            this.appendChatMessage('assistant', res.message.content || '');
            this.updateChatContextPreview();
        } catch (error) {
            console.error('Chat failed:', error);
            this.appendChatMessage('assistant', `请求失败：${error.message || error}`);
            this.showNotification('对话请求失败', 'error');
        }
    }

    // ========== Task Rendering ==========

    renderTasks(tasks) {
        const taskList = this.elements.taskList;
        taskList.innerHTML = '';

        if (tasks.length === 0) {
            taskList.innerHTML = '<div class="empty-message">暂无任务</div>';
            return;
        }

        tasks.forEach((task) => {
            const taskItem = document.createElement('div');
            taskItem.className = `task-item ${task.status}`;
            taskItem.dataset.status = task.status;

            const estimatedStr = task.estimated_minutes > 0
                ? `估计${task.estimated_minutes}分钟`
                : '未评估';
            const actualStr = task.actual_minutes > 0
                ? `实际${task.actual_minutes}分钟`
                : '进行中';

            taskItem.innerHTML = `
                <div class="task-header">
                    <div class="task-title">${task.title}</div>
                    <span class="task-status ${task.status}">${this.getTaskStatusText(task.status)}</span>
                </div>
                <div class="task-description">${task.description || '无描述'}</div>
                <div class="task-meta">
                    <div class="task-meta-item">
                        <i class="fas fa-clock"></i>
                        ${estimatedStr}
                    </div>
                    <div class="task-meta-item">
                        <i class="fas fa-stopwatch"></i>
                        ${actualStr}
                    </div>
                    <div class="task-meta-item">
                        <i class="fas fa-tasks"></i>
                        阶段: ${task.phase}
                    </div>
                </div>
            `;

            taskItem.addEventListener('click', () => this.selectTask(task));
            taskList.appendChild(taskItem);
        });
    }

    renderCoachingNotes(notes) {
        const coachingNotes = this.elements.coachingNotes;
        coachingNotes.innerHTML = '';

        if (notes.length === 0) {
            coachingNotes.innerHTML = '<div class="empty-message">暂无指导</div>';
            return;
        }

        notes.forEach((note) => {
            const noteDiv = document.createElement('div');
            noteDiv.className = `coaching-note ${note.type}`;
            noteDiv.innerHTML = `
                <div class="note-content">${note.content}</div>
                <div class="note-time">${new Date(note.created_at).toLocaleDateString('zh-CN')}</div>
            `;
            coachingNotes.appendChild(noteDiv);
        });
    }

    // ========== Timer Management ==========

    startTimer() {
        if (this.isTimerRunning) return;

        this.isTimerRunning = true;
        this.elements.startBtn.disabled = true;
        this.elements.pauseBtn.disabled = false;

        this.timerInterval = setInterval(() => {
            this.timeRemaining--;

            if (this.timeRemaining <= 0) {
                this.completeTimerPhase();
            } else {
                this.updateTimerDisplay();
            }
        }, 1000);

        this.updateTimerDisplay();
    }

    pauseTimer() {
        this.isTimerRunning = false;
        clearInterval(this.timerInterval);

        this.elements.startBtn.disabled = false;
        this.elements.pauseBtn.disabled = true;

        this.elements.timerStatus.textContent = '已暂停';
    }

    resetTimer() {
        this.isTimerRunning = false;
        clearInterval(this.timerInterval);

        this.timeRemaining = this.currentPhase === 'work' ? 25 * 60 : 5 * 60;
        this.updateTimerDisplay();

        this.elements.startBtn.disabled = false;
        this.elements.pauseBtn.disabled = true;
        this.elements.timerStatus.textContent = '准备就绪';
    }

    completeTimerPhase() {
        clearInterval(this.timerInterval);
        this.isTimerRunning = false;

        if (this.currentPhase === 'work') {
            this.pomodorosCompleted++;
            this.elements.todayPomodoros.textContent = this.pomodorosCompleted;

            // Determine break duration
            const breakDuration = this.pomodorosCompleted % 4 === 0 ? 15 : 5;
            this.timeRemaining = breakDuration * 60;
            this.currentPhase = 'break';

            this.showNotification(
                `🎉 一个番茄钟完成！休息${breakDuration}分钟吧。`,
                'success'
            );

            // Log the completed pomodoro
            if (this.currentProjectId) {
                api.logTime({
                    task_id: this.currentTaskId || '',
                    project_id: this.currentProjectId,
                    duration_minutes: 25,
                    pomodoros: 1,
                    completed: false,
                }).catch(console.error);
            }
        } else {
            // Break completed
            this.timeRemaining = 25 * 60;
            this.currentPhase = 'work';
            this.showNotification('✅ 休息结束，准备好继续工作！', 'success');
        }

        this.updateTimerDisplay();
        this.elements.startBtn.disabled = false;
        this.elements.pauseBtn.disabled = true;
    }

    updateTimerDisplay() {
        const minutes = Math.floor(this.timeRemaining / 60);
        const seconds = this.timeRemaining % 60;
        this.elements.timerDisplay.textContent =
            `${minutes.toString().padStart(2, '0')}:${seconds.toString().padStart(2, '0')}`;

        if (this.isTimerRunning) {
            this.elements.timerStatus.textContent =
                this.currentPhase === 'work' ? '⏱️ 工作中...' : '☕ 休息中...';
        }
    }

    // ========== Panel Expansion ==========

    toggleLeftPanelExpand() {
        const expanded = this.elements.leftPanel.classList.contains('expanded');
        if (expanded) {
            this.elements.leftPanel.classList.remove('expanded');
        } else {
            this.elements.leftPanel.classList.add('expanded');
        }
    }

    toggleRightPanelExpand() {
        const expanded = this.elements.rightPanel.classList.contains('expanded');
        if (expanded) {
            this.elements.rightPanel.classList.remove('expanded');
        } else {
            this.elements.rightPanel.classList.add('expanded');
        }
    }

    // ========== File Tree Rendering ==========

    renderFileTree(project) {
        const browser = this.elements.workspaceBrowser;
        browser.innerHTML = '';

        const folders = ['📋 Roadmap', '📊 Task Progress', '🤖 Coach Log'];
        const list = document.createElement('ul');
        list.className = 'file-tree';

        folders.forEach((folder) => {
            const item = document.createElement('li');
            item.className = 'file-item folder';
            item.innerHTML = `
                <span class="file-icon">📁</span>
                <span class="file-label">${folder}</span>
            `;
            list.appendChild(item);
        });

        browser.appendChild(list);
    }

    // ========== Analytics ==========

    async showAnalytics() {
        if (!this.currentDashboardData) return;

        const modal = this.elements.analyticsModal;
        modal.classList.add('active');

        const stats = this.currentDashboardData.time_stats;

        // Update statistics table
        this.elements.statsTableBody.innerHTML = `
            <tr>
                <td>总计小时数</td>
                <td>${stats.total_hours.toFixed(1)}h</td>
            </tr>
            <tr>
                <td>平均任务耗时</td>
                <td>${stats.average_duration.toFixed(0)} 分钟</td>
            </tr>
            <tr>
                <td>番茄钟总数</td>
                <td>${stats.pomodoros_count}</td>
            </tr>
            <tr>
                <td>按时完成率</td>
                <td>${stats.on_time_percent.toFixed(0)}%</td>
            </tr>
            <tr>
                <td>最快任务</td>
                <td>${stats.fastest_task || '-'}</td>
            </tr>
            <tr>
                <td>最慢任务</td>
                <td>${stats.slowest_task || '-'}</td>
            </tr>
        `;

        // Render gantt chart
        this.renderGanttChart(this.currentDashboardData.gantt_data);

        // Render pie chart
        this.renderPieChart(this.currentDashboardData.tasks);
    }

    closeAnalytics() {
        this.elements.analyticsModal.classList.remove('active');
    }

    renderGanttChart(ganttData) {
        const ganttContainer = this.elements.ganttChart;
        ganttContainer.innerHTML = '';

        if (!ganttData.tasks || ganttData.tasks.length === 0) {
            ganttContainer.innerHTML = '<div class="empty-message">暂无任务数据</div>';
            return;
        }

        const chart = document.createElement('pre');
        chart.style.fontSize = '0.85rem';
        chart.style.overflow = 'auto';
        chart.textContent = this.generateASCIIGantt(ganttData.tasks);
        ganttContainer.appendChild(chart);
    }

    generateASCIIGantt(tasks) {
        let chart = '📊 任务甘特图\n\n';
        chart += '任务名'.padEnd(20) + '进度\n';
        chart += '='.repeat(50) + '\n';

        tasks.forEach((task) => {
            const barLength = Math.ceil((task.duration / 120) * 20); // Normalize to 120 min
            const bar = '█'.repeat(Math.min(barLength, 20));
            chart += task.name.substring(0, 20).padEnd(20) + bar + '\n';
        });

        return chart;
    }

    renderPieChart(tasks) {
        const canvas = this.elements.pieChartCanvas;
        const ctx = canvas.getContext('2d');

        const statusCounts = {
            'completed': tasks.filter((t) => t.status === 'completed').length,
            'in_progress': tasks.filter((t) => t.status === 'in_progress').length,
            'pending': tasks.filter((t) => t.status === 'pending').length,
        };

        new Chart(ctx, {
            type: 'doughnut',
            data: {
                labels: ['已完成', '进行中', '待办'],
                datasets: [
                    {
                        data: [
                            statusCounts.completed,
                            statusCounts.in_progress,
                            statusCounts.pending,
                        ],
                        backgroundColor: ['#10b981', '#f59e0b', '#ef4444'],
                    },
                ],
            },
            options: {
                responsive: true,
                maintainAspectRatio: true,
            },
        });
    }

    // ========== Settings ==========

    showSettings() {
        this.elements.settingsModal.classList.add('active');
    }

    closeSettings() {
        this.elements.settingsModal.classList.remove('active');
    }

    async saveSettings() {
        const settings = {
            theme: this.elements.themeToggle.checked ? 'dark' : 'light',
            font_size: parseInt(this.elements.fontSizeSlider.value),
            language: this.elements.languageSelect.value,
            llm_provider: this.elements.llmProviderSelect.value,
            llm_model: this.elements.llmModelSelect.value,
            llm_base_url: (this.elements.llmBaseUrlInput?.value || '').trim() || null,
            cli_claude_command: (this.elements.cliClaudeCommandInput?.value || '').trim() || null,
            cli_codex_command: (this.elements.cliCodexCommandInput?.value || '').trim() || null,
            cli_timeout_seconds: parseInt(this.elements.cliTimeoutInput?.value || '120', 10) || 120,
        };

        const apiKey = (this.elements.llmApiKeyInput?.value || '').trim();
        if (apiKey) {
            settings.llm_api_key = apiKey;
        }

        try {
            await api.updateSettings(settings);
            this.showNotification('设置已保存', 'success');
            if (this.elements.llmApiKeyInput) {
                this.elements.llmApiKeyInput.value = '';
            }
            this.closeSettings();
        } catch (error) {
            console.error('Failed to save settings:', error);
            this.showNotification('保存设置失败', 'error');
        }
    }

    async loadSettings() {
        try {
            const settings = await api.getSettings();

            this.elements.themeToggle.checked = settings.theme === 'dark';
            this.elements.fontSizeSlider.value = settings.font_size;
            this.elements.fontSizeValue.textContent = settings.font_size;
            this.elements.languageSelect.value = settings.language;
            this.elements.llmProviderSelect.value = settings.llm_provider;
            this.elements.llmModelSelect.value = settings.llm_model;
            if (this.elements.llmBaseUrlInput) {
                this.elements.llmBaseUrlInput.value = settings.llm_base_url || '';
            }
            if (this.elements.cliClaudeCommandInput) {
                this.elements.cliClaudeCommandInput.value = settings.cli_claude_command || '';
            }
            if (this.elements.cliCodexCommandInput) {
                this.elements.cliCodexCommandInput.value = settings.cli_codex_command || '';
            }
            if (this.elements.cliTimeoutInput) {
                this.elements.cliTimeoutInput.value = settings.cli_timeout_seconds || 120;
            }
            if (this.elements.llmApiKeyInput) {
                this.elements.llmApiKeyInput.placeholder = settings.has_llm_api_key
                    ? '已保存（本地加密）；输入新 key 将覆盖'
                    : '未设置；输入 key 将保存';
            }

            if (this.elements.chatProviderSelect) {
                const providerSupportedInChat = Array.from(this.elements.chatProviderSelect.options)
                    .some((option) => option.value === settings.llm_provider);
                if (settings.llm_provider && providerSupportedInChat) {
                    this.elements.chatProviderSelect.value = settings.llm_provider;
                } else {
                    this.elements.chatProviderSelect.value = 'claude_code';
                }
            }
            if (this.elements.chatModelInput) {
                this.elements.chatModelInput.value = settings.llm_model || '';
            }

            // Apply theme and font size
            this.toggleTheme(settings.theme === 'dark');
            this.changeFontSize(settings.font_size);
            this.updateChatModelSummary();
            this.updateChatContextPreview();
        } catch (error) {
            console.error('Failed to load settings:', error);
        }
    }

    toggleTheme(isDark) {
        if (isDark) {
            document.body.classList.add('dark-mode');
        } else {
            document.body.classList.remove('dark-mode');
        }
    }

    changeFontSize(size) {
        document.documentElement.style.fontSize = `${size}px`;
        this.elements.fontSizeValue.textContent = size;
    }

    // ========== Utility Methods ==========

    getTaskStatusText(status) {
        const statusMap = {
            'pending': '待办',
            'in_progress': '进行中',
            'completed': '已完成',
        };
        return statusMap[status] || status;
    }

    filterTasks(filter) {
        const tasks = document.querySelectorAll('.task-item');
        tasks.forEach((task) => {
            if (filter === 'all') {
                task.style.display = '';
            } else {
                task.style.display = task.dataset.status === filter ? '' : 'none';
            }
        });
    }

    selectTask(task) {
        this.currentTaskId = task.id;
    }

    connectPomodoroWebSocket(projectId) {
        this.pomodoroWebSocket = api.connectPomodoroWebSocket(projectId, {
            onOpen: () => {
                console.log('Connected to Pomodoro updates');
            },
            onMessage: (data) => {
                console.log('Pomodoro update:', data);
                // Handle real-time updates
            },
            onError: (error) => {
                console.error('WebSocket error:', error);
            },
            onClose: () => {
                console.log('Disconnected from Pomodoro updates');
            },
        });
    }

    showNotification(message, type = 'info') {
        const notification = document.createElement('div');
        notification.className = `notification notification-${type}`;
        notification.textContent = message;
        notification.style.cssText = `
            position: fixed;
            bottom: 20px;
            right: 20px;
            background-color: ${type === 'error' ? '#ef4444' : type === 'success' ? '#10b981' : '#6366f1'};
            color: white;
            padding: 16px 24px;
            border-radius: 8px;
            box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
            z-index: 9999;
            animation: slideInRight 0.3s ease;
        `;

        document.body.appendChild(notification);

        setTimeout(() => {
            notification.style.animation = 'slideOutRight 0.3s ease';
            setTimeout(() => notification.remove(), 300);
        }, 3000);
    }
}

// Create global UI instance
const ui = new DashboardUI();
