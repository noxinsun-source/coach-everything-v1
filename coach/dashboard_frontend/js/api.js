/**
 * API Client for Coach Everything Dashboard
 * Handles all communication with FastAPI backend
 */

class CoachAPI {
    constructor(baseURL = 'http://127.0.0.1:8000') {
        this.baseURL = baseURL;
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

            if (!response.ok) {
                throw new Error(`API Error: ${response.status} ${response.statusText}`);
            }

            // Handle empty responses
            const text = await response.text();
            return text ? JSON.parse(text) : null;
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

    // ========== WebSocket Methods ==========

    /**
     * Connect to Pomodoro WebSocket
     */
    connectPomodoroWebSocket(projectId, handlers = {}) {
        const wsUrl = `ws://127.0.0.1:8000/ws/pomodoro/${projectId}`;
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
            console.error('WebSocket error:', error);
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
