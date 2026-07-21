"use client";

import { useState, FormEvent } from "react";
import Button from "@/components/Common/Button";
import type { KeywordAnalysisInput } from "@/lib/types";

const SAMPLE_DATA: KeywordAnalysisInput = {
  keyword: "무선 이어폰",
  monthly_searches: 18500,
  num_top_sellers: 25,
  avg_listing_price: 59900,
  search_trend: [40, 45, 50, 55, 65, 70, 75, 80, 85, 88, 90, 92],
  review_count_top_10: [500, 600, 700, 800, 900, 1000, 1100, 1200, 1300, 1400],
};

const EMPTY_TREND = Array(12).fill(0);
const EMPTY_REVIEWS = Array(10).fill(0);

interface KeywordFormProps {
  onSubmit: (input: KeywordAnalysisInput) => void | Promise<void>;
  isLoading?: boolean;
  initial?: Partial<KeywordAnalysisInput>;
  submitLabel?: string;
}

export default function KeywordForm({
  onSubmit,
  isLoading,
  initial,
  submitLabel = "키워드 분석하기",
}: KeywordFormProps) {
  const [keyword, setKeyword] = useState(initial?.keyword ?? "");
  const [monthlySearches, setMonthlySearches] = useState(initial?.monthly_searches ?? 0);
  const [numTopSellers, setNumTopSellers] = useState(initial?.num_top_sellers ?? 0);
  const [avgListingPrice, setAvgListingPrice] = useState(initial?.avg_listing_price ?? 0);
  const [searchTrend, setSearchTrend] = useState<number[]>(initial?.search_trend ?? EMPTY_TREND);
  const [reviewCounts, setReviewCounts] = useState<number[]>(
    initial?.review_count_top_10 ?? EMPTY_REVIEWS
  );

  function fillSample() {
    setKeyword(SAMPLE_DATA.keyword);
    setMonthlySearches(SAMPLE_DATA.monthly_searches);
    setNumTopSellers(SAMPLE_DATA.num_top_sellers);
    setAvgListingPrice(SAMPLE_DATA.avg_listing_price);
    setSearchTrend(SAMPLE_DATA.search_trend);
    setReviewCounts(SAMPLE_DATA.review_count_top_10);
  }

  function updateTrend(idx: number, value: number) {
    setSearchTrend((prev) => prev.map((v, i) => (i === idx ? value : v)));
  }

  function updateReview(idx: number, value: number) {
    setReviewCounts((prev) => prev.map((v, i) => (i === idx ? value : v)));
  }

  async function handleSubmit(e: FormEvent) {
    e.preventDefault();
    await onSubmit({
      keyword,
      monthly_searches: monthlySearches,
      num_top_sellers: numTopSellers,
      avg_listing_price: avgListingPrice,
      search_trend: searchTrend,
      review_count_top_10: reviewCounts,
    });
  }

  return (
    <form onSubmit={handleSubmit} className="flex flex-col gap-5">
      <div className="flex items-center justify-between">
        <h2 className="text-sm font-semibold text-gray-700">키워드 정보 입력</h2>
        <button
          type="button"
          onClick={fillSample}
          className="text-xs font-medium text-primary-600 hover:underline"
        >
          샘플 데이터 채우기
        </button>
      </div>

      <div className="grid grid-cols-1 gap-4 sm:grid-cols-2">
        <div className="sm:col-span-2">
          <label className="mb-1 block text-sm font-medium text-gray-700">키워드</label>
          <input
            required
            value={keyword}
            onChange={(e) => setKeyword(e.target.value)}
            placeholder="예: 무선 이어폰"
            className="w-full rounded-lg border border-gray-300 px-3 py-2 text-sm focus:border-primary-500 focus:outline-none focus:ring-1 focus:ring-primary-500"
          />
        </div>

        <div>
          <label className="mb-1 block text-sm font-medium text-gray-700">월간 검색량</label>
          <input
            type="number"
            required
            min={0}
            value={monthlySearches || ""}
            onChange={(e) => setMonthlySearches(Number(e.target.value))}
            className="w-full rounded-lg border border-gray-300 px-3 py-2 text-sm focus:border-primary-500 focus:outline-none focus:ring-1 focus:ring-primary-500"
          />
        </div>

        <div>
          <label className="mb-1 block text-sm font-medium text-gray-700">상위 판매자 수</label>
          <input
            type="number"
            required
            min={0}
            value={numTopSellers || ""}
            onChange={(e) => setNumTopSellers(Number(e.target.value))}
            className="w-full rounded-lg border border-gray-300 px-3 py-2 text-sm focus:border-primary-500 focus:outline-none focus:ring-1 focus:ring-primary-500"
          />
        </div>

        <div>
          <label className="mb-1 block text-sm font-medium text-gray-700">평균 판매가 (₩)</label>
          <input
            type="number"
            required
            min={0}
            value={avgListingPrice || ""}
            onChange={(e) => setAvgListingPrice(Number(e.target.value))}
            className="w-full rounded-lg border border-gray-300 px-3 py-2 text-sm focus:border-primary-500 focus:outline-none focus:ring-1 focus:ring-primary-500"
          />
        </div>
      </div>

      <div>
        <label className="mb-1 block text-sm font-medium text-gray-700">
          지난 12개월 트렌드 <span className="text-gray-400">(0-100)</span>
        </label>
        <div className="grid grid-cols-6 gap-2 sm:grid-cols-12">
          {searchTrend.map((v, i) => (
            <input
              key={i}
              type="number"
              min={0}
              max={100}
              value={v}
              onChange={(e) => updateTrend(i, Number(e.target.value))}
              className="w-full rounded-md border border-gray-300 px-1.5 py-1.5 text-center text-xs focus:border-primary-500 focus:outline-none focus:ring-1 focus:ring-primary-500"
              title={`${i + 1}개월 전`}
            />
          ))}
        </div>
      </div>

      <div>
        <label className="mb-1 block text-sm font-medium text-gray-700">
          상위 10개 상품 리뷰 수
        </label>
        <div className="grid grid-cols-5 gap-2 sm:grid-cols-10">
          {reviewCounts.map((v, i) => (
            <input
              key={i}
              type="number"
              min={0}
              value={v}
              onChange={(e) => updateReview(i, Number(e.target.value))}
              className="w-full rounded-md border border-gray-300 px-1.5 py-1.5 text-center text-xs focus:border-primary-500 focus:outline-none focus:ring-1 focus:ring-primary-500"
              title={`${i + 1}위 상품`}
            />
          ))}
        </div>
      </div>

      <Button type="submit" isLoading={isLoading} className="w-full sm:w-auto sm:self-end">
        {submitLabel}
      </Button>
    </form>
  );
}
