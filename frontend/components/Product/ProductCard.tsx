import type { RecommendedProduct } from "@/lib/types";

const RISK_STYLE: Record<string, string> = {
  LOW: "bg-green-100 text-green-700",
  MEDIUM: "bg-yellow-100 text-yellow-700",
  HIGH: "bg-red-100 text-red-700",
};

const GRADE_BADGE: Record<string, { emoji: string; style: string }> = {
  GOLD: { emoji: "🥇", style: "bg-amber-100 text-amber-800" },
  SILVER: { emoji: "🥈", style: "bg-gray-200 text-gray-700" },
  BRONZE: { emoji: "🥉", style: "bg-orange-100 text-orange-800" },
};

function currency(n: number) {
  return `₩${n.toLocaleString()}`;
}

function paybackLabel(months: number | null) {
  if (months === null) return "회수 불가";
  if (months < 1) return "1개월 이내";
  return `${months.toFixed(1)}개월`;
}

export default function ProductCard({
  product,
  onClick,
}: {
  product: RecommendedProduct;
  onClick: () => void;
}) {
  const grade = GRADE_BADGE[product.grade] ?? GRADE_BADGE.BRONZE;

  return (
    <button
      onClick={onClick}
      className="flex flex-col gap-3 rounded-2xl border border-gray-200 bg-white p-5 text-left transition-shadow hover:shadow-md"
    >
      <div className="flex items-start justify-between gap-2">
        <div className="flex items-start gap-2">
          <span
            className={`shrink-0 rounded-full px-2 py-0.5 text-xs font-semibold ${grade.style}`}
            title={product.grade_reason}
          >
            {grade.emoji} {product.grade}
          </span>
          <h3 className="font-semibold text-gray-900">{product.product_name}</h3>
        </div>
        <span
          className={`shrink-0 rounded-full px-2 py-0.5 text-xs font-semibold ${RISK_STYLE[product.risk_level] ?? "bg-gray-100 text-gray-600"}`}
        >
          위험도 {product.risk_level}
        </span>
      </div>

      <div className="flex items-center gap-2 text-xs text-gray-400">
        <span className="rounded bg-gray-100 px-1.5 py-0.5">{product.source_platform}</span>
        <span>점수 {product.product_score.toFixed(0)}/100</span>
      </div>

      <div className="grid grid-cols-2 gap-3 text-sm">
        <div>
          <p className="text-gray-500">원가 / 판매가</p>
          <p className="font-medium text-gray-900">
            {currency(product.cost_of_goods)} / {currency(product.recommended_selling_price)}
          </p>
        </div>
        <div>
          <p className="text-gray-500">마진율</p>
          <p className="font-medium text-gray-900">{product.profit_margin_percent.toFixed(0)}%</p>
        </div>
        <div>
          <p className="text-gray-500">예상 월이익</p>
          <p className="font-medium text-gray-900">
            {currency(product.estimated_monthly_profit)}
          </p>
        </div>
        <div>
          <p className="text-gray-500">ROI</p>
          <p className="font-medium text-primary-600">{product.roi_percent.toFixed(0)}%</p>
        </div>
        <div className="col-span-2">
          <p className="text-gray-500">원금 회수 기간</p>
          <p className="font-medium text-gray-900">{paybackLabel(product.payback_period_months)}</p>
        </div>
      </div>
    </button>
  );
}
