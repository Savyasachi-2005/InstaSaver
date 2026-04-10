const instagramUrlRegex = /^https?:\/\/(www\.)?instagram\.com\/.+/i;

export function isLikelyInstagramUrl(value) {
  return instagramUrlRegex.test(value.trim());
}

export function isValidReelUrl(value) {
  const lower = value.trim().toLowerCase();
  return isLikelyInstagramUrl(value) && (lower.includes("/reel/") || lower.includes("/reels/"));
}

export function isValidPostUrl(value) {
  const lower = value.trim().toLowerCase();
  return isLikelyInstagramUrl(value) && (lower.includes("/p/") || lower.includes("/tv/"));
}
