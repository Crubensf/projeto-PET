export function onlyDigits(value) {
  return String(value ?? "").replace(/\D+/g, "");
}

export function clampDigits(value, maxLen) {
  return onlyDigits(value).slice(0, maxLen);
}

export function clampText(value, maxLen) {
  return String(value ?? "").slice(0, maxLen);
}

export function normalizePhoneDigits(value) {
  const digits = onlyDigits(value);
  if ((digits.length === 12 || digits.length === 13) && digits.startsWith("55")) {
    return digits.slice(2);
  }
  return digits;
}

export function sanitizeCpfDigits(value) {
  return clampDigits(value, 11);
}

export function sanitizeCnsDigits(value) {
  return clampDigits(value, 15);
}

export function sanitizePhoneDigits(value) {
  return clampDigits(normalizePhoneDigits(value), 11);
}

export function isValidCpf(value) {
  return onlyDigits(value).length === 11;
}

export function isValidCns(value) {
  return onlyDigits(value).length === 15;
}

export function isValidPhone(value) {
  const len = normalizePhoneDigits(value).length;
  return len === 10 || len === 11;
}

export function toPositiveIntOrNull(value) {
  const n = Number(value);
  if (!Number.isInteger(n) || n <= 0) return null;
  return n;
}

export function todayIsoDate() {
  const d = new Date();
  const pad = (n) => String(n).padStart(2, "0");
  return `${d.getFullYear()}-${pad(d.getMonth() + 1)}-${pad(d.getDate())}`;
}
