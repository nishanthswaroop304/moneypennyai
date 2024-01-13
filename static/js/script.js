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

    addSuggestionListener('prompt-suggestion1', "Top travel credit cards");
    addSuggestionListener('prompt-suggestion2', "High cashback grocery cards");
    addSuggestionListener('prompt-suggestion3', "Cards designed for building credit");

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
    
        // Locate the existing spinner element and its text container
        const spinnerDiv = document.getElementById('loading-spinner');
        const spinnerText = spinnerDiv.querySelector('p'); // Assuming the <p> tag contains the text
        spinnerDiv.style.display = 'block'; // Show the spinner
    
        // Append the spinner to the chat box, making it the last element
        const chatBox = document.getElementById('chat-box');
        chatBox.appendChild(spinnerDiv);
    
        // Texts to cycle through for the spinner
        const spinnerTexts = [
            "Crunching credit card data...",
            "Finding the best options...",
            "Almost there, hang tight!",
            "Finalizing the best picks..."
        ];
        let currentTextIndex = 0;
    
        // Function to update spinner text
        function updateSpinnerText() {
            spinnerText.textContent = spinnerTexts[currentTextIndex];
            currentTextIndex = (currentTextIndex + 1) % spinnerTexts.length;
        
            // Stop changing text after the third text has been displayed
            if (currentTextIndex === 0) { // Resets back to 0 after displaying the last text
                clearInterval(textChangeInterval);
            }
        }
        
    
        // Immediately update the spinner text
        updateSpinnerText();
    
        // Start the interval to change text every 10 seconds
        const textChangeInterval = setInterval(updateSpinnerText, 5000);
    
        // Send the message to your backend and wait for the response
        const response = await fetch('/send-message', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ message: message })
        });
    
        // Once response is received, hide the spinner and clear the interval
        spinnerDiv.style.display = 'none'; // Hide the spinner
        clearInterval(textChangeInterval);
    
        if (!response.ok) {
            appendMessage('assistant', "Sorry, I'm having trouble processing that.");
            return;
        }
    
        const data = await response.json();
    
        // Initialize Markdown-it
        const md = window.markdownit();
    
        // Use Markdown-it to render the response
        const formattedReply = md.render(data.reply);
    
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
            let suggestionText = suggestion.trim();
            
            // Check if the line is a divider or header (contains ###)
            if (suggestionText.includes('###')) {
                return; // Skip this line
            }

            if (suggestionText) {
                // Extract text without the leading number and period
                let textWithoutNumber = suggestionText.replace(/^\d+\.\s*/, '');

                // Remove quotes from the suggestion text
                textWithoutNumber = textWithoutNumber.replace(/^["']|["']$/g, '');

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
        let formattedText = '';
        const lines = responseText.split('\n');
    
        let isList = false; // Flag to track if we are inside a bullet list
    
        lines.forEach(line => {
            line = line.trim();
    
            // Bold headers (credit card names) - Check for '**' and remove them
            if (line.startsWith('**') && line.endsWith('**')) {
                if (isList) {
                    formattedText += '</ul>'; // Close the list if it was open
                    isList = false;
                }
                // Remove '**' from start and end to apply bold formatting
                formattedText += `<p><strong>${line.slice(2, -2)}</strong></p>`;
            }
            // Bullet points for card benefits
            else if (line.startsWith('✨') || line.startsWith('🍏') || line.startsWith('🎉') ||
                     line.startsWith('🏪') || line.startsWith('🍽️') || line.startsWith('💸') ||
                     line.startsWith('📱') || line.startsWith('💼') || line.startsWith('🍔') || line.startsWith('🔝')) {
                if (!isList) {
                    formattedText += '<ul>'; // Start a new bullet list
                    isList = true;
                }
                formattedText += `<li>${line}</li>`;
            }
            // Other lines
            else {
                if (isList) {
                    formattedText += '</ul>'; // Close the list if it was open
                    isList = false;
                }
                formattedText += `<p>${line}</p>`;
            }
        });
    
        if (isList) {
            formattedText += '</ul>'; // Close the list if it's still open
        }
    
        return '<div>' + formattedText + '</div>';
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
