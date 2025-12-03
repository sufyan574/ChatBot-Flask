const sendBtn = document.getElementById("send-btn");
const resetBtn = document.getElementById("reset-btn");
const input = document.getElementById("message-input");
const messagesDiv = document.getElementById("messages");

function addMessage(role, text) {
    const msgEl = document.createElement("div");
    msgEl.className = role;
    msgEl.textContent = `${role.toUpperCase()}: ${text}`;
    messagesDiv.appendChild(msgEl);
    messagesDiv.scrollTop = messagesDiv.scrollHeight;
}

sendBtn.addEventListener("click", async () => {
    const text = input.value.trim();
    if (!text) return;
    addMessage("user", text);
    input.value = "";

    const res = await fetch("/ask", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ message: text })
    });

    const data = await res.json();
    if (data.response) {
        addMessage("model", data.response);
    } else if (data.error) {
        addMessage("model", "Error: " + data.error);
    }
});

resetBtn.addEventListener("click", async () => {
    await fetch("/reset", { method: "POST" });
    messagesDiv.innerHTML = "";
});
