const API_URL = "http://127.0.0.1:8000/api/chat";
const form = document.querySelector("#chat-form");
const input = document.querySelector("#message");
const messages = document.querySelector("#messages");
const send = document.querySelector("#send");

function addMessage(text, role, sources = []) {
  const wrap = document.createElement("div");
  const bubble = document.createElement("div");
  bubble.className = `bubble ${role}`;
  bubble.textContent = text;
  wrap.appendChild(bubble);
  if (sources.length) {
    const source = document.createElement("div");
    source.className = "sources";
    source.textContent = "Sumber: " + sources.join(", ");
    wrap.appendChild(source);
  }
  messages.appendChild(wrap);
  messages.scrollTop = messages.scrollHeight;
}

async function ask(question) {
  const message = question.trim();
  if (!message) return;
  addMessage(message, "user");
  input.value = "";
  send.disabled = true;
  send.textContent = "...";
  const pending = document.createElement("div");
  pending.className = "bubble bot";
  pending.textContent = "Sedang mencari informasi...";
  messages.appendChild(pending);
  try {
    const response = await fetch(API_URL, {
      method: "POST",
      headers: {"Content-Type": "application/json"},
      body: JSON.stringify({message})
    });
    const data = await response.json();
    if (!response.ok) throw new Error(data.detail || "Terjadi kesalahan pada server.");
    pending.remove();
    addMessage(data.answer, "bot", data.sources || []);
  } catch (error) {
    pending.remove();
    addMessage("Maaf, layanan belum dapat dihubungi. Pastikan backend aktif dan API key Gemini sudah diatur. Detail: " + error.message, "bot");
  } finally {
    send.disabled = false;
    send.textContent = "Kirim";
    input.focus();
  }
}

form.addEventListener("submit", event => {
  event.preventDefault();
  ask(input.value);
});
document.querySelectorAll("[data-question]").forEach(button => {
  button.addEventListener("click", () => ask(button.dataset.question));
});
