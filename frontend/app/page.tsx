"use client";

import { useEffect, useState } from "react";
import Link from "next/link";
import Loading from "@/components/Common/Loading";
import ErrorMessage from "@/components/Common/Error";
import Button from "@/components/Common/Button";
import ProductModal from "@/components/Product/ProductModal";
import ProfitChart from "@/components/Dashboard/ProfitChart";
import { getKeywordHistory, getMyProducts } from "@/lib/api";
import { getErrorMessage } from "@/lib/errors";
import { useAuth } from "@/contexts/AuthContext";
import { useUser } from "@/contexts/UserContext";
import type { KeywordAnalysisResult, ProductGrade, RecommendedProduct } from "@/lib/types";

function currency(n: number) {
  return `₩${n.toLocaleString()}`;
}

const GRADE_BADGE: Record<ProductGrade, string> = { GOLD: "🥇", SILVER: "🥈", BRONZE: "🥉" };

function paybackLabel(months: number | null) {
  if (months === null) return "회수 불가";
  if (months < 1) return "1개월 이내";
  return `${months.toFixed(1)}개월`;
}

function LandingHero() {
  return (
    <div className="mx-auto flex max-w-2xl flex-col items-center gap-6 px-4 py-24 text-center">
      <h1 className="text-3xl font-extrabold text-gray-900 sm:text-4xl">
        30초 안에 <span className="text-primary-600">팔릴 상품</span>을 찾아보세요
      </h1>
      <p className="text-gray-500">
        키워드 트렌드, 경쟁도, 수익성을 분석해서 지금 팔면 좋은 상품을 추천해드립니다.
      </p>
      <Link href="/auth">
        <Button className="px-6 py-3 text-base">지금 시작하기</Button>
      </Link>
    </div>
  );
}

interface KeywordStat {
  keyword: string;
  opportunity_score: number;
  created_at: string;
  productCount: number;
  avgRoi: number;
}

