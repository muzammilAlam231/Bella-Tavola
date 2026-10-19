(function () {
    const form = document.querySelector("#reservation-form");
    const msg = document.querySelector("#form-message");
    const btn = document.querySelector("#reserve-btn");
    // Do not allow picking past dates (en-CA locale formats as YYYY-MM-DD)
    form.elements.reservation_date.min = new Date().toLocaleDateString("en-CA");
    // FastAPI returns detail as a string (our errors) or a list (validation errors)
    function extractError(data) {
        if (typeof data.detail === "string") return data.detail;
        if (Array.isArray(data.detail)) {
            return data.detail
                .map((e) => e.msg.replace("Value error, ", ""))
                .join(" | ");
        }
        return "Something went wrong. Please try again.";
    }
    function show(kind, text) {
        msg.className = kind;
        msg.textContent = text;
    }
    form.addEventListener("submit", async (event) => {
        event.preventDefault();
        show("", "");
        if (!form.checkValidity()) {
            form.reportValidity();               // browser shows which field is wrong
            return;
        }
        const payload = Object.fromEntries(new FormData(form));
        payload.party_size = Number(payload.party_size);
        if (!payload.special_requests) payload.special_requests = null;
        btn.disabled = true;                    // prevents duplicate submissions
        btn.textContent = "Booking...";
        try {
            const res = await fetch("/api/reservations", {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify(payload),
            });
            const data = await res.json().catch(() => ({}));
            if (!res.ok) throw new Error(extractError(data));
            show("success",
                `Thank you, ${data.name}! Table for ${data.party_size} on ${data.reservation_date} at ` +
                `${data.reservation_time.slice(0, 5)} is confirmed. Reference #${data.id}.`);
            form.reset();
            form.elements.party_size.value = 2;
        } catch (err) {
            show("error", err instanceof TypeError
                ? "We could not reach the server. Check your connection and try again."
                : err.message);
        } finally {
            btn.disabled = false;
            btn.textContent = "Book my table";
        }
    });
})();