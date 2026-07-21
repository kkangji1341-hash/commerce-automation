"use client";

import { useEffect, useState, FormEvent } from "react";
import { useRouter } from "next/navigation";
import toast from "react-hot-toast";
import Loading from "@/components/Common/Loading";
import ErrorMessage from "@/components/Common/Error";
import Button from "@/components/Common/Button";
import ProductList from "@/components/Product/ProductList";
import { getKeywordHistory, getMyProducts } from "@/lib/api";
import { getErrorMessage } from "@/lib/errors";
import { useRequireAuth } from "@/lib/useRequireAuth";
import { useAuth } from "@/contexts/AuthContext";
import { useUser } from "@/contexts/UserContext";
import type { KeywordAnalysisResult, RecommendedProduct } from "@/lib/types";

const RECOMMENDATION_LABEL: Record<string, string> = {
  HIGHLY_RECOMMENDED: "적극 추천",
  RECOMMENDED: "추천",
  CAUTION: "신중 검토",
  NOT_RECOMMENDED: "비추천",
};

export default function MyProductsPage() {
  const { isReady } = useRequireAuth();
  const { logout } = useAuth();
  const { user, updateCompanyName } = useUser();
  const router = useRouter();

  const [history, setHistory] = useState<KeywordAnalysisResult[]>([]);
  const [products, setProducts] = useState<RecommendedProduct[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const [companyName, setCompanyName] = useState("");
  const [isSaving, setIsSaving] = useState(false);

  useEffect(() => {
    if (user) setCompanyName(user.company_name ?? "");
  }, [user]);

  useEffect(() => {
    if (!isReady) return;
    setIsLoading(true);
    Promise.all([getKeywordHistory(), getMyProducts()])
      .then(([h, p]) => {
        setHistory(h.items);
        setProducts(p.items);
      })
      .catch((err) => setError(getErrorMessage(err, "정보를 불러오지 못했습니다")))
      .finally(() => setIsLoading(false));
  }, [isReady]);

  async function handleProfileSave(e: FormEvent) {
    e.preventDefault();
    setIsSaving(true);
    try {
      await updateCompanyName(companyName);
    } catch (err) {
      toast.error(getErrorMessage(err, "정보 저장에 실패했습니다"));
    } finally {
      setIsSaving(false);
    }
  }

  function handleLogout() {
    logout();
    router.push("/auth");
  }

  if (!isReady) return <Loading />;

  return (
    <div className="mx-auto flex max-w-4xl flex-col gap-8 p-4 pb-20 sm:p-6">
      <div className="flex items-center justify-between">
        <h1 className="text-2xl font-bold text-gray-900">마이페이지</h1>
        <Button variant="secondary" onClick={handleLogout}>
          로그아웃
        </Button>
      </div>

      <section className="rounded-2xl border border-gray-200 bg-white p-6">
        <h2 className="mb-4 text-sm font-semibold text-gray-700">사용자 정보</h2>
        <form onSubmit={handleProfileSave} className="flex flex-col gap-4 sm:flex-row sm:items-end">
          <div className="flex-1">
            <label className="mb-1 block text-sm font-medium text-gray-700">이메일</label>
            <input
              disabled
              value={user?.email ?? ""}
              className="w-full rounded-lg border border-gray-200 bg-gray-50 px-3 py-2 text-sm text-gray-500"
            />
          </div>
          <div className="flex-1">
            <label className="mb-1 block text-sm font-medium text-gray-700">회사명</label>
            <input
              value={companyName}
              onChange={(e) => setCompanyName(e.target.value)}
              className="w-full rounded-lg border border-gray-300 px-3 py-2 text-sm focus:border-primary-500 focus:outline-none focus:ring-1 focus:ring-primary-500"
              placeholder="(주)커머스오토메이션"
            />
          </div>
          <Button type="submit" isLoading={isSaving}>
            저장
          </Button>
        </form>
      </section>

      {error && <ErrorMessage message={error} />}
      {isLoading && <Loading />}

      {!isLoading && (
        <>
          <section>
            <h2 className="mb-3 text-sm font-semibold text-gray-700">
              저장된 키워드 히스토리 ({history.length})
            </h2>
            {history.length === 0 ? (
              <p className="rounded-xl border border-dashed border-gray-300 p-6 text-center text-sm text-gray-400">
                아직 분석한 키워드가 없습니다
              </p>
            ) : (
              <div className="overflow-x-auto rounded-2xl border border-gray-200 bg-white">
                <table className="w-full min-w-[560px] text-sm">
                  <thead className="bg-gray-50 text-left text-xs text-gray-500">
                    <tr>
                      <th className="px-4 py-3">키워드</th>
                      <th className="px-4 py-3">기회점수</th>
                      <th className="px-4 py-3">경쟁도</th>
                      <th className="px-4 py-3">추천도</th>
                      <th className="px-4 py-3">분석일</th>
                    </tr>
                  </thead>
                  <tbody className="divide-y divide-gray-100">
                    {history.map((h) => (
                      <tr key={h.id}>
                        <td className="px-4 py-3 font-medium text-gray-900">{h.keyword}</td>
                        <td className="px-4 py-3 text-primary-600">
                          {h.opportunity_score.toFixed(1)}
                        </td>
                        <td className="px-4 py-3 text-gray-600">{h.competition_level}</td>
                        <td className="px-4 py-3 text-gray-600">
                          {RECOMMENDATION_LABEL[h.recommendation] ?? h.recommendation}
                        </td>
                        <td className="px-4 py-3 text-gray-400">
                          {new Date(h.created_at).toLocaleDateString()}
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            )}
          </section>

          <section>
            <h2 className="mb-3 text-sm font-semibold text-gray-700">
              추천받은 상품 ({products.length})
            </h2>
            <ProductList products={products} />
          </section>
        </>
      )}
    </div>
  );
}