export default function DashboardPage() {
  const { isAuthenticated, isInitializing } = useAuth();
  const { user } = useUser();

  const [history, setHistory] = useState<KeywordAnalysisResult[]>([]);
  const [products, setProducts] = useState<RecommendedProduct[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [selectedProduct, setSelectedProduct] = useState<RecommendedProduct | null>(null);

  useEffect(() => {
    if (!isAuthenticated) {
      setIsLoading(false);
      return;
    }
    setIsLoading(true);
    Promise.all([getKeywordHistory(), getMyProducts()])
      .then(([h, p]) => {
        setHistory(h.items);
        setProducts(p.items);
      })
      .catch((err) => setError(getErrorMessage(err, "정보를 불러오지 못했습니다")))
      .finally(() => setIsLoading(false));
  }, [isAuthenticated]);

  if (isInitializing) return <Loading />;
  if (!isAuthenticated) return <LandingHero />;

  // ---- 1. 사용자 분석 현황 ----
  const gradeCounts: Record<ProductGrade, number> = { GOLD: 0, SILVER: 0, BRONZE: 0 };
  for (const p of products) gradeCounts[p.grade] = (gradeCounts[p.grade] ?? 0) + 1;

  // ---- 2. 나의 TOP 5 키워드 (동일 키워드는 가장 최근 분석 기준으로 통합) ----
  const latestByKeyword = new Map<string, KeywordAnalysisResult>();
  for (const h of history) {
    const existing = latestByKeyword.get(h.keyword);
    if (!existing || new Date(h.created_at) > new Date(existing.created_at)) {
      latestByKeyword.set(h.keyword, h);
    }
  }
  const keywordStats: KeywordStat[] = [...latestByKeyword.values()].map((h) => {
    const related = products.filter((p) => p.keyword === h.keyword);
    const avgRoi =
      related.length > 0 ? related.reduce((sum, p) => sum + p.roi_percent, 0) / related.length : 0;
    return {
      keyword: h.keyword,
      opportunity_score: h.opportunity_score,
      created_at: h.created_at,
      productCount: related.length,
      avgRoi,
    };
  });
  const top5Keywords = [...keywordStats]
    .sort((a, b) => b.opportunity_score - a.opportunity_score)
    .slice(0, 5);

  // ---- 3. 최근 추천 상품 (최신순 5개) ----
  const recentProducts = [...products]
    .sort((a, b) => new Date(b.created_at).getTime() - new Date(a.created_at).getTime())
    .slice(0, 5);

  // ---- 4. 예상 월/연 이익 ----
  const totalMonthlyProfit = products.reduce((sum, p) => sum + p.estimated_monthly_profit, 0);
  const annualProfit = totalMonthlyProfit * 12;

  return (
    <div className="mx-auto flex max-w-4xl flex-col gap-8 p-4 sm:p-6">
      <div>
        <h1 className="text-2xl font-bold text-gray-900">
          안녕하세요{user?.company_name ? `, ${user.company_name}` : ""} 👋
        </h1>
        <p className="mt-1 text-sm text-gray-500">오늘의 상품 선정 현황을 확인하세요</p>
      </div>

      {error && <ErrorMessage message={error} />}
      {isLoading && <Loading />}

      {!isLoading && (
        <>
          {/* 1. 사용자 분석 현황 */}
          <section>
            <div className="mb-3 flex items-center justify-between">
              <h2 className="text-sm font-semibold text-gray-700">사용자 분석 현황</h2>
              <Link href="/keywords" className="text-xs font-medium text-primary-600 hover:underline">
                새 키워드 분석하기 →
              </Link>
            </div>
            <div className="grid grid-cols-2 gap-4 sm:grid-cols-3">
              <div className="rounded-2xl border border-gray-200 bg-white p-5 text-center">
                <p className="text-xs text-gray-500">총 분석한 키워드</p>
                <p className="mt-1 text-2xl font-bold text-gray-900">{history.length}개</p>
              </div>
              <div className="rounded-2xl border border-gray-200 bg-white p-5 text-center">
                <p className="text-xs text-gray-500">저장한 상품</p>
                <p className="mt-1 text-2xl font-bold text-gray-900">{products.length}개</p>
              </div>
              <div className="col-span-2 rounded-2xl border border-gray-200 bg-white p-5 text-center sm:col-span-1">
                <p className="text-xs text-gray-500">등급별 분포</p>
                <p className="mt-1 text-sm font-semibold text-gray-900">
                  🥇 {gradeCounts.GOLD}개 &nbsp;|&nbsp; 🥈 {gradeCounts.SILVER}개 &nbsp;|&nbsp; 🥉{" "}
                  {gradeCounts.BRONZE}개
                </p>
              </div>
            </div>
          </section>

          {/* 2. 나의 TOP 5 키워드 */}
          <section>
            <h2 className="mb-3 text-sm font-semibold text-gray-700">나의 TOP 5 키워드</h2>
            {top5Keywords.length === 0 ? (
              <p className="rounded-xl border border-dashed border-gray-300 p-6 text-center text-sm text-gray-400">
                아직 분석한 키워드가 없습니다
              </p>
            ) : (
              <div className="overflow-x-auto rounded-2xl border border-gray-200 bg-white">
                <table className="w-full min-w-[520px] text-sm">
                  <thead className="bg-gray-50 text-left text-xs text-gray-500">
                    <tr>
                      <th className="px-4 py-3">키워드</th>
                      <th className="px-4 py-3">기회점수</th>
                      <th className="px-4 py-3">저장된 상품 수</th>
                      <th className="px-4 py-3">평균 ROI</th>
                    </tr>
                  </thead>
                  <tbody className="divide-y divide-gray-100">
                    {top5Keywords.map((k) => (
                      <tr key={k.keyword}>
                        <td className="px-4 py-3 font-medium text-gray-900">{k.keyword}</td>
                        <td className="px-4 py-3 text-primary-600">
                          {k.opportunity_score.toFixed(1)}
                        </td>
                        <td className="px-4 py-3 text-gray-600">{k.productCount}개</td>
                        <td className="px-4 py-3 text-gray-600">
                          {k.productCount > 0 ? `${k.avgRoi.toFixed(0)}%` : "-"}
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            )}
          </section>

          {/* 3. 최근 추천 상품 */}
          <section>
            <h2 className="mb-3 text-sm font-semibold text-gray-700">최근 추천 상품</h2>
            {recentProducts.length === 0 ? (
              <p className="rounded-xl border border-dashed border-gray-300 p-6 text-center text-sm text-gray-400">
                아직 추천받은 상품이 없습니다
              </p>
            ) : (
              <div className="overflow-x-auto rounded-2xl border border-gray-200 bg-white">
                <table className="w-full min-w-[560px] text-sm">
                  <thead className="bg-gray-50 text-left text-xs text-gray-500">
                    <tr>
                      <th className="px-4 py-3">상품명</th>
                      <th className="px-4 py-3">등급</th>
                      <th className="px-4 py-3">원금 회수 기간</th>
                      <th className="px-4 py-3">예상 월이익</th>
                      <th className="px-4 py-3"></th>
                    </tr>
                  </thead>
                  <tbody className="divide-y divide-gray-100">
                    {recentProducts.map((p) => (
                      <tr key={p.id}>
                        <td className="px-4 py-3 font-medium text-gray-900">{p.product_name}</td>
                        <td className="px-4 py-3">
                          {GRADE_BADGE[p.grade]} {p.grade}
                        </td>
                        <td className="px-4 py-3 text-gray-600">
                          {paybackLabel(p.payback_period_months)}
                        </td>
                        <td className="px-4 py-3 text-gray-600">
                          {currency(p.estimated_monthly_profit)}
                        </td>
                        <td className="px-4 py-3 text-right">
                          <button
                            onClick={() => setSelectedProduct(p)}
                            className="text-xs font-medium text-primary-600 hover:underline"
                          >
                            상세보기 →
                          </button>
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            )}
          </section>

          {/* 4. 예상 월 이익 계산 */}
          <section>
            <h2 className="mb-3 text-sm font-semibold text-gray-700">예상 월 이익</h2>
            <div className="mb-4 grid grid-cols-2 gap-4">
              <div className="rounded-2xl border border-gray-200 bg-white p-5 text-center">
                <p className="text-xs text-gray-500">저장 상품 월이익 합계</p>
                <p className="mt-1 text-xl font-bold text-primary-600">
                  {currency(totalMonthlyProfit)}
                </p>
              </div>
              <div className="rounded-2xl border border-gray-200 bg-white p-5 text-center">
                <p className="text-xs text-gray-500">예상 연 이익 (월이익 × 12)</p>
                <p className="mt-1 text-xl font-bold text-gray-900">{currency(annualProfit)}</p>
              </div>
            </div>
            <div className="rounded-2xl border border-gray-200 bg-white p-5">
              <p className="mb-2 text-xs text-gray-500">최근 저장한 상품 10개 기준 월이익 추이</p>
              <ProfitChart products={products} />
            </div>
          </section>
        </>
      )}

      {selectedProduct && (
        <ProductModal product={selectedProduct} onClose={() => setSelectedProduct(null)} />
      )}
    </div>
  );
}
