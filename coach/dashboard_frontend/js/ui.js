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
        this.focusDurationMinutes = this.readStoredPomodoroDuration();
        this.breakDurationMinutes = 5;
        this.longBreakDurationMinutes = 15;
        this.currentBreakDurationMinutes = this.breakDurationMinutes;
        this.currentPhaseDurationSeconds = this.focusDurationMinutes * 60;
        this.timeRemaining = this.currentPhaseDurationSeconds;
        this.isTimerRunning = false;
        this.currentPhase = 'work'; // 'work' or 'break'
        this.pomodorosCompleted = 0;
        this.totalFocusMinutes = 0;
        this.timerViewMode = this.readStoredTimerViewMode();
        this.analyticsDataMode = 'auto';
        this.pieChartInstance = null;
        this.isChatRunning = false;
        this.chatRuntimeHideTimer = null;
        this.lastChatUserText = '';

        this.initializeElements();
        this.initializeTimerControls();
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
            chatRuntime: document.getElementById('chatRuntime'),
            chatRuntimeIcon: document.getElementById('chatRuntimeIcon'),
            chatRuntimeText: document.getElementById('chatRuntimeText'),
            chatRuntimeToggle: document.getElementById('chatRuntimeToggle'),
            chatRuntimeTrace: document.getElementById('chatRuntimeTrace'),
            chatRuntimeTraceList: document.getElementById('chatRuntimeTraceList'),
            chatInput: document.getElementById('chatInput'),
            chatSendBtn: document.getElementById('chatSendBtn'),
            chatContextPreview: document.getElementById('chatContextPreview'),

            // Timer
            timerDurationInput: document.getElementById('timerDurationInput'),
            timerViewTimeBtn: document.getElementById('timerViewTimeBtn'),
            timerViewRingBtn: document.getElementById('timerViewRingBtn'),
            timerTimeView: document.getElementById('timerTimeView'),
            timerRingView: document.getElementById('timerRingView'),
            timerRing: document.getElementById('timerRing'),
            timerRingTime: document.getElementById('timerRingTime'),
            timerRingPhase: document.getElementById('timerRingPhase'),
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
            analyticsModeLabel: document.getElementById('analyticsModeLabel'),
            loadDemoAnalyticsBtn: document.getElementById('loadDemoAnalyticsBtn'),
            clearAnalyticsDataBtn: document.getElementById('clearAnalyticsDataBtn'),
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
        if (this.elements.chatRuntimeToggle) {
            this.elements.chatRuntimeToggle.addEventListener('click', () => this.toggleChatRuntimeTrace());
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
        if (this.elements.timerDurationInput) {
            this.elements.timerDurationInput.addEventListener('change', () => this.handleTimerDurationChange());
        }
        if (this.elements.timerViewTimeBtn) {
            this.elements.timerViewTimeBtn.addEventListener('click', () => this.setTimerViewMode('time'));
        }
        if (this.elements.timerViewRingBtn) {
            this.elements.timerViewRingBtn.addEventListener('click', () => this.setTimerViewMode('ring'));
        }

        // Panel expansion
        this.elements.expandLeftBtn.addEventListener('click', () => this.toggleLeftPanelExpand());
        this.elements.expandRightBtn.addEventListener('click', () => this.toggleRightPanelExpand());

        // Analytics
        this.elements.viewAnalyticsBtn.addEventListener('click', () => this.showAnalytics());
        if (this.elements.loadDemoAnalyticsBtn) {
            this.elements.loadDemoAnalyticsBtn.addEventListener('click', () => this.setAnalyticsMode('demo'));
        }
        if (this.elements.clearAnalyticsDataBtn) {
            this.elements.clearAnalyticsDataBtn.addEventListener('click', () => this.setAnalyticsMode('empty'));
        }

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

    readStoredPomodoroDuration() {
        const stored = localStorage.getItem('coachFocusDurationMinutes');
        return this.clampDurationMinutes(stored || 25);
    }

    readStoredTimerViewMode() {
        const stored = localStorage.getItem('coachTimerViewMode');
        return stored === 'ring' ? 'ring' : 'time';
    }

    clampDurationMinutes(value) {
        const parsed = parseInt(value, 10);
        if (Number.isNaN(parsed)) return 25;
        return Math.min(240, Math.max(1, parsed));
    }

    initializeTimerControls() {
        if (this.elements.timerDurationInput) {
            this.elements.timerDurationInput.value = this.focusDurationMinutes;
        }
        if (this.elements.pauseBtn) {
            this.elements.pauseBtn.disabled = true;
        }
        this.setTimerViewMode(this.timerViewMode);
        this.updatePomodoroStatsDisplay();
        this.updateTimerDisplay();
    }

    handleTimerDurationChange() {
        if (!this.elements.timerDurationInput) return;
        const previousDurationSeconds = this.currentPhaseDurationSeconds || this.focusDurationMinutes * 60;
        const nextDuration = this.clampDurationMinutes(this.elements.timerDurationInput.value);

        this.focusDurationMinutes = nextDuration;
        this.elements.timerDurationInput.value = nextDuration;
        localStorage.setItem('coachFocusDurationMinutes', String(nextDuration));

        if (this.currentPhase === 'work') {
            const nextDurationSeconds = nextDuration * 60;
            const elapsedSeconds = this.isTimerRunning
                ? Math.max(0, previousDurationSeconds - this.timeRemaining)
                : 0;
            this.currentPhaseDurationSeconds = nextDurationSeconds;
            this.timeRemaining = this.isTimerRunning
                ? Math.max(1, nextDurationSeconds - elapsedSeconds)
                : nextDurationSeconds;
            if (!this.isTimerRunning) {
                this.elements.timerStatus.textContent = '准备就绪';
            }
        }

        this.updateTimerDisplay();
    }

    setTimerViewMode(mode) {
        this.timerViewMode = mode === 'ring' ? 'ring' : 'time';
        localStorage.setItem('coachTimerViewMode', this.timerViewMode);

        const isRing = this.timerViewMode === 'ring';
        this.elements.timerTimeView?.classList.toggle('hidden', isRing);
        this.elements.timerRingView?.classList.toggle('hidden', !isRing);
        this.elements.timerViewTimeBtn?.classList.toggle('active', !isRing);
        this.elements.timerViewRingBtn?.classList.toggle('active', isRing);
        this.elements.timerViewTimeBtn?.setAttribute('aria-pressed', String(!isRing));
        this.elements.timerViewRingBtn?.setAttribute('aria-pressed', String(isRing));
        this.updateTimerDisplay();
    }

    formatMinutes(totalMinutes) {
        const roundedMinutes = Math.max(0, Math.round(totalMinutes || 0));
        const hours = Math.floor(roundedMinutes / 60);
        const minutes = roundedMinutes % 60;
        return `${hours}h ${minutes}m`;
    }

    updatePomodoroStatsDisplay() {
        if (this.elements.todayPomodoros) {
            this.elements.todayPomodoros.textContent = this.pomodorosCompleted;
        }
        if (this.elements.totalHours) {
            this.elements.totalHours.textContent = this.formatMinutes(this.totalFocusMinutes);
        }
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
            this.totalFocusMinutes = Math.round((dashboardData.time_stats.total_hours || 0) * 60);
            this.pomodorosCompleted = dashboardData.time_stats.pomodoros_count || 0;
            this.updatePomodoroStatsDisplay();

            // Render tasks
            this.renderTasks(dashboardData.tasks);

            // Render coaching notes
            this.renderCoachingNotes(dashboardData.recent_coaching_notes);

            // Render file browser
            this.renderFileTree(dashboardData.project, dashboardData.workspace_files || []);

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
            this.analyticsDataMode = 'auto';
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
            .replace(/\[([^\]]+)\]\((https?:\/\/[^)\s]+)\)/g, '<a href="$2" target="_blank" rel="noopener noreferrer">$1</a>')
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
        let tableRows = [];

        const closeList = () => {
            if (!listType) return;
            html.push(`</${listType}>`);
            listType = null;
            listClass = '';
        };

        const closeTable = () => {
            if (tableRows.length === 0) return;
            const rows = tableRows
                .filter((row) => !/^\|?\s*:?-{3,}:?\s*(\|\s*:?-{3,}:?\s*)+\|?$/.test(row))
                .map((row) => row.trim().replace(/^\|/, '').replace(/\|$/, '').split('|').map((cell) => cell.trim()));
            tableRows = [];
            if (rows.length === 0) return;

            const [header, ...bodyRows] = rows;
            html.push('<div class="markdown-table-wrap"><table class="markdown-table"><thead><tr>');
            header.forEach((cell) => {
                html.push(`<th>${this.renderMarkdownInline(cell)}</th>`);
            });
            html.push('</tr></thead><tbody>');
            bodyRows.forEach((row) => {
                html.push('<tr>');
                row.forEach((cell) => {
                    html.push(`<td>${this.renderMarkdownInline(cell)}</td>`);
                });
                html.push('</tr>');
            });
            html.push('</tbody></table></div>');
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
                closeTable();
                return;
            }

            if (/^\|.+\|$/.test(trimmed)) {
                closeList();
                tableRows.push(trimmed);
                return;
            }

            const headingMatch = trimmed.match(/^(#{1,3})\s+(.+)$/);
            if (headingMatch) {
                closeList();
                closeTable();
                const level = Math.min(headingMatch[1].length + 3, 6);
                html.push(`<h${level}>${this.renderMarkdownInline(headingMatch[2])}</h${level}>`);
                return;
            }

            const checkboxMatch = trimmed.match(/^[-*]\s+\[([ xX])\]\s+(.+)$/);
            if (checkboxMatch) {
                closeTable();
                openList('ul', 'markdown-checklist');
                const checked = checkboxMatch[1].toLowerCase() === 'x' ? ' checked' : '';
                html.push(`<li><input type="checkbox" disabled${checked}> <span>${this.renderMarkdownInline(checkboxMatch[2])}</span></li>`);
                return;
            }

            const orderedMatch = trimmed.match(/^\d+\.\s+(.+)$/);
            if (orderedMatch) {
                closeTable();
                openList('ol');
                html.push(`<li>${this.renderMarkdownInline(orderedMatch[1])}</li>`);
                return;
            }

            const unorderedMatch = trimmed.match(/^[-*]\s+(.+)$/);
            if (unorderedMatch) {
                closeTable();
                openList('ul');
                html.push(`<li>${this.renderMarkdownInline(unorderedMatch[1])}</li>`);
                return;
            }

            const quoteMatch = trimmed.match(/^>\s+(.+)$/);
            if (quoteMatch) {
                closeList();
                closeTable();
                html.push(`<blockquote>${this.renderMarkdownInline(quoteMatch[1])}</blockquote>`);
                return;
            }

            closeList();
            closeTable();
            html.push(`<p>${this.renderMarkdownInline(trimmed)}</p>`);
        });

        closeList();
        closeTable();
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
        return el;
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

    setChatRuntimeState(state, message) {
        if (!this.elements.chatRuntime || !this.elements.chatRuntimeText) return;
        clearTimeout(this.chatRuntimeHideTimer);
        this.elements.chatRuntime.hidden = false;
        this.elements.chatRuntime.dataset.state = state;
        this.elements.chatRuntimeText.textContent = message;
    }

    hideChatRuntime(delayMs = 900) {
        clearTimeout(this.chatRuntimeHideTimer);
        this.chatRuntimeHideTimer = setTimeout(() => {
            if (this.elements.chatRuntime) {
                this.elements.chatRuntime.hidden = true;
            }
        }, delayMs);
    }

    resetChatRuntime() {
        clearTimeout(this.chatRuntimeHideTimer);
        if (this.elements.chatRuntimeTraceList) {
            this.elements.chatRuntimeTraceList.innerHTML = '';
        }
        if (this.elements.chatRuntimeTrace) {
            this.elements.chatRuntimeTrace.hidden = true;
        }
        if (this.elements.chatRuntimeToggle) {
            this.elements.chatRuntimeToggle.setAttribute('aria-expanded', 'false');
            this.elements.chatRuntimeToggle.textContent = '过程';
        }
    }

    toggleChatRuntimeTrace() {
        if (!this.elements.chatRuntimeTrace || !this.elements.chatRuntimeToggle) return;
        const shouldOpen = this.elements.chatRuntimeTrace.hidden;
        this.elements.chatRuntimeTrace.hidden = !shouldOpen;
        this.elements.chatRuntimeToggle.setAttribute('aria-expanded', String(shouldOpen));
        this.elements.chatRuntimeToggle.textContent = shouldOpen ? '折叠' : '过程';
    }

    addChatTrace(message, state = 'running', meta = '') {
        if (!this.elements.chatRuntimeTraceList || !message) return;

        const item = document.createElement('div');
        item.className = `chat-trace-item chat-trace-${state}`;

        const time = new Date().toLocaleTimeString('zh-CN', {
            hour: '2-digit',
            minute: '2-digit',
            second: '2-digit',
        });

        const prefix = document.createElement('span');
        prefix.className = 'chat-trace-time';
        prefix.textContent = time;

        const content = document.createElement('span');
        content.className = 'chat-trace-content';
        content.textContent = meta ? `${meta}: ${message}` : message;

        item.appendChild(prefix);
        item.appendChild(content);
        this.elements.chatRuntimeTraceList.appendChild(item);

        const items = this.elements.chatRuntimeTraceList.querySelectorAll('.chat-trace-item');
        if (items.length > 80) {
            items[0].remove();
        }
        this.elements.chatRuntimeTraceList.scrollTop = this.elements.chatRuntimeTraceList.scrollHeight;
    }

    normalizeChatError(error) {
        const message = String(error?.message || error || '未知错误');
        if (message.includes('Failed to fetch')) {
            return '连接失败：请确认后端正在运行，并用 http://127.0.0.1:8001/ 打开页面';
        }
        if (message.includes('cli_not_found') || message.includes('CLI not found')) {
            return '本地 CLI 未找到：请检查 Claude Code / Codex 命令配置';
        }
        if (message.includes('timeout')) {
            return '模型请求超时：CLI 长时间没有返回';
        }
        return message;
    }

    countTaskLikeItems(content) {
        const lines = String(content || '').split('\n');
        return lines.filter((line) => {
            const trimmed = line.trim();
            return /^[-*+]\s+(?:\[[ xX]\]\s*)?\S+/.test(trimmed)
                || /^\d+[.)、]\s+\S+/.test(trimmed)
                || (/^\|.+\|$/.test(trimmed) && !trimmed.includes('---'));
        }).length;
    }

    deriveChatProjectName() {
        const source = this.lastChatUserText || '对话任务拆分';
        const cleaned = source
            .replace(/[^\w\u4e00-\u9fff ]+/g, ' ')
            .replace(/\s+/g, ' ')
            .trim();
        return (cleaned || '对话任务拆分').slice(0, 28);
    }

    attachTaskSyncAction(messageEl, content) {
        if (!messageEl || !content) return;
        const mode = this.elements.chatModeSelect?.value || 'task_breakdown';
        const taskCount = this.countTaskLikeItems(content);
        if (mode !== 'task_breakdown' && taskCount === 0) return;

        const action = document.createElement('div');
        action.className = 'chat-sync-action';

        const label = document.createElement('span');
        label.className = 'chat-sync-label';
        label.textContent = taskCount > 0
            ? `识别到 ${taskCount} 个候选任务`
            : '可同步为任务拆分';

        const button = document.createElement('button');
        button.className = 'chat-sync-btn';
        button.type = 'button';
        button.innerHTML = '<i class="fas fa-arrows-rotate"></i> 同步到任务拆分';
        button.addEventListener('click', () => this.syncAssistantTasks(content, action, button));

        action.appendChild(label);
        action.appendChild(button);
        messageEl.appendChild(action);
    }

    async syncAssistantTasks(content, actionEl, buttonEl) {
        if (!content || !buttonEl) return;
        buttonEl.disabled = true;
        buttonEl.innerHTML = '<i class="fas fa-spinner fa-spin"></i> 同步中';

        try {
            const syncResult = await api.syncChatTasks({
                project_id: this.currentProjectId,
                project_name: this.deriveChatProjectName(),
                content,
            });

            const projects = await api.getProjects();
            this.populateProjectSelector(projects);
            this.elements.projectSelector.value = syncResult.project.id;
            await this.loadProject(syncResult.project.id);
            this.showTasksTab();

            if (actionEl) {
                actionEl.classList.add('synced');
                const label = actionEl.querySelector('.chat-sync-label');
                if (label) {
                    label.textContent = `已同步 ${syncResult.created_count} 个任务，工作区文件 ${syncResult.workspace_files.length} 个`;
                }
            }
            buttonEl.innerHTML = '<i class="fas fa-check"></i> 已同步';
            this.showNotification('已同步到任务拆分和工作区文件', 'success');
        } catch (error) {
            console.error('Sync tasks failed:', error);
            buttonEl.disabled = false;
            buttonEl.innerHTML = '<i class="fas fa-triangle-exclamation"></i> 重试同步';
            if (actionEl) {
                actionEl.classList.add('sync-error');
                const label = actionEl.querySelector('.chat-sync-label');
                if (label) {
                    label.textContent = `同步失败：${error.message || error}`;
                }
            }
            this.showNotification('任务同步失败', 'error');
        }
    }

    async sendChat() {
        if (!this.elements.chatInput) return;
        if (this.isChatRunning) return;
        const text = (this.elements.chatInput.value || '').trim();
        if (!text) return;
        this.elements.chatInput.value = '';
        this.lastChatUserText = text;
        this.appendChatMessage('user', text);
        this.updateChatContextPreview();

        this.isChatRunning = true;
        this.elements.chatSendBtn.disabled = true;
        this.resetChatRuntime();
        this.setChatRuntimeState('running', '正在发送到模型...');
        this.addChatTrace('请求已进入发送队列', 'running');

        let finalContent = '';
        let streamError = null;

        try {
            const payload = this.buildChatPayload();
            await api.chatStream(payload, {
                status: (data) => {
                    const message = data.message || '模型正在运行中';
                    this.setChatRuntimeState('running', message);
                    this.addChatTrace(message, 'running', data.stage || 'status');
                },
                trace: (data) => {
                    const message = data.message || '';
                    const state = /error|failed|fail|timeout|reconnect|network/i.test(message)
                        ? 'warning'
                        : 'running';
                    this.setChatRuntimeState(state === 'warning' ? 'warning' : 'running', message || '模型过程更新');
                    this.addChatTrace(message, state, data.source || 'process');
                },
                message: (data) => {
                    finalContent = data.content || '';
                },
                error: (data) => {
                    streamError = new Error(data.message || '模型请求失败');
                    this.setChatRuntimeState('error', this.normalizeChatError(streamError));
                    this.addChatTrace(this.normalizeChatError(streamError), 'error', data.code || 'error');
                },
                done: (data) => {
                    this.setChatRuntimeState('done', data.message || '模型回答完成');
                    this.addChatTrace(data.message || '模型回答完成', 'done');
                },
            });

            if (streamError) {
                throw streamError;
            }
            const assistantMessage = this.appendChatMessage('assistant', finalContent || '模型没有返回文本内容。');
            this.attachTaskSyncAction(assistantMessage, finalContent);
            this.updateChatContextPreview();
            this.setChatRuntimeState('done', '回答完成');
            this.hideChatRuntime();
        } catch (error) {
            console.error('Chat failed:', error);
            const readableError = this.normalizeChatError(error);
            this.setChatRuntimeState('error', readableError);
            this.addChatTrace(readableError, 'error', 'request');
            this.appendChatMessage('assistant', `请求失败：${readableError}`);
            this.showNotification('对话请求失败', 'error');
        } finally {
            this.isChatRunning = false;
            this.elements.chatSendBtn.disabled = false;
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
            const createdAt = task.created_at
                ? new Date(task.created_at).toLocaleString('zh-CN', {
                    month: '2-digit',
                    day: '2-digit',
                    hour: '2-digit',
                    minute: '2-digit',
                })
                : '刚刚';
            const safeStatus = this.escapeHtml(task.status || 'pending');
            const safeTitle = this.escapeHtml(task.title || '未命名任务');
            const safePhase = this.escapeHtml(task.phase || '未分组');

            taskItem.innerHTML = `
                <div class="task-header">
                    <div class="task-title-row">
                        <input class="task-check" type="checkbox" disabled ${task.status === 'completed' ? 'checked' : ''}>
                        <div class="task-title">${safeTitle}</div>
                    </div>
                    <span class="task-status ${safeStatus}">${this.getTaskStatusText(task.status)}</span>
                </div>
                <div class="task-description markdown-task">${this.renderMarkdown(task.description || '无描述')}</div>
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
                        阶段: <span class="task-phase-pill">${safePhase}</span>
                    </div>
                    <div class="task-meta-item">
                        <i class="fas fa-calendar-plus"></i>
                        ${createdAt}
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
        if (this.timeRemaining <= 0) {
            this.currentPhaseDurationSeconds = this.currentPhase === 'work'
                ? this.focusDurationMinutes * 60
                : this.currentBreakDurationMinutes * 60;
            this.timeRemaining = this.currentPhaseDurationSeconds;
        }

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

        this.currentPhaseDurationSeconds = this.currentPhase === 'work'
            ? this.focusDurationMinutes * 60
            : this.currentBreakDurationMinutes * 60;
        this.timeRemaining = this.currentPhaseDurationSeconds;
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
            this.totalFocusMinutes += this.focusDurationMinutes;
            this.updatePomodoroStatsDisplay();
            if (this.currentDashboardData?.time_stats) {
                const stats = this.currentDashboardData.time_stats;
                stats.total_hours = this.totalFocusMinutes / 60;
                stats.pomodoros_count = this.pomodorosCompleted;
                stats.average_duration = this.pomodorosCompleted > 0
                    ? this.totalFocusMinutes / this.pomodorosCompleted
                    : 0;
            }

            // Determine break duration
            const breakDuration = this.pomodorosCompleted % 4 === 0
                ? this.longBreakDurationMinutes
                : this.breakDurationMinutes;
            this.currentBreakDurationMinutes = breakDuration;
            this.currentPhaseDurationSeconds = breakDuration * 60;
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
                    duration_minutes: this.focusDurationMinutes,
                    pomodoros: 1,
                    completed: false,
                }).catch(console.error);
            }
        } else {
            // Break completed
            this.currentPhaseDurationSeconds = this.focusDurationMinutes * 60;
            this.timeRemaining = this.currentPhaseDurationSeconds;
            this.currentPhase = 'work';
            this.currentBreakDurationMinutes = this.breakDurationMinutes;
            this.showNotification('✅ 休息结束，准备好继续工作！', 'success');
        }

        this.updateTimerDisplay();
        this.elements.startBtn.disabled = false;
        this.elements.pauseBtn.disabled = true;
    }

    updateTimerDisplay() {
        const minutes = Math.floor(this.timeRemaining / 60);
        const seconds = this.timeRemaining % 60;
        const timeText = `${minutes.toString().padStart(2, '0')}:${seconds.toString().padStart(2, '0')}`;
        this.elements.timerDisplay.textContent = timeText;
        if (this.elements.timerRingTime) {
            this.elements.timerRingTime.textContent = timeText;
        }
        if (this.elements.timerRingPhase) {
            this.elements.timerRingPhase.textContent = this.currentPhase === 'work' ? '专注' : '休息';
        }
        if (this.elements.timerRing) {
            const progress = this.currentPhaseDurationSeconds > 0
                ? Math.max(0, Math.min(100, (this.timeRemaining / this.currentPhaseDurationSeconds) * 100))
                : 0;
            this.elements.timerRing.style.setProperty('--timer-progress', progress.toFixed(2));
        }

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

    renderFileTree(project, workspaceFiles = []) {
        const browser = this.elements.workspaceBrowser;
        browser.innerHTML = '';

        const projectPath = project?.vault_path || '';
        if (projectPath) {
            const pathInfo = document.createElement('div');
            pathInfo.className = 'workspace-path';
            pathInfo.textContent = projectPath;
            browser.appendChild(pathInfo);
        }

        const files = workspaceFiles.length > 0
            ? workspaceFiles
            : [
                { name: 'Roadmap.md', type: 'file' },
                { name: 'Task Progress.md', type: 'file' },
                { name: 'Coach Log.md', type: 'file' },
            ];
        const list = document.createElement('ul');
        list.className = 'file-tree';

        files.forEach((file) => {
            const item = document.createElement('li');
            item.className = `file-item ${file.type || 'file'}`;
            item.title = file.path || file.name;
            item.innerHTML = `
                <span class="file-icon">${file.type === 'folder' ? '📁' : '📄'}</span>
                <span class="file-label">${this.escapeHtml(file.name)}</span>
            `;
            list.appendChild(item);
        });

        browser.appendChild(list);
    }

    // ========== Analytics ==========

    async showAnalytics() {
        const modal = this.elements.analyticsModal;
        modal.classList.add('active');
        this.renderAnalyticsModal();
    }

    setAnalyticsMode(mode) {
        this.analyticsDataMode = mode;
        this.renderAnalyticsModal();
    }

    getEmptyAnalyticsData() {
        return {
            tasks: [],
            gantt_data: { tasks: [] },
            time_stats: {
                total_hours: 0,
                average_duration: 0,
                pomodoros_count: 0,
                on_time_percent: 0,
                fastest_task: '',
                slowest_task: '',
            },
        };
    }

    getDemoAnalyticsData() {
        const tasks = [
            {
                id: 'demo-1',
                title: '确定研究问题',
                status: 'completed',
                estimated_minutes: 60,
                actual_minutes: 52,
                phase: '准备',
            },
            {
                id: 'demo-2',
                title: '文献调研与笔记整理',
                status: 'completed',
                estimated_minutes: 120,
                actual_minutes: 135,
                phase: '调研',
            },
            {
                id: 'demo-3',
                title: '实验方案设计',
                status: 'in_progress',
                estimated_minutes: 90,
                actual_minutes: 65,
                phase: '方案',
            },
            {
                id: 'demo-4',
                title: '结果图表草稿',
                status: 'pending',
                estimated_minutes: 75,
                actual_minutes: 0,
                phase: '写作',
            },
        ];
        const totalMinutes = tasks.reduce((sum, task) => sum + (task.actual_minutes || 0), 0);
        const completedTasks = tasks.filter((task) => task.status === 'completed');

        return {
            tasks,
            time_stats: {
                total_hours: totalMinutes / 60,
                average_duration: totalMinutes / tasks.filter((task) => task.actual_minutes > 0).length,
                pomodoros_count: Math.round(totalMinutes / this.focusDurationMinutes),
                on_time_percent: 50,
                fastest_task: completedTasks[0]?.title || '',
                slowest_task: completedTasks[1]?.title || '',
            },
            gantt_data: {
                tasks: tasks
                    .filter((task) => task.actual_minutes > 0)
                    .map((task) => ({
                        id: task.id,
                        name: task.title,
                        duration: task.actual_minutes,
                        status: task.status,
                    })),
            },
        };
    }

    getAnalyticsData() {
        if (this.analyticsDataMode === 'demo') {
            return { mode: 'demo', data: this.getDemoAnalyticsData() };
        }
        if (this.analyticsDataMode === 'empty') {
            return { mode: 'empty', data: this.getEmptyAnalyticsData() };
        }
        if (this.currentDashboardData) {
            return { mode: 'live', data: this.currentDashboardData };
        }
        return { mode: 'demo', data: this.getDemoAnalyticsData() };
    }

    renderAnalyticsModal() {
        const { mode, data } = this.getAnalyticsData();
        const modeLabels = {
            live: '项目数据',
            demo: '模拟数据',
            empty: '已清空展示',
        };
        if (this.elements.analyticsModeLabel) {
            this.elements.analyticsModeLabel.textContent = modeLabels[mode] || '统计数据';
        }

        const stats = data.time_stats;
        const totalMinutes = Math.round((stats.total_hours || 0) * 60);

        // Update statistics table
        this.elements.statsTableBody.innerHTML = `
            <tr>
                <td>累计耗时</td>
                <td>${this.formatMinutes(totalMinutes)}</td>
            </tr>
            <tr>
                <td>平均任务耗时</td>
                <td>${Math.round(stats.average_duration || 0)} 分钟</td>
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
        this.renderGanttChart(data.gantt_data);

        // Render pie chart
        this.renderPieChart(data.tasks);
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

        const maxDuration = Math.max(...ganttData.tasks.map((task) => task.duration || 0), 1);
        const chart = document.createElement('div');
        chart.className = 'gantt-list';

        ganttData.tasks.forEach((task) => {
            const duration = task.duration || 0;
            const width = Math.max(8, Math.round((duration / maxDuration) * 100));
            const status = ['completed', 'in_progress', 'pending'].includes(task.status)
                ? task.status
                : 'pending';
            const row = document.createElement('div');
            row.className = 'gantt-row';
            row.innerHTML = `
                <div class="gantt-row-header">
                    <span>${this.escapeHtml(task.name)}</span>
                    <span>${duration} 分钟</span>
                </div>
                <div class="gantt-bar-track">
                    <div class="gantt-bar gantt-bar-${status}" style="width: ${width}%"></div>
                </div>
            `;
            chart.appendChild(row);
        });

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
        if (!canvas || typeof Chart === 'undefined') return;
        const ctx = canvas.getContext('2d');
        if (this.pieChartInstance) {
            this.pieChartInstance.destroy();
        }

        const slices = tasks
            .map((task) => ({
                label: task.title || task.name || '未命名任务',
                value: task.actual_minutes || task.duration || task.estimated_minutes || 0,
            }))
            .filter((task) => task.value > 0)
            .slice(0, 6);

        const hasData = slices.length > 0;
        const labels = hasData ? slices.map((task) => task.label) : ['暂无数据'];
        const values = hasData ? slices.map((task) => task.value) : [1];

        this.pieChartInstance = new Chart(ctx, {
            type: 'doughnut',
            data: {
                labels,
                datasets: [
                    {
                        data: values,
                        backgroundColor: hasData
                            ? ['#7dd3fc', '#a7f3d0', '#fde68a', '#c4b5fd', '#fda4af', '#93c5fd']
                            : ['#e5e7eb'],
                        borderWidth: 0,
                    },
                ],
            },
            options: {
                responsive: true,
                maintainAspectRatio: true,
                cutout: '58%',
                plugins: {
                    legend: {
                        position: 'bottom',
                    },
                },
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
