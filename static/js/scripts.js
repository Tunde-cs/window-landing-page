/*!
* Start Bootstrap - Landing Page v6.0.5 (https://startbootstrap.com/theme/landing-page)
* Copyright 2013-2022 Start Bootstrap
* Licensed under MIT (https://github.com/StartBootstrap/startbootstrap-landing-page/blob/master/LICENSE)
*/
// This file is intentionally blank
// Use this file to add JavaScript to your project

document.addEventListener("DOMContentLoaded", function () {
    document.querySelectorAll('a[href^="#"]').forEach(anchor => {
        anchor.addEventListener("click", function (e) {
            e.preventDefault();
            document.querySelector(this.getAttribute("href")).scrollIntoView({
                behavior: "smooth"
            });
        });
    });
});

function toggleChat() {
    let chatContainer = document.getElementById("chat-container");
    chatContainer.style.display = (chatContainer.style.display === "block") ? "none" : "block";
}

async function sendMessage() {
    const userInput = document.getElementById("user-input").value.trim();
    const chatLog = document.getElementById("chat-log");

    if (!userInput) return;

    // Display user message
    const userMessage = document.createElement("div");
    userMessage.className = "user-message";
    userMessage.textContent = `You: ${userInput}`;
    chatLog.appendChild(userMessage);

    document.getElementById("user-input").value = "";

    // Show AI typing indicator
    const botMessage = document.createElement("div");
    botMessage.className = "bot-message";
    botMessage.textContent = "Thinking...";
    chatLog.appendChild(botMessage);

    try {
        const response = await fetch("http://127.0.0.1:5000/chat", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ message: userInput }),
        });
        const data = await response.json();
        botMessage.textContent = `Bot: ${data.reply}`;
    } catch (error) {
        botMessage.textContent = "Error reaching AI. Try again later.";
    }

    chatLog.scrollTop = chatLog.scrollHeight;
}
