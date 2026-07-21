"use client";

import { useEffect, useState } from "react";
import Link from "next/link";
import Loading from "@/components/Common/Loading";
import ErrorMessage from "@/components/Common/Error";
import Button from "@/components/Common/Button";
import { getKeywordHistory, getMyProducts } from "@/lib/api";
import { getErrorMessage } from "@/lib/errors";
import { useAuth } from "@/contexts/AuthContext";
import { useUser } from "@/contexts/UserContext";
import type { KeywordAnalysisResult, RecommendedProduct } from "@/lib/types";

function currency(n: number) {
  return `₩${n.toLocaleString()}`;
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

export default function DashboardPage() {
  const { isAuthenticated, isInitializing } = useAuth();
  const { user } = useUser();

  const [history, setHistory] = useState<KeywordAnalysisResult[]>([]);
  const [products, setProducts] = useState<RecommendedProduct[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

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

  const recentAnalyses = history.slice(0, 3);
  const topProducts = [...products].sort((a, b) => b.product_score - a.product_score).slice(0, 5);

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
          <div className="grid grid-cols-2 gap-4 sm:grid-cols-3">
            <div className="rounded-2xl border border-gray-200 bg-white p-5 text-center">
              <p className="text-xs text-gray-500">총 분석 수</p>
              <p className="mt-1 text-2xl font-bold text-gray-900">{history.length}</p>
            </div>
            <div className="rounded-2xl border border-gray-200 bg-white p-5 text-center">
              <p className="text-xs text-gray-500">저장된 상품 수</p>
              <p className="mt-1 text-2xl font-bold text-gray-900">{products.length}</p>
            </div>
            <div className="col-span-2 rounded-2xl border border-gray-200 bg-white p-5 text-center sm:col-span-1">
              <p className="text-xs text-gray-500">평균 기회점수</p>
              <p className="mt-1 text-2xl font-bold text-primary-600">
                {history.length > 0
                  ? (
                      history.reduce((sum, h) => sum + h.opportunity_score, 0) / history.length
                    ).toFixed(1)
                  : "-"}
              </p>
            </div>
          </div>

          <section>
            <div className="mb-3 flex items-center justify-between">
              <h2 className="text-sm font-semibold text-gray-700">최근 분석</h2>
              <Link href="/keywords" className="text-xs font-medium text-primary-600 hover:underline">
                새 키워드 분석하기 →
              </Link>
            </div>
            {recentAnalyses.length === 0 ? (
              <p className="rounded-xl border border-dashed border-gray-300 p-6 text-center text-sm text-gray-400">
                아직 분석한 키워드가 없습니다
              </p>
            ) : (
              <div className="grid grid-cols-1 gap-3 sm:grid-cols-3">
                {recentAnalyses.map((h) => (
                  <div key={h.id} className="rounded-xl border border-gray-200 bg-white p-4">
                    <p className="font-semibold text-gray-900">{h.keyword}</p>
                    <p className="mt-1 text-xs text-gray-500">{h.recommendation}</p>
                    <p className="mt-2 text-xl font-bold text-primary-600">
                      {h.opportunity_score.toFixed(1)}
                      <span className="text-xs font-normal text-gray-400"> 점</span>
                    </p>
                  </div>
                ))}
              </div>
            )}
          </section>

          <section>
            <h2 className="mb-3 text-sm font-semibold text-gray-700">내 추천 상품 Top 5</h2>
            {topProducts.length === 0 ? (
              <p className="rounded-xl border border-dashed border-gray-300 p-6 text-center text-sm text-gray-400">
                아직 추천받은 상품이 없습니다
              </p>
            ) : (
              <div className="overflow-x-auto rounded-2xl border border-gray-200 bg-white">
                <table className="w-full min-w-[480px] text-sm">
                  <thead className="bg-gray-50 text-left text-xs text-gray-500">
                    <tr>
                      <th className="px-4 py-3">상품명</th>
                      <th className="px-4 py-3">점수</th>
                      <th className="px-4 py-3">예상 월이익</th>
                      <th className="px-4 py-3">ROI</th>
                    </tr>
                  </thead>
                  <tbody className="divide-y divide-gray-100">
                    {topProducts.map((p) => (
                      <tr key={p.id}>
                        <td className="px-4 py-3 font-medium text-gray-900">{p.product_name}</td>
                        <td className="px-4 py-3 text-gray-600">{p.product_score.toFixed(0)}</td>
                        <td className="px-4 py-3 text-gray-600">
                          {currency(p.estimated_monthly_profit)}
                        </td>
                        <td className="px-4 py-3 text-primary-600">
                          {p.roi_percent.toFixed(0)}%
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            )}
          </section>
        </>
      )}
    </div>
  );
}
