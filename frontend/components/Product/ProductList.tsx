"use client";

import { useState } from "react";
import type { RecommendedProduct } from "@/lib/types";
import ProductCard from "./ProductCard";
import ProductModal from "./ProductModal";

export default function ProductList({ products }: { products: RecommendedProduct[] }) {
  const [selected, setSelected] = useState<RecommendedProduct | null>(null);

  if (products.length === 0) {
    return (
      <p className="rounded-xl border border-dashed border-gray-300 p-8 text-center text-sm text-gray-400">
        추천할 상품이 없습니다
      </p>
    );
  }

  return (
    <>
      <div className="grid grid-cols-1 gap-4 sm:grid-cols-2 lg:grid-cols-3">
        {products.map((p) => (
          <ProductCard key={p.id} product={p} onClick={() => setSelected(p)} />
        ))}
      </div>
      {selected && <ProductModal product={selected} onClose={() => setSelected(null)} />}
    </>
  );
}
