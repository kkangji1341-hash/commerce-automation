"use client";

import { useState } from "react";
import { useRouter } from "next/navigation";
import LoginForm from "@/components/Auth/LoginForm";
import SignupForm from "@/components/Auth/SignupForm";

export default function AuthPage() {
  const [mode, setMode] = useState<"login" | "signup">("login");
  const router = useRouter();

  function handleSuccess() {
    router.push("/");
  }

  return (
    <div className="flex min-h-[calc(100vh-56px)] items-center justify-center bg-gray-50 px-4">
      <div className="w-full max-w-sm rounded-2xl border border-gray-200 bg-white p-8 shadow-sm">
        <h1 className="mb-1 text-xl font-bold text-gray-900">
          {mode === "login" ? "로그인" : "회원가입"}
        </h1>
        <p className="mb-6 text-sm text-gray-500">
          상품 선정 & 키워드 분석 대시보드에 오신 것을 환영합니다
        </p>

        {mode === "login" ? (
          <LoginForm onSuccess={handleSuccess} />
        ) : (
          <SignupForm onSuccess={handleSuccess} />
        )}

        <div className="mt-6 text-center text-sm text-gray-500">
          {mode === "login" ? (
            <>
              계정이 없으신가요?{" "}
              <button
                onClick={() => setMode("signup")}
                className="inline-block min-h-[44px] py-2 font-medium text-primary-600 hover:underline"
              >
                회원가입
              </button>
            </>
          ) : (
            <>
              이미 계정이 있으신가요?{" "}
              <button
                onClick={() => setMode("login")}
                className="inline-block min-h-[44px] py-2 font-medium text-primary-600 hover:underline"
              >
                로그인
              </button>
            </>
          )}
        </div>
      </div>
    </div>
  );
}
