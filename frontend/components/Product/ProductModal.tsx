"use client";

import { useEffect } from "react";
import type { RecommendedProduct } from "@/lib/types";

function currency(n: number) {
  return `₩${n.toLocaleString()}`;
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
          <h2 className="text-lg font-bold text-gray-900">{product.product_name}</h2>
          <button
            onClick={onClose}
            className="rounded-full p-1 text-gray-400 hover:bg-gray-100 hover:text-gray-600"
            aria-label="닫기"
          >
            ✕
          </button>
        </div>

        <dl className="grid grid-cols-2 gap-y-3 text-sm">
          <dt className="text-gray-500">소싱처</dt>
          <dd className="text-right font-medium text-gray-900">{product.source_platform}</dd>

          <dt className="text-gray-500">원가</dt>
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

          <dt className="text-gray-500">위험도</dt>
          <dd className="text-right font-medium text-gray-900">{product.risk_level}</dd>
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
