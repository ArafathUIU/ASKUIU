document.addEventListener('DOMContentLoaded', function () {
    const queryForm = document.getElementById('query-form');
    const messageInput = document.getElementById('user_message');
    const messagesContainer = document.getElementById('messages-container');
    const typingIndicator = document.querySelector('.typing-indicator');

    // Function to add a new message
    function addMessage(text, isUser) {
        const messageDiv = document.createElement('div');
        messageDiv.className = `flex mb-4 message-entry ${isUser ? 'justify-end' : 'items-start'}`;

        if (!isUser) {
            messageDiv.innerHTML = `
                <div class="w-8 h-8 rounded-full bg-orange-300 flex items-center justify-center mr-2 flex-shrink-0">
                    <i class="fas fa-robot text-orange-700 text-sm"></i>
                </div>
                <div class="max-w-xs md:max-w-md lg:max-w-lg bg-white p-3 rounded-lg shadow-sm border border-orange-100">
                    <p class="text-gray-800">${text}</p>
                    <p class="text-xs text-gray-500 mt-1">${getCurrentTime()}</p>
                </div>
            `;
        } else {
            messageDiv.innerHTML = `
                <div class="max-w-xs md:max-w-md lg:max-w-lg bg-orange-500 text-white p-3 rounded-lg shadow-sm">
                    <p>${text}</p>
                    <p class="text-xs text-orange-100 mt-1">${getCurrentTime()}</p>
                </div>
                <div class="w-8 h-8 rounded-full bg-orange-100 flex items-center justify-center ml-2 flex-shrink-0">
                    <i class="fas fa-user text-orange-600 text-sm"></i>
                </div>
            `;
        }

        messagesContainer.appendChild(messageDiv);
        messagesContainer.scrollTop = messagesContainer.scrollHeight;
    }

    // Get current time in HH:MM AM/PM format
    function getCurrentTime() {
        const now = new Date();
        let hours = now.getHours();
        const minutes = now.getMinutes().toString().padStart(2, '0');
        const ampm = hours >= 12 ? 'PM' : 'AM';
        hours = hours % 12;
        hours = hours ? hours : 12;
        return `${hours}:${minutes} ${ampm}`;
    }

    // Send message function
    async function sendMessage() {
        const message = messageInput.value.trim();
        if (!message) return;

        addMessage(message, true); // Add user message
        messageInput.value = '';

        // Show typing indicator
        typingIndicator.classList.remove('hidden');
        messagesContainer.scrollTop = messagesContainer.scrollHeight;

        try {
            const response = await fetch('/', {
                method: 'POST',
                headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
                body: new URLSearchParams({ 'user_message': message })
            });

            const data = await response.json();
            typingIndicator.classList.add('hidden');

            addMessage(data.response || 'No response received.', false); // Bot message
        } catch (error) {
            typingIndicator.classList.add('hidden');
            addMessage('Error: ' + error.message, false);
        }
    }

    // Event listener for form submit
    queryForm.addEventListener('submit', async function (event) {
        event.preventDefault();
        await sendMessage();
    });

    // Enter key submission
    messageInput.addEventListener('keypress', async function (e) {
        if (e.key === 'Enter') {
            e.preventDefault();
            await sendMessage();
        }
    });

    // Initial welcome message
    setTimeout(() => {
        addMessage("Try asking me anything! I can help with general questions, provide information, or just chat.", false);
    }, 1500);
});
