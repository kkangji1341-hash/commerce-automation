import * as Sentry from "@sentry/nextjs";

// DSN이 없으면 조용히 비활성 상태로 남는다 — 로컬 개발 환경에서
// Sentry 계정을 안 만들어도 앱이 정상 동작해야 하기 때문.
const dsn = process.env.NEXT_PUBLIC_SENTRY_DSN;

if (dsn) {
  Sentry.init({
    dsn,
    environment: process.env.NEXT_PUBLIC_SENTRY_ENVIRONMENT || "production",
    tracesSampleRate: 0.1,
    sendDefaultPii: false,
  });
}
