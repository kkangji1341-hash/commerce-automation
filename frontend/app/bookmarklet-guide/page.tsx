"use client";

import { useEffect, useState } from "react";
import toast from "react-hot-toast";
import { useRequireAuth } from "@/lib/useRequireAuth";

const BOOKMARKLET_SCRIPT_PATH = "/bookmarklet.js";
const API_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

function buildBookmarkletHref(scriptUrl: string, apiBase: string) {
  const code = `(function(){window.__PDC_API_BASE__='${apiBase}';var s=document.createElement('script');s.src='${scriptUrl}?t='+Date.now();document.body.appendChild(s);})();`;
  return `javascript:${encodeURIComponent(code)}`;
}

export default function BookmarkletGuidePage() {
  const { isReady } = useRequireAuth();
  const [href, setHref] = useState("");

  useEffect(() => {
    if (typeof window === "undefined") return;
    setHref(buildBookmarkletHref(window.location.origin + BOOKMARKLET_SCRIPT_PATH, API_URL));
  }, []);

  function copyCode() {
    if (!href) return;
    navigator.clipboard.writeText(href);
    toast.success("북마크렛 코드를 복사했습니다");
  }

  if (!isReady) return null;

  return (
    <div className="mx-auto flex max-w-2xl flex-col gap-6 p-4 pb-20 sm:p-6">
      <div>
        <h1 className="text-2xl font-bold text-gray-900">상세페이지 이미지 수집 북마크렛</h1>
        <p className="mt-1 text-sm text-gray-500">
          알리바바·타오바오처럼 자동 접속을 막는 사이트는 서버가 대신 접속해서 가져올 수
          없어요. 대신 이미 로그인해서 보고 있는 내 브라우저 화면에서 직접 이미지를 모아
          ZIP으로 내려받는 방식으로 만들었습니다.
        </p>
      </div>

      <div className="rounded-2xl border border-amber-200 bg-amber-50 p-4 text-sm text-amber-800">
        ⚠️ 북마크렛은 지금 보고 있는 페이지에서 이미지 주소만 모아 우리 서버로 보내고,
        실제 다운로드와 ZIP 압축은 서버가 대신합니다(이미지 서버 대부분이 브라우저의 직접
        요청은 막아둬서, 주소만 넘기는 방식으로 우회합니다). 최대 60개까지 처리됩니다.
      </div>

      <div className="rounded-2xl border border-gray-200 bg-white p-6">
        <h2 className="mb-3 font-semibold text-gray-900">① 설치 (북마크바로 드래그)</h2>
        <p className="mb-3 text-sm text-gray-500">
          아래 버튼을 브라우저 북마크바로 드래그해서 등록하세요. (북마크바가 안 보이면
          Ctrl+Shift+B로 켤 수 있어요)
        </p>
        {href && (
          <a
            href={href}
            onClick={(e) => e.preventDefault()}
            draggable
            className="inline-flex min-h-[44px] cursor-move items-center rounded-lg bg-primary-600 px-4 py-2 text-sm font-semibold text-white"
          >
            🖼️ 이미지 ZIP 수집
          </a>
        )}
      </div>

      <div className="rounded-2xl border border-gray-200 bg-white p-6">
        <h2 className="mb-3 font-semibold text-gray-900">② 드래그가 안 될 때 (직접 등록)</h2>
        <ol className="list-decimal space-y-1 pl-5 text-sm text-gray-600">
          <li>아래 코드를 복사하세요</li>
          <li>브라우저 북마크에 새 항목을 추가하고, 이름은 아무거나(예: "이미지 수집")</li>
          <li>URL/주소 칸에 복사한 코드를 붙여넣고 저장하세요</li>
        </ol>
        <button
          type="button"
          onClick={copyCode}
          className="mt-3 min-h-[44px] rounded-lg border border-gray-300 px-4 text-sm font-medium text-gray-700 hover:bg-gray-50"
        >
          코드 복사
        </button>
      </div>

      <div className="rounded-2xl border border-gray-200 bg-white p-6">
        <h2 className="mb-3 font-semibold text-gray-900">③ 사용 방법</h2>
        <ol className="list-decimal space-y-1 pl-5 text-sm text-gray-600">
          <li>알리바바/타오바오 등에서 원하는 상품 상세페이지로 이동</li>
          <li>페이지가 다 로딩된 후 북마크바의 "🖼️ 이미지 ZIP 수집" 클릭</li>
          <li>우측 상단에 진행 상황이 표시되고, 완료되면 자동으로 ZIP 다운로드</li>
        </ol>
      </div>
    </div>
  );
}
