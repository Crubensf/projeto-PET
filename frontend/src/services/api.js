const API_ORIGIN = "";

function buildUrl(path) {
  if (typeof path !== "string" || !path.trim()) {
    throw new Error(`apiFetch: path inválido (${String(path)})`);
  }

  if (/^https?:\/\//i.test(path)) return path;

  const normalizedPath = path.startsWith("/") ? path : `/${path}`;

  if (!API_ORIGIN) return normalizedPath;

  return new URL(normalizedPath, API_ORIGIN).toString();
}

export async function apiFetch(path, options = {}) {
  const url = buildUrl(path);

  const res = await fetch(url, {
    headers: {
      "Content-Type": "application/json",
      ...(options.headers || {}),
    },
    ...options,
  });

  if (!res.ok) {
    let message = `Erro ${res.status}`;

    try {
      const data = await res.json();
      if (data?.detail) {
        message = typeof data.detail === "string" ? data.detail : JSON.stringify(data.detail);
      } else if (data?.message) {
        message = data.message;
      }
    } catch {
      // sem body JSON
    }

    throw new Error(message);
  }

  if (res.status === 204) return null;
  return res.json();
}

export const api = {
  get: (p) => apiFetch(p),
  post: (p, body) => apiFetch(p, { method: "POST", body: JSON.stringify(body) }),
  put: (p, body) => apiFetch(p, { method: "PUT", body: JSON.stringify(body) }),
  patch: (p, body) => apiFetch(p, { method: "PATCH", body: JSON.stringify(body) }),
  del: (p) => apiFetch(p, { method: "DELETE" }),
};

export default api;
