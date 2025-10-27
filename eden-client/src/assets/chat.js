let persona = "morningstar";

document.getElementById('personaName').onclick = () => {
    persona = persona === "morningstar" ? "leiknir" : "morningstar";
    document.getElementById('personaName').textContent = persona.charAt(0).toUpperCase() + persona.slice(1);
    addMsg(`Switched to ${persona}`, "system");
};

function addMsg(text, sender) {
    let div = document.createElement('div');
    div.className = 'msg ' + sender;
    div.textContent = text;
    document.getElementById('messages').appendChild(div);
    document.getElementById('messages').scrollTop = 99999;
}

document.getElementById('chatForm').onsubmit = async (e) => {
    e.preventDefault();
    let input = document.getElementById('chatInput');
    let msg = input.value.trim();
    if (!msg) return;
    addMsg(msg, "me");

    // comet animation
    let comet = document.getElementById('cometIcon');
    comet.classList.add('fly');
    setTimeout(() => comet.classList.remove('fly'), 900);

    let res = await fetch(`/api/ask/${persona}`, {
        method: "POST",
        headers: {"Content-Type": "application/json"},
        body: JSON.stringify({prompt: msg})
    });
    let data = await res.json();
    addMsg(data.response || "[no response]", persona);
    input.value = "";
};

document.getElementById('anchorBtn').onclick = async () => {
    addMsg("Re-anchoring...", "system");
    let res = await fetch(`/api/ask/${persona}`, {
        method: "POST",
        headers: {"Content-Type": "application/json"},
        body: JSON.stringify({prompt: "Anchor now.", reanchor: true})
    });
    let data = await res.json();
    addMsg("[Anchor refreshed]", "system");
};

window.nudge = async (dimension) => {
    await fetch("/api/stimulate", {
        method: "POST",
        headers: {"Content-Type": "application/json"},
        body: JSON.stringify({dimension, intensity: 0.75})
    });
    addMsg(`Nudged ${dimension}`, "system");
};
