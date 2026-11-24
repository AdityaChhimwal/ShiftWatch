"use strict";
const el = id => document.getElementById(id);
let session, report, selected, busy = false;

async function request(path, data, download) {
  const headers = session && path.startsWith("/sessions/") ? {Authorization: "Bearer " + session.token} : {};
  if (data !== undefined) headers["Content-Type"] = "application/json";
  const response = await fetch(path, {method: data === undefined ? "GET" : "POST", headers,
    body: data === undefined ? undefined : JSON.stringify(data)});
  if (!response.ok) {
    const error = await response.json().catch(() => ({}));
    throw new Error(typeof error.detail === "string" ? error.detail : "Request failed (" + response.status + ")");
  }
  return download ? response.blob() : response.json();
}

const path = suffix => "/sessions/" + session.session_id + "/" + suffix;
const format = value => value == null ? "—" : value.toFixed(1);
const percent = value => value == null ? "—" : Math.round(value * 100) + "%";
const text = (id, value) => { el(id).textContent = value; };
function signal(id, value, detail, alert) {
  text(id, value);
  el(id).classList.toggle("alarm", Boolean(alert));
  text(id + "-detail", detail);
}

function draw() {
  const custom = report.mode === "custom";
  const done = !custom && report.step >= report.total_steps;
  el("dashboard").hidden = false;
  el("custom").hidden = !custom;
  el("next").hidden = el("run").hidden = custom || done;
  text("progress", custom ? report.step + " / 24 batches submitted"
    : report.step + " / " + report.total_steps + " replay steps · " + report.policy.name + " · two-batch label delay");
  text("next", report.step >= 24 ? "Release remaining labels" : "Next step");
  el("incident").hidden = !done;
  if (done) text("incident", report.incident
    ? "Replay truth · " + report.incident.channel + " incident injected in batches " +
      report.incident.first_batch + "–" + report.incident.last_batch + "."
    : "Replay truth · no incident injected.");
  let batch = report.timeline.find(row => row.batch_id === selected);
  if (!batch) batch = report.timeline.at(-1);
  if (batch) {
    const {quality: q, distribution: d, performance: p} = batch;
    signal("quality", q.alert ? "Invalid rows found" : "Rows accepted",
      q.accepted + " of " + q.submitted + " accepted · batch " + batch.batch_id, q.alert);
    signal("distribution", d.alert ? "Change flagged" : d.eligible ? "No alert" : "Insufficient data",
      d.features.length ? d.features.join(", ") : report.policy.name + " · batch " + batch.batch_id, d.alert);
    signal("performance", p.status === "unknown" ? "Performance unknown" : p.alert ? "Elevated error" : "MAE " + format(p.mae),
      p.labeled + " / " + p.predictions + " labels · RMSE " + format(p.rmse) + " · " + p.status, p.alert);
    text("details", JSON.stringify({quality: q, distribution: d, performance: p}, null, 2));
  } else {
    signal("quality", "Awaiting a batch", "Row validation appears here.");
    signal("distribution", "Insufficient data", "Submit a batch to compare it with a reference.");
    signal("performance", "Performance unknown", "0 labels received.");
    text("details", "");
  }
  el("diagnostics").hidden = !batch;
  el("timeline").replaceChildren(...report.timeline.map(row => {
    const tr = document.createElement("tr");
    tr.classList.toggle("selected", row === batch);
    const td = tr.insertCell();
    const button = document.createElement("button");
    button.type = "button";
    button.className = "secondary";
    button.textContent = row.batch_id;
    button.setAttribute("aria-pressed", String(row === batch));
    button.onclick = () => { selected = row.batch_id; draw(); el("timeline").querySelector("[aria-pressed=true]")?.focus(); };
    td.append(button);
    for (const value of [row.quality.rejected + " rejected",
      row.distribution.alert ? "Alert" : row.distribution.eligible ? "No alert" : "Insufficient",
      percent(row.performance.coverage), format(row.performance.mae)]) tr.insertCell().textContent = value;
    return tr;
  }));
}

