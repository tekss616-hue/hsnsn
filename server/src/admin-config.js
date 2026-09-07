export const ADMIN_EMAIL = String(process.env.ADMIN_EMAIL || 'bajanznsb@gmail.com').trim().toLowerCase();

export function isAdminEmail(email) {
  return String(email || '').trim().toLowerCase() === ADMIN_EMAIL;
}
