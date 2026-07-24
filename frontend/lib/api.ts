import axios, { AxiosError, InternalAxiosRequestConfig } from "axios";
import type {
  AnalyzeAndGenerateResponse,
  KeywordAnalysisInput,
  KeywordAnalysisResult,
  KeywordFetchAutoResponse,
  KeywordHistoryResponse,
  LoginInput,
  MyCalculationsResponse,
  MyProductsResponse,
  ProductCalculation,
  ProductCalculationInput,
  ProductRecommendInput,
  ProductRecommendResponse,
  SignupInput,
  TokenResponse,
  UserResponse,
} from "./types";

const API_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";
const API_V1 = `${API_URL}/api/v1`;

const ACCESS_TOKEN_KEY = "access_token";
const REFRESH_TOKEN_KEY = "refresh_token";

export function getAccessToken(): string | null {
  if (typeof window === "undefined") return null;
  return localStorage.getItem(ACCESS_TOKEN_KEY);
}

export function getRefreshToken(): string | null {
  if (typeof window === "undefined") return null;
  return localStorage.getItem(REFRESH_TOKEN_KEY);
}

export function setTokens(tokens: TokenResponse) {
  localStorage.setItem(ACCESS_TOKEN_KEY, tokens.access_token);
  localStorage.setItem(REFRESH_TOKEN_KEY, tokens.refresh_token);
}

export function clearTokens() {
  localStorage.removeItem(ACCESS_TOKEN_KEY);
  localStorage.removeItem(REFRESH_TOKEN_KEY);
}

const client = axios.create({ baseURL: API_V1 });

client.interceptors.request.use((config: InternalAxiosRequestConfig) => {
  const token = getAccessToken();
  if (token) {
    config.headers = config.headers ?? {};
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

// 401 응답 시 refresh_token으로 한 번 재발급 후 원 요청을 재시도한다.
// 동시에 여러 요청이 401을 받아도 refresh 호출은 한 번만 나가도록 in-flight 프라미스를 공유한다.
let refreshPromise: Promise<string | null> | null = null;

async function performRefresh(): Promise<string | null> {
  const refreshToken = getRefreshToken();
  if (!refreshToken) return null;
  try {
    const { data } = await axios.post<TokenResponse>(`${API_V1}/auth/refresh-token`, {
      refresh_token: refreshToken,
    });
    setTokens(data);
    return data.access_token;
  } catch {
    clearTokens();
    return null;
  }
}

client.interceptors.response.use(
  (response) => response,
  async (error: AxiosError) => {
    const original = error.config as (InternalAxiosRequestConfig & { _retry?: boolean }) | undefined;

    if (error.response?.status === 401 && original && !original._retry) {
      original._retry = true;

      if (!refreshPromise) {
        refreshPromise = performRefresh().finally(() => {
          refreshPromise = null;
        });
      }
      const newToken = await refreshPromise;

      if (newToken) {
        original.headers = original.headers ?? {};
        original.headers.Authorization = `Bearer ${newToken}`;
        return client(original);
      }

      clearTokens();
      if (typeof window !== "undefined") {
        window.location.href = "/auth";
      }
    }

    return Promise.reject(error);
  }
);

export async function signUp(input: SignupInput): Promise<UserResponse> {
  const { data } = await client.post<UserResponse>("/auth/signup", input);
  return data;
}

export async function login(input: LoginInput): Promise<TokenResponse> {
  const { data } = await client.post<TokenResponse>("/auth/login", input);
  setTokens(data);
  return data;
}

export async function getMe(): Promise<UserResponse> {
  const { data } = await client.get<UserResponse>("/auth/me");
  return data;
}

export async function updateMe(companyName: string): Promise<UserResponse> {
  const { data } = await client.patch<UserResponse>("/auth/me", { company_name: companyName });
  return data;
}

export function logout() {
  clearTokens();
}

export async function analyzeKeyword(input: KeywordAnalysisInput): Promise<KeywordAnalysisResult> {
  const { data } = await client.post<KeywordAnalysisResult>("/keywords/analyze", input);
  return data;
}

export async function fetchKeywordAuto(keyword: string): Promise<KeywordFetchAutoResponse> {
  const { data } = await client.post<KeywordFetchAutoResponse>("/keywords/fetch-auto", { keyword });
  return data;
}

export async function getKeywordHistory(): Promise<KeywordHistoryResponse> {
  const { data } = await client.get<KeywordHistoryResponse>("/keywords/history");
  return data;
}

export async function analyzeAndGenerate(keyword: string): Promise<AnalyzeAndGenerateResponse> {
  const { data } = await client.post<AnalyzeAndGenerateResponse>("/keywords/analyze-and-generate", {
    keyword,
  });
  return data;
}

export async function recommendProducts(
  input: ProductRecommendInput
): Promise<ProductRecommendResponse> {
  const { data } = await client.post<ProductRecommendResponse>("/products/recommend", input);
  return data;
}

export async function getMyProducts(): Promise<MyProductsResponse> {
  const { data } = await client.get<MyProductsResponse>("/products/my-products");
  return data;
}

export async function createCalculation(
  input: ProductCalculationInput
): Promise<ProductCalculation> {
  const { data } = await client.post<ProductCalculation>("/calculations/create", input);
  return data;
}

export async function getMyCalculations(): Promise<MyCalculationsResponse> {
  const { data } = await client.get<MyCalculationsResponse>("/calculations/my-calculations");
  return data;
}

export async function updateCalculation(
  id: number,
  input: Omit<ProductCalculationInput, "keyword_analysis_id">
): Promise<ProductCalculation> {
  const { data } = await client.put<ProductCalculation>(`/calculations/${id}`, input);
  return data;
}

export async function deleteCalculation(id: number): Promise<void> {
  await client.delete(`/calculations/${id}`);
}

export async function hideCalculation(id: number): Promise<ProductCalculation> {
  const { data } = await client.patch<ProductCalculation>(`/calculations/${id}/hide`);
  return data;
}

export default client;
