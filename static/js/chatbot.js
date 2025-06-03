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

    // ✅ Open chatbot automatically after 5 seconds
    setTimeout(function () {
        if (chatWindow.style.display !== "block") {
            openChatbot();
            displayMessage("Chatbot", "👋 Hi there! I’m Window Genius AI. I can help you get a quote, schedule a consultation, or answer questions!", "chatbot");
        }
    }, 5000);

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

    // ✅ CSRF Token Helper
    function getCSRFToken() {
        const cookieValue = document.cookie
            .split("; ")
            .find(row => row.startsWith("csrftoken="));
        return cookieValue ? cookieValue.split("=")[1] : "";
    }

    // ✅ Lead capture variables
    let capturedName = "";
    let capturedEmail = "";
    let capturedPhone = "";
    let leadSent = false;

    // ✅ Send message to OpenAI API and handle reply
    function sendMessage() {
        const userMessage = chatInput.value.trim();
        if (!userMessage) return;

        displayMessage("You", userMessage, "user");

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
            credentials: "include"
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
                extractLeadInfo(userMessage); // ✅ Check lead info on every message
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

    // ✅ Display message in chat
    function displayMessage(sender, message, type) {
        const msgDiv = document.createElement("div");
        msgDiv.classList.add(type === "user" ? "user-message" : "chatbot-message");
        msgDiv.innerHTML = `<strong>${sender}:</strong> ${message}`;
        chatMessages.appendChild(msgDiv);
        chatMessages.scrollTop = chatMessages.scrollHeight;
    }

    // ✅ Extract and detect lead info
    function extractLeadInfo(message) {
        if (!capturedName && /\b(name is|I'm|I am)\s+([A-Z][a-z]+(?:\s[A-Z][a-z]+)?)/i.test(message)) {
            capturedName = message.match(/\b(name is|I'm|I am)\s+([A-Z][a-z]+(?:\s[A-Z][a-z]+)?)/i)[2];
        }

        if (!capturedEmail && /\b[\w\.-]+@[\w\.-]+\.\w{2,4}\b/.test(message)) {
            capturedEmail = message.match(/\b[\w\.-]+@[\w\.-]+\.\w{2,4}\b/)[0];
        }

        if (!capturedPhone && /(?:\+?\d{1,2}[\s.-]?)?(?:\(?\d{3}\)?[\s.-]?)?\d{3}[\s.-]?\d{4}/.test(message)) {
            capturedPhone = message.match(/(?:\+?\d{1,2}[\s.-]?)?(?:\(?\d{3}\)?[\s.-]?)?\d{3}[\s.-]?\d{4}/)[0];
        }

        if (capturedName && capturedEmail && capturedPhone && !leadSent) {
            sendLeadToBackend(capturedName, capturedEmail, capturedPhone);
        }
    }

    // ✅ POST lead data to backend
    function sendLeadToBackend(name, email, phone) {
        fetch(`${window.location.origin}/api/save-lead/`, {
            method: "POST",
            headers: {
                "Content-Type": "application/json",
                "X-CSRFToken": getCSRFToken()
            },
            body: JSON.stringify({ name, email, phone }),
            credentials: "include"
        })
        .then(response => {
            if (response.ok) {
                console.log("✅ Lead info sent successfully");
                leadSent = true;
            } else {
                console.error("❌ Failed to send lead info");
            }
        })
        .catch(error => {
            console.error("❌ Error sending lead info:", error);
        });
    }

    // ✅ Show chatbot
    function openChatbot() {
        chatWindow.style.display = "block";
        chatbotButton.style.display = "none";
    }

    // ✅ Hide chatbot on outside click
    document.addEventListener("click", function (event) {
        if (!chatWindow.contains(event.target) && event.target !== chatbotButton) {
            chatWindow.style.display = "none";
            chatbotButton.style.display = "block";
        }
    });
});

console.log("✅ chatbot.js script is fully initialized");
