import Link from "next/link";

export default function Footer() {
  return (
    <footer className="border-t border-gray-200 bg-white py-6 text-center text-xs text-gray-400">
      <div className="mb-2 flex items-center justify-center gap-3">
        <Link href="/terms" className="hover:text-gray-600 hover:underline">
          이용약관
        </Link>
        <span>·</span>
        <Link href="/privacy" className="hover:text-gray-600 hover:underline">
          개인정보처리방침
        </Link>
      </div>
      © {new Date().getFullYear()} 상품선정 & 키워드분석 · Phase 1 MVP
    </footer>
  );
}
