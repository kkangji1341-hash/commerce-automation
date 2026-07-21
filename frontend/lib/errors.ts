import { AxiosError } from "axios";

export function getErrorMessage(error: unknown, fallback = "요청 중 오류가 발생했습니다"): string {
  if (error instanceof AxiosError) {
    const detail = error.response?.data?.detail;
    if (typeof detail === "string") return detail;
    if (Array.isArray(detail) && detail[0]?.msg) return detail[0].msg;
    if (error.message) return error.message;
  }
  if (error instanceof Error) return error.message;
  return fallback;
}
