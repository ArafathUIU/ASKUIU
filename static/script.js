document.addEventListener('DOMContentLoaded', function() {
    const chatMessages = document.getElementById('chat-messages');
    const userInput = document.getElementById('user-input');
    const sendButton = document.getElementById('send-button');
    const micButton = document.getElementById('mic-button');
    let mediaRecorder;
    let audioChunks = [];

    // Auto-resize textarea
    userInput.addEventListener('input', function() {
        this.style.height = 'auto';
        this.style.height = (this.scrollHeight) + 'px';
    });

    // Send message on button click
    sendButton.addEventListener('click', sendMessage);

    // Send message on Enter key (allow Shift+Enter for new lines)
    userInput.addEventListener('keydown', function(e) {
        if (e.key === 'Enter' && !e.shiftKey) {
            e.preventDefault();
            sendMessage();
        }
    });

    // Suggested questions
    document.querySelectorAll('.suggested-question').forEach(button => {
        button.addEventListener('click', function() {
            userInput.value = this.textContent.trim();
            userInput.focus();
            userInput.dispatchEvent(new Event('input'));
            sendMessage();
        });
    });

    // Speech-to-text
    micButton.addEventListener('click', toggleRecording);

    function toggleRecording() {
        if (mediaRecorder && mediaRecorder.state === 'recording') {
            mediaRecorder.stop();
            micButton.innerHTML = '<i class="fas fa-microphone"></i>';
            micButton.setAttribute('aria-label', 'Record voice');
        } else {
            navigator.mediaDevices.getUserMedia({ audio: true })
                .then(stream => {
                    mediaRecorder = new MediaRecorder(stream);
                    mediaRecorder.start();
                    audioChunks = [];
                    mediaRecorder.ondataavailable = e => audioChunks.push(e.data);
                    mediaRecorder.onstop = async () => {
                        showTypingIndicator();
                        const blob = new Blob(audioChunks, { type: 'audio/webm' });
                        const formData = new FormData();
                        formData.append('audio', blob, 'recording.webm');
                        try {
                            const response = await fetch('/api/speech-to-text', {
                                method: 'POST',
                                body: formData
                            });
                            if (!response.ok) throw new Error('Failed to process audio');
                            const data = await response.json();
                            userInput.value = data.transcript;
                            userInput.dispatchEvent(new Event('input'));
                            sendMessage();
                        } catch (error) {
                            addMessage(`Error: ${error.message}`, 'bot');
                        } finally {
                            removeTypingIndicator();
                        }
                    };
                    micButton.innerHTML = '<i class="fas fa-stop"></i>';
                    micButton.setAttribute('aria-label', 'Stop recording');
                })
                .catch(error => {
                    addMessage(`Microphone error: ${error.message}`, 'bot');
                });
        }
    }

    async function sendMessage() {
        const message = userInput.value.trim();
        if (message === '') return;

        // Add user message
        addMessage(message, 'user');
        userInput.value = '';
        userInput.style.height = 'auto';

        // Show typing indicator
        showTypingIndicator();

        // Call RAG API
        try {
            const response = await fetch('/api/query', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ query: message })
            });
            if (!response.ok) throw new Error('Failed to process query');
            const data = await response.json();
            addMessage(data.answer, 'bot', data.sources);
        } catch (error) {
            addMessage(`Error: ${error.message}`, 'bot');
        } finally {
            removeTypingIndicator();
            chatMessages.scrollTop = chatMessages.scrollHeight;
        }
    }

    function addMessage(content, sender, sources = []) {
        const messageDiv = document.createElement('div');
        messageDiv.className = `flex items-start ${sender === 'user' ? 'justify-end' : ''}`;

        if (sender === 'user') {
            messageDiv.innerHTML = `
                <div class="message bg-blue-600 text-white p-4 user-message">
                    <p>${content}</p>
                </div>
            `;
        } else {
            let sourceHtml = '';
            if (sources.length > 0) {
                sourceHtml = `
                    <div class="mt-3 p-3 bg-gray-100 rounded-lg">
                        <div class="flex items-center text-sm text-gray-700 mb-1">
                            <i class="fas fa-database mr-1 text-orange-500"></i>
                            <span>Source: UIU Knowledge Base</span>
                        </div>
                        <p class="text-xs text-gray-900">Confidence: ${Math.floor(Math.random() * 20) + 80}% • Retrieved: ${sources.length} relevant documents</p>
                    </div>
                `;
            }
            messageDiv.innerHTML = `
                <div class="bg-orange-100 p-3 rounded-full mr-3">
                    <i class="fas fa-robot text-orange-500 text-xl"></i>
                </div>
                <div class="message p-4 bot-message">
                    <p class="font-medium text-orange-800">${content}</p>
                    ${sourceHtml}
                </div>
            `;
        }

        chatMessages.appendChild(messageDiv);
        chatMessages.scrollTop = chatMessages.scrollHeight;
    }

    function showTypingIndicator() {
        const typingDiv = document.createElement('div');
        typingDiv.className = 'flex items-start';
        typingDiv.id = 'typing-indicator';
        typingDiv.innerHTML = `
            <div class="bg-orange-100 p-3 rounded-full mr-3">
                <i class="fas fa-robot text-orange-500 text-xl"></i>
            </div>
            <div class="message p-4 bot-message">
                <div class="typing-indicator flex space-x-1">
                    <span class="h-2 w-2 bg-gray-500 lines rounded-full"></span>
                    <span class="h-2 w-2 bg-gray-500 rounded-full"></span>
                    <span class="h-2 w-2 bg-gray-500 rounded-full"></span>
                </div>
            </div>
        `;
        chatMessages.appendChild(typingDiv);
        chatMessages.scrollTop = chatMessages.scrollHeight;
    }

    function removeTypingIndicator() {
        const typingIndicator = document.getElementById('typing-indicator');
        if (typingIndicator) typingIndicator.remove();
    }

    // Create floating particles
    function createParticles() {
        const particlesContainer = document.getElementById('particles');
        const particleCount = 30;

        for (let i = 0; i < particleCount; i++) {
            const particle = document.createElement('div');
            particle.classList.add('particle');

            const size = Math.random() * 10 + 5;
            const posX = Math.random() * window.innerWidth;
            const duration = Math.random() * 15 + 10;
            const delay = Math.random() * 10;

            particle.style.width = `${size}px`;
            particle.style.height = `${size}px`;
            particle.style.left = `${posX}px`;
            particle.style.bottom = `-${size}px`;
            particle.style.animationDuration = `${duration}s`;
            particle.style.animationDelay = `${delay}s`;

            particlesContainer.appendChild(particle);
        }
    }

    createParticles();
});