const API_BASE = import.meta.env.VITE_API_BASE_URL;

export async function apiGet(path) {
  const res = await fetch(`${API_BASE}${path}`);
  if (!res.ok) throw new Error("Erro na API");
  return res.json();
}

export async function apiPost(path, body) {
  const res = await fetch(`${API_BASE}${path}`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(body)
  });
  if (!res.ok) throw new Error("Erro na API");
  return res.json();
}

export async function apiPatch(path) {
  const res = await fetch(`${API_BASE}${path}`, {
    method: "PATCH"
  });
  if (!res.ok) throw new Error("Erro na API");
  return res.json();
}
