const { withSentryConfig } = require("@sentry/nextjs");

/** @type {import('next').NextConfig} */
const nextConfig = {
  reactStrictMode: true,
};

// SENTRY_ORG/SENTRY_PROJECT가 없으면(로컬 개발, DSN 미설정 등) 소스맵 업로드를
// 건너뛴다 — 빌드가 Sentry 계정 없이도 항상 성공해야 하기 때문.
module.exports = process.env.SENTRY_ORG
  ? withSentryConfig(nextConfig, {
      silent: true,
      org: process.env.SENTRY_ORG,
      project: process.env.SENTRY_PROJECT,
    })
  : nextConfig;
