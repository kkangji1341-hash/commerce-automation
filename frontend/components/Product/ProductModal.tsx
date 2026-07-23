"use client";

import { useEffect } from "react";
import type { RecommendedProduct } from "@/lib/types";

const GRADE_BADGE: Record<string, string> = { GOLD: "🥇", SILVER: "🥈", BRONZE: "🥉" };

function currency(n: number) {
  return `₩${n.toLocaleString()}`;
}

function paybackLabel(months: number | null) {
  if (months === null) return "회수 불가";
  if (months < 1) return "1개월 이내";
  return `${months.toFixed(1)}개월`;
}

export default function ProductModal({
  product,
  onClose,
}: {
  product: RecommendedProduct;
  onClose: () => void;
}) {
  useEffect(() => {
    function onKeyDown(e: KeyboardEvent) {
      if (e.key === "Escape") onClose();
    }
    window.addEventListener("keydown", onKeyDown);
    return () => window.removeEventListener("keydown", onKeyDown);
  }, [onClose]);

  return (
    <div
      className="fixed inset-0 z-30 flex items-center justify-center bg-black/40 p-4"
      onClick={onClose}
    >
      <div
        className="max-h-[85vh] w-full max-w-lg overflow-y-auto rounded-2xl bg-white p-6 shadow-xl"
        onClick={(e) => e.stopPropagation()}
      >
        <div className="mb-4 flex items-start justify-between">
          <div>
            <span className="mb-1 inline-block rounded-full bg-amber-50 px-2 py-0.5 text-xs font-semibold text-amber-800">
              {GRADE_BADGE[product.grade] ?? ""} {product.grade}
            </span>
            <h2 className="text-lg font-bold text-gray-900">{product.product_name}</h2>
            <p className="text-xs text-gray-500">{product.grade_reason}</p>
          </div>
          <button
            onClick={onClose}
            className="flex h-11 w-11 shrink-0 items-center justify-center rounded-full text-gray-400 hover:bg-gray-100 hover:text-gray-600"
            aria-label="닫기"
          >
            ✕
          </button>
        </div>

        {product.is_estimated && (
          <p className="mb-4 rounded-lg bg-yellow-50 px-3 py-2 text-xs text-yellow-800">
            ⚠ 이 상품은 정식 소싱처 데이터가 아니라 네이버 판매가를 바탕으로 원가 등을 추정한
            결과입니다. 실제 사입을 진행하기 전에 반드시 소싱처를 직접 확인하세요.
          </p>
        )}

        <dl className="grid grid-cols-2 gap-y-3 text-sm">
          <dt className="text-gray-500">소싱처</dt>
          <dd className="text-right font-medium text-gray-900">{product.source_platform}</dd>

          <dt className="text-gray-500">원가{product.is_estimated && " (추정)"}</dt>
          <dd className="text-right font-medium text-gray-900">
            {currency(product.cost_price)}
          </dd>

          <dt className="text-gray-500">배송비</dt>
          <dd className="text-right font-medium text-gray-900">
            {currency(product.shipping_cost)}
          </dd>

          <dt className="text-gray-500">최소 주문 수량</dt>
          <dd className="text-right font-medium text-gray-900">
            {product.min_order_quantity.toLocaleString()}개
          </dd>

          <dt className="text-gray-500">배송 기간</dt>
          <dd className="text-right font-medium text-gray-900">{product.lead_time_days}일</dd>

          <dt className="text-gray-500">추천 판매가</dt>
          <dd className="text-right font-medium text-gray-900">
            {currency(product.recommended_selling_price)}
          </dd>

          <dt className="text-gray-500">단가 이익</dt>
          <dd className="text-right font-medium text-gray-900">
            {currency(product.profit_per_unit)} ({product.profit_margin_percent.toFixed(0)}%)
          </dd>

          <dt className="text-gray-500">예상 월판매</dt>
          <dd className="text-right font-medium text-gray-900">
            {product.estimated_monthly_sales.toLocaleString()}개
          </dd>

          <dt className="text-gray-500">예상 월매출</dt>
          <dd className="text-right font-medium text-gray-900">
            {currency(product.estimated_monthly_revenue)}
          </dd>

          <dt className="text-gray-500">예상 월이익</dt>
          <dd className="text-right font-medium text-gray-900">
            {currency(product.estimated_monthly_profit)}
          </dd>

          <dt className="text-gray-500">ROI</dt>
          <dd className="text-right font-medium text-primary-600">
            {product.roi_percent.toFixed(0)}%
          </dd>

          <dt className="text-gray-500">원금 회수 기간</dt>
          <dd className="text-right font-medium text-gray-900">
            {paybackLabel(product.payback_period_months)}
          </dd>

          <dt className="text-gray-500">위험도</dt>
          <dd className="text-right font-medium text-gray-900">{product.risk_level}</dd>

          <dt className="text-gray-500">판매자 경쟁도</dt>
          <dd className="text-right font-medium text-gray-900">{product.seller_competition_level}</dd>

          <dt className="text-gray-500">시장 포화도</dt>
          <dd className="text-right font-medium text-gray-900">{product.market_saturation_level}</dd>
        </dl>

        {product.risk_factors.length > 0 && (
          <div className="mt-4">
            <p className="mb-1.5 text-sm font-semibold text-gray-700">위험 요인</p>
            <ul className="flex flex-col gap-1 text-sm text-gray-600">
              {product.risk_factors.map((f, i) => (
                <li key={i} className="rounded-lg bg-red-50 px-3 py-1.5">
                  {f}
                </li>
              ))}
            </ul>
          </div>
        )}

        {product.recommendation_reasons.length > 0 && (
          <div className="mt-4">
            <p className="mb-1.5 text-sm font-semibold text-gray-700">추천 이유</p>
            <ul className="flex flex-col gap-1 text-sm text-gray-600">
              {product.recommendation_reasons.map((r, i) => (
                <li key={i} className="rounded-lg bg-gray-50 px-3 py-1.5">
                  {r}
                </li>
              ))}
            </ul>
          </div>
        )}
      </div>
    </div>
  );
}
