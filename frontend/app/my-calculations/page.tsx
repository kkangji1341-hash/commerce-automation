"use client";

import { useEffect, useState } from "react";
import toast from "react-hot-toast";
import Loading from "@/components/Common/Loading";
import ErrorMessage from "@/components/Common/Error";
import Button from "@/components/Common/Button";
import { deleteCalculation, getMyCalculations, hideCalculation, updateCalculation } from "@/lib/api";
import { getErrorMessage } from "@/lib/errors";
import { useRequireAuth } from "@/lib/useRequireAuth";
import type { ProductCalculation } from "@/lib/types";

function currency(n: number) {
  return `₩${Math.round(n).toLocaleString()}`;
}

interface EditState {
  product_name: string;
  cost: number;
  cost_shipping: number;
  selling_shipping: number;
  margin_rate: number;
  ad_cost: number;
  benefits_cost: number;
}

export default function MyCalculationsPage() {
  const { isReady } = useRequireAuth();

  const [items, setItems] = useState<ProductCalculation[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const [editingId, setEditingId] = useState<number | null>(null);
  const [editState, setEditState] = useState<EditState | null>(null);
  const [isSaving, setIsSaving] = useState(false);

  function load() {
    setIsLoading(true);
    getMyCalculations()
      .then((res) => setItems(res.items))
      .catch((err) => setError(getErrorMessage(err, "계산 결과를 불러오지 못했습니다")))
      .finally(() => setIsLoading(false));
  }

  useEffect(() => {
    if (!isReady) return;
    load();
  }, [isReady]);

  function startEdit(item: ProductCalculation) {
    setEditingId(item.id);
    setEditState({
      product_name: item.product_name,
      cost: item.cost,
      cost_shipping: item.cost_shipping,
      selling_shipping: item.selling_shipping,
      margin_rate: item.margin_rate,
      ad_cost: item.ad_cost,
      benefits_cost: item.benefits_cost,
    });
  }

  async function saveEdit(id: number) {
    if (!editState) return;
    setIsSaving(true);
    try {
      await updateCalculation(id, editState);
      toast.success("수정했습니다");
      setEditingId(null);
      setEditState(null);
      load();
    } catch (err) {
      toast.error(getErrorMessage(err, "수정에 실패했습니다"));
    } finally {
      setIsSaving(false);
    }
  }

  async function handleDelete(id: number) {
    if (!confirm("이 계산 결과를 완전히 삭제할까요?")) return;
    try {
      await deleteCalculation(id);
      toast.success("삭제했습니다");
      setItems((prev) => prev.filter((i) => i.id !== id));
    } catch (err) {
      toast.error(getErrorMessage(err, "삭제에 실패했습니다"));
    }
  }

  async function handleHide(id: number) {
    try {
      await hideCalculation(id);
      toast.success("목록에서 숨겼습니다");
      setItems((prev) => prev.filter((i) => i.id !== id));
    } catch (err) {
      toast.error(getErrorMessage(err, "숨기기에 실패했습니다"));
    }
  }

  if (!isReady) return <Loading />;

  return (
    <div className="mx-auto flex max-w-4xl flex-col gap-6 p-4 pb-20 sm:p-6">
      <div>
        <h1 className="text-2xl font-bold text-gray-900">저장한 마진 계산 ({items.length})</h1>
        <p className="mt-1 text-sm text-gray-500">계산기에서 저장한 상품별 판매가와 마진을 비교하세요</p>
      </div>

      {error && <ErrorMessage message={error} />}
      {isLoading && <Loading />}

      {!isLoading && items.length === 0 && (
        <p className="rounded-xl border border-dashed border-gray-300 p-8 text-center text-sm text-gray-400">
          아직 저장한 마진 계산 결과가 없습니다
        </p>
      )}

      {!isLoading && items.length > 0 && (
        <div className="flex flex-col gap-4">
          {items.map((item) => {
            const isEditing = editingId === item.id;
            return (
              <div key={item.id} className="rounded-2xl border border-gray-200 bg-white p-5">
                {isEditing && editState ? (
                  <div className="flex flex-col gap-3">
                    <input
                      value={editState.product_name}
                      onChange={(e) => setEditState({ ...editState, product_name: e.target.value })}
                      className="min-h-[44px] w-full rounded-lg border border-gray-300 px-3 py-2 text-sm"
                    />
                    <div className="grid grid-cols-2 gap-3">
                      <div>
                        <label className="mb-1 block text-xs text-gray-500">원가</label>
                        <input
                          type="number"
                          value={editState.cost}
                          onChange={(e) => setEditState({ ...editState, cost: Number(e.target.value) })}
                          className="min-h-[44px] w-full rounded-lg border border-gray-300 px-3 py-2 text-sm"
                        />
                      </div>
                      <div>
                        <label className="mb-1 block text-xs text-gray-500">마진율(%)</label>
                        <input
                          type="number"
                          value={Math.round(editState.margin_rate * 100)}
                          onChange={(e) =>
                            setEditState({ ...editState, margin_rate: Number(e.target.value) / 100 })
                          }
                          className="min-h-[44px] w-full rounded-lg border border-gray-300 px-3 py-2 text-sm"
                        />
                      </div>
                      <div>
                        <label className="mb-1 block text-xs text-gray-500">구입처 배송비</label>
                        <input
                          type="number"
                          value={editState.cost_shipping}
                          onChange={(e) =>
                            setEditState({ ...editState, cost_shipping: Number(e.target.value) })
                          }
                          className="min-h-[44px] w-full rounded-lg border border-gray-300 px-3 py-2 text-sm"
                        />
                      </div>
                      <div>
                        <label className="mb-1 block text-xs text-gray-500">판매 배송비</label>
                        <input
                          type="number"
                          value={editState.selling_shipping}
                          onChange={(e) =>
                            setEditState({ ...editState, selling_shipping: Number(e.target.value) })
                          }
                          className="min-h-[44px] w-full rounded-lg border border-gray-300 px-3 py-2 text-sm"
                        />
                      </div>
                      <div>
                        <label className="mb-1 block text-xs text-gray-500">광고비</label>
                        <input
                          type="number"
                          value={editState.ad_cost}
                          onChange={(e) => setEditState({ ...editState, ad_cost: Number(e.target.value) })}
                          className="min-h-[44px] w-full rounded-lg border border-gray-300 px-3 py-2 text-sm"
                        />
                      </div>
                      <div>
                        <label className="mb-1 block text-xs text-gray-500">스토어 혜택</label>
                        <input
                          type="number"
                          value={editState.benefits_cost}
                          onChange={(e) =>
                            setEditState({ ...editState, benefits_cost: Number(e.target.value) })
                          }
                          className="min-h-[44px] w-full rounded-lg border border-gray-300 px-3 py-2 text-sm"
                        />
                      </div>
                    </div>
                    <div className="flex gap-2">
                      <Button isLoading={isSaving} onClick={() => saveEdit(item.id)} className="flex-1">
                        저장
                      </Button>
                      <Button
                        variant="secondary"
                        onClick={() => {
                          setEditingId(null);
                          setEditState(null);
                        }}
                        className="flex-1"
                      >
                        취소
                      </Button>
                    </div>
                  </div>
                ) : (
                  <>
                    <div className="mb-3 flex items-start justify-between gap-2">
                      <h3 className="font-semibold text-gray-900">{item.product_name}</h3>
                      <div className="flex shrink-0 gap-2">
                        <button
                          onClick={() => startEdit(item)}
                          className="flex min-h-[44px] items-center text-xs font-medium text-primary-600 hover:underline"
                        >
                          수정
                        </button>
                        <button
                          onClick={() => handleHide(item.id)}
                          className="flex min-h-[44px] items-center text-xs font-medium text-gray-500 hover:underline"
                        >
                          숨기기
                        </button>
                        <button
                          onClick={() => handleDelete(item.id)}
                          className="flex min-h-[44px] items-center text-xs font-medium text-red-600 hover:underline"
                        >
                          삭제
                        </button>
                      </div>
                    </div>
                    <div className="mb-3 rounded-xl bg-primary-50 p-3 text-center">
                      <p className="text-[11px] text-gray-500">판매가</p>
                      <p className="text-2xl font-extrabold text-primary-700">
                        {currency(item.selling_price)}
                      </p>
                    </div>
                    <div className="grid grid-cols-2 gap-3 text-sm sm:grid-cols-4">
                      <div>
                        <p className="text-gray-500">원가</p>
                        <p className="font-medium text-gray-900">{currency(item.cost)}</p>
                      </div>
                      <div>
                        <p className="text-gray-500">마진율</p>
                        <p className="font-medium text-gray-900">{Math.round(item.margin_rate * 100)}%</p>
                      </div>
                      <div>
                        <p className="text-gray-500">최종 마진</p>
                        <p className="font-medium text-gray-900">{currency(item.final_margin)}</p>
                      </div>
                      <div>
                        <p className="text-gray-500">최종 마진율</p>
                        <p className="font-medium text-primary-600">
                          {(item.final_margin_rate * 100).toFixed(1)}%
                        </p>
                      </div>
                    </div>
                  </>
                )}
              </div>
            );
          })}
        </div>
      )}
    </div>
  );
}
