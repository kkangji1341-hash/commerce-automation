"use client";

import {
  ResponsiveContainer,
  LineChart,
  Line,
  XAxis,
  YAxis,
  Tooltip,
  CartesianGrid,
} from "recharts";
import type { RecommendedProduct } from "@/lib/types";

function currency(n: number) {
  return `₩${n.toLocaleString()}`;
}

export default function ProfitChart({ products }: { products: RecommendedProduct[] }) {
  // 최근 생성 순 10개를 시간순(오래된 -> 최근)으로 정렬해서 추세를 보여준다.
  const recent10 = [...products]
    .sort((a, b) => new Date(a.created_at).getTime() - new Date(b.created_at).getTime())
    .slice(-10);

  const data = recent10.map((p, idx) => ({
    label: `#${idx + 1}`,
    name: p.product_name,
    profit: p.estimated_monthly_profit,
  }));

  if (data.length === 0) {
    return (
      <p className="rounded-xl border border-dashed border-gray-300 p-6 text-center text-sm text-gray-400">
        아직 저장된 상품이 없습니다
      </p>
    );
  }

  return (
    <div className="h-56 w-full">
      <ResponsiveContainer width="100%" height="100%">
        <LineChart data={data} margin={{ top: 8, right: 12, left: 0, bottom: 0 }}>
          <CartesianGrid strokeDasharray="3 3" stroke="#E5E7EB" />
          <XAxis dataKey="label" tick={{ fontSize: 10, fill: "#9CA3AF" }} />
          <YAxis
            tick={{ fontSize: 10, fill: "#9CA3AF" }}
            tickFormatter={(v) => `${(v / 10000).toFixed(0)}만`}
          />
          <Tooltip
            contentStyle={{ fontSize: 12, borderRadius: 8 }}
            formatter={(value: number) => [currency(value), "예상 월이익"]}
            labelFormatter={(label, payload) => payload?.[0]?.payload?.name ?? label}
          />
          <Line
            type="monotone"
            dataKey="profit"
            stroke="#3B82F6"
            strokeWidth={2}
            dot={{ r: 3 }}
            activeDot={{ r: 5 }}
          />
        </LineChart>
      </ResponsiveContainer>
    </div>
  );
}