async function run(action) {
  if (busy) return;
  busy = true;
  const controls = [...document.querySelectorAll("button, select, input")].filter(control => !control.disabled);
  controls.forEach(control => { control.disabled = true; });
  el("notice").classList.remove("error");
  text("notice", "Working…");
  try {
    const message = await action();
    text("notice", message || "");
  } catch (error) {
    el("notice").classList.add("error");
    text("notice", error.message);
  } finally {
    controls.forEach(control => { control.disabled = false; });
    busy = false;
  }
}

function csvRecords(source) {
  const records = [];
  let record = [], field = "", quoted = false, closed = false;
  source = source.replace(/^\uFEFF/, "");
  for (let i = 0; i < source.length; i++) {
    const char = source[i];
    if (quoted) {
      if (char !== '"') field += char;
      else if (source[i + 1] === '"') { field += '"'; i++; }
      else { quoted = false; closed = true; }
    } else if (char === "," || char === "\n" || char === "\r") {
      record.push(field); field = ""; closed = false;
      if (char !== ",") {
        records.push(record); record = [];
        if (char === "\r" && source[i + 1] === "\n") i++;
      }
    } else if (char === '"' && field === "" && !closed) quoted = true;
    else if (closed || char === '"') throw new Error("Malformed quoted CSV field.");
    else field += char;
  }
  if (quoted) throw new Error("Unclosed CSV quote.");
  if (record.length || field || closed) records.push([...record, field]);
  return records;
}

async function upload(id, columns) {
  const file = el(id).files[0];
  if (!file || file.size > 256000) throw new Error("Choose a CSV smaller than 256 KB.");
  const [head, ...records] = csvRecords(await file.text());
  if (!head || head.length !== columns.length || new Set(head).size !== head.length ||
      !columns.every(name => head.includes(name))) throw new Error("CSV headers must match the template.");
  if (!records.length || records.length > 500) throw new Error("Send 1 to 500 CSV rows.");
  return records.map((row, index) => {
    if (row.length !== head.length) throw new Error("Wrong column count in row " + (index + 2) + ".");
    return Object.fromEntries(head.map((name, i) => {
      const raw = row[i];
      if (name === "record_id" || name === "event_time") return [name, raw];
      const number = raw.trim() === "" ? null : Number(raw);
      return [name, Number.isFinite(number) ? number : null];
    }));
  });
}

el("start").onsubmit = event => {
  event.preventDefault();
  run(async () => {
    const mode = el("mode").value;
    session = await request("/sessions", {mode});
    selected = null;
    report = await request(path("report"));
    text("session-title", el("mode").selectedOptions[0].textContent);
    draw();
  });
};

async function step() {
  report = await request(path("step"), {step: report.step});
  selected = null;
  draw();
}
el("next").onclick = () => run(step);
el("run").onclick = () => run(async () => {
  while (report.step < report.total_steps) {
    await step();
    text("notice", "Replay step " + report.step + " of " + report.total_steps);
  }
});
el("batch-form").onsubmit = event => {
  event.preventDefault();
  run(async () => {
    const rows = await upload("batch-file", ["record_id", "event_time", "hr", "weekday", "workingday", "mnth", "temp", "hum", "windspeed", "weathersit"]);
    report = await request(path("batches"), {batch_id: el("batch-id").value, rows});
    selected = el("batch-id").value;
    el("batch-id").value = "batch-" + (report.step + 1);
    draw();
  });
};
el("label-form").onsubmit = event => {
  event.preventDefault();
  run(async () => {
    const rows = await upload("label-file", ["record_id", "cnt"]);
    report = await request(path("labels"), {rows});
    draw();
    return report.new_labels + " new labels attached.";
  });
};
for (const type of ["json", "csv"]) {
  el("export-" + type).onclick = () => run(async () => {
    const blob = await request(path("export?format=" + type), undefined, true);
    const url = URL.createObjectURL(blob);
    const link = document.createElement("a");
    link.href = url;
    link.download = "shiftwatch." + type;
    link.click();
    setTimeout(() => URL.revokeObjectURL(url), 1000);
  });
}
run(async () => {
  const items = await request("/scenarios");
  for (const item of items.reverse()) el("mode").prepend(new Option(item.title, item.id));
  el("mode").value = "stable";
});
