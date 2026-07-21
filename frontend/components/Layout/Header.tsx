"use client";

import Link from "next/link";
import { useRouter } from "next/navigation";
import { useAuth } from "@/contexts/AuthContext";
import { useUser } from "@/contexts/UserContext";

export default function Header() {
  const { isAuthenticated, logout } = useAuth();
  const { user } = useUser();
  const router = useRouter();

  function handleLogout() {
    logout();
    router.push("/auth");
  }

  return (
    <header className="sticky top-0 z-20 border-b border-gray-200 bg-white/90 backdrop-blur">
      <div className="mx-auto flex h-14 max-w-6xl items-center justify-between px-4">
        <Link href="/" className="text-lg font-bold text-primary-600">
          상품선정 & 키워드분석
        </Link>

        <nav className="flex items-center gap-4 text-sm text-gray-600">
          {isAuthenticated ? (
            <>
              <span className="hidden sm:inline text-gray-500">
                {user?.email}
                {user?.company_name ? ` · ${user.company_name}` : ""}
              </span>
              <button
                onClick={handleLogout}
                className="rounded-md px-3 py-1.5 font-medium text-gray-700 hover:bg-gray-100"
              >
                로그아웃
              </button>
            </>
          ) : (
            <Link
              href="/auth"
              className="rounded-md bg-primary-600 px-3 py-1.5 font-medium text-white hover:bg-primary-700"
            >
              로그인
            </Link>
          )}
        </nav>
      </div>
    </header>
  );
}
