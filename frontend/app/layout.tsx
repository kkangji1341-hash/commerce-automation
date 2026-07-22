import type { Metadata, Viewport } from "next";
import { Toaster } from "react-hot-toast";
import "./globals.css";
import { AuthProvider } from "@/contexts/AuthContext";
import { UserProvider } from "@/contexts/UserContext";
import Header from "@/components/Layout/Header";
import Sidebar from "@/components/Layout/Sidebar";
import MobileNav from "@/components/Layout/MobileNav";
import Footer from "@/components/Layout/Footer";

export const metadata: Metadata = {
  title: "상품선정 & 키워드분석",
  description: "Phase 1 MVP - 키워드 분석 & 상품 추천 대시보드",
};

export const viewport: Viewport = {
  width: "device-width",
  initialScale: 1,
  maximumScale: 5,
};

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="ko">
      <body className="min-h-screen bg-gray-50 font-sans text-gray-900">
        <AuthProvider>
          <UserProvider>
            <Toaster position="top-center" toastOptions={{ duration: 3000 }} />
            <Header />
            <div className="flex min-h-[calc(100vh-56px)]">
              <Sidebar />
              <main className="min-w-0 flex-1 pb-16 md:pb-0">{children}</main>
            </div>
            <MobileNav />
            <Footer />
          </UserProvider>
        </AuthProvider>
      </body>
    </html>
  );
}
