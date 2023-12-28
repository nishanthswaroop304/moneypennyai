document.addEventListener('DOMContentLoaded', function() {
    const chatUserInput = document.getElementById('chat-user-input');
    const sendButton = document.getElementById('send-btn');
    const initialSendButton = document.getElementById('initial-send-btn'); // New button in the initial state
    const initialUserInput = document.getElementById('initial-user-input'); // Input in the initial state
    const chatBox = document.getElementById('chat-box');

    function switchToChatUI() {
        const initialState = document.getElementById('initial-state');
        const chatContainer = document.getElementById('chat-container');
    
        initialState.style.display = 'none'; // Hide the initial state
        chatContainer.style.display = 'flex'; // Show the chat container
    
        // Scroll to the bottom of the chat box to show the latest messages
        scrollToBottom();
    }
    

    function scrollToBottom() {
    const chatBox = document.getElementById('chat-box');
    chatBox.scrollTop = chatBox.scrollHeight;
}

    function addSuggestionListener(suggestionId, question) {
        const suggestion = document.getElementById(suggestionId);
        suggestion.addEventListener('click', function() {
            sendMessage(question);
            suggestion.style.display = 'none';
            switchToChatUI();
        });
    }

    addSuggestionListener('prompt-suggestion1', "What are the best travel credit cards?");
    addSuggestionListener('prompt-suggestion2', "Which is the best card for groceries?");
    addSuggestionListener('prompt-suggestion3', "Best cards to improve credit score");

    function appendMessage(role, text) {
        const messageDiv = document.createElement('div');
        messageDiv.classList.add('message');
        if (role === 'assistant') {
            const iconSpan = document.createElement('span');
            iconSpan.classList.add('icon-span');
            //iconSpan.innerHTML = '&#128269; Answer: ';
            iconSpan.innerHTML = '&#128172; MoneyPenny:';
            messageDiv.appendChild(iconSpan);
        }
        const textDiv = document.createElement('div');
        textDiv.innerHTML = text;
        messageDiv.appendChild(textDiv);
        messageDiv.classList.add(role === 'user' ? 'user-msg' : 'assistant-msg');
        chatBox.appendChild(messageDiv);
    }

    async function sendMessage(message) {
        appendMessage('user', message);
        scrollToBottom(); // Scroll after appending the user message
    
        // Locate the existing spinner element
        const spinnerDiv = document.getElementById('loading-spinner');
        spinnerDiv.style.display = 'block'; // Show the spinner
    
        // Append the spinner to the chat box, making it the last element
        const chatBox = document.getElementById('chat-box');
        chatBox.appendChild(spinnerDiv);
    
        // Send the message to your backend and wait for the response
        const response = await fetch('/send-message', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ message: message })
        });
    
        // Once response is received, hide the spinner
        spinnerDiv.style.display = 'none'; // Hide the spinner
    
        if (!response.ok) {
            appendMessage('assistant', "Sorry, I'm having trouble processing that.");
            return;
        }
    
        const data = await response.json();
        console.log("Received suggestions:", data.suggestions); // Debugging line

        // Check if suggestions are part of the response
    if (data.suggestions) {
        displayPromptSuggestions(data.suggestions);
    } else {
        console.log("No suggestions found in the response.");
    }

        const formattedReply = formatResponse(data.reply);
        appendMessage('assistant', formattedReply);
    
        // Display prompt suggestions
        displayPromptSuggestions(data.suggestions);
    
        scrollToBottom(); // Scroll to show the latest messages
    }
    
    // Function to display prompt suggestions
    function displayPromptSuggestions(suggestions) {
        const suggestionsContainer = document.getElementById('prompt-suggestions-container');
        suggestionsContainer.innerHTML = ''; // Clear previous suggestions
    
        if (suggestions) {
            suggestions.split('\n').forEach((suggestion) => {
                const suggestionText = suggestion.trim();
                if (suggestionText) {
                    // Extract text without the leading number and period
                    const textWithoutNumber = suggestionText.replace(/^\d+\.\s*/, '');
                    const suggestionElement = document.createElement('p');
                    suggestionElement.textContent = textWithoutNumber;
                    suggestionsContainer.appendChild(suggestionElement);
    
                    // Make each suggestion clickable
                    suggestionElement.classList.add('clickable-suggestion');
                    suggestionElement.addEventListener('click', function() {
                        sendMessage(textWithoutNumber); // Use the text without the number prefix
                        document.getElementById('chat-user-input').value = ''; // Clear the input field
                    });
                }
            });
        }
    }
    
    
    // Clear suggestions when a new user message is typed
    document.getElementById('chat-user-input').addEventListener('input', function() {
        document.getElementById('prompt-suggestions-container').innerHTML = '';
    });
    

    function formatResponse(responseText) {
        let formattedText = responseText.replace(/\*\*(.*?)\*\*/gm, '<strong>$1</strong>');
        formattedText = formattedText.replace(/^\d+\.\s+/gm, '<li>').replace(/\n/g, '</li>');
        formattedText = '<ol>' + formattedText + '</ol>';
        formattedText = '<p>' + formattedText + '</p>';
        return formattedText;
    }

    initialSendButton.addEventListener('click', function() {
        const message = initialUserInput.value.trim();
        if (message) {
            sendMessage(message);
            initialUserInput.value = ''; // Clear the input field after sending
            switchToChatUI(); // Switch to the chat UI
        }
    });

    // New event listener for 'Enter' keypress in the initial input box
    initialUserInput.addEventListener('keypress', function(e) {
        if (e.key === 'Enter' && initialUserInput.value.trim()) {
            initialSendButton.click();
        }
    });

    sendButton.addEventListener('click', function() {
        const message = chatUserInput.value.trim();
        if (message) {
            sendMessage(message);
            chatUserInput.value = ''; // Clear the input field after sending
        }
    });

    chatUserInput.addEventListener('keypress', function(e) {
        if (e.key === 'Enter' && chatUserInput.value.trim()) {
            sendButton.click();
        }
    });

    

});
