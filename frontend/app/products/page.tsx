"use client";

import { Suspense, useEffect, useState } from "react";
import { useSearchParams } from "next/navigation";
import toast from "react-hot-toast";
import KeywordForm from "@/components/Keyword/KeywordForm";
import ProductList from "@/components/Product/ProductList";
import Loading from "@/components/Common/Loading";
import ErrorMessage from "@/components/Common/Error";
import { getKeywordHistory, recommendProducts } from "@/lib/api";
import { getCachedKeywordInput } from "@/lib/keywordCache";
import { getErrorMessage } from "@/lib/errors";
import { useRequireAuth } from "@/lib/useRequireAuth";
import type { KeywordAnalysisInput, KeywordAnalysisResult, RecommendedProduct } from "@/lib/types";

const DEFAULT_BUDGET = 5_000_000;
const DEFAULT_LIMIT = 5;

function ProductsPageContent() {
  const { isReady } = useRequireAuth();
  const searchParams = useSearchParams();

  const [history, setHistory] = useState<KeywordAnalysisResult[]>([]);
  const [selectedId, setSelectedId] = useState<string>("manual");
  const [prefill, setPrefill] = useState<Partial<KeywordAnalysisInput> | undefined>(undefined);
  const [cacheMissWarning, setCacheMissWarning] = useState(false);

  const [budget, setBudget] = useState(DEFAULT_BUDGET);
  const [limit, setLimit] = useState(DEFAULT_LIMIT);

  const [products, setProducts] = useState<RecommendedProduct[] | null>(null);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    if (!isReady) return;
    getKeywordHistory()
      .then((res) => setHistory(res.items))
      .catch(() => {});
  }, [isReady]);

  useEffect(() => {
    const keywordId = searchParams.get("keywordId");
    if (keywordId) {
      applySelection(keywordId);
    }
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [searchParams]);

  function applySelection(id: string) {
    setSelectedId(id);
    setCacheMissWarning(false);
    if (id === "manual") {
      setPrefill(undefined);
      return;
    }
    const cached = getCachedKeywordInput(Number(id));
    if (cached) {
      setPrefill(cached);
    } else {
      const item = history.find((h) => String(h.id) === id);
      setPrefill(item ? { keyword: item.keyword } : undefined);
      setCacheMissWarning(true);
    }
  }

  async function handleSubmit(input: KeywordAnalysisInput) {
    setIsLoading(true);
    setError(null);
    try {
      const res = await recommendProducts({ ...input, budget, limit });
      setProducts(res.products);
      toast.success(`${res.products.length}개 상품을 추천받았습니다`);
    } catch (err) {
      setError(getErrorMessage(err, "상품 추천에 실패했습니다"));
    } finally {
      setIsLoading(false);
    }
  }

  if (!isReady) return <Loading />;

  return (
    <div className="mx-auto flex max-w-4xl flex-col gap-6 p-4 sm:p-6">
      <div>
        <h1 className="text-2xl font-bold text-gray-900">상품 추천</h1>
        <p className="mt-1 text-sm text-gray-500">
          분석한 키워드를 바탕으로 팔릴 만한 상품을 추천받으세요
        </p>
      </div>

      <div className="rounded-2xl border border-gray-200 bg-white p-6">
        <div className="mb-5">
          <label className="mb-1 block text-sm font-medium text-gray-700">
            키워드 선택 (히스토리에서 선택)
          </label>
          <select
            value={selectedId}
            onChange={(e) => applySelection(e.target.value)}
            className="w-full rounded-lg border border-gray-300 px-3 py-2 text-sm focus:border-primary-500 focus:outline-none focus:ring-1 focus:ring-primary-500"
          >
            <option value="manual">직접 입력</option>
            {history.map((h) => (
              <option key={h.id} value={h.id}>
                {h.keyword} (기회점수 {h.opportunity_score.toFixed(1)}) ·{" "}
                {new Date(h.created_at).toLocaleDateString()}
              </option>
            ))}
          </select>
          {cacheMissWarning && (
            <p className="mt-2 text-xs text-yellow-600">
              이 키워드의 세부 입력값이 이 브라우저에 저장되어 있지 않습니다. 정확한 재분석을 위해
              나머지 값을 다시 입력해주세요.
            </p>
          )}
        </div>

        <div className="mb-5 grid grid-cols-2 gap-4">
          <div>
            <label className="mb-1 block text-sm font-medium text-gray-700">초기 투자 예산 (₩)</label>
            <input
              type="number"
              min={0}
              value={budget}
              onChange={(e) => setBudget(Number(e.target.value))}
              className="w-full rounded-lg border border-gray-300 px-3 py-2 text-sm focus:border-primary-500 focus:outline-none focus:ring-1 focus:ring-primary-500"
            />
          </div>
          <div>
            <label className="mb-1 block text-sm font-medium text-gray-700">추천 상품 개수</label>
            <input
              type="number"
              min={1}
              max={20}
              value={limit}
              onChange={(e) => setLimit(Number(e.target.value))}
              className="w-full rounded-lg border border-gray-300 px-3 py-2 text-sm focus:border-primary-500 focus:outline-none focus:ring-1 focus:ring-primary-500"
            />
          </div>
        </div>

        <KeywordForm
          key={selectedId}
          onSubmit={handleSubmit}
          isLoading={isLoading}
          initial={prefill}
          submitLabel="상품 추천받기"
        />
      </div>

      {error && <ErrorMessage message={error} />}

      {isLoading && <Loading label="상품을 추천하는 중..." />}

      {products && !isLoading && <ProductList products={products} />}
    </div>
  );
}

export default function ProductsPage() {
  return (
    <Suspense fallback={<Loading />}>
      <ProductsPageContent />
    </Suspense>
  );
}
