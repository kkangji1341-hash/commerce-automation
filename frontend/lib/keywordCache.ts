// 백엔드가 키워드 분석의 원본 입력값(search_trend, review_count_top_10 등)을
// 저장하지 않기 때문에, "히스토리에서 키워드 선택 -> 바로 상품 추천" 플로우를
// 위해 분석 성공 시 입력값을 localStorage에 캐싱해둔다.
import type { CachedKeywordInput, KeywordAnalysisInput } from "./types";

const CACHE_KEY = "keyword_input_cache";
const MAX_ENTRIES = 30;

function readCache(): CachedKeywordInput[] {
  if (typeof window === "undefined") return [];
  try {
    const raw = localStorage.getItem(CACHE_KEY);
    return raw ? (JSON.parse(raw) as CachedKeywordInput[]) : [];
  } catch {
    return [];
  }
}

export function cacheKeywordInput(analysisId: number, input: KeywordAnalysisInput) {
  const entries = readCache().filter((e) => e.analysisId !== analysisId);
  entries.unshift({ ...input, analysisId });
  localStorage.setItem(CACHE_KEY, JSON.stringify(entries.slice(0, MAX_ENTRIES)));
}

export function getCachedKeywordInput(analysisId: number): CachedKeywordInput | null {
  return readCache().find((e) => e.analysisId === analysisId) ?? null;
}
