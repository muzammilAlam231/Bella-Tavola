const $ = (s) => document.querySelector(s);
const FLAGS = ["is_vegetarian", "is_vegan", "is_gluten_free", "is_featured", "is_available"];
let auth = sessionStorage.getItem("bella-admin-auth");
function extractError(data) {
    if (typeof data.detail === "string") return data.detail;
    if (Array.isArray(data.detail)) {
        return data.detail.map((e) => e.msg.replace("Value error, ", "")).join(" | ");
    }
    return "Something went wrong.";
}
function setMsg(el, kind, text) { el.className = "msg " + kind; el.textContent = text; }
async function api(path, options = {}) {
    const res = await fetch(path, {
        ...options,
        headers: { "Content-Type": "application/json", Authorization: `Basic ${auth}` },
    });
    if (res.status === 401) { logout(); throw new Error("Please log in again."); }
    if (res.status === 204) return null;
    const data = await res.json().catch(() => ({}));
    if (!res.ok) throw new Error(extractError(data));
    return data;
}
function cell(text) { const c = document.createElement("td"); c.textContent = text; return c; }
function button(label, cls, onClick) {
    const b = document.createElement("button");
    b.type = "button"; b.className = "small-btn " + cls; b.textContent = label;
    b.addEventListener("click", onClick);
    return b;
}
function messageRow(text, cols) {
    const tr = document.createElement("tr"); const c = cell(text); c.colSpan = cols; tr.append(c); return tr;
}
/* ---------- login / logout ---------- */
function showApp() {
    $("#login-view").hidden = true; $("#app-view").hidden = false;
    loadReservations(); loadMenu();
}
function logout() {
    auth = null; sessionStorage.removeItem("bella-admin-auth");
    $("#app-view").hidden = true; $("#login-view").hidden = false;
}
$("#logout").addEventListener("click", logout);

$("#login-form").addEventListener("submit", async (e) => {
    e.preventDefault();
    const f = new FormData(e.target);
    auth = btoa(`${f.get("username")}:${f.get("password")}`);
    setMsg($("#login-msg"), "", "Checking...");
    try {
        await api("/api/admin/me");
        sessionStorage.setItem("bella-admin-auth", auth);
        e.target.reset(); setMsg($("#login-msg"), "", "");
        showApp();
    } catch (err) {
        setMsg($("#login-msg"), "error", "Wrong username or password.");
    }
});
/* ---------- tabs ---------- */
document.querySelectorAll(".tab").forEach((tab) => tab.addEventListener("click", () => {
    document.querySelectorAll(".tab").forEach((t) => t.classList.toggle("active", t === tab));
    $("#tab-reservations").hidden = tab.dataset.tab !== "reservations";
    $("#tab-menu").hidden = tab.dataset.tab !== "menu";
}));
/* ---------- reservations ---------- */
async function loadReservations() {
    const body = $("#res-body");
    body.replaceChildren(messageRow("Loading...", 8));
    try {
        const rows = await api("/api/reservations");
        if (!rows.length) { body.replaceChildren(messageRow("No reservations yet.", 8)); return; }
        body.replaceChildren(...rows.map((r) => {
            const tr = document.createElement("tr");
            if (r.status === "cancelled") tr.className = "row-cancelled";
            const next = r.status === "cancelled" ? "confirmed" : "cancelled";
            const actions = document.createElement("td");
            actions.append(
                button(next === "cancelled" ? "Cancel" : "Restore", "", () => changeStatus(r.id, next)),
                button("Delete", "danger", () => removeReservation(r.id)));
            tr.append(cell(r.reservation_date), cell(r.reservation_time.slice(0, 5)), cell(r.name),
                cell(String(r.party_size)), cell(`${r.email} / ${r.phone}`), cell(r.special_requests || "-"),
                cell(r.status), actions);
            return tr;
        }));
    } catch (err) { setMsg($("#admin-msg"), "error", err.message); }
}
async function changeStatus(id, status) {

    try {
        await api(`/api/reservations/${id}/status`, { method: "PATCH", body: JSON.stringify({ status }) });
        setMsg($("#admin-msg"), "success", "Reservation updated."); loadReservations();
    } catch (err) { setMsg($("#admin-msg"), "error", err.message); }
}
async function removeReservation(id) {
    if (!confirm("Delete this reservation permanently?")) return;
    try {
        await api(`/api/reservations/${id}`, { method: "DELETE" });
        setMsg($("#admin-msg"), "success", "Reservation deleted."); loadReservations();
    } catch (err) { setMsg($("#admin-msg"), "error", err.message); }
}
/* ---------- menu management ---------- */
const form = $("#menu-form");
async function loadMenu() {
    const body = $("#menu-body");
    body.replaceChildren(messageRow("Loading...", 6));
    try {
        const items = await api("/api/menu?include_unavailable=true");
        body.replaceChildren(...items.map((i) => {
            const tr = document.createElement("tr");
            const diet = i.is_vegan ? "vegan" : i.is_vegetarian ? "vegetarian" : "";
            const tags = [diet, i.is_gluten_free ? "gluten-free" : "",
                i.is_featured ? "featured" : ""].filter(Boolean).join(", ");
            const actions = document.createElement("td");
            actions.append(button("Edit", "", () => startEdit(i)), button("Delete", "danger", () => removeItem(i)));
            tr.append(cell(i.name), cell(i.category), cell("$" + i.price.toFixed(2)), cell(tags || "-"),
                cell(i.is_available ? "Yes" : "No"), actions);
            return tr;
        }));
    } catch (err) { setMsg($("#admin-msg"), "error", err.message); }
}
function resetForm() {
    form.reset(); form.elements.id.value = ""; form.elements.is_available.checked = true;
    $("#menu-save").textContent = "Add item"; $("#menu-cancel").hidden = true;
}
function startEdit(item) {
    const TEXT = ["id", "name", "price", "category", "ingredients", "description"];
    for (const k of TEXT) form.elements[k].value = item[k] ?? "";
    for (const k of FLAGS) form.elements[k].checked = item[k];
    $("#menu-save").textContent = "Save changes"; $("#menu-cancel").hidden = false;
    form.scrollIntoView({ behavior: "smooth" });
}
$("#menu-cancel").addEventListener("click", resetForm);
async function removeItem(item) {
    if (!confirm(`Delete "${item.name}"?`)) return;
    try {
        await api(`/api/menu/${item.id}`, { method: "DELETE" });
        setMsg($("#admin-msg"), "success", "Item deleted."); loadMenu();
    } catch (err) { setMsg($("#admin-msg"), "error", err.message); }
}
form.addEventListener("submit", async (e) => {
    e.preventDefault();
    const f = form.elements;
    const payload = {
        name: f.name.value.trim(), price: Number(f.price.value), category: f.category.value.trim(),
        ingredients: f.ingredients.value.trim(), description: f.description.value.trim()
    };
    for (const k of FLAGS) payload[k] = f[k].checked;
    const id = f.id.value;
    const save = $("#menu-save"); save.disabled = true;
    try {
        await api(id ? `/api/menu/${id}` : "/api/menu",
            { method: id ? "PUT" : "POST", body: JSON.stringify(payload) });
        setMsg($("#admin-msg"), "success", id ? "Item updated." : "Item added.");
        resetForm(); loadMenu();
    } catch (err) { setMsg($("#admin-msg"), "error", err.message); }
    finally { save.disabled = false; }
});
/* ---------- start ---------- */
if (auth) { api("/api/admin/me").then(showApp).catch(() => { }); }
