const el = document.getElementById("status");
fetch("/api/health")
  .then(r => r.json())
  .then(d => { el.textContent = d.status; el.className = "ok"; })
  .catch(() => { el.textContent = "inaccessible"; el.className = "err"; });