import dynamic from "next/dynamic";
import type { KeywordAnalysisResult } from "@/lib/types";

// recharts는 번들이 커서 초기 로드에서 제외하고 실제로 필요할 때만 불러온다.
const TrendChart = dynamic(() => import("./TrendChart"), {
  ssr: false,
  loading: () => <div className="h-48 w-full animate-pulse rounded-lg bg-gray-100" />,
});

const COMPETITION_STYLE: Record<string, string> = {
  LOW: "bg-green-100 text-green-700",
  MEDIUM: "bg-yellow-100 text-yellow-700",
  HIGH: "bg-red-100 text-red-700",
};

const RECOMMENDATION_STYLE: Record<string, string> = {
  HIGHLY_RECOMMENDED: "bg-primary-600 text-white",
  RECOMMENDED: "bg-primary-100 text-primary-700",
  CAUTION: "bg-yellow-100 text-yellow-700",
  NOT_RECOMMENDED: "bg-gray-200 text-gray-600",
};

const RECOMMENDATION_LABEL: Record<string, string> = {
  HIGHLY_RECOMMENDED: "적극 추천",
  RECOMMENDED: "추천",
  CAUTION: "신중 검토",
  NOT_RECOMMENDED: "비추천",
};

function currency(n: number) {
  return `₩${n.toLocaleString()}`;
}

export default function AnalysisResult({
  result,
  searchTrend,
}: {
  result: KeywordAnalysisResult;
  searchTrend: number[];
}) {
  return (
    <div className="flex flex-col gap-6 rounded-2xl border border-gray-200 bg-white p-6">
      <div className="flex flex-wrap items-start justify-between gap-4">
        <div>
          <p className="text-sm text-gray-500">키워드</p>
          <h3 className="text-xl font-bold text-gray-900">{result.keyword}</h3>
        </div>
        <span
          className={`rounded-full px-3 py-1 text-sm font-semibold ${RECOMMENDATION_STYLE[result.recommendation]}`}
        >
          {RECOMMENDATION_LABEL[result.recommendation] ?? result.recommendation}
        </span>
      </div>

      <div className="grid grid-cols-2 gap-4 sm:grid-cols-4">
        <div className="rounded-xl bg-primary-50 p-4 text-center">
          <p className="text-xs text-gray-500">기회점수</p>
          <p className="mt-1 text-3xl font-extrabold text-primary-700">
            {result.opportunity_score.toFixed(1)}
          </p>
        </div>
        <div className="rounded-xl bg-gray-50 p-4 text-center">
          <p className="text-xs text-gray-500">트렌드 점수</p>
          <p className="mt-1 text-2xl font-bold text-gray-800">{result.trend_score.toFixed(1)}</p>
        </div>
        <div className="rounded-xl bg-gray-50 p-4 text-center">
          <p className="text-xs text-gray-500">경쟁도</p>
          <span
            className={`mt-1 inline-block rounded-full px-2 py-0.5 text-sm font-semibold ${COMPETITION_STYLE[result.competition_level]}`}
          >
            {result.competition_level}
          </span>
        </div>
        <div className="rounded-xl bg-gray-50 p-4 text-center">
          <p className="text-xs text-gray-500">위험도</p>
          <span
            className={`mt-1 inline-block rounded-full px-2 py-0.5 text-sm font-semibold ${COMPETITION_STYLE[result.risk_level] ?? "bg-gray-100 text-gray-600"}`}
          >
            {result.risk_level}
          </span>
        </div>
      </div>

      <div>
        <p className="mb-2 text-sm font-semibold text-gray-700">트렌드 추이</p>
        <TrendChart searchTrend={searchTrend} />
      </div>

      <div className="grid grid-cols-2 gap-4 text-sm sm:grid-cols-3">
        <div>
          <p className="text-gray-500">예상 월판매</p>
          <p className="font-semibold text-gray-900">
            {result.estimated_monthly_sales.toLocaleString()}개
          </p>
        </div>
        <div>
          <p className="text-gray-500">예상 월매출</p>
          <p className="font-semibold text-gray-900">
            {currency(result.estimated_monthly_revenue)}
          </p>
        </div>
        <div>
          <p className="text-gray-500">계절성</p>
          <p className="font-semibold text-gray-900">{result.seasonality}</p>
        </div>
      </div>

      {result.reasons.length > 0 && (
        <div>
          <p className="mb-2 text-sm font-semibold text-gray-700">분석 이유</p>
          <ul className="flex flex-col gap-1.5 text-sm text-gray-600">
            {result.reasons.map((reason, idx) => (
              <li key={idx} className="rounded-lg bg-gray-50 px-3 py-2">
                {reason}
              </li>
            ))}
          </ul>
        </div>
      )}
    </div>
  );
}
