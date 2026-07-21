"use client";

import { useEffect } from "react";
import { useRouter } from "next/navigation";
import { useAuth } from "@/contexts/AuthContext";

// 로그인 안 된 상태로 보호된 페이지에 들어오면 /auth로 돌려보낸다.
export function useRequireAuth() {
  const { isAuthenticated, isInitializing } = useAuth();
  const router = useRouter();

  useEffect(() => {
    if (!isInitializing && !isAuthenticated) {
      router.replace("/auth");
    }
  }, [isInitializing, isAuthenticated, router]);

  return { isReady: !isInitializing && isAuthenticated };
}
