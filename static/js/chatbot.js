// ✅ Clean chatbot.js aligned with Django Conversation + ChatbotLead
document.addEventListener("DOMContentLoaded", function () {
    console.log("✅ chatbot.js loaded!");

    const chatbotButton = document.getElementById("chatbot-button");
    const chatWindow = document.getElementById("chat-window");
    const chatMessages = document.getElementById("chat-messages");
    const chatInput = document.getElementById("chat-input");
    const sendButton = document.getElementById("chat-send-button");
    const minimizeChat = document.getElementById("minimize-chat");
    const closeChat = document.getElementById("close-chat");

    if (!chatbotButton || !chatWindow || !chatMessages || !chatInput || !sendButton || !minimizeChat || !closeChat) {
        console.error("❌ Missing chatbot DOM elements.");
        return;
    }

    // ✅ Open chatbot automatically after 5 seconds
    setTimeout(function () {
        if (chatWindow.style.display !== "block") {
            openChatbot();
            // ✅ Fetch backend intro instead of sending "hi"
            fetch(`${window.location.origin}/api/chat/`, {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({ message: "hi" })  // empty → triggers backend intro
            })
            .then(res => res.json())
            .then(data => {
                if (data.reply) {
                    displayMessage("Chatbot", data.reply, "chatbot");
                }
            })
            .catch(err => console.error("Init chat error:", err));

        }
    }, 5000);

    // ✅ Toggle open/close/minimize
    chatbotButton.addEventListener("click", openChatbot);

    minimizeChat.addEventListener("click", function () {
        chatWindow.style.display = "none";
        chatbotButton.style.display = "block";
    });

    closeChat.addEventListener("click", function () {
        chatWindow.style.display = "none";
        chatbotButton.style.display = "block";
        chatMessages.innerHTML = "";
    });

    // ✅ Enter key to send
    chatInput.addEventListener("keypress", function (event) {
        if (event.key === "Enter" && !event.shiftKey) {
            event.preventDefault();
            sendMessage(chatInput.value.trim());
        }
    });

    // ✅ Send button to send
    sendButton.addEventListener("click", function () {
        sendMessage(chatInput.value.trim());
    });

    // ✅ Display a message in chat window
    function displayMessage(sender, message, type) {
        const msgDiv = document.createElement("div");
        msgDiv.classList.add(type === "user" ? "user-message" : "chatbot-message");
        msgDiv.innerHTML = `<strong>${sender}:</strong> ${message}`;
        chatMessages.appendChild(msgDiv);
        chatMessages.scrollTop = chatMessages.scrollHeight;
    }

    // ✅ Send message to Django backend
    function sendMessage(userMessage) {
        if (!userMessage) return;

        displayMessage("You", userMessage, "user");
        chatInput.value = "";

        fetch(`${window.location.origin}/api/chat/`, {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ message: userMessage })
        })
        .then(res => {
            if (!res.ok) throw new Error(`HTTP error! Status: ${res.status}`);
            return res.json();
        })
        .then(data => {
            if (data && data.reply) {
                displayMessage("Chatbot", data.reply, "chatbot");
            } else {
                displayMessage("Chatbot", "⚠️ Sorry, I didn’t understand that.", "chatbot");
            }
        })
        .catch(err => {
            console.error("❌ Chat error:", err);
            displayMessage("Chatbot", "⚠️ Something went wrong. Please try again.");
        });
    }

    // ✅ Show chatbot window
    function openChatbot() {
        chatWindow.style.display = "block";
        chatbotButton.style.display = "none";
    }

    // ✅ Close chatbot if clicked outside
    document.addEventListener("click", function (event) {
        if (!chatWindow.contains(event.target) && event.target !== chatbotButton) {
            chatWindow.style.display = "none";
            chatbotButton.style.display = "block";
        }
    });
});

console.log("✅ Clean chatbot.js fully initialized");
