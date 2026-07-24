"use client";

import { useState } from "react";
import { useRouter } from "next/navigation";
import toast from "react-hot-toast";
import Button from "@/components/Common/Button";
import { analyzeAndGenerate, createCalculation, fetchKeywordAuto } from "@/lib/api";
import { getErrorMessage } from "@/lib/errors";
import type { AnalyzeAndGenerateResponse } from "@/lib/types";

const COMPETITION_STYLE: Record<string, string> = {
  LOW: "bg-green-100 text-green-700",
  MEDIUM: "bg-yellow-100 text-yellow-700",
  HIGH: "bg-red-100 text-red-700",
};

// 마진 계산기 기본값 — /calculator의 "자동 조회"와 동일한 원가율(35%)과
// 기본 마진율(15%)을 그대로 재사용한다.
const AUTO_COST_RATIO = 0.35;
const DEFAULT_MARGIN_RATE = 0.15;
const DEFAULT_COST_FALLBACK = 10000; // 네이버 평균가 조회 실패 시에만 사용하는 최후 기본값

export default function VariantExplorer() {
  const router = useRouter();
  const [keyword, setKeyword] = useState("");
  const [isLoading, setIsLoading] = useState(false);
  const [result, setResult] = useState<AnalyzeAndGenerateResponse | null>(null);
  const [isSaving, setIsSaving] = useState(false);

  async function handleAnalyze() {
    if (!keyword.trim()) {
      toast.error("메인 키워드를 입력해주세요");
      return;
    }
    setIsLoading(true);
    setResult(null);
    try {
      const res = await analyzeAndGenerate(keyword.trim());
      if (res.top_variants.length === 0) {
        toast.error("이 키워드로는 세부 키워드를 찾지 못했습니다. 다른 키워드로 시도해보세요");
        return;
      }
      setResult(res);
    } catch (err) {
      toast.error(getErrorMessage(err, "세부 키워드 분석에 실패했습니다"));
    } finally {
      setIsLoading(false);
    }
  }

  async function handleCalculateFinalTitle() {
    if (!result) return;
    setIsSaving(true);
    try {
      let cost = DEFAULT_COST_FALLBACK;
      try {
        const auto = await fetchKeywordAuto(result.main_keyword);
        if (auto.avg_price) cost = Math.max(1, Math.round(auto.avg_price * AUTO_COST_RATIO));
      } catch {
        // 원가 자동조회 실패해도 기본값으로 계속 진행 (전체 흐름을 막지 않음)
      }
      await createCalculation({
        product_name: result.final_title,
        cost,
        cost_shipping: 3000,
        selling_shipping: 3000,
        margin_rate: DEFAULT_MARGIN_RATE,
        ad_cost: 50,
        benefits_cost: 0,
      });
      toast.success("마진 계산을 저장했습니다");
      router.push("/my-calculations");
    } catch (err) {
      toast.error(getErrorMessage(err, "마진 계산 저장 중 오류가 발생했습니다"));
    } finally {
      setIsSaving(false);
    }
  }

  return (
    <div className="rounded-2xl border border-gray-200 bg-white p-6">
      <h2 className="mb-1 text-sm font-semibold text-gray-700">
        빠른 상품명 발굴 (검색량 + 클릭률 기반)
      </h2>
      <p className="mb-4 text-xs text-gray-500">
        메인 키워드 하나만 입력하면 네이버 검색광고 데이터에서 실제 세부 키워드를 찾아 경쟁력
        순위를 매기고, 상품명 후보를 자동 생성합니다.
      </p>

      <div className="flex gap-2">
        <input
          value={keyword}
          onChange={(e) => setKeyword(e.target.value)}
          placeholder="예: 우산"
          className="min-h-[44px] w-full rounded-lg border border-gray-300 px-3 py-2 text-sm focus:border-primary-500 focus:outline-none focus:ring-1 focus:ring-primary-500"
        />
        <Button type="button" isLoading={isLoading} onClick={handleAnalyze} className="shrink-0 whitespace-nowrap">
          세부 키워드 분석
        </Button>
      </div>

      {result && (
        <div className="mt-5 flex flex-col gap-4">
          <div className="overflow-x-auto rounded-xl border border-gray-200">
            <table className="w-full min-w-[520px] text-sm">
              <thead className="bg-gray-50 text-left text-xs text-gray-500">
                <tr>
                  <th className="px-3 py-2">순위</th>
                  <th className="px-3 py-2">세부 키워드</th>
                  <th className="px-3 py-2">검색량</th>
                  <th className="px-3 py-2">클릭률</th>
                  <th className="px-3 py-2">경쟁도</th>
                  <th className="px-3 py-2">점수</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-gray-100">
                {result.top_variants.map((v, i) => (
                  <tr key={v.keyword}>
                    <td className="px-3 py-2 text-gray-400">{i + 1}</td>
                    <td className="px-3 py-2 font-medium text-gray-900">{v.keyword}</td>
                    <td className="px-3 py-2 text-gray-600">{v.monthly_searches.toLocaleString()}</td>
                    <td className="px-3 py-2 text-gray-600">{v.click_rate.toFixed(2)}%</td>
                    <td className="px-3 py-2">
                      <span
                        className={`rounded-full px-2 py-0.5 text-xs font-semibold ${COMPETITION_STYLE[v.competition] ?? "bg-gray-100 text-gray-600"}`}
                      >
                        {v.competition}
                      </span>
                    </td>
                    <td className="px-3 py-2 text-gray-600">{v.score.toFixed(1)}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
          <p className="text-[11px] text-gray-400">
            점수 = (검색량×0.6) + (클릭률×0.4) − 경쟁도 페널티. 절대값보다 상대 순위로 보세요 —
            경쟁이 있는 카테고리는 음수가 나올 수 있습니다.
          </p>

          <div>
            <p className="mb-2 text-sm font-semibold text-gray-700">
              생성된 상품명 후보 {result.total_candidates_generated}개 (상위 6개 선택됨)
            </p>
            <div className="grid grid-cols-1 gap-1 sm:grid-cols-2">
              {result.all_candidates.map((c) => {
                const isSelected = result.top_candidates.some(
                  (t) => t.variant === c.variant && t.modifier === c.modifier
                );
                return (
                  <div
                    key={`${c.variant}-${c.modifier}`}
                    className={`flex min-h-[36px] items-center gap-2 rounded-lg px-3 ${
                      isSelected ? "bg-primary-50 text-primary-900" : "bg-gray-50 text-gray-500"
                    }`}
                  >
                    <span className={isSelected ? "text-primary-500" : "text-gray-300"}>
                      {isSelected ? "✓" : "·"}
                    </span>
                    <span className="text-sm">{c.name}</span>
                  </div>
                );
              })}
            </div>
          </div>

          <div className="rounded-xl border border-primary-100 bg-primary-50 p-4 text-center">
            <p className="text-xs text-gray-500">🎯 최종 상품명 (중복 단어 자동 제거)</p>
            <p className="mt-1 text-lg font-bold text-primary-700">{result.final_title}</p>
          </div>

          <Button onClick={handleCalculateFinalTitle} isLoading={isSaving} className="w-full">
            이 제목으로 마진계산하기
          </Button>
        </div>
      )}
    </div>
  );
}
