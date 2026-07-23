"use client";

import { useState } from "react";
import Link from "next/link";
import toast from "react-hot-toast";
import KeywordForm from "@/components/Keyword/KeywordForm";
import AnalysisResult from "@/components/Keyword/AnalysisResult";
import Loading from "@/components/Common/Loading";
import ErrorMessage from "@/components/Common/Error";
import { analyzeKeyword } from "@/lib/api";
import { cacheKeywordInput } from "@/lib/keywordCache";
import { getErrorMessage } from "@/lib/errors";
import { useRequireAuth } from "@/lib/useRequireAuth";
import type { KeywordAnalysisInput, KeywordAnalysisResult } from "@/lib/types";

export default function KeywordsPage() {
  const { isReady } = useRequireAuth();
  const [result, setResult] = useState<KeywordAnalysisResult | null>(null);
  const [lastTrend, setLastTrend] = useState<number[]>([]);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  async function handleSubmit(input: KeywordAnalysisInput) {
    setIsLoading(true);
    setError(null);
    try {
      const analysis = await analyzeKeyword(input);
      setResult(analysis);
      setLastTrend(input.search_trend);
      cacheKeywordInput(analysis.id, input);
      toast.success("분석 결과가 히스토리에 저장되었습니다");
    } catch (err) {
      setError(getErrorMessage(err, "키워드 분석에 실패했습니다"));
    } finally {
      setIsLoading(false);
    }
  }

  if (!isReady) return <Loading />;

  return (
    <div className="mx-auto flex max-w-4xl flex-col gap-6 p-4 sm:p-6">
      <div>
        <h1 className="text-2xl font-bold text-gray-900">키워드 분석</h1>
        <p className="mt-1 text-sm text-gray-500">
          판매하려는 상품의 키워드를 분석해서 기회점수를 확인하세요
        </p>
      </div>

      <div className="rounded-2xl border border-gray-200 bg-white p-6">
        <KeywordForm onSubmit={handleSubmit} isLoading={isLoading} />
      </div>

      {error && <ErrorMessage message={error} />}

      {result && (
        <>
          <AnalysisResult result={result} searchTrend={lastTrend} />
          <div className="flex flex-col items-end gap-2 text-sm sm:flex-row sm:items-center sm:justify-end sm:gap-4">
            <Link
              href={`/products?keywordId=${result.id}`}
              className="flex min-h-[44px] items-center font-medium text-gray-500 hover:underline"
            >
              참고: 상품 추천 보기 →
            </Link>
            <Link
              href={`/calculator?keywordId=${result.id}`}
              className="flex min-h-[44px] w-full items-center justify-center gap-2 rounded-lg bg-primary-600 px-4 text-sm font-medium text-white hover:bg-primary-700 sm:w-auto"
            >
              🧮 마진 계산하기
            </Link>
          </div>
        </>
      )}
    </div>
  );
}
