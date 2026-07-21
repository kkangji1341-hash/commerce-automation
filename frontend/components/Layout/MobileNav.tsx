"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";
import { useAuth } from "@/contexts/AuthContext";

const NAV_ITEMS = [
  { href: "/", label: "대시보드", icon: "🏠" },
  { href: "/keywords", label: "키워드", icon: "🔍" },
  { href: "/products", label: "상품추천", icon: "📦" },
  { href: "/my-products", label: "마이페이지", icon: "👤" },
];

export default function MobileNav() {
  const pathname = usePathname();
  const { isAuthenticated } = useAuth();

  if (!isAuthenticated) return null;

  return (
    <nav className="fixed inset-x-0 bottom-0 z-20 flex border-t border-gray-200 bg-white md:hidden">
      {NAV_ITEMS.map((item) => {
        const active = pathname === item.href;
        return (
          <Link
            key={item.href}
            href={item.href}
            className={`flex flex-1 flex-col items-center gap-0.5 py-2 text-xs ${
              active ? "text-primary-600" : "text-gray-500"
            }`}
          >
            <span className="text-lg">{item.icon}</span>
            {item.label}
          </Link>
        );
      })}
    </nav>
  );
}
