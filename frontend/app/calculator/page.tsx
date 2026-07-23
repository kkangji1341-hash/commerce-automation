"use client";

import { Suspense, useEffect, useMemo, useState } from "react";
import Link from "next/link";
import { useRouter, useSearchParams } from "next/navigation";
import toast from "react-hot-toast";
import Button from "@/components/Common/Button";
import Loading from "@/components/Common/Loading";
import ErrorMessage from "@/components/Common/Error";
import { createCalculation, getKeywordHistory } from "@/lib/api";
import { getErrorMessage } from "@/lib/errors";
import { useRequireAuth } from "@/lib/useRequireAuth";
import type { KeywordAnalysisResult } from "@/lib/types";

// 백엔드 calculation_service.SALES_CONVERSION_RATE와 반드시 같은 값이어야
// 실시간 미리보기와 저장 결과가 일치한다.
const SALES_CONVERSION_RATE = 0.05;
// product_recommendation_system.DEFAULT_COST_RATIO와 동일한 기본 원가율.
// "자동 조회"는 별도 API 호출 없이 이 비율을 그대로 재사용한 추정치다.
const AUTO_COST_RATIO = 0.35;

function currency(n: number) {
  return `₩${Math.round(n).toLocaleString()}`;
}

function CalculatorPageContent() {
  const { isReady } = useRequireAuth();
  const router = useRouter();
  const searchParams = useSearchParams();

  const [history, setHistory] = useState<KeywordAnalysisResult[]>([]);
  const [selectedId, setSelectedId] = useState<string>("manual");

  const [productName, setProductName] = useState("");
  const [cost, setCost] = useState<number>(0);
  const [shippingCost, setShippingCost] = useState<number>(0);
  const [marginRate, setMarginRate] = useState<number>(1.0); // 1.0 = 100%
  const [monthlySearches, setMonthlySearches] = useState<number>(0);

  const [isSaving, setIsSaving] = useState(false);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    if (!isReady) return;
    getKeywordHistory()
      .then((res) => setHistory(res.items))
      .catch(() => {});
  }, [isReady]);

  useEffect(() => {
    const keywordId = searchParams.get("keywordId");
    if (keywordId) applySelection(keywordId);
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [searchParams, history]);

  function applySelection(id: string) {
    setSelectedId(id);
    if (id === "manual") return;
    const item = history.find((h) => String(h.id) === id);
    if (item) {
      setMonthlySearches(item.monthly_searches);
      if (!productName) setProductName(item.keyword);
    }
  }

  const selectedAnalysis = history.find((h) => String(h.id) === selectedId) ?? null;

  function autoLookupCost() {
    if (!selectedAnalysis) {
      toast.error("먼저 키워드를 선택해주세요");
      return;
    }
    const estimated = Math.max(1, Math.round(selectedAnalysis.avg_selling_price * AUTO_COST_RATIO));
    setCost(estimated);
    toast.success(`평균 판매가(${currency(selectedAnalysis.avg_selling_price)}) 기준 원가율 35% 추정치를 채웠습니다`);
  }

  const preview = useMemo(() => {
    const sellingPrice = Math.round(cost * (1 + marginRate));
    const monthlySalesEstimate = Math.round(monthlySearches * SALES_CONVERSION_RATE);
    const monthlyRevenue = sellingPrice * monthlySalesEstimate;
    const unitProfit = sellingPrice - cost - shippingCost;
    const monthlyProfit = unitProfit * monthlySalesEstimate;
    const roiPercent = cost > 0 ? (unitProfit / cost) * 100 : 0;
    return { sellingPrice, monthlySalesEstimate, monthlyRevenue, monthlyProfit, roiPercent, unitProfit };
  }, [cost, shippingCost, marginRate, monthlySearches]);

  async function handleSave() {
    if (!productName.trim()) {
      toast.error("상품명을 입력해주세요");
      return;
    }
    if (cost <= 0) {
      toast.error("원가를 입력해주세요");
      return;
    }
    setIsSaving(true);
    setError(null);
    try {
      await createCalculation({
        keyword_analysis_id: selectedAnalysis?.id ?? null,
        product_name: productName.trim(),
        cost,
        shipping_cost: shippingCost,
        margin_rate: marginRate,
        monthly_searches: monthlySearches,
      });
      toast.success("마진 계산 결과를 저장했습니다");
      router.push("/my-calculations");
    } catch (err) {
      setError(getErrorMessage(err, "저장에 실패했습니다"));
    } finally {
      setIsSaving(false);
    }
  }

  if (!isReady) return <Loading />;

  return (
    <div className="mx-auto flex max-w-2xl flex-col gap-6 p-4 sm:p-6">
      <div className="flex items-start justify-between gap-2">
        <div>
          <h1 className="text-2xl font-bold text-gray-900">마진 계산기</h1>
          <p className="mt-1 text-sm text-gray-500">
            원가와 마진율을 입력하면 판매가·예상 이익·ROI를 바로 계산해드려요
          </p>
        </div>
        <Link
          href="/my-calculations"
          className="flex min-h-[44px] shrink-0 items-center text-xs font-medium text-primary-600 hover:underline"
        >
          저장한 계산 보기 →
        </Link>
      </div>

      <div className="rounded-2xl border border-gray-200 bg-white p-6">
        <div className="mb-5">
          <label className="mb-1 block text-sm font-medium text-gray-700">
            키워드 선택 (히스토리에서 선택)
          </label>
          <select
            value={selectedId}
            onChange={(e) => applySelection(e.target.value)}
            className="min-h-[44px] w-full rounded-lg border border-gray-300 px-3 py-2 text-sm focus:border-primary-500 focus:outline-none focus:ring-1 focus:ring-primary-500"
          >
            <option value="manual">직접 입력</option>
            {history.map((h) => (
              <option key={h.id} value={h.id}>
                {h.keyword} (월 검색량 {h.monthly_searches.toLocaleString()}) ·{" "}
                {new Date(h.created_at).toLocaleDateString()}
              </option>
            ))}
          </select>
        </div>

        <div className="flex flex-col gap-4">
          <div>
            <label className="mb-1 block text-sm font-medium text-gray-700">상품명</label>
            <input
              value={productName}
              onChange={(e) => setProductName(e.target.value)}
              placeholder="예: 프리미엄 무선 이어폰"
              className="min-h-[44px] w-full rounded-lg border border-gray-300 px-3 py-2 text-sm focus:border-primary-500 focus:outline-none focus:ring-1 focus:ring-primary-500"
            />
          </div>

          <div>
            <label className="mb-1 block text-sm font-medium text-gray-700">원가 (₩)</label>
            <div className="flex gap-2">
              <input
                type="number"
                min={0}
                value={cost || ""}
                onChange={(e) => setCost(Number(e.target.value))}
                className="min-h-[44px] w-full rounded-lg border border-gray-300 px-3 py-2 text-sm focus:border-primary-500 focus:outline-none focus:ring-1 focus:ring-primary-500"
              />
              <Button type="button" variant="secondary" onClick={autoLookupCost} className="shrink-0 whitespace-nowrap">
                자동 조회
              </Button>
            </div>
            <p className="mt-1 text-[11px] text-gray-400">
              자동 조회는 선택한 키워드의 네이버 평균 판매가 × 35%(가정)로 원가를 추정합니다. 실제 소싱
              원가로 반드시 확인 후 사용하세요.
            </p>
          </div>

          <div>
            <label className="mb-1 block text-sm font-medium text-gray-700">배송료 (₩)</label>
            <input
              type="number"
              min={0}
              value={shippingCost || ""}
              onChange={(e) => setShippingCost(Number(e.target.value))}
              className="min-h-[44px] w-full rounded-lg border border-gray-300 px-3 py-2 text-sm focus:border-primary-500 focus:outline-none focus:ring-1 focus:ring-primary-500"
            />
          </div>

          <div>
            <div className="mb-1 flex items-center justify-between">
              <label className="text-sm font-medium text-gray-700">마진율</label>
              <span className="text-sm font-semibold text-primary-600">
                {Math.round(marginRate * 100)}%
              </span>
            </div>
            <input
              type="range"
              min={0}
              max={5}
              step={0.05}
              value={marginRate}
              onChange={(e) => setMarginRate(Number(e.target.value))}
              className="h-11 w-full"
            />
          </div>

          <div>
            <label className="mb-1 block text-sm font-medium text-gray-700">월간 검색량</label>
            <input
              type="number"
              min={0}
              value={monthlySearches || ""}
              onChange={(e) => setMonthlySearches(Number(e.target.value))}
              className="min-h-[44px] w-full rounded-lg border border-gray-300 px-3 py-2 text-sm focus:border-primary-500 focus:outline-none focus:ring-1 focus:ring-primary-500"
            />
            <p className="mt-1 text-[11px] text-gray-400">
              예상 월판매량 = 월간 검색량 × {SALES_CONVERSION_RATE * 100}%
            </p>
          </div>
        </div>
      </div>

      <div className="rounded-2xl border border-primary-100 bg-primary-50 p-6">
        <h2 className="mb-4 text-sm font-semibold text-gray-700">실시간 계산 결과</h2>
        <dl className="grid grid-cols-2 gap-y-3 text-sm">
          <dt className="text-gray-500">판매가</dt>
          <dd className="text-right font-semibold text-gray-900">{currency(preview.sellingPrice)}</dd>

          <dt className="text-gray-500">예상 월판매</dt>
          <dd className="text-right font-semibold text-gray-900">
            {preview.monthlySalesEstimate.toLocaleString()}개
          </dd>

          <dt className="text-gray-500">월매출</dt>
          <dd className="text-right font-semibold text-gray-900">{currency(preview.monthlyRevenue)}</dd>

          <dt className="text-gray-500">단가 이익</dt>
          <dd className="text-right font-semibold text-gray-900">{currency(preview.unitProfit)}</dd>

          <dt className="text-gray-500">월이익 (순이익)</dt>
          <dd className="text-right text-lg font-bold text-primary-700">
            {currency(preview.monthlyProfit)}
          </dd>

          <dt className="text-gray-500">ROI</dt>
          <dd className="text-right text-lg font-bold text-primary-700">
            {preview.roiPercent.toFixed(0)}%
          </dd>
        </dl>
      </div>

      {error && <ErrorMessage message={error} />}

      <Button onClick={handleSave} isLoading={isSaving} className="w-full">
        저장
      </Button>
    </div>
  );
}

export default function CalculatorPage() {
  return (
    <Suspense fallback={<Loading />}>
      <CalculatorPageContent />
    </Suspense>
  );
}
