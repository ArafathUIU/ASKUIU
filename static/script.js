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
    const chatHistoryEl = document.getElementById('chat-history');
    const sidebar = document.getElementById('sidebar');
    const sidebarOverlay = document.getElementById('sidebar-overlay');
    const sidebarToggle = document.getElementById('sidebar-toggle');
    const yearSpan = document.getElementById('year');

    // State
    const STORAGE_KEY = 'askuiu-chats';
    const ACTIVE_CHAT_KEY = 'askuiu-active-chat';
    let activeChatId = null;

    if (yearSpan) {
        yearSpan.textContent = new Date().getFullYear();
    }

    // ========== Theme ==========
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
        const icon = themeToggle.querySelector('i');
        icon.className = isDark ? 'fas fa-sun' : 'fas fa-moon';
        themeLabel.textContent = isDark ? 'Light Mode' : 'Dark Mode';
    }

    themeToggle.addEventListener('click', function () {
        const isDark = document.documentElement.classList.toggle('dark');
        document.documentElement.classList.toggle('light', !isDark);
        localStorage.setItem('askuiu-theme', isDark ? 'dark' : 'light');
        updateThemeUI(isDark);
    });

    initTheme();

    // ========== Sidebar ==========
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

    sidebarToggle.addEventListener('click', openSidebar);
    sidebarOverlay.addEventListener('click', closeSidebar);

    chatHistoryEl.addEventListener('click', function (e) {
        const item = e.target.closest('.history-item');
        if (item && window.innerWidth < 1024) {
            closeSidebar();
        }
    });

    // ========== Chat History ==========
    function loadChats() {
        const raw = localStorage.getItem(STORAGE_KEY);
        if (!raw) return [];
        try {
            return JSON.parse(raw);
        } catch {
            return [];
        }
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
            const text = el.querySelector('.message-text');
            if (!text) return;
            messages.push({
                role: el.dataset.role,
                text: text.textContent,
                time: el.dataset.time
            });
        });
        chat.messages = messages;

        const firstUser = messages.find(m => m.role === 'user');
        if (firstUser) {
            chat.title = firstUser.text.slice(0, 40) + (firstUser.text.length > 40 ? '...' : '');
        }

        saveChats(chats);
        renderHistory();
    }

    function renderHistory() {
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
                <div class="flex items-center gap-3 overflow-hidden">
                    <i class="fas fa-satellite text-uiu-orange text-xs"></i>
                    <span class="text-sm truncate text-gray-200">${escapeHtml(chat.title)}</span>
                </div>
                <button class="delete-chat opacity-0 group-hover:opacity-100 w-7 h-7 rounded-lg hover:bg-red-900/30 text-red-400 transition flex items-center justify-center" aria-label="Delete chat">
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
                renderMessage(msg.text, msg.role === 'user', false);
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
        }
    });

    newChatBtn.addEventListener('click', function () {
        createNewChat('New Mission');
        showWelcome();
        renderHistory();
        if (window.innerWidth < 1024) closeSidebar();
        messageInput.focus();
    });

    // ========== Messages ==========
    function escapeHtml(text) {
        const div = document.createElement('div');
        div.textContent = text;
        return div.innerHTML;
    }

    function linkify(text) {
        const urlRegex = /(https?:\/\/[^\s]+)/g;
        return escapeHtml(text).replace(urlRegex, function (url) {
            return `<a href="${url}" target="_blank" rel="noopener noreferrer" class="text-uiu-orange hover:text-mars-sand underline">${url}</a>`;
        });
    }

    function formatTime(date) {
        let hours = date.getHours();
        const minutes = date.getMinutes().toString().padStart(2, '0');
        const ampm = hours >= 12 ? 'PM' : 'AM';
        hours = hours % 12;
        hours = hours ? hours : 12;
        return `${hours}:${minutes} ${ampm}`;
    }

    function renderMessage(text, isUser, animate = true) {
        welcomeSection.classList.add('hidden');
        const time = formatTime(new Date());
        const isDark = document.documentElement.classList.contains('dark');
        const textColor = isUser ? 'text-white' : (isDark ? 'text-gray-100' : 'text-gray-800');
        const metaColor = isUser ? 'text-white/80' : 'text-gray-500';

        const wrapper = document.createElement('div');
        wrapper.className = `message-wrapper flex ${isUser ? 'justify-end' : 'justify-start'} ${animate ? 'message-entry' : ''}`;
        wrapper.dataset.role = isUser ? 'user' : 'bot';
        wrapper.dataset.time = time;

        if (isUser) {
            wrapper.innerHTML = `
                <div class="flex items-end max-w-[85%] md:max-w-lg lg:max-w-xl gap-2">
                    <div class="message-bubble-user px-5 py-3.5 rounded-2xl">
                        <div class="message-text text-sm leading-relaxed ${textColor}">${escapeHtml(text)}</div>
                        <p class="text-[10px] ${metaColor} mt-1.5 text-right">${time}</p>
                    </div>
                    <div class="w-8 h-8 rounded-full bg-mars-slate border border-uiu-orange/30 flex items-center justify-center flex-shrink-0">
                        <i class="fas fa-user-astronaut text-uiu-orange text-xs"></i>
                    </div>
                </div>
            `;
        } else {
            wrapper.innerHTML = `
                <div class="flex items-end max-w-[85%] md:max-w-lg lg:max-w-xl gap-2">
                    <div class="w-9 h-9 rounded-full bg-gradient-to-br from-uiu-orange to-mars-rust text-white flex items-center justify-center flex-shrink-0 shadow-lg shadow-uiu-orange/20">
                        <i class="fas fa-robot text-xs"></i>
                    </div>
                    <div class="message-bubble-bot px-5 py-3.5 rounded-2xl ${textColor}">
                        <div class="message-text text-sm leading-relaxed">${linkify(text)}</div>
                        <p class="text-[10px] ${metaColor} mt-1.5">${time}</p>
                    </div>
                </div>
            `;
        }

        messagesContainer.appendChild(wrapper);
        scrollToBottom();
    }

    function scrollToBottom() {
        messagesContainer.scrollTo({
            top: messagesContainer.scrollHeight,
            behavior: 'smooth'
        });
    }

    // ========== Quick Questions ==========
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

    // ========== Send Message ==========
    async function sendMessage() {
        const message = messageInput.value.trim();
        if (!message) return;

        if (!activeChatId) {
            createNewChat(message);
            renderHistory();
        }

        renderMessage(message, true);
        messageInput.value = '';
        sendButton.disabled = true;

        typingIndicator.classList.remove('hidden');
        scrollToBottom();

        try {
            const response = await fetch('/', {
                method: 'POST',
                headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
                body: new URLSearchParams({ 'user_message': message })
            });

            const data = await response.json();
            typingIndicator.classList.add('hidden');
            sendButton.disabled = false;

            renderMessage(data.response || 'No response received.', false);
            updateActiveChat();
        } catch (error) {
            typingIndicator.classList.add('hidden');
            sendButton.disabled = false;
            renderMessage('Sorry, there was a network error. Please try again.', false);
            updateActiveChat();
        }
    }

    queryForm.addEventListener('submit', function (event) {
        event.preventDefault();
        sendMessage();
    });

    messageInput.addEventListener('keypress', function (e) {
        if (e.key === 'Enter') {
            e.preventDefault();
            sendMessage();
        }
    });

    // ========== Init ==========
    function init() {
        const savedActive = localStorage.getItem(ACTIVE_CHAT_KEY);
        const chats = loadChats();
        if (savedActive && chats.some(c => c.id === savedActive)) {
            activeChatId = savedActive;
            loadChat(activeChatId);
        } else if (chats.length > 0) {
            activeChatId = chats[0].id;
            loadChat(activeChatId);
        } else {
            showWelcome();
        }
        renderHistory();
        messageInput.focus();
    }

    init();
})();
