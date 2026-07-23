import { AxiosError } from "axios";

// pydantic v2는 커스텀 validator에서 던진 ValueError 메시지 앞에
// "Value error, "를 자동으로 붙인다. 사용자에게는 불필요하므로 제거한다.
function stripPydanticPrefix(msg: string): string {
  return msg.replace(/^Value error,\s*/, "");
}

export function getErrorMessage(error: unknown, fallback = "요청 중 오류가 발생했습니다"): string {
  if (error instanceof AxiosError) {
    const detail = error.response?.data?.detail;
    if (typeof detail === "string") return stripPydanticPrefix(detail);
    if (Array.isArray(detail) && detail[0]?.msg) return stripPydanticPrefix(detail[0].msg);
    if (error.message) return error.message;
  }
  if (error instanceof Error) return error.message;
  return fallback;
}
