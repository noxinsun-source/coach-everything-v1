/**
 * API Client for Coach Everything Dashboard
 * Handles all communication with FastAPI backend
 */

class CoachAPI {
    constructor(baseURL = '') {
        const browserOrigin = typeof window !== 'undefined' ? window.location.origin : '';
        const browserProtocol = typeof window !== 'undefined' ? window.location.protocol : '';
        this.baseURL = baseURL || (
            browserProtocol === 'file:' || !browserOrigin || browserOrigin === 'null'
                ? 'http://127.0.0.1:8001'
                : browserOrigin
        );
        this.defaultHeaders = {
            'Content-Type': 'application/json',
        };
    }

    /**
     * Generic fetch wrapper
     */
    async request(endpoint, options = {}) {
        const url = `${this.baseURL}${endpoint}`;
        const config = {
            ...options,
            headers: {
                ...this.defaultHeaders,
                ...options.headers,
            },
        };

        try {
            const response = await fetch(url, config);

            const text = await response.text();
            let data = null;
            if (text) {
                try {
                    data = JSON.parse(text);
                } catch {
                    data = { detail: text };
                }
            }

            if (!response.ok) {
                const detail = data?.detail || data?.message || response.statusText;
                throw new Error(`API Error: ${response.status} ${detail}`);
            }

            return data;
        } catch (error) {
            console.error(`Request failed for ${endpoint}:`, error);
            throw error;
        }
    }

    // ========== Project Endpoints ==========

    /**
     * Get all projects
     */
    async getProjects() {
        return this.request('/api/projects');
    }

    /**
     * Create a new project
     */
    async createProject(projectData) {
        return this.request('/api/projects', {
            method: 'POST',
            body: JSON.stringify(projectData),
        });
    }

    /**
     * Get complete dashboard data for a project
     */
    async getProjectDashboard(projectId) {
        return this.request(`/api/projects/${projectId}/dashboard`);
    }

    async updateProjectWorkspace(projectId, workspaceData) {
        return this.request(`/api/projects/${projectId}/workspace`, {
            method: 'PATCH',
            body: JSON.stringify(workspaceData),
        });
    }

    async createWorkspaceFolder(projectId, folderData) {
        return this.request(`/api/projects/${projectId}/workspace/folders`, {
            method: 'POST',
            body: JSON.stringify(folderData),
        });
    }

    async saveProjectChatMessage(projectId, messageData) {
        return this.request(`/api/projects/${projectId}/chat-messages`, {
            method: 'POST',
            body: JSON.stringify(messageData),
        });
    }

    // ========== Task Endpoints ==========

    /**
     * Create a new task for a project
     */
    async createTask(projectId, taskData) {
        return this.request(`/api/projects/${projectId}/tasks`, {
            method: 'POST',
            body: JSON.stringify(taskData),
        });
    }

    /**
     * Update task status
     */
    async updateTask(taskId, updates) {
        return this.request(`/api/tasks/${taskId}`, {
            method: 'PATCH',
            body: JSON.stringify(updates),
        });
    }

    // ========== Time Tracking Endpoints ==========

    /**
     * Log time for a task
     */
    async logTime(timeLogData) {
        return this.request('/api/time-logs', {
            method: 'POST',
            body: JSON.stringify(timeLogData),
        });
    }

    /**
     * Get time logs for a project
     */
    async getTimeLogs(projectId) {
        return this.request(`/api/projects/${projectId}/time-logs`);
    }

    // ========== Settings Endpoints ==========

    /**
     * Get user settings
     */
    async getSettings() {
        return this.request('/api/settings');
    }

    /**
     * Update user settings
     */
    async updateSettings(settingsData) {
        return this.request('/api/settings', {
            method: 'POST',
            body: JSON.stringify(settingsData),
        });
    }

    async chat(chatData) {
        return this.request('/api/chat', {
            method: 'POST',
            body: JSON.stringify(chatData),
        });
    }

    async syncChatTasks(syncData) {
        return this.request('/api/chat/sync-tasks', {
            method: 'POST',
            body: JSON.stringify(syncData),
        });
    }

    async chatStream(chatData, handlers = {}) {
        const response = await fetch(`${this.baseURL}/api/chat/stream`, {
            method: 'POST',
            headers: this.defaultHeaders,
            body: JSON.stringify(chatData),
        });

        if (!response.ok) {
            const text = await response.text();
            let detail = text;
            try {
                detail = JSON.parse(text)?.detail || detail;
            } catch {
                // Keep raw text.
            }
            throw new Error(`API Error: ${response.status} ${detail}`);
        }

        if (!response.body) {
            throw new Error('Streaming is not supported by this browser');
        }

        const reader = response.body.getReader();
        const decoder = new TextDecoder();
        let buffer = '';

        const dispatch = (rawEvent) => {
            const lines = rawEvent.split('\n');
            let eventName = 'message';
            const dataLines = [];

            lines.forEach((line) => {
                if (line.startsWith('event:')) {
                    eventName = line.slice(6).trim();
                } else if (line.startsWith('data:')) {
                    dataLines.push(line.slice(5).trimStart());
                }
            });

            if (dataLines.length === 0) return;

            let data = dataLines.join('\n');
            try {
                data = JSON.parse(data);
            } catch {
                data = { message: data };
            }

            if (handlers[eventName]) {
                handlers[eventName](data);
            }
            if (handlers.event) {
                handlers.event(eventName, data);
            }
        };

        while (true) {
            const { done, value } = await reader.read();
            if (done) break;

            buffer += decoder.decode(value, { stream: true });
            let boundary = buffer.indexOf('\n\n');
            while (boundary >= 0) {
                const rawEvent = buffer.slice(0, boundary).trim();
                buffer = buffer.slice(boundary + 2);
                if (rawEvent) dispatch(rawEvent);
                boundary = buffer.indexOf('\n\n');
            }
        }

        const trailing = buffer.trim();
        if (trailing) dispatch(trailing);
    }

    // ========== WebSocket Methods ==========

    /**
     * Connect to Pomodoro WebSocket
     */
    connectPomodoroWebSocket(projectId, handlers = {}) {
        const base = new URL(this.baseURL || 'http://127.0.0.1:8001');
        const browserProtocol = typeof window !== 'undefined' ? window.location.protocol : base.protocol;
        const proto = (browserProtocol === 'https:' || base.protocol === 'https:') ? 'wss' : 'ws';
        const host = (typeof window !== 'undefined' && window.location.host) || base.host || '127.0.0.1:8001';
        const wsUrl = `${proto}://${host}/ws/pomodoro/${projectId}`;
        const ws = new WebSocket(wsUrl);

        ws.onopen = () => {
            console.log('Pomodoro WebSocket connected');
            if (handlers.onOpen) handlers.onOpen();
        };

        ws.onmessage = (event) => {
            try {
                const data = JSON.parse(event.data);
                if (handlers.onMessage) handlers.onMessage(data);
            } catch (error) {
                console.error('Failed to parse WebSocket message:', error);
            }
        };

        ws.onerror = (error) => {
            console.debug('Pomodoro WebSocket error:', error);
            if (handlers.onError) handlers.onError(error);
        };

        ws.onclose = () => {
            console.log('Pomodoro WebSocket disconnected');
            if (handlers.onClose) handlers.onClose();
        };

        return ws;
    }

    /**
     * Send Pomodoro event through WebSocket
     */
    sendPomodoroEvent(ws, event) {
        if (ws && ws.readyState === WebSocket.OPEN) {
            ws.send(JSON.stringify(event));
        }
    }
}

// Create global API instance
const api = new CoachAPI();
