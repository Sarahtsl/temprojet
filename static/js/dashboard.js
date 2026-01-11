// ===================== CONSTANTES =====================
const MIN_OK = 2;
const MAX_OK = 8;
const KEY_STATE = "dht_incident_state_v3";

// ===================== ÉTAT =====================
let state = {
  lastTimestamp: null,
  alertCounter: 0,
  op1: { ack:false, comment:"", savedAt:null, draft:"" },
  op2: { ack:false, comment:"", savedAt:null, draft:"" },
  op3: { ack:false, comment:"", savedAt:null, draft:"" },
};

// ===================== UTILS =====================
function $(id){ return document.getElementById(id); }

function loadState() {
  try {
    const s = localStorage.getItem(KEY_STATE);
    if (s) state = { ...state, ...JSON.parse(s) };
  } catch {}
}

function saveState() {
  localStorage.setItem(KEY_STATE, JSON.stringify(state));
}

function formatAge(sec) {
  sec = Math.max(0, sec);
  if (sec < 60) return sec + "s";
  if (sec < 3600) return Math.floor(sec/60) + "min";
  return Math.floor(sec/3600) + "h";
}

// ===================== OPÉRATEURS =====================
function renderOperator(op) {
  const operator = state[op];
  $(op+"_ack").checked = operator.ack;
  $(op+"_comment").value = operator.draft || operator.comment;
  $(op+"_status").textContent = operator.savedAt || "-";
  $(op+"_ack_status").textContent = operator.ack ? "Validé ✅" : "Non validé";
  $(op+"_show").textContent = operator.comment || "-";
}

function bindDraft(op) {
  $(op+"_comment").addEventListener("input", e => {
    state[op].draft = e.target.value;
    saveState();
  });
}

function bindSaveButton(op) {
  $(op+"_save").onclick = () => saveOperator(op);
}

function resetOperators() {
  ["op1","op2","op3"].forEach(op => {
    state[op] = { ack:false, comment:"", savedAt:null, draft:"" };
  });
}

// ===================== INCIDENT UI =====================
function setIncidentUI(isIncident) {
  $("incident-badge").textContent = isIncident ? "ALERTE" : "OK";
  $("incident-status").textContent = isIncident ? "Incident en cours" : "Pas d’incident";
  $("incident-counter").textContent = state.alertCounter;

  ["op1","op2","op3"].forEach(op => $(op).classList.add("hidden"));

  if (isIncident) {
    if (state.alertCounter > 0) $("op1").classList.remove("hidden");
    if (state.alertCounter > 3) $("op2").classList.remove("hidden");
    if (state.alertCounter > 6) $("op3").classList.remove("hidden");
  }

  renderOperator("op1");
  renderOperator("op2");
  renderOperator("op3");
}

// ===================== API =====================
function getCSRFToken() {
  const meta = document.querySelector("meta[name='csrf-token']");
  return meta ? meta.getAttribute("content") : "";
}
async function saveOperator(op) {
  const ack = $(op+"_ack").checked;
  const comment = $(op+"_comment").value;
  const opNum = parseInt(op.replace("op",""));

  const res = await fetch("/incident/update/", {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
      "X-CSRFToken": getCSRFToken()
    },
    body: JSON.stringify({
      op: opNum,
      ack: ack,
      comment: comment,
      close: true   // <-- on clôture l'incident après validation
    })
  });

  const data = await res.json();

  if (!res.ok) {
    if(data.error === "no active incident") {
      alert("⚠ Aucun incident actif");
    } else {
      console.error("❌ Erreur serveur", op, data);
    }
    return;
  }

  state[op].ack = ack;
  state[op].comment = comment;
  state[op].savedAt = new Date().toLocaleString();
  state[op].draft = "";
  saveState();
  renderOperator(op);

  // Message de confirmation
  alert("✅ Commentaire enregistré et incident clôturé !");
}

// ===================== DATA =====================
async function loadLatest() {
  const res = await fetch("/api/");
  const data = await res.json();

  if (!Array.isArray(data) || data.length === 0) return;

  const last = data[0]; // dernière mesure

  $("temp").textContent = last.temperature.toFixed(1) + " °C";
  $("hum").textContent  = last.humidity.toFixed(1) + " %";

  const date = new Date(last.created_at);
  const diff = Math.floor((Date.now() - date) / 1000);

  $("temp-time").textContent = formatAge(diff);
  $("hum-time").textContent  = formatAge(diff);

  // gestion incident
  const isIncident = last.temperature < MIN_OK || last.temperature > MAX_OK;

  if (last.created_at !== state.lastTimestamp) {
    state.lastTimestamp = last.created_at;

    if (isIncident) {
        state.alertCounter += 1; // compteur pour le nouvel incident
        resetOperators();
    } else {
        state.alertCounter = 0;
        resetOperators();
    }

    saveState();
  }

  setIncidentUI(isIncident);
}

// ===================== INIT =====================
loadState();
["op1","op2","op3"].forEach(op => {
  bindDraft(op);
  bindSaveButton(op);
});
loadLatest();
setInterval(loadLatest, 5000);
