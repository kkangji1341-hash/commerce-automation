# Commerce Automation — 상품 선정 & 키워드 분석

네이버 오픈마켓 셀러를 위한 키워드 분석 · 상품 소싱 추천 SaaS. 키워드 하나만 입력하면(또는 자동 수집으로 아예 손대지 않고) 트렌드·경쟁도·수익성을 종합해 기회점수를 계산하고, 원가/배송비/등급까지 고려한 소싱 상품을 추천합니다.

- 프론트엔드(운영): https://commerce-automation-kappa.vercel.app
- 백엔드 API(운영): https://backend-production-bce0.up.railway.app
- API 문서(Swagger): https://backend-production-bce0.up.railway.app/docs

## 주요 기능

- **키워드 분석**: 검색 트렌드(12개월), 경쟁도, 예상 월매출을 바탕으로 0-100점 기회점수 산출, 위험도/계절성/추천 등급까지 자동 판정
- **키워드 자동 수집**: 키워드만 입력하면 네이버 데이터랩(검색 트렌드) · 네이버 쇼핑검색(평균가/판매자수) · 네이버 검색광고 API(절대 월간 검색량)를 조합해 폼을 자동으로 채움 — 실패 시 조용히 수동 입력으로 폴백(가짜 데이터를 만들지 않음)
- **상품 추천**: 분석된 키워드를 기반으로 소싱 후보 상품에 원가/마진/ROI/원금 회수 기간을 계산하고 GOLD/SILVER/BRONZE 등급 부여
- **대시보드**: 사용자별 분석 현황, TOP 5 키워드, 최근 추천 상품, 예상 월/연 이익 통계
- **모바일 최적화**: 반응형 레이아웃, 44px 이상 터치 타겟, 하단 탭 네비게이션

## 기술 스택

| 영역 | 스택 |
|---|---|
| 백엔드 | FastAPI, SQLAlchemy 2.0 (async), Alembic, JWT(access/refresh) |
| DB | SQLite(로컬, aiosqlite) / PostgreSQL(운영, asyncpg — Railway) |
| 프론트엔드 | Next.js 14 (App Router), TypeScript, Tailwind CSS, axios, recharts |
| 외부 API | 네이버 데이터랩(검색어트렌드), 네이버 쇼핑검색, 네이버 검색광고(keywordstool), Google Trends(pytrends, 폴백) |
| 배포 | Railway(백엔드), Vercel(프론트엔드) |

## 아키텍처

```
frontend (Next.js)  ──axios──▶  backend (FastAPI)
                                   ├─ api/v1/{auth,keywords,products}   요청/응답
                                   ├─ services/                        비즈니스 로직 + DB 저장
                                   ├─ services/keyword_analysis_engine 트렌드·경쟁도·기회점수 계산
                                   ├─ services/product_recommendation_system  원가/마진/등급 계산
                                   ├─ crawlers/keyword_crawler         네이버 API 3종 자동 수집
                                   └─ models/ (SQLAlchemy) ──Alembic──▶ PostgreSQL / SQLite
```

인증은 JWT access(15분)/refresh(7일) 토큰 방식이며, 프론트엔드 axios 인터셉터가 401 응답 시 refresh 토큰으로 한 번 재시도 후 실패하면 로그인 페이지로 리다이렉트합니다.

## 로컬 실행

### 백엔드

```bash
cd backend
python -m venv .venv && .venv\Scripts\activate   # Windows
pip install -r requirements.txt
cp .env.example .env   # 값 채우기 (아래 환경변수 설명 참고)
alembic upgrade head
uvicorn app.main:app --reload
```

`http://localhost:8000/docs` 에서 Swagger UI 확인.

### 프론트엔드

```bash
cd frontend
npm install
cp .env.local.example .env.local   # NEXT_PUBLIC_API_URL=http://localhost:8000
npm run dev
```

`http://localhost:3000` 접속.

## 환경변수

### backend/.env

| 변수 | 설명 |
|---|---|
| `DATABASE_URL` | DB 연결 문자열. 로컬은 SQLite, Railway는 `DATABASE_URL`을 postgres://로 자동 주입(내부적으로 `postgresql+asyncpg://`로 변환됨) |
| `SECRET_KEY` | JWT 서명 키. 프로덕션에서는 반드시 무작위 값으로 교체 |
| `NAVER_CLIENT_ID` / `NAVER_CLIENT_SECRET` | 네이버 데이터랩(검색어트렌드) API 자격증명 |
| `NAVER_SEARCH_CLIENT_ID` / `NAVER_SEARCH_CLIENT_SECRET` | 네이버 검색 API(쇼핑) 자격증명 — 데이터랩과 별개 앱 필요 |
| `NAVER_AD_CUSTOMER_ID` / `NAVER_AD_API_KEY` / `NAVER_AD_SECRET_KEY` | 네이버 검색광고 API(절대 월간 검색량) 자격증명 — HMAC-SHA256 서명 인증 |

세 그룹의 네이버 자격증명이 모두 없어도 서버는 정상 동작합니다(자동 수집 기능만 비활성화되고 수동 입력으로 대체).

### frontend/.env.local

| 변수 | 설명 |
|---|---|
| `NEXT_PUBLIC_API_URL` | 백엔드 API 베이스 URL (로컬: `http://localhost:8000`) |

## 주요 API 엔드포인트

| Method | Path | 설명 | 인증 |
|---|---|---|---|
| POST | `/api/v1/auth/signup` | 회원가입 | - |
| POST | `/api/v1/auth/login` | 로그인, access/refresh 토큰 발급 | - |
| POST | `/api/v1/auth/refresh-token` | 토큰 재발급 | - |
| GET/PATCH | `/api/v1/auth/me` | 내 정보 조회/수정 | 필요 |
| POST | `/api/v1/keywords/analyze` | 키워드 분석 (비로그인도 가능, 로그인 시 이력 저장) | 선택 |
| POST | `/api/v1/keywords/fetch-auto` | 키워드 자동 수집(트렌드/가격/판매자수/검색량) | - |
| GET | `/api/v1/keywords/history` | 내 키워드 분석 이력 | 필요 |
| POST | `/api/v1/products/recommend` | 상품 추천 (비로그인도 가능, 로그인 시 저장) | 선택 |
| GET | `/api/v1/products/my-products` | 내가 저장한 추천 상품 | 필요 |

전체 스키마는 `/docs`(Swagger)에서 확인 가능합니다.

## 배포

- **백엔드**: Railway, `Procfile`(`alembic upgrade head && uvicorn ...`)로 배포 시 마이그레이션 자동 실행. Root Directory `backend`.
- **프론트엔드**: Vercel, Root Directory `frontend`. `main` 브랜치 push 시 자동 재배포.
- 로컬에서 수동 배포하려면 각각 `railway up`(backend/), `vercel --prod`(repo root) 사용.

## 데이터베이스 마이그레이션

Alembic으로 관리하며 `backend/alembic/versions/`에 순서대로 적용됩니다:
1. `0001_initial` — users, keyword_analyses, product_recommendations 기본 스키마
2. `0002_add_company_name` — users.company_name 추가
3. `0003_product_grade_and_risk_fields` — 등급/위험도 세분화, 원금 회수 기간 필드 추가

새 마이그레이션 생성: `alembic revision -m "설명"` (모델 변경 후 수동 작성, autogenerate 미사용).
