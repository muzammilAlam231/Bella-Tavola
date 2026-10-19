const API = "/api";
const $ = (selector) => document.querySelector(selector);
// Small helper: create an element safely
function el(tag, className, text) {
    const node = document.createElement(tag);
    if (className) node.className = className;
    if (text !== undefined) node.textContent = text;
    return node;
}
function buildCard(item) {
    const card = el("article", "card");
    const banner = el("div", `card-banner cat-${item.category.toLowerCase()}`, item.category);
    const top = el("div", "card-top");
    top.append(el("h3", "", item.name), el("span", "price", `$${item.price.toFixed(2)}`));
    const tags = el("div", "tags");
    if (item.is_vegan) tags.append(el("span", "tag tag-green", "Vegan"));
    else if (item.is_vegetarian) tags.append(el("span", "tag tag-green", "Vegetarian"));
    if (item.is_gluten_free) tags.append(el("span", "tag tag-gold", "Gluten-free"));
    const body = el("div", "card-body");
    body.append(top, el("p", "desc", item.description), tags);
    card.append(banner, body);
    return card;
}
let allItems = [];
async function loadMenu() {
    const status = $("#menu-status");
    status.textContent = "Loading menu...";
    try {
        const res = await fetch(`${API}/menu`);
        if (!res.ok) throw new Error(`Server returned ${res.status}`);
        allItems = await res.json();
        status.textContent = "";
        renderFeatured();
        renderFilters();
        renderMenu("All");
    } catch (err) {
        console.error(err);
        status.textContent = "Sorry, we could not load the menu. Please refresh or try again later.";
    }
}
function renderFeatured() {
    $("#featured-grid").replaceChildren(...allItems.filter((i) => i.is_featured).map(buildCard));
}
function renderMenu(category) {
    const list = category === "All" ? allItems : allItems.filter((i) => i.category === category);
    $("#menu-grid").replaceChildren(...list.map(buildCard));
}
function renderFilters() {
    const bar = $("#filters");
    const categories = ["All", ...new Set(allItems.map((i) => i.category))];
    bar.replaceChildren(
        ...categories.map((cat) => {
            const btn = el("button", "filter-btn" + (cat === "All" ? " active" : ""), cat);
            btn.type = "button";
            btn.addEventListener("click", () => {
                bar.querySelectorAll(".filter-btn").forEach((b) => b.classList.remove("active"));
                btn.classList.add("active");
                renderMenu(cat);
            });
            return btn;
        })
    );
}
// Mobile navigation
$("#menu-toggle").addEventListener("click", () => $("#nav-links").classList.toggle("open"));
document.querySelectorAll("#nav-links a").forEach((a) =>
    a.addEventListener("click", () => $("#nav-links").classList.remove("open"))
);
loadMenu();