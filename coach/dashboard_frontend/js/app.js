/**
 * Coach Everything Dashboard - Main Application Entry Point
 */

// Application initialization
document.addEventListener('DOMContentLoaded', () => {
    console.log('Coach Everything Dashboard Loading...');

    // Add CSS animations to document
    addAnimationStyles();

    // Initialize the dashboard
    initializeDashboard();
});

/**
 * Add animation styles to document
 */
function addAnimationStyles() {
    const style = document.createElement('style');
    style.textContent = `
        @keyframes slideInRight {
            from {
                opacity: 0;
                transform: translateX(100%);
            }
            to {
                opacity: 1;
                transform: translateX(0);
            }
        }

        @keyframes slideOutRight {
            from {
                opacity: 1;
                transform: translateX(0);
            }
            to {
                opacity: 0;
                transform: translateX(100%);
            }
        }

        @keyframes fadeIn {
            from {
                opacity: 0;
            }
            to {
                opacity: 1;
            }
        }

        @keyframes spin {
            to {
                transform: rotate(360deg);
            }
        }

        @keyframes pulse {
            0%, 100% {
                opacity: 1;
            }
            50% {
                opacity: 0.5;
            }
        }
    `;
    document.head.appendChild(style);
}

/**
 * Initialize the dashboard application
 */
function initializeDashboard() {
    try {
        // Check API connectivity
        checkAPIConnection();

        // Set up keyboard shortcuts
        setupKeyboardShortcuts();

        // Set initial theme based on system preference
        applySystemTheme();

        console.log('Dashboard initialized successfully');
    } catch (error) {
        console.error('Dashboard initialization failed:', error);
        showErrorScreen(error);
    }
}

/**
 * Check if the API backend is accessible
 */
async function checkAPIConnection() {
    try {
        const response = await fetch('/api/projects');
        if (response.ok) {
            console.log('✅ API backend connected');
        } else {
            throw new Error(`API returned ${response.status}`);
        }
    } catch (error) {
        console.warn('⚠️ API backend not accessible:', error);
        showAPIWarning();
    }
}

/**
 * Show warning if API is not accessible
 */
function showAPIWarning() {
    const warning = document.createElement('div');
    warning.style.cssText = `
        position: fixed;
        top: 0;
        left: 0;
        right: 0;
        background-color: #f59e0b;
        color: #78350f;
        padding: 12px 24px;
        z-index: 10000;
        display: flex;
        justify-content: space-between;
        align-items: center;
    `;
    warning.innerHTML = `
        <span>⚠️ API backend not accessible. Make sure the backend is running</span>
        <button style="background: none; border: none; cursor: pointer; font-size: 1.2rem; color: #78350f;">×</button>
    `;

    const closeBtn = warning.querySelector('button');
    closeBtn.addEventListener('click', () => warning.remove());

    document.body.appendChild(warning);
}

/**
 * Set up keyboard shortcuts
 */
function setupKeyboardShortcuts() {
    document.addEventListener('keydown', (e) => {
        // Ctrl/Cmd + S: Open settings
        if ((e.ctrlKey || e.metaKey) && e.key === 's') {
            e.preventDefault();
            ui.showSettings();
        }

        // Ctrl/Cmd + Shift + A: Show analytics
        if ((e.ctrlKey || e.metaKey) && e.shiftKey && e.key === 'a') {
            e.preventDefault();
            ui.showAnalytics();
        }

        // Escape: Close modals
        if (e.key === 'Escape') {
            ui.closeSettings();
            ui.closeAnalytics();
            document.querySelectorAll('.left-panel.expanded, .right-panel.expanded').forEach((el) => {
                el.classList.remove('expanded');
            });
        }
    });
}

/**
 * Apply system theme preference
 */
function applySystemTheme() {
    if (window.matchMedia && window.matchMedia('(prefers-color-scheme: dark)').matches) {
        document.body.classList.add('dark-mode');
    }

    // Listen for theme changes
    window.matchMedia('(prefers-color-scheme: dark)').addEventListener('change', (e) => {
        if (e.matches) {
            document.body.classList.add('dark-mode');
        } else {
            document.body.classList.remove('dark-mode');
        }
    });
}

/**
 * Show error screen if dashboard fails to initialize
 */
function showErrorScreen(error) {
    document.body.innerHTML = `
        <div style="
            display: flex;
            flex-direction: column;
            justify-content: center;
            align-items: center;
            height: 100vh;
            background-color: #fee2e2;
            color: #991b1b;
            font-family: system-ui, -apple-system, sans-serif;
        ">
            <h1 style="font-size: 2rem; margin-bottom: 1rem;">❌ Dashboard 初始化失败</h1>
            <p style="font-size: 1rem; margin-bottom: 1rem;">
                请确保 FastAPI 后端服务正在运行：<br>
                <code style="background: rgba(0,0,0,0.1); padding: 8px 16px; border-radius: 4px;">
                    python coach/dashboard_backend.py
                </code>
            </p>
            <p style="color: #b91c1c; font-size: 0.9rem;">错误详情：${error.message}</p>
        </div>
    `;
}

/**
 * Service Worker registration (for potential offline support in future)
 */
if ('serviceWorker' in navigator) {
    navigator.serviceWorker
        .register('./sw.js')
        .then(() => {
            console.log('Service Worker registered');
        })
        .catch((error) => {
            console.log('Service Worker registration failed:', error);
        });
}

// Export utilities for use in console if needed
window.CoachApp = {
    api,
    ui,
    checkAPIConnection,
    applySystemTheme,
};
