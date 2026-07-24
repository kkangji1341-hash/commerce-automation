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

// 아래 상수/계산식은 backend/app/services/calculation_service.py의
// _compute_financials()와 반드시 같아야 한다 — 실시간 미리보기가 저장 결과와
// 어긋나면 안 되기 때문. 값을 바꿀 땐 양쪽을 함께 수정할 것.
const STORE_FEE_RATE = 0.0563;
const SHIPPING_FEE_RATE = 0.0363;
const VAT_RATE = 0.1;

// product_recommendation_system.DEFAULT_COST_RATIO와 동일한 기본 원가율.
// "자동 조회"는 별도 API 호출 없이 이 비율을 그대로 재사용한 추정치다.
const AUTO_COST_RATIO = 0.35;

function currency(n: number) {
  return `₩${Math.round(n).toLocaleString()}`;
}

function roundTo10(n: number) {
  return Math.round(n / 10) * 10;
}

function CalculatorPageContent() {
  const { isReady } = useRequireAuth();
  const router = useRouter();
  const searchParams = useSearchParams();

  const [history, setHistory] = useState<KeywordAnalysisResult[]>([]);
  const [selectedId, setSelectedId] = useState<string>("manual");

  const [productName, setProductName] = useState("");
  const [cost, setCost] = useState<number>(0);
  const [costShipping, setCostShipping] = useState<number>(3000);
  const [sellingShipping, setSellingShipping] = useState<number>(3000);
  const [marginRate, setMarginRate] = useState<number>(0.15); // 0.15 = 15%
  const [adCost, setAdCost] = useState<number>(50);
  const [benefitsCost, setBenefitsCost] = useState<number>(0);
  const [showDetail, setShowDetail] = useState(false);

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
    if (item && !productName) setProductName(item.keyword);
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
    // 판매가는 원가 자체에만 마진율+부가세를 얹는다. 구입처 배송비는 판매가 산정에는
    // 관여하지 않고 최종 마진을 깎는 비용으로만 별도 반영한다.
    const sellingPrice = roundTo10(cost * (1 + marginRate) * (1 + VAT_RATE));
    const storeFee = sellingPrice * STORE_FEE_RATE;
    const shippingFee = sellingShipping * SHIPPING_FEE_RATE;
    const returnFee = sellingShipping * SHIPPING_FEE_RATE * 2;
    const vat = sellingPrice * VAT_RATE;
    const finalMargin = Math.round(
      sellingPrice - cost - costShipping - storeFee - shippingFee - returnFee - vat - adCost - benefitsCost
    );
    const finalMarginRate = sellingPrice > 0 ? finalMargin / sellingPrice : 0;
    return { sellingPrice, storeFee, shippingFee, returnFee, vat, finalMargin, finalMarginRate };
  }, [cost, costShipping, sellingShipping, marginRate, adCost, benefitsCost]);

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
        cost_shipping: costShipping,
        selling_shipping: sellingShipping,
        margin_rate: marginRate,
        ad_cost: adCost,
        benefits_cost: benefitsCost,
      });
      toast.success("이 상품을 저장했습니다");
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
          <p className="mt-1 text-sm text-gray-500">원가를 입력하면 판매가를 계산해드려요</p>
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
            키워드 선택 (히스토리에서 선택, 선택)
          </label>
          <select
            value={selectedId}
            onChange={(e) => applySelection(e.target.value)}
            className="min-h-[44px] w-full rounded-lg border border-gray-300 px-3 py-2 text-sm focus:border-primary-500 focus:outline-none focus:ring-1 focus:ring-primary-500"
          >
            <option value="manual">직접 입력</option>
            {history.map((h) => (
              <option key={h.id} value={h.id}>
                {h.keyword} · {new Date(h.created_at).toLocaleDateString()}
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
          </div>

          <div className="grid grid-cols-2 gap-4">
            <div>
              <label className="mb-1 block text-sm font-medium text-gray-700">구입처 배송비 (₩)</label>
              <input
                type="number"
                min={0}
                value={costShipping}
                onChange={(e) => setCostShipping(Number(e.target.value))}
                className="min-h-[44px] w-full rounded-lg border border-gray-300 px-3 py-2 text-sm focus:border-primary-500 focus:outline-none focus:ring-1 focus:ring-primary-500"
              />
            </div>
            <div>
              <label className="mb-1 block text-sm font-medium text-gray-700">판매 배송비 (₩)</label>
              <input
                type="number"
                min={0}
                value={sellingShipping}
                onChange={(e) => setSellingShipping(Number(e.target.value))}
                className="min-h-[44px] w-full rounded-lg border border-gray-300 px-3 py-2 text-sm focus:border-primary-500 focus:outline-none focus:ring-1 focus:ring-primary-500"
              />
            </div>
          </div>

          <div>
            <div className="mb-1 flex items-center justify-between">
              <label className="text-sm font-medium text-gray-700">마진율 조정</label>
              <span className="text-sm font-semibold text-primary-600">
                {Math.round(marginRate * 100)}%
              </span>
            </div>
            <input
              type="range"
              min={0}
              max={2}
              step={0.01}
              value={marginRate}
              onChange={(e) => setMarginRate(Number(e.target.value))}
              className="h-11 w-full"
            />
          </div>

          <div className="grid grid-cols-2 gap-4">
            <div>
              <label className="mb-1 block text-sm font-medium text-gray-700">
                광고비 (₩) <span className="text-gray-400">(선택)</span>
              </label>
              <input
                type="number"
                min={0}
                value={adCost}
                onChange={(e) => setAdCost(Number(e.target.value))}
                className="min-h-[44px] w-full rounded-lg border border-gray-300 px-3 py-2 text-sm focus:border-primary-500 focus:outline-none focus:ring-1 focus:ring-primary-500"
              />
            </div>
            <div>
              <label className="mb-1 block text-sm font-medium text-gray-700">
                스토어 혜택 (₩) <span className="text-gray-400">(선택)</span>
              </label>
              <input
                type="number"
                min={0}
                value={benefitsCost}
                onChange={(e) => setBenefitsCost(Number(e.target.value))}
                className="min-h-[44px] w-full rounded-lg border border-gray-300 px-3 py-2 text-sm focus:border-primary-500 focus:outline-none focus:ring-1 focus:ring-primary-500"
              />
            </div>
          </div>
        </div>
      </div>

      <div className="rounded-2xl border border-primary-100 bg-primary-50 p-6 text-center">
        <p className="text-xs text-gray-500">🎯 판매가 (마진율 {Math.round(marginRate * 100)}% + 부가세 10% 포함)</p>
        <p className="mt-1 text-4xl font-extrabold text-primary-700">{currency(preview.sellingPrice)}</p>

        <div className="mt-5 grid grid-cols-2 gap-4 border-t border-primary-100 pt-4 text-sm">
          <div>
            <p className="text-gray-500">최종 마진</p>
            <p className="text-lg font-bold text-gray-900">{currency(preview.finalMargin)}</p>
          </div>
          <div>
            <p className="text-gray-500">최종 마진율</p>
            <p className="text-lg font-bold text-gray-900">{(preview.finalMarginRate * 100).toFixed(1)}%</p>
          </div>
        </div>
      </div>

      <div className="rounded-2xl border border-gray-200 bg-white">
        <button
          type="button"
          onClick={() => setShowDetail((v) => !v)}
          className="flex min-h-[44px] w-full items-center justify-between px-5 text-sm font-medium text-gray-700"
        >
          세부 비용 확인
          <span>{showDetail ? "▲" : "▼"}</span>
        </button>
        {showDetail && (
          <dl className="grid grid-cols-2 gap-y-2 border-t border-gray-100 px-5 py-4 text-sm">
            <dt className="text-gray-500">원가</dt>
            <dd className="text-right text-gray-900">-{currency(cost)}</dd>

            <dt className="text-gray-500">구입처 배송비</dt>
            <dd className="text-right text-gray-900">-{currency(costShipping)}</dd>

            <dt className="text-gray-500">스토어 수수료 (5.63%)</dt>
            <dd className="text-right text-gray-900">-{currency(preview.storeFee)}</dd>

            <dt className="text-gray-500">배송비 연동 수수료 (3.63%)</dt>
            <dd className="text-right text-gray-900">-{currency(preview.shippingFee)}</dd>

            <dt className="text-gray-500">반품 배송비 수수료</dt>
            <dd className="text-right text-gray-900">-{currency(preview.returnFee)}</dd>

            <dt className="text-gray-500">부가세 (10%)</dt>
            <dd className="text-right text-gray-900">-{currency(preview.vat)}</dd>

            <dt className="text-gray-500">광고비</dt>
            <dd className="text-right text-gray-900">-{currency(adCost)}</dd>

            {benefitsCost > 0 && (
              <>
                <dt className="text-gray-500">스토어 혜택</dt>
                <dd className="text-right text-gray-900">-{currency(benefitsCost)}</dd>
              </>
            )}

            <dt className="pt-2 font-semibold text-gray-700">최종 마진</dt>
            <dd className="pt-2 text-right font-semibold text-primary-700">
              {currency(preview.finalMargin)}
            </dd>
          </dl>
        )}
      </div>

      {error && <ErrorMessage message={error} />}

      <Button onClick={handleSave} isLoading={isSaving} className="w-full">
        이 상품 저장
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
