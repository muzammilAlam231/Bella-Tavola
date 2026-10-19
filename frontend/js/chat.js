(function () {
    const toggle = document.querySelector("#chat-toggle");
    const panel = document.querySelector("#chat-panel");
    const closeBtn = document.querySelector("#chat-close");
    const log = document.querySelector("#chat-log");
    const form = document.querySelector("#chat-form");
    const input = document.querySelector("#chat-input");
    const sendBtn = document.querySelector("#chat-send");
    const KEY = "bella-chat-history";
    let history = [];
    try { history = JSON.parse(sessionStorage.getItem(KEY)) || []; } catch { history = []; }
    function save() {
        try { sessionStorage.setItem(KEY, JSON.stringify(history.slice(-20))); } catch { /* ignore */ }
    }
    function addBubble(role, text) {
        const div = document.createElement("div");
        div.className = `bubble ${role}`;
        div.textContent = text;                       // textContent = safe against HTML injection
        log.append(div);
        log.scrollTop = log.scrollHeight;
        return div;
    }
    function openChat() {
        panel.hidden = false;
        toggle.hidden = true;
        if (!log.children.length) {
            if (history.length) history.forEach((m) => addBubble(m.role, m.content));
            else addBubble("assistant",
                "Hi! Ask me about our menu, ingredients, dietary options, opening hours or booking policy.");
        }
        input.focus();
    }
    function closeChat() { panel.hidden = true; toggle.hidden = false; }
    toggle.addEventListener("click", openChat);
    closeBtn.addEventListener("click", closeChat);
    form.addEventListener("submit", async (event) => {
        event.preventDefault();
        const text = input.value.trim();
        if (!text) return;
        input.value = "";
        addBubble("user", text);
        history.push({ role: "user", content: text });
        const typing = addBubble("assistant typing", "Typing...");
        sendBtn.disabled = true;
        input.disabled = true;
        try {
            const res = await fetch("/api/chat", {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({ messages: history }),
            });
            const data = await res.json().catch(() => ({}));
            if (!res.ok) {
                throw new Error(typeof data.detail === "string"
                    ? data.detail : "Something went wrong. Please try again.");
            }
            typing.remove();
            addBubble("assistant", data.reply);
            history.push({ role: "assistant", content: data.reply });
            save();
        } catch (err) {
            typing.remove();
            history.pop();                              // drop the failed question from the history
            input.value = text;                         // let the visitor resend it easily
            addBubble("assistant error", err instanceof TypeError
                ? "I cannot reach the server right now. Please check your connection."
                : err.message);
        } finally {
            sendBtn.disabled = false;
            input.disabled = false;
            input.focus();
        }
    });
})();
