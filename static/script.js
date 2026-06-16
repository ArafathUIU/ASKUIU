document.addEventListener('DOMContentLoaded', function () {
    const queryForm = document.getElementById('query-form');
    const messageInput = document.getElementById('user_message');
    const messagesContainer = document.getElementById('messages-container');
    const typingIndicator = document.querySelector('.typing-indicator');
    const sendButton = document.getElementById('send-button');
    const themeToggle = document.getElementById('theme-toggle');
    const quickQuestions = document.getElementById('quick-questions');
    const yearSpan = document.getElementById('year');

    if (yearSpan) {
        yearSpan.textContent = new Date().getFullYear();
    }

    // Theme handling
    function initTheme() {
        const saved = localStorage.getItem('askuiu-theme');
        const prefersDark = window.matchMedia('(prefers-color-scheme: dark)').matches;
        if (saved === 'dark' || (!saved && prefersDark)) {
            document.documentElement.classList.add('dark');
            updateThemeIcon(true);
        }
    }

    function updateThemeIcon(isDark) {
        const icon = themeToggle.querySelector('i');
        icon.className = isDark ? 'fas fa-sun' : 'fas fa-moon';
    }

    themeToggle.addEventListener('click', function () {
        const isDark = document.documentElement.classList.toggle('dark');
        localStorage.setItem('askuiu-theme', isDark ? 'dark' : 'light');
        updateThemeIcon(isDark);
    });

    initTheme();

    // Quick question chips
    if (quickQuestions) {
        quickQuestions.addEventListener('click', function (e) {
            const btn = e.target.closest('.quick-question');
            if (btn) {
                messageInput.value = btn.textContent.trim();
                sendMessage();
            }
        });
    }

    // Timestamp helper
    function setTimestamp(element) {
        if (!element) return;
        const now = new Date();
        element.textContent = formatTime(now);
    }

    document.querySelectorAll('[data-timestamp]').forEach(setTimestamp);

    function formatTime(date) {
        let hours = date.getHours();
        const minutes = date.getMinutes().toString().padStart(2, '0');
        const ampm = hours >= 12 ? 'PM' : 'AM';
        hours = hours % 12;
        hours = hours ? hours : 12;
        return `${hours}:${minutes} ${ampm}`;
    }

    // Escape HTML to prevent XSS
    function escapeHtml(text) {
        const div = document.createElement('div');
        div.textContent = text;
        return div.innerHTML;
    }

    // Convert URLs in text to clickable links
    function linkify(text) {
        const urlRegex = /(https?:\/\/[^\s]+)/g;
        return escapeHtml(text).replace(urlRegex, function (url) {
            return `<a href="${url}" target="_blank" rel="noopener noreferrer" class="text-uiu-orange hover:text-uiu-orange-hover underline">${url}</a>`;
        });
    }

    // Add a new message
    function addMessage(text, isUser) {
        const messageDiv = document.createElement('div');
        messageDiv.className = `flex message-entry ${isUser ? 'justify-end' : 'items-start'}`;

        const time = formatTime(new Date());

        if (!isUser) {
            messageDiv.innerHTML = `
                <div class="w-9 h-9 rounded-full bg-uiu-orange text-white flex items-center justify-center mr-2 flex-shrink-0 shadow-sm">
                    <i class="fas fa-robot text-sm"></i>
                </div>
                <div class="max-w-[85%] md:max-w-md lg:max-w-lg bg-white dark:bg-gray-800 p-4 rounded-2xl rounded-tl-none shadow-sm border border-uiu-gray-200 dark:border-gray-700 transition-colors duration-300">
                    <div class="text-uiu-black dark:text-gray-100 text-sm leading-relaxed">${linkify(text)}</div>
                    <p class="text-[11px] text-uiu-gray-600 dark:text-gray-400 mt-2">${time}</p>
                </div>
            `;
        } else {
            messageDiv.innerHTML = `
                <div class="max-w-[85%] md:max-w-md lg:max-w-lg bg-uiu-orange text-white p-4 rounded-2xl rounded-tr-none shadow-md">
                    <div class="text-sm leading-relaxed">${escapeHtml(text)}</div>
                    <p class="text-[11px] text-white/80 mt-2">${time}</p>
                </div>
                <div class="w-9 h-9 rounded-full bg-uiu-orange-light dark:bg-gray-700 flex items-center justify-center ml-2 flex-shrink-0 border border-uiu-orange/20">
                    <i class="fas fa-user text-uiu-orange dark:text-uiu-orange text-sm"></i>
                </div>
            `;
        }

        messagesContainer.appendChild(messageDiv);
        scrollToBottom();
    }

    function scrollToBottom() {
        messagesContainer.scrollTo({
            top: messagesContainer.scrollHeight,
            behavior: 'smooth'
        });
    }

    async function sendMessage() {
        const message = messageInput.value.trim();
        if (!message) return;

        addMessage(message, true);
        messageInput.value = '';
        sendButton.disabled = true;

        // Hide quick questions after first user message
        if (quickQuestions) {
            quickQuestions.style.display = 'none';
        }

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

            addMessage(data.response || 'No response received.', false);
        } catch (error) {
            typingIndicator.classList.add('hidden');
            sendButton.disabled = false;
            addMessage('Sorry, there was a network error. Please try again.', false);
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
});
