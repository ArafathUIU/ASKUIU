(function () {
    'use strict';

    // DOM Elements
    const queryForm = document.getElementById('query-form');
    const messageInput = document.getElementById('user_message');
    const messagesContainer = document.getElementById('messages-container');
    const welcomeSection = document.getElementById('welcome-section');
    const typingIndicator = document.querySelector('.typing-indicator');
    const sendButton = document.getElementById('send-button');
    const themeToggle = document.getElementById('theme-toggle');
    const themeLabel = document.getElementById('theme-label');
    const quickQuestions = document.getElementById('quick-questions');
    const newChatBtn = document.getElementById('new-chat-btn');
    const clearChatBtn = document.getElementById('clear-chat-btn');
    const chatHistoryEl = document.getElementById('chat-history');
    const sidebar = document.getElementById('sidebar');

    const sidebarOverlay = document.getElementById('sidebar-overlay');
    const sidebarToggle = document.getElementById('sidebar-toggle');
    const yearSpan = document.getElementById('year');
    const rocketLaunch = document.getElementById('rocket-launch');
    const activeEngineBadge = document.getElementById('active-engine-badge');
    const categoryChips = document.querySelectorAll('.category-chip');

    // State
    const STORAGE_KEY = 'askuiu-chats-v2';
    const ACTIVE_CHAT_KEY = 'askuiu-active-chat-v2';
    let activeChatId = null;
    let selectedCategory = '';

    if (yearSpan) {
        yearSpan.textContent = new Date().getFullYear();
    }

    // Category Filter Chips
    categoryChips.forEach(chip => {
        chip.addEventListener('click', function () {
            categoryChips.forEach(c => c.classList.remove('active'));
            this.classList.add('active');
            selectedCategory = this.dataset.category || '';
        });
    });

    // Theme
    function initTheme() {
        const saved = localStorage.getItem('askuiu-theme');
        const prefersDark = window.matchMedia('(prefers-color-scheme: dark)').matches;
        if (saved === 'light' || (!saved && !prefersDark)) {
            document.documentElement.classList.remove('dark');
            document.documentElement.classList.add('light');
            updateThemeUI(false);
        } else {
            document.documentElement.classList.add('dark');
            document.documentElement.classList.remove('light');
            updateThemeUI(true);
        }
    }

    function updateThemeUI(isDark) {
        if (!themeToggle) return;
        const icon = themeToggle.querySelector('i');
        if (icon) icon.className = isDark ? 'fas fa-sun' : 'fas fa-moon';
        if (themeLabel) themeLabel.textContent = isDark ? 'Light Mode' : 'Dark Mode';
    }

    if (themeToggle) {
        themeToggle.addEventListener('click', function () {
            const isDark = document.documentElement.classList.toggle('dark');
            document.documentElement.classList.toggle('light', !isDark);
            localStorage.setItem('askuiu-theme', isDark ? 'dark' : 'light');
            updateThemeUI(isDark);
        });
    }

    initTheme();

    // Fetch System Health & Stats
    async function fetchSystemStats() {
        try {
            const res = await fetch('/api/health');
            if (res.ok) {
                const data = await res.json();
                if (data.index_stats && data.index_stats.total_documents) {
                    const docCountEl = document.getElementById('sidebar-doc-count');
                    if (docCountEl) docCountEl.textContent = `${data.index_stats.total_documents} Docs`;
                }
                if (activeEngineBadge && data.active_provider) {
                    const providerMap = {
                        'groq': 'Groq (Qwen 27B)',
                        'gemini': 'Gemini 2.5 Flash',
                        'opencodego': 'OpenCode Go',
                        'openai': 'OpenAI Engine',
                        'extractive_fallback': 'UIU Grounded Fallback'
                    };
                    activeEngineBadge.textContent = providerMap[data.active_provider] || 'Grounded RAG';
                }
            }
        } catch (e) {
            console.warn('Could not fetch system stats:', e);
        }
    }
    fetchSystemStats();

    // Sidebar
    function openSidebar() {
        sidebar.classList.remove('-translate-x-full');
        sidebarOverlay.classList.remove('hidden');
        document.body.classList.add('overflow-hidden');
    }

    function closeSidebar() {
        sidebar.classList.add('-translate-x-full');
        sidebarOverlay.classList.add('hidden');
        document.body.classList.remove('overflow-hidden');
    }

    if (sidebarToggle) sidebarToggle.addEventListener('click', openSidebar);
    if (sidebarOverlay) sidebarOverlay.addEventListener('click', closeSidebar);

    // Chat History Management
    function loadChats() {
        const raw = localStorage.getItem(STORAGE_KEY);
        if (!raw) return [];
        try { return JSON.parse(raw); } catch { return []; }
    }

    function saveChats(chats) {
        localStorage.setItem(STORAGE_KEY, JSON.stringify(chats));
    }

    function generateId() {
        return Date.now().toString(36) + Math.random().toString(36).slice(2, 8);
    }

    function createNewChat(title) {
        const chat = {
            id: generateId(),
            title: title || 'New Mission',
            createdAt: Date.now(),
            messages: []
        };
        const chats = loadChats();
        chats.unshift(chat);
        saveChats(chats);
        activeChatId = chat.id;
        localStorage.setItem(ACTIVE_CHAT_KEY, chat.id);
        return chat;
    }

    function updateActiveChat() {
        const chats = loadChats();
        const chat = chats.find(c => c.id === activeChatId);
        if (!chat) return;

        const messageEls = messagesContainer.querySelectorAll('.message-wrapper');
        const messages = [];
        messageEls.forEach(el => {
            const textEl = el.querySelector('.message-text');
            if (!textEl) return;
            const sources = el._sources || [];
            messages.push({
                role: el.dataset.role,
                text: el._rawText || textEl.textContent,
                time: el.dataset.time,
                sources: sources
            });
        });
        chat.messages = messages;

        const firstUser = messages.find(m => m.role === 'user');
        if (firstUser) {
            chat.title = firstUser.text.slice(0, 36) + (firstUser.text.length > 36 ? '...' : '');
        }

        saveChats(chats);
        renderHistory();
    }

    function renderHistory() {
        if (!chatHistoryEl) return;
        const chats = loadChats();
        chatHistoryEl.innerHTML = '';

        if (chats.length === 0) {
            chatHistoryEl.innerHTML = `
                <div class="text-center py-6 text-xs text-gray-500">
                    No mission logs yet
                </div>
            `;
            return;
        }

        chats.forEach(chat => {
            const div = document.createElement('div');
            div.className = `history-item group flex items-center justify-between p-3 rounded-xl cursor-pointer border border-transparent hover:bg-white/5 transition ${chat.id === activeChatId ? 'active' : ''}`;
            div.dataset.id = chat.id;
            div.innerHTML = `
                <div class="flex items-center gap-2.5 overflow-hidden">
                    <i class="fas fa-satellite text-uiu-orange text-xs"></i>
                    <span class="text-sm truncate text-gray-200">${escapeHtml(chat.title)}</span>
                </div>
                <button class="delete-chat opacity-0 group-hover:opacity-100 w-7 h-7 rounded-lg hover:bg-red-900/40 text-red-400 transition flex items-center justify-center" aria-label="Delete mission">
                    <i class="fas fa-trash text-xs"></i>
                </button>
            `;
            chatHistoryEl.appendChild(div);
        });
    }

    function loadChat(chatId) {
        const chats = loadChats();
        const chat = chats.find(c => c.id === chatId);
        if (!chat) return;

        activeChatId = chat.id;
        localStorage.setItem(ACTIVE_CHAT_KEY, chat.id);

        messagesContainer.innerHTML = '';
        welcomeSection.classList.add('hidden');

        if (chat.messages.length === 0) {
            showWelcome();
        } else {
            chat.messages.forEach(msg => {
                renderMessage(msg.text, msg.role === 'user', false, msg.sources || []);
            });
        }

        renderHistory();
        scrollToBottom();
    }

    function showWelcome() {
        messagesContainer.innerHTML = '';
        messagesContainer.appendChild(welcomeSection);
        welcomeSection.classList.remove('hidden');
    }

    if (chatHistoryEl) {
        chatHistoryEl.addEventListener('click', function (e) {
            const deleteBtn = e.target.closest('.delete-chat');
            if (deleteBtn) {
                e.stopPropagation();
                const item = deleteBtn.closest('.history-item');
                const id = item.dataset.id;
                let chats = loadChats();
                chats = chats.filter(c => c.id !== id);
                saveChats(chats);
                if (activeChatId === id) {
                    activeChatId = chats.length > 0 ? chats[0].id : null;
                    localStorage.setItem(ACTIVE_CHAT_KEY, activeChatId || '');
                    if (activeChatId) {
                        loadChat(activeChatId);
                    } else {
                        showWelcome();
                        renderHistory();
                    }
                } else {
                    renderHistory();
                }
                return;
            }

            const item = e.target.closest('.history-item');
            if (item) {
                loadChat(item.dataset.id);
                if (window.innerWidth < 1024) closeSidebar();
            }
        });
    }

    if (newChatBtn) {
        newChatBtn.addEventListener('click', function () {
            createNewChat('New Mission');
            showWelcome();
            renderHistory();
            if (window.innerWidth < 1024) closeSidebar();
            messageInput.focus();
        });
    }

    if (clearChatBtn) {
        clearChatBtn.addEventListener('click', function () {
            if (activeChatId) {
                let chats = loadChats();
                chats = chats.filter(c => c.id !== activeChatId);
                saveChats(chats);
                activeChatId = null;
                localStorage.removeItem(ACTIVE_CHAT_KEY);
            }
            showWelcome();
            renderHistory();
            messageInput.value = '';
            messageInput.focus();
        });
    }

    // Quick Question click handlers
    document.querySelectorAll('.quick-question').forEach(btn => {
        btn.addEventListener('click', function () {
            const query = this.querySelector('p.font-bold')?.textContent?.trim();
            if (query) {
                messageInput.value = query;
                sendMessage();
            }
        });
    });

    // Markdown & Link Helpers
    function escapeHtml(text) {
        const div = document.createElement('div');
        div.textContent = text || '';
        return div.innerHTML;
    }

    function formatMarkdown(text) {
        if (!text) return '';
        let html = escapeHtml(text);

        // Bold **text**
        html = html.replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>');

        // Inline citations [1], [2]
        html = html.replace(/\[(\d+)\]/g, '<a href="#source-$1" class="inline-citation">[$1]</a>');

        // External URLs
        const urlRegex = /(https?:\/\/[^\s<]+)/g;
        html = html.replace(urlRegex, function (url) {
            return `<a href="${url}" target="_blank" rel="noopener noreferrer" class="text-uiu-orange hover:text-mars-sand underline">${url}</a>`;
        });

        // Bullet lists
        const lines = html.split('\n');
        let inList = false;
        let formattedLines = [];

        for (let line of lines) {
            const trimmed = line.trim();
            if (trimmed.startsWith('- ') || trimmed.startsWith('* ')) {
                if (!inList) {
                    formattedLines.push('<ul>');
                    inList = true;
                }
                formattedLines.push(`<li>${trimmed.substring(2)}</li>`);
            } else {
                if (inList) {
                    formattedLines.push('</ul>');
                    inList = false;
                }
                if (trimmed) {
                    formattedLines.push(`<p>${line}</p>`);
                }
            }
        }
        if (inList) formattedLines.push('</ul>');

        return formattedLines.join('');
    }

    function formatTime(date) {
        let hours = date.getHours();
        const minutes = date.getMinutes().toString().padStart(2, '0');
        const ampm = hours >= 12 ? 'PM' : 'AM';
        hours = hours % 12 || 12;
        return `${hours}:${minutes} ${ampm}`;
    }

    // Message Rendering
    function renderMessage(text, isUser, animate = true, sources = []) {
        welcomeSection.classList.add('hidden');
        const time = formatTime(new Date());

        const wrapper = document.createElement('div');
        wrapper.className = `message-wrapper flex ${isUser ? 'justify-end' : 'justify-start'} ${animate ? 'message-entry' : ''}`;
        wrapper.dataset.role = isUser ? 'user' : 'bot';
        wrapper.dataset.time = time;
        wrapper._rawText = text;
        wrapper._sources = sources;

        if (isUser) {
            wrapper.innerHTML = `
                <div class="flex items-end max-w-[85%] md:max-w-lg lg:max-w-xl gap-2">
                    <div class="message-bubble-user px-5 py-3.5 rounded-2xl">
                        <div class="message-text text-sm leading-relaxed text-white">${escapeHtml(text)}</div>
                        <p class="text-[10px] text-white/80 mt-1.5 text-right">${time}</p>
                    </div>
                    <div class="w-8 h-8 rounded-full bg-mars-slate border border-uiu-orange/30 flex items-center justify-center flex-shrink-0">
                        <i class="fas fa-user-astronaut text-uiu-orange text-xs"></i>
                    </div>
                </div>
            `;
        } else {
            const formattedContent = formatMarkdown(text);
            const sourcesHtml = buildSourcesAccordionHtml(sources);

            wrapper.innerHTML = `
                <div class="flex items-start max-w-[92%] md:max-w-xl lg:max-w-2xl gap-3">
                    <div class="w-9 h-9 rounded-full bg-gradient-to-br from-uiu-orange to-mars-rust text-white flex items-center justify-center flex-shrink-0 shadow-lg shadow-uiu-orange/20 mt-1">
                        <i class="fas fa-robot text-xs"></i>
                    </div>
                    <div class="flex-1 message-bubble-bot px-5 py-4 rounded-2xl text-gray-100">
                        <div class="flex items-center justify-between border-b border-white/5 pb-2 mb-2">
                            <span class="text-[11px] font-bold tracking-wider text-uiu-orange uppercase flex items-center gap-1.5">
                                <i class="fas fa-shield-halved text-[10px]"></i> UIU Verified Intelligence
                            </span>
                            <button class="copy-btn text-gray-400 hover:text-white text-xs px-2 py-1 rounded transition flex items-center gap-1" title="Copy answer">
                                <i class="fas fa-copy"></i>
                            </button>
                        </div>
                        <div class="message-text text-sm leading-relaxed">${formattedContent}</div>
                        ${sourcesHtml}
                        <p class="text-[10px] text-gray-500 mt-2 text-right">${time}</p>
                    </div>
                </div>
            `;

            setupMessageInteractions(wrapper, text);
        }

        messagesContainer.appendChild(wrapper);
        scrollToBottom();
        return wrapper;
    }

    function buildSourcesAccordionHtml(sources) {
        if (!sources || sources.length === 0) return '';

        let itemsHtml = sources.map((src, idx) => {
            const num = idx + 1;
            const title = escapeHtml(src.title || 'Official Document');
            const sourceUrl = src.source || 'https://www.uiu.ac.bd/';
            const category = escapeHtml(src.category || 'general').toUpperCase();
            const confidence = src.confidence ? Math.round(src.confidence * 100) : 85;
            const excerpt = escapeHtml(src.text ? src.text.slice(0, 240) + '...' : '');

            return `
                <div class="source-card" id="source-${num}">
                    <div class="source-header" onclick="this.parentElement.classList.toggle('expanded');">
                        <div class="flex items-center gap-2 overflow-hidden mr-2">
                            <span class="w-5 h-5 rounded bg-uiu-orange/20 text-uiu-orange text-[10px] font-bold flex items-center justify-center flex-shrink-0">[${num}]</span>
                            <span class="font-medium text-xs text-gray-200 truncate">${title}</span>
                        </div>
                        <div class="flex items-center gap-1.5 flex-shrink-0">
                            <span class="text-[9px] px-1.5 py-0.5 rounded bg-white/5 text-gray-400 font-semibold uppercase">${category}</span>
                            <span class="text-[9px] px-1.5 py-0.5 rounded bg-emerald-950/60 text-emerald-400 border border-emerald-800/40">${confidence}%</span>
                            <a href="${sourceUrl}" target="_blank" rel="noopener" class="p-1 text-gray-400 hover:text-uiu-orange transition" title="Open verified UIU link" onclick="event.stopPropagation();">
                                <i class="fas fa-external-link-alt text-[10px]"></i>
                            </a>
                        </div>
                    </div>
                    <div class="source-body hidden">
                        <p class="mb-1">${excerpt}</p>
                        <a href="${sourceUrl}" target="_blank" rel="noopener" class="text-uiu-orange hover:underline text-[10px] flex items-center gap-1">
                            Visit official source <i class="fas fa-arrow-right text-[8px]"></i>
                        </a>
                    </div>
                </div>
            `;
        }).join('');

        return `
            <div class="mt-4 pt-3 border-t border-white/10">
                <p class="text-[10px] font-bold text-mars-sand uppercase tracking-wider mb-2 flex items-center gap-1">
                    <i class="fas fa-book-bookmark text-uiu-orange"></i> Grounded Sources (${sources.length})
                </p>
                <div class="space-y-1.5">
                    ${itemsHtml}
                </div>
            </div>
        `;
    }

    function setupMessageInteractions(wrapper, text) {
        // Toggle source accordion bodies
        const headers = wrapper.querySelectorAll('.source-header');
        headers.forEach(header => {
            header.addEventListener('click', function () {
                const card = this.closest('.source-card');
                const body = card.querySelector('.source-body');
                if (body) {
                    body.classList.toggle('hidden');
                }
            });
        });

        // Copy button
        const copyBtn = wrapper.querySelector('.copy-btn');
        if (copyBtn) {
            copyBtn.addEventListener('click', function () {
                navigator.clipboard.writeText(text).then(() => {
                    const origHtml = copyBtn.innerHTML;
                    copyBtn.innerHTML = '<i class="fas fa-check text-emerald-400"></i>';
                    setTimeout(() => copyBtn.innerHTML = origHtml, 2000);
                });
            });
        }
    }

    function scrollToBottom() {
        messagesContainer.scrollTo({
            top: messagesContainer.scrollHeight,
            behavior: 'smooth'
        });
    }

    // Quick Questions
    if (quickQuestions) {
        quickQuestions.addEventListener('click', function (e) {
            const btn = e.target.closest('.quick-question');
            if (btn) {
                const p = btn.querySelector('p.font-bold');
                messageInput.value = p ? p.textContent.trim() : btn.textContent.trim();
                sendMessage();
            }
        });
    }

    // Rocket Launch Animation
    function launchRocket() {
        if (!rocketLaunch) return;
        rocketLaunch.classList.remove('launching');
        void rocketLaunch.offsetWidth;
        rocketLaunch.classList.add('launching');
        setTimeout(() => {
            rocketLaunch.classList.remove('launching');
        }, 1200);
    }

    // Stream / Send Message
    async function sendMessage() {
        const message = messageInput.value.trim();
        if (!message) return;

        launchRocket();

        if (!activeChatId) {
            createNewChat(message);
            renderHistory();
        }

        renderMessage(message, true);
        messageInput.value = '';
        sendButton.disabled = true;

        typingIndicator.classList.remove('hidden');
        scrollToBottom();

        // Create empty bot bubble for streaming
        const time = formatTime(new Date());
        const botWrapper = document.createElement('div');
        botWrapper.className = 'message-wrapper flex justify-start message-entry';
        botWrapper.dataset.role = 'bot';
        botWrapper.dataset.time = time;

        botWrapper.innerHTML = `
            <div class="flex items-start max-w-[92%] md:max-w-xl lg:max-w-2xl gap-3">
                <div class="w-9 h-9 rounded-full bg-gradient-to-br from-uiu-orange to-mars-rust text-white flex items-center justify-center flex-shrink-0 shadow-lg shadow-uiu-orange/20 mt-1">
                    <i class="fas fa-robot text-xs"></i>
                </div>
                <div class="flex-1 message-bubble-bot px-5 py-4 rounded-2xl text-gray-100">
                    <div class="flex items-center justify-between border-b border-white/5 pb-2 mb-2">
                        <span class="text-[11px] font-bold tracking-wider text-uiu-orange uppercase flex items-center gap-1.5">
                            <i class="fas fa-shield-halved text-[10px]"></i> UIU Verified Intelligence
                        </span>
                        <button class="copy-btn text-gray-400 hover:text-white text-xs px-2 py-1 rounded transition flex items-center gap-1" title="Copy answer">
                            <i class="fas fa-copy"></i>
                        </button>
                    </div>
                    <div class="message-text text-sm leading-relaxed streaming-cursor"></div>
                    <div class="sources-slot"></div>
                    <p class="text-[10px] text-gray-500 mt-2 text-right">${time}</p>
                </div>
            </div>
        `;
        messagesContainer.appendChild(botWrapper);
        scrollToBottom();

        const textEl = botWrapper.querySelector('.message-text');
        const sourcesSlot = botWrapper.querySelector('.sources-slot');
        let accumulatedText = '';
        let retrievedSources = [];

        try {
            // Attempt SSE Streaming
            const streamUrl = `/api/stream?query=${encodeURIComponent(message)}` +
                (selectedCategory ? `&category=${encodeURIComponent(selectedCategory)}` : '');

            const response = await fetch(streamUrl);

            if (response.ok && response.headers.get('content-type')?.includes('text/event-stream')) {
                typingIndicator.classList.add('hidden');
                const reader = response.body.getReader();
                const decoder = new TextDecoder();
                let buffer = '';

                while (true) {
                    const { done, value } = await reader.read();
                    if (done) break;

                    buffer += decoder.decode(value, { stream: true });
                    const lines = buffer.split('\n\n');
                    buffer = lines.pop(); // Keep incomplete chunk

                    for (const block of lines) {
                        for (const line of block.split('\n')) {
                            if (line.startsWith('data: ')) {
                                try {
                                    const data = JSON.parse(line.slice(6));
                                    if (data.type === 'sources') {
                                        retrievedSources = data.sources || [];
                                    } else if (data.type === 'token') {
                                        accumulatedText += data.content;
                                        textEl.innerHTML = formatMarkdown(accumulatedText);
                                        scrollToBottom();
                                    } else if (data.type === 'error') {
                                        accumulatedText += `\n\n*(Error: ${data.message})*`;
                                    }
                                } catch (err) {
                                    // ignore JSON parse artifact
                                }
                            }
                        }
                    }
                }
            } else {
                // Fallback to non-streaming POST
                const fallbackRes = await fetch('/', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ user_message: message, category: selectedCategory })
                });
                const resData = await fallbackRes.json();
                accumulatedText = resData.response || 'No response generated.';
                retrievedSources = resData.sources || [];
            }
        } catch (err) {
            console.error('Query error:', err);
            accumulatedText = 'Sorry, there was a connection error contacting mission control. Please try again.';
        } finally {
            typingIndicator.classList.add('hidden');
            sendButton.disabled = false;
            textEl.classList.remove('streaming-cursor');
            textEl.innerHTML = formatMarkdown(accumulatedText);

            botWrapper._rawText = accumulatedText;
            botWrapper._sources = retrievedSources;

            if (retrievedSources.length > 0) {
                sourcesSlot.innerHTML = buildSourcesAccordionHtml(retrievedSources);
            }
            setupMessageInteractions(botWrapper, accumulatedText);
            updateActiveChat();
            scrollToBottom();
        }
    }

    queryForm.addEventListener('submit', function (event) {
        event.preventDefault();
        sendMessage();
    });

    messageInput.addEventListener('keydown', function (e) {
        if (e.key === 'Enter' && !e.shiftKey) {
            e.preventDefault();
            sendMessage();
        }
    });

    // Initialize
    function init() {
        renderHistory();
        showWelcome();
        activeChatId = null;
        localStorage.removeItem(ACTIVE_CHAT_KEY);
        messageInput.focus();
    }

    init();
})();
