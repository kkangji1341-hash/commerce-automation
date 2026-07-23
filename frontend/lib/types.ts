// 백엔드 API(app/schemas/*)와 1:1로 맞춘 타입 정의

export interface UserResponse {
  id: number;
  email: string;
  company_name: string | null;
  is_active: boolean;
  created_at: string;
}

export interface TokenResponse {
  access_token: string;
  refresh_token: string;
  token_type: string;
}

export interface SignupInput {
  email: string;
  password: string;
  company_name?: string;
}

export interface LoginInput {
  email: string;
  password: string;
}

export interface KeywordAnalysisInput {
  keyword: string;
  monthly_searches: number;
  cpc_cost?: number;
  num_top_sellers: number;
  avg_listing_price: number;
  search_trend: number[];
  review_count_top_10: number[];
  platform?: string;
}

export type CompetitionLevel = "LOW" | "MEDIUM" | "HIGH";
export type RiskLevel = "LOW" | "MEDIUM" | "HIGH";
export type Recommendation =
  | "HIGHLY_RECOMMENDED"
  | "RECOMMENDED"
  | "CAUTION"
  | "NOT_RECOMMENDED";

export interface KeywordAnalysisResult {
  id: number;
  keyword: string;
  monthly_searches: number;
  trend_score: number;
  competition_score: number;
  competition_level: CompetitionLevel;
  opportunity_score: number;
  avg_selling_price: number;
  estimated_monthly_sales: number;
  estimated_monthly_revenue: number;
  seasonality: string;
  risk_level: RiskLevel;
  recommendation: Recommendation;
  reasons: string[];
  created_at: string;
}

export interface KeywordHistoryResponse {
  items: KeywordAnalysisResult[];
  total: number;
}

export interface ProductRecommendInput extends KeywordAnalysisInput {
  budget?: number;
  limit?: number;
}

export type ProductGrade = "GOLD" | "SILVER" | "BRONZE";

export interface RecommendedProduct {
  id: number;
  product_name: string;
  keyword: string;
  product_score: number;
  match_score: number;
  recommended_selling_price: number;
  cost_of_goods: number;
  profit_per_unit: number;
  profit_margin_percent: number;
  estimated_monthly_sales: number;
  estimated_monthly_revenue: number;
  estimated_monthly_profit: number;
  payback_period_months: number | null;
  roi_percent: number;
  risk_level: RiskLevel;
  risk_factors: string[];
  seller_competition_level: RiskLevel;
  market_saturation_level: RiskLevel;
  grade: ProductGrade;
  grade_reason: string;
  recommendation_reasons: string[];
  source_id: string;
  source_platform: string;
  cost_price: number;
  shipping_cost: number;
  min_order_quantity: number;
  lead_time_days: number;
  is_estimated: boolean;
  created_at: string;
}

export interface ProductRecommendResponse {
  products: RecommendedProduct[];
}

export interface MyProductsResponse {
  items: RecommendedProduct[];
  total: number;
}

export interface KeywordFetchAutoResponse {
  keyword: string;
  search_trend: number[];
  trend_source: string;
  monthly_searches: number | null;
  monthly_searches_source: string | null;
  avg_price: number | null;
  avg_price_source: string | null;
  seller_count: number | null;
  seller_count_source: string | null;
  status: "success" | "partial_success" | "failed";
  message: string;
}

// 히스토리에서 키워드를 재선택할 때 /products/recommend 재호출에 필요한
// 원본 입력값. 백엔드가 분석 결과만 저장하고 원본 입력은 저장하지 않기 때문에
// 프론트에서 localStorage에 별도로 캐싱해서 보완한다.
export interface CachedKeywordInput extends KeywordAnalysisInput {
  analysisId: number;
}

export interface ProductCalculationInput {
  keyword_analysis_id?: number | null;
  product_name: string;
  cost: number;
  shipping_cost: number;
  margin_rate: number; // 1.0 = 100%
  monthly_searches: number;
}

export interface ProductCalculation {
  id: number;
  keyword_analysis_id: number | null;
  product_name: string;
  cost: number;
  shipping_cost: number;
  margin_rate: number;
  monthly_searches: number;
  selling_price: number;
  monthly_sales_estimate: number;
  monthly_revenue: number;
  monthly_profit: number;
  roi_percent: number;
  created_at: string;
}

export interface MyCalculationsResponse {
  items: ProductCalculation[];
  total: number;
}
