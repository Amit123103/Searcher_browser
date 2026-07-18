/* ============================================
   Searcher Browser Mobile — App Logic
   ============================================ */

(function () {
    'use strict';

    // ==========================================
    // STATE
    // ==========================================
    const state = {
        tabs: [],
        activeTabId: null,
        currentNav: 'home',
        theme: 'dark',
        bookmarks: [],
        history: [],
        scratchpad: '',
        aiOpen: false,
    };

    let tabIdCounter = 0;

    // ==========================================
    // DOM REFERENCES
    // ==========================================
    const $ = (sel) => document.querySelector(sel);
    const $$ = (sel) => document.querySelectorAll(sel);

    const dom = {};

    function cacheDom() {
        dom.app = $('#app');
        dom.addressBar = $('#address-bar');
        dom.backBtn = $('#btn-back');
        dom.forwardBtn = $('#btn-forward');
        dom.reloadBtn = $('#btn-reload');
        dom.bookmarkBtn = $('#btn-bookmark-page');
        dom.tabBar = $('#tab-bar-items');
        dom.tabAdd = $('#tab-add');
        dom.contentArea = $('#content-area');
        dom.startPage = $('#start-page');
        dom.searchBox = $('#search-box');
        dom.searchForm = $('#search-form');
        dom.webView = $('#web-view');
        dom.webIframe = $('#web-iframe');
        dom.webBlocked = $('#web-blocked');
        dom.webBlockedOpenBtn = $('#web-blocked-open');
        dom.bottomNav = $('#bottom-nav');
        dom.navItems = $$('.nav-item');
        dom.pages = $$('.page');
        dom.toast = $('#toast');
        dom.bookmarksList = $('#bookmarks-list');
        dom.historyList = $('#history-list');
        dom.scratchpadArea = $('#scratchpad-area');

        // AI
        dom.aiOverlay = $('#ai-overlay');
        dom.aiPanel = $('#ai-panel');
        dom.aiClose = $('#ai-close');
        dom.aiInput = $('#ai-input');
        dom.aiSendBtn = $('#ai-send-btn');
        dom.aiSummaryText = $('#ai-summary-text');
        dom.aiActions = $$('.ai-action-btn');

        // Settings
        dom.themeOptions = $$('.theme-option');
        dom.clearHistoryBtn = $('#clear-history');
        dom.clearBookmarksBtn = $('#clear-bookmarks');

        // Install
        dom.installBanner = $('#install-banner');
        dom.installBtn = $('#install-btn');
        dom.installDismiss = $('#install-dismiss');
    }

    // ==========================================
    // INITIALIZATION
    // ==========================================
    function init() {
        cacheDom();
        loadState();
        applyTheme(state.theme);
        renderTabs();
        renderBookmarks();
        renderHistory();
        bindEvents();
        registerServiceWorker();

        if (dom.scratchpadArea) {
            dom.scratchpadArea.value = state.scratchpad;
        }

        // Create default tab if none exist
        if (state.tabs.length === 0) {
            addTab();
        }
    }

    // ==========================================
    // PERSISTENCE (localStorage)
    // ==========================================
    function loadState() {
        try {
            const saved = localStorage.getItem('searcher_state');
            if (saved) {
                const parsed = JSON.parse(saved);
                state.theme = parsed.theme || 'dark';
                state.bookmarks = parsed.bookmarks || [];
                state.history = parsed.history || [];
                state.scratchpad = parsed.scratchpad || '';
            }
        } catch (e) {
            console.warn('Failed to load state:', e);
        }
    }

    function saveState() {
        try {
            localStorage.setItem('searcher_state', JSON.stringify({
                theme: state.theme,
                bookmarks: state.bookmarks,
                history: state.history,
                scratchpad: state.scratchpad,
            }));
        } catch (e) {
            console.warn('Failed to save state:', e);
        }
    }

    // ==========================================
    // THEME
    // ==========================================
    function applyTheme(theme) {
        state.theme = theme;
        document.documentElement.setAttribute('data-theme', theme);

        dom.themeOptions.forEach((btn) => {
            btn.classList.toggle('active', btn.dataset.theme === theme);
        });

        saveState();
    }

    // ==========================================
    // TABS
    // ==========================================
    function createTab(url, title) {
        const id = ++tabIdCounter;
        return {
            id,
            url: url || null,
            title: title || 'New Tab',
            isStartPage: !url,
            canGoBack: false,
            canGoForward: false,
            historyStack: [],
            historyIndex: -1,
        };
    }

    function addTab(url, title) {
        const tab = createTab(url, title);
        state.tabs.push(tab);
        switchTab(tab.id);
        renderTabs();
        return tab;
    }

    function closeTab(id) {
        const idx = state.tabs.findIndex((t) => t.id === id);
        if (idx === -1) return;

        state.tabs.splice(idx, 1);

        if (state.tabs.length === 0) {
            addTab();
            return;
        }

        if (state.activeTabId === id) {
            const newIdx = Math.min(idx, state.tabs.length - 1);
            switchTab(state.tabs[newIdx].id);
        }

        renderTabs();
    }

    function switchTab(id) {
        state.activeTabId = id;
        const tab = getActiveTab();
        if (!tab) return;

        renderTabs();
        updateContentForTab(tab);
        updateNavButtons(tab);
    }

    function getActiveTab() {
        return state.tabs.find((t) => t.id === state.activeTabId);
    }

    function updateContentForTab(tab) {
        if (tab.isStartPage || !tab.url) {
            showStartPage();
            dom.addressBar.value = '';
        } else {
            navigateInTab(tab.url, false);
        }
    }

    function updateNavButtons(tab) {
        if (!tab) return;
        dom.backBtn.disabled = !tab.canGoBack;
        dom.forwardBtn.disabled = !tab.canGoForward;
    }

    function renderTabs() {
        dom.tabBar.innerHTML = '';

        state.tabs.forEach((tab) => {
            const el = document.createElement('button');
            el.className = 'tab-item' + (tab.id === state.activeTabId ? ' active' : '');
            el.innerHTML = `
                <span class="tab-title">${escapeHtml(tab.title)}</span>
                <span class="tab-close" data-tab-close="${tab.id}">&times;</span>
            `;
            el.addEventListener('click', (e) => {
                if (e.target.classList.contains('tab-close')) {
                    e.stopPropagation();
                    closeTab(parseInt(e.target.dataset.tabClose));
                    return;
                }
                switchTab(tab.id);
            });
            dom.tabBar.appendChild(el);
        });
    }

    // ==========================================
    // NAVIGATION
    // ==========================================
    function navigateToUrl(input) {
        const text = input.trim();
        if (!text) return;

        let url;
        if (text.includes(' ') || !text.includes('.')) {
            // Search query
            url = 'https://www.google.com/search?q=' + encodeURIComponent(text);
        } else {
            url = text.startsWith('http://') || text.startsWith('https://')
                ? text
                : 'https://' + text;
        }

        const tab = getActiveTab();
        if (!tab) {
            const newTab = addTab(url, getDomainFromUrl(url));
            return;
        }

        tab.url = url;
        tab.title = getDomainFromUrl(url);
        tab.isStartPage = false;

        // Push to history stack
        if (tab.historyIndex < tab.historyStack.length - 1) {
            tab.historyStack = tab.historyStack.slice(0, tab.historyIndex + 1);
        }
        tab.historyStack.push(url);
        tab.historyIndex = tab.historyStack.length - 1;
        tab.canGoBack = tab.historyIndex > 0;
        tab.canGoForward = false;

        navigateInTab(url, true);
        renderTabs();

        // Add to history
        addToHistory(url, tab.title);
    }

    function navigateInTab(url, isNew) {
        dom.startPage.classList.remove('active');
        dom.startPage.style.display = 'none';
        hideAllPages();

        dom.webView.classList.add('active');
        dom.addressBar.value = url;

        // Try to load in iframe — most sites block this, so show redirect option
        dom.webIframe.style.display = 'none';
        dom.webBlocked.style.display = 'flex';
        dom.webBlockedOpenBtn.onclick = () => {
            window.open(url, '_blank');
        };

        // Store the URL for the open button
        dom.webBlocked.dataset.url = url;

        // Try iframe anyway — some sites allow it
        dom.webIframe.onload = function () {
            try {
                // Try to access iframe content — will throw if blocked
                const doc = dom.webIframe.contentDocument || dom.webIframe.contentWindow.document;
                if (doc && doc.body) {
                    dom.webIframe.style.display = 'block';
                    dom.webBlocked.style.display = 'none';
                }
            } catch (e) {
                // Cross-origin — show blocked message
                dom.webIframe.style.display = 'none';
                dom.webBlocked.style.display = 'flex';
            }
        };

        dom.webIframe.onerror = function() {
            dom.webIframe.style.display = 'none';
            dom.webBlocked.style.display = 'flex';
        };

        dom.webIframe.src = url;

        const tab = getActiveTab();
        if (tab) {
            updateNavButtons(tab);
        }
    }

    function goBack() {
        const tab = getActiveTab();
        if (!tab || tab.historyIndex <= 0) return;

        tab.historyIndex--;
        tab.url = tab.historyStack[tab.historyIndex];
        tab.canGoBack = tab.historyIndex > 0;
        tab.canGoForward = tab.historyIndex < tab.historyStack.length - 1;

        navigateInTab(tab.url, false);
        updateNavButtons(tab);
    }

    function goForward() {
        const tab = getActiveTab();
        if (!tab || tab.historyIndex >= tab.historyStack.length - 1) return;

        tab.historyIndex++;
        tab.url = tab.historyStack[tab.historyIndex];
        tab.canGoBack = tab.historyIndex > 0;
        tab.canGoForward = tab.historyIndex < tab.historyStack.length - 1;

        navigateInTab(tab.url, false);
        updateNavButtons(tab);
    }

    function reloadPage() {
        const tab = getActiveTab();
        if (!tab || tab.isStartPage) return;

        if (dom.webIframe.src) {
            dom.webIframe.src = dom.webIframe.src;
        }
    }

    function showStartPage() {
        dom.webView.classList.remove('active');
        hideAllPages();
        dom.startPage.style.display = 'flex';
        dom.startPage.classList.add('active');
        setActiveNav('home');
    }

    // ==========================================
    // BOOKMARKS
    // ==========================================
    function addBookmark(url, title) {
        if (!url || url.startsWith('file://')) return false;

        const exists = state.bookmarks.find((b) => b.url === url);
        if (exists) return false;

        state.bookmarks.unshift({
            url,
            title: title || getDomainFromUrl(url),
            addedAt: new Date().toISOString(),
        });

        saveState();
        renderBookmarks();
        return true;
    }

    function removeBookmark(url) {
        state.bookmarks = state.bookmarks.filter((b) => b.url !== url);
        saveState();
        renderBookmarks();
    }

    function isBookmarked(url) {
        return state.bookmarks.some((b) => b.url === url);
    }

    function renderBookmarks() {
        if (!dom.bookmarksList) return;

        if (state.bookmarks.length === 0) {
            dom.bookmarksList.innerHTML = `
                <div class="empty-state">
                    <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round">
                        <path d="M19 21l-7-5-7 5V5a2 2 0 0 1 2-2h10a2 2 0 0 1 2 2z"></path>
                    </svg>
                    <div class="empty-state-text">No bookmarks yet</div>
                    <div class="empty-state-sub">Tap the star icon when browsing to save pages here</div>
                </div>
            `;
            return;
        }

        dom.bookmarksList.innerHTML = state.bookmarks.map((b) => `
            <div class="list-item" data-url="${escapeAttr(b.url)}">
                <div class="list-icon">
                    <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                        <path d="M19 21l-7-5-7 5V5a2 2 0 0 1 2-2h10a2 2 0 0 1 2 2z"></path>
                    </svg>
                </div>
                <div class="list-info">
                    <div class="list-title">${escapeHtml(b.title)}</div>
                    <div class="list-url">${escapeHtml(b.url)}</div>
                </div>
                <button class="list-delete" data-delete-bookmark="${escapeAttr(b.url)}" title="Remove">
                    <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                        <line x1="18" y1="6" x2="6" y2="18"></line>
                        <line x1="6" y1="6" x2="18" y2="18"></line>
                    </svg>
                </button>
            </div>
        `).join('');

        // Bind click events
        dom.bookmarksList.querySelectorAll('.list-item').forEach((el) => {
            el.addEventListener('click', (e) => {
                if (e.target.closest('.list-delete')) {
                    e.stopPropagation();
                    removeBookmark(e.target.closest('.list-delete').dataset.deleteBookmark);
                    showToast('Bookmark removed');
                    return;
                }
                const url = el.dataset.url;
                navigateToUrl(url);
                setActiveNav('home');
            });
        });
    }

    // ==========================================
    // HISTORY
    // ==========================================
    function addToHistory(url, title) {
        if (!url || url.startsWith('file://') || url === 'about:blank') return;

        state.history.unshift({
            url,
            title: title || getDomainFromUrl(url),
            visitedAt: new Date().toISOString(),
        });

        // Keep last 200
        if (state.history.length > 200) {
            state.history = state.history.slice(0, 200);
        }

        saveState();
        renderHistory();
    }

    function clearHistory() {
        state.history = [];
        saveState();
        renderHistory();
        showToast('History cleared');
    }

    function renderHistory() {
        if (!dom.historyList) return;

        if (state.history.length === 0) {
            dom.historyList.innerHTML = `
                <div class="empty-state">
                    <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round">
                        <circle cx="12" cy="12" r="10"></circle>
                        <polyline points="12 6 12 12 16 14"></polyline>
                    </svg>
                    <div class="empty-state-text">No history yet</div>
                    <div class="empty-state-sub">Your browsing history will appear here</div>
                </div>
            `;
            return;
        }

        dom.historyList.innerHTML = state.history.map((h) => `
            <div class="list-item" data-url="${escapeAttr(h.url)}">
                <div class="list-icon">
                    <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                        <circle cx="12" cy="12" r="10"></circle>
                        <polyline points="12 6 12 12 16 14"></polyline>
                    </svg>
                </div>
                <div class="list-info">
                    <div class="list-title">${escapeHtml(h.title)}</div>
                    <div class="list-url">${escapeHtml(h.url)}</div>
                    <div class="list-time">${formatTime(h.visitedAt)}</div>
                </div>
            </div>
        `).join('');

        dom.historyList.querySelectorAll('.list-item').forEach((el) => {
            el.addEventListener('click', () => {
                navigateToUrl(el.dataset.url);
                setActiveNav('home');
            });
        });
    }

    // ==========================================
    // AI SIDEBAR
    // ==========================================
    function openAI() {
        state.aiOpen = true;
        dom.aiOverlay.classList.add('active');
        dom.aiPanel.classList.add('active');
        document.body.style.overflow = 'hidden';
    }

    function closeAI() {
        state.aiOpen = false;
        dom.aiOverlay.classList.remove('active');
        dom.aiPanel.classList.remove('active');
        document.body.style.overflow = '';
    }

    function handleAIAction(action) {
        const responses = {
            quotes: '❞ Key Quote: "The paradigm is shifting rapidly toward ambient computing, where screens fade into the background and intent drives interaction."',
            thread: '🧵 Thread:\n1/ Ambient computing is reshaping how we interact with technology.\n2/ Predictive, agentic workspaces are replacing the desktop metaphor.\n3/ Natural language is becoming the primary interface.',
            views: '🔍 Opposing View: Critics argue that always-on ambient systems raise significant privacy concerns. The trade-off between convenience and surveillance remains unresolved.',
        };

        dom.aiSummaryText.textContent = responses[action] || 'Processing...';
    }

    function handleAIQuestion(question) {
        if (!question.trim()) return;

        dom.aiSummaryText.textContent = `You asked: "${question}"\n\n🤖 AI is thinking...\n\nBased on the current context, here is a simulated response. In a production version, this would connect to an LLM API like Google Gemini for real-time intelligent answers.`;
        dom.aiInput.value = '';
    }

    // ==========================================
    // NAVIGATION (Bottom Nav)
    // ==========================================
    function setActiveNav(navId) {
        state.currentNav = navId;

        dom.navItems.forEach((item) => {
            item.classList.toggle('active', item.dataset.nav === navId);
        });

        // Show/hide pages
        hideAllPages();

        if (navId === 'home') {
            const tab = getActiveTab();
            if (tab && tab.url && !tab.isStartPage) {
                dom.webView.classList.add('active');
                dom.startPage.style.display = 'none';
            } else {
                dom.startPage.style.display = 'flex';
                dom.startPage.classList.add('active');
                dom.webView.classList.remove('active');
            }
        } else {
            dom.startPage.style.display = 'none';
            dom.webView.classList.remove('active');
            const page = $(`#page-${navId}`);
            if (page) {
                page.classList.add('active');
            }
        }
    }

    function hideAllPages() {
        dom.pages.forEach((p) => p.classList.remove('active'));
    }

    // ==========================================
    // TOAST
    // ==========================================
    let toastTimeout;
    function showToast(message) {
        dom.toast.textContent = message;
        dom.toast.classList.add('show');
        clearTimeout(toastTimeout);
        toastTimeout = setTimeout(() => {
            dom.toast.classList.remove('show');
        }, 2500);
    }

    // ==========================================
    // SERVICE WORKER & PWA
    // ==========================================
    let deferredPrompt = null;

    function registerServiceWorker() {
        if ('serviceWorker' in navigator) {
            navigator.serviceWorker.register('sw.js')
                .then((reg) => console.log('SW registered:', reg.scope))
                .catch((err) => console.warn('SW registration failed:', err));
        }

        window.addEventListener('beforeinstallprompt', (e) => {
            e.preventDefault();
            deferredPrompt = e;
            showInstallBanner();
        });
    }

    function showInstallBanner() {
        if (dom.installBanner) {
            dom.installBanner.classList.add('show');
        }
    }

    function installPWA() {
        if (!deferredPrompt) return;
        deferredPrompt.prompt();
        deferredPrompt.userChoice.then((result) => {
            if (result.outcome === 'accepted') {
                showToast('Searcher installed! 🎉');
            }
            deferredPrompt = null;
            dom.installBanner.classList.remove('show');
        });
    }

    // ==========================================
    // EVENT BINDINGS
    // ==========================================
    function bindEvents() {
        // Address bar
        dom.addressBar.addEventListener('keydown', (e) => {
            if (e.key === 'Enter') {
                e.preventDefault();
                navigateToUrl(dom.addressBar.value);
            }
        });

        // Search form (start page)
        dom.searchForm.addEventListener('submit', (e) => {
            e.preventDefault();
            navigateToUrl(dom.searchBox.value);
        });

        // Navigation buttons
        dom.backBtn.addEventListener('click', goBack);
        dom.forwardBtn.addEventListener('click', goForward);
        dom.reloadBtn.addEventListener('click', reloadPage);

        // Bookmark button
        dom.bookmarkBtn.addEventListener('click', () => {
            const tab = getActiveTab();
            if (!tab || !tab.url) {
                showToast('Navigate to a page first');
                return;
            }
            if (isBookmarked(tab.url)) {
                removeBookmark(tab.url);
                showToast('Bookmark removed');
                dom.bookmarkBtn.classList.remove('active');
            } else {
                addBookmark(tab.url, tab.title);
                showToast('Page bookmarked ⭐');
                dom.bookmarkBtn.classList.add('active');
            }
        });

        // Tab add
        dom.tabAdd.addEventListener('click', () => {
            addTab();
        });

        // Bottom navigation
        dom.navItems.forEach((item) => {
            item.addEventListener('click', () => {
                setActiveNav(item.dataset.nav);
            });
        });

        // AI sidebar
        const aiNavItem = $('[data-nav="ai"]');
        if (aiNavItem) {
            aiNavItem.addEventListener('click', (e) => {
                e.preventDefault();
                openAI();
            });
        }

        dom.aiOverlay.addEventListener('click', closeAI);
        dom.aiClose.addEventListener('click', closeAI);

        dom.aiActions.forEach((btn) => {
            btn.addEventListener('click', () => {
                handleAIAction(btn.dataset.action);
            });
        });

        dom.aiSendBtn.addEventListener('click', () => {
            handleAIQuestion(dom.aiInput.value);
        });

        dom.aiInput.addEventListener('keydown', (e) => {
            if (e.key === 'Enter') {
                e.preventDefault();
                handleAIQuestion(dom.aiInput.value);
            }
        });

        // Theme options
        dom.themeOptions.forEach((btn) => {
            btn.addEventListener('click', () => {
                applyTheme(btn.dataset.theme);
            });
        });

        // Clear buttons
        if (dom.clearHistoryBtn) {
            dom.clearHistoryBtn.addEventListener('click', clearHistory);
        }

        if (dom.clearBookmarksBtn) {
            dom.clearBookmarksBtn.addEventListener('click', () => {
                state.bookmarks = [];
                saveState();
                renderBookmarks();
                showToast('All bookmarks cleared');
            });
        }

        // Scratchpad
        if (dom.scratchpadArea) {
            dom.scratchpadArea.addEventListener('input', () => {
                state.scratchpad = dom.scratchpadArea.value;
                saveState();
            });
        }

        // Install PWA
        if (dom.installBtn) {
            dom.installBtn.addEventListener('click', installPWA);
        }

        if (dom.installDismiss) {
            dom.installDismiss.addEventListener('click', () => {
                dom.installBanner.classList.remove('show');
            });
        }

        // Top sites links
        $$('.site-link').forEach((link) => {
            link.addEventListener('click', (e) => {
                e.preventDefault();
                const url = link.getAttribute('href');
                if (url && url !== '#') {
                    navigateToUrl(url);
                }
            });
        });

        // News item clicks
        $$('.news-item').forEach((link) => {
            link.addEventListener('click', (e) => {
                e.preventDefault();
                const url = link.getAttribute('href');
                if (url && url !== '#') {
                    navigateToUrl(url);
                }
            });
        });

        // Offline detection
        window.addEventListener('online', () => showToast('You\'re back online! 🌐'));
        window.addEventListener('offline', () => showToast('You\'re offline 📡'));
    }

    // ==========================================
    // UTILITY
    // ==========================================
    function escapeHtml(str) {
        const div = document.createElement('div');
        div.textContent = str || '';
        return div.innerHTML;
    }

    function escapeAttr(str) {
        return (str || '').replace(/"/g, '&quot;').replace(/'/g, '&#39;');
    }

    function getDomainFromUrl(url) {
        try {
            const u = new URL(url);
            return u.hostname.replace('www.', '');
        } catch {
            return url.substring(0, 30);
        }
    }

    function formatTime(isoStr) {
        try {
            const d = new Date(isoStr);
            const now = new Date();
            const diff = now - d;
            const mins = Math.floor(diff / 60000);
            const hours = Math.floor(diff / 3600000);
            const days = Math.floor(diff / 86400000);

            if (mins < 1) return 'Just now';
            if (mins < 60) return `${mins}m ago`;
            if (hours < 24) return `${hours}h ago`;
            if (days < 7) return `${days}d ago`;
            return d.toLocaleDateString();
        } catch {
            return '';
        }
    }

    // ==========================================
    // BOOT
    // ==========================================
    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', init);
    } else {
        init();
    }
})();
