// ✅ Add this code to the chatbot.js file
    document.addEventListener("DOMContentLoaded", function () {
        const chatbotButton = document.getElementById("chatbot-button");
        const chatWindow = document.getElementById("chat-window");
        const chatMessages = document.getElementById("chat-messages");
        const chatInput = document.getElementById("chat-input");
        const sendButton = document.getElementById("chat-send-button");
        const minimizeChat = document.getElementById("minimize-chat");
        const closeChat = document.getElementById("close-chat");
    
        // ✅ Automatically open chatbot after 1.5 seconds
        setTimeout(function () {
            openChatbot();
            displayMessage("Chatbot", "👋 Welcome! How can I assist you with your window needs today?", "chatbot");
        }, 1500);  // Adjust delay if needed
    
        // ✅ Show chat window when button is clicked
        chatbotButton.addEventListener("click", function () {
            openChatbot();
        });
    
        // ✅ Minimize chat
        minimizeChat.addEventListener("click", function () {
            chatWindow.style.display = "none";
            chatbotButton.style.display = "block";
        });
    
        // ✅ Close chat and clear messages
        closeChat.addEventListener("click", function () {
            chatWindow.style.display = "none";
            chatbotButton.style.display = "block";
            chatMessages.innerHTML = "";
        });
    
        // ✅ Send message on Enter key press
        chatInput.addEventListener("keypress", function (event) {
            if (event.key === "Enter" && !event.shiftKey) {
                event.preventDefault();
                sendMessage();
            }
        });
    
        // ✅ Send message on button click
        sendButton.addEventListener("click", function () {
            sendMessage();
        });

        // ✅ Function to get CSRF token from cookies
        function getCSRFToken() {
            const cookieValue = document.cookie
                .split("; ")
                .find(row => row.startsWith("csrftoken="));
            return cookieValue ? cookieValue.split("=")[1] : "";
        }
    
        // ✅ Function to send messages
        function sendMessage() {
            const userMessage = chatInput.value.trim();
            if (!userMessage) return;
        
            displayMessage("You", userMessage, "user");
        
            // ✅ Choose correct API URL for local and Heroku
            const apiUrl = window.location.hostname === "127.0.0.1"
                ? "http://127.0.0.1:8000/api/chat/"  
                : "https://windowgeniusai.herokuapp.com/api/chat/";  
        
            fetch(apiUrl, {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({ message: userMessage }),
                mode: "cors",  
                cache: "no-cache",
                credentials: "include"  // ✅ Ensure authentication and cookies work
            })
            .then(response => {
                if (!response.ok) {
                    throw new Error(`HTTP error! Status: ${response.status}`);
                }
                return response.json();
            })
            .then(data => {
                displayMessage("Chatbot", data.reply, "chatbot");
            })
            .catch(error => {
                console.error("Error:", error);
                displayMessage("Chatbot", "Oops! Something went wrong. 😕", "chatbot");
            });
        
            chatInput.value = "";
        }
        
        // ✅ Function to display messages in chat
        function displayMessage(sender, message, type) {
            const msgDiv = document.createElement("div");
            msgDiv.classList.add(type === "user" ? "user-message" : "chatbot-message");
            msgDiv.innerHTML = `<strong>${sender}:</strong> ${message}`;
            chatMessages.appendChild(msgDiv);
            chatMessages.scrollTop = chatMessages.scrollHeight;
        }
    
        // ✅ Function to open chatbot
        function openChatbot() {
            chatWindow.style.display = "block";
            chatbotButton.style.display = "none";
        }
    });
    document.addEventListener("click", function(event) {
        const chatbot = document.getElementById("chatbot-container");
        const chatButton = document.getElementById("chatbot-button");

        if (chatbot && !chatbot.contains(event.target) && event.target !== chatButton) {
            chatbot.classList.add("hidden"); // ✅ Hide chatbot
        }
    });

    // ✅ Toggle chatbot visibility when clicking the button
    document.getElementById("chatbot-button").addEventListener("click", function() {
        document.getElementById("chatbot-container").classList.toggle("hidden");
    });
     
