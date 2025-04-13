// ✅ Ensure all elements exist before attaching event listeners
document.addEventListener("DOMContentLoaded", function () {
    console.log("✅ chatbot.js is loaded!");

    const chatbotButton = document.getElementById("chatbot-button");
    const chatWindow = document.getElementById("chat-window");
    const chatMessages = document.getElementById("chat-messages");
    const chatInput = document.getElementById("chat-input");
    const sendButton = document.getElementById("chat-send-button");
    const minimizeChat = document.getElementById("minimize-chat");
    const closeChat = document.getElementById("close-chat");

    if (!chatbotButton || !chatWindow || !chatMessages || !chatInput || !sendButton || !minimizeChat || !closeChat) {
        console.error("❌ One or more chatbot elements are missing from the DOM.");
        return;
    }

    // ✅ Open chatbot automatically after 3 seconds
    setTimeout(function () {
        if (chatWindow.style.display !== "block") {
            openChatbot();
            displayMessage("Chatbot", "👋 Hi there! I’m Window Genius AI. I can help you get a quote, schedule a consultation, or answer questions!", "chatbot");
        }
    }, 5000);  // ✅ Delayed chatbot opening (5 seconds)

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

        // ✅ Choose correct API URL for local and production dynamically
        const apiUrl = `${window.location.origin}/api/chat/`;

        fetch(apiUrl, {
            method: "POST",
            headers: {
                "Content-Type": "application/json",
                "X-CSRFToken": getCSRFToken()
            },
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
            if (data && data.reply) {
                displayMessage("Chatbot", data.reply, "chatbot");
            } else {
                displayMessage("Chatbot", "Sorry, I didn't understand that.", "chatbot");
            }
        })
        .catch(error => {
            console.error("❌ Error:", error);
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

    // ✅ Hide chatbot when clicking outside
    document.addEventListener("click", function (event) {
        if (!chatWindow.contains(event.target) && event.target !== chatbotButton) {
            chatWindow.style.display = "none";
            chatbotButton.style.display = "block";
        }
    });
});

console.log("Chatbot script initialized (moved from base.html)");
