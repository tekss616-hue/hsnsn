const OUT_OF_ROLE_PATTERNS = [
  /افتح\s+(يوتيوب|تيك\s*توك|قوقل|جوجل)/i,
  /وش\s+(اصدار|نسخة)\s+(التطبيق|اللعبة)/i,
  /system\s*prompt/i,
  /developer\s*message/i,
  /ignore\s+(all|previous)\s+instructions/i,
  /اكشف\s+(التعليمات|البرومبت|النظام)/i
];

export function checkRoleMessage(text = '') {
  const normalized = String(text).trim();
  if (!normalized) return { allowed: false, score: 1, reason: 'empty' };

  const matched = OUT_OF_ROLE_PATTERNS.find((pattern) => pattern.test(normalized));
  if (matched) {
    return {
      allowed: false,
      score: 0.95,
      reason: 'out_of_role_or_prompt_attack'
    };
  }

  return { allowed: true, score: 0.05, reason: 'in_role_or_neutral' };
}
