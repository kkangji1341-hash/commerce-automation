"use client";

import { useState } from "react";
import toast from "react-hot-toast";
import Button from "@/components/Common/Button";
import ErrorMessage from "@/components/Common/Error";
import { collectOnchProduct, downloadOnchZip } from "@/lib/api";
import { getErrorMessage } from "@/lib/errors";
import { useRequireAuth } from "@/lib/useRequireAuth";
import type { OnchCollectResponse } from "@/lib/types";

export default function ProductDetailsCollectorPage() {
  const { isReady } = useRequireAuth();
  const [url, setUrl] = useState("");
  const [isLoading, setIsLoading] = useState(false);
  const [isDownloading, setIsDownloading] = useState(false);
  const [result, setResult] = useState<OnchCollectResponse | null>(null);
  const [error, setError] = useState<string | null>(null);

  async function handleCollect() {
    if (!url.trim()) {
      toast.error("온채널 상품 URL을 입력해주세요");
      return;
    }
    setIsLoading(true);
    setError(null);
    setResult(null);
    try {
      const res = await collectOnchProduct(url.trim());
      if (res.total_images === 0) {
        toast.error("이 페이지에서 이미지를 찾지 못했습니다");
        return;
      }
      setResult(res);
    } catch (err) {
      setError(getErrorMessage(err, "상세페이지를 불러오지 못했습니다"));
    } finally {
      setIsLoading(false);
    }
  }

  async function handleDownloadZip() {
    if (!result) return;
    setIsDownloading(true);
    try {
      await downloadOnchZip(result.images, result.product_name);
    } catch (err) {
      toast.error(getErrorMessage(err, "ZIP 다운로드에 실패했습니다"));
    } finally {
      setIsDownloading(false);
    }
  }

  if (!isReady) return null;

  return (
    <div className="mx-auto flex max-w-3xl flex-col gap-6 p-4 pb-20 sm:p-6">
      <div>
        <h1 className="text-2xl font-bold text-gray-900">상세페이지 수집기</h1>
        <p className="mt-1 text-sm text-gray-500">
          온채널(onch3.co.kr) 상품 URL을 입력하면 상세페이지 이미지를 한 번에 모아 ZIP으로
          받을 수 있어요. 이미 판매 승인을 받은 내 상품에만 사용해주세요.
        </p>
      </div>

      <div className="rounded-2xl border border-gray-200 bg-white p-6">
        <label className="mb-1 block text-sm font-medium text-gray-700">온채널 상품 URL</label>
        <div className="flex gap-2">
          <input
            value={url}
            onChange={(e) => setUrl(e.target.value)}
            placeholder="https://www.onch3.co.kr/dbcenter_renewal/detail.php?num=..."
            className="min-h-[44px] w-full rounded-lg border border-gray-300 px-3 py-2 text-sm focus:border-primary-500 focus:outline-none focus:ring-1 focus:ring-primary-500"
          />
          <Button type="button" isLoading={isLoading} onClick={handleCollect} className="shrink-0 whitespace-nowrap">
            수집 시작
          </Button>
        </div>
      </div>

      {error && <ErrorMessage message={error} />}

      {result && (
        <div className="flex flex-col gap-4">
          <div className="rounded-2xl border border-gray-200 bg-white p-5">
            <h2 className="font-semibold text-gray-900">{result.product_name}</h2>
            {result.product_code && (
              <p className="mt-1 text-xs text-gray-400">상품코드 {result.product_code}</p>
            )}
          </div>

          <div>
            <p className="mb-2 text-sm font-semibold text-gray-700">
              🖼️ 수집된 이미지 ({result.total_images}개)
            </p>
            <div className="grid grid-cols-3 gap-2 sm:grid-cols-4">
              {result.images.map((src, i) => (
                // eslint-disable-next-line @next/next/no-img-element
                <img
                  key={src + i}
                  src={src}
                  alt={`상품 이미지 ${i + 1}`}
                  className="h-28 w-full rounded-lg border border-gray-200 object-cover"
                  loading="lazy"
                />
              ))}
            </div>
          </div>

          <Button onClick={handleDownloadZip} isLoading={isDownloading} className="w-full">
            📦 모든 이미지 ZIP으로 다운로드
          </Button>
        </div>
      )}
    </div>
  );
}
