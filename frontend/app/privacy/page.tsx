export default function PrivacyPage() {
  return (
    <div className="mx-auto flex max-w-2xl flex-col gap-6 p-4 pb-20 sm:p-6">
      <div>
        <h1 className="text-2xl font-bold text-gray-900">개인정보처리방침</h1>
        <p className="mt-1 text-sm text-gray-500">시행일: 2026년 8월 11일</p>
      </div>

      <section className="flex flex-col gap-2 text-sm leading-relaxed text-gray-700">
        <h2 className="font-semibold text-gray-900">1. 수집하는 개인정보 항목</h2>
        <ul className="list-disc pl-5">
          <li>회원가입 시: 이메일 주소, 비밀번호(암호화 저장), 회사명(선택)</li>
          <li>서비스 이용 중: 분석한 키워드, 생성한 상품명, 저장한 마진 계산 내역</li>
          <li>자동 수집: 접속 IP(부정 이용 방지·요청 빈도 제한 목적으로만 일시적으로 사용)</li>
        </ul>
        <p>비밀번호는 원문이 아닌 암호화된 형태로만 저장되며, 서비스 운영자도 원문을 볼 수 없습니다.</p>
      </section>

      <section className="flex flex-col gap-2 text-sm leading-relaxed text-gray-700">
        <h2 className="font-semibold text-gray-900">2. 개인정보의 수집 및 이용 목적</h2>
        <ul className="list-disc pl-5">
          <li>회원 식별 및 로그인 유지</li>
          <li>키워드 분석·마진 계산 내역 저장 및 조회 기능 제공</li>
          <li>부정 이용(무차별 로그인 시도, 자동화된 반복 요청 등) 탐지 및 차단</li>
        </ul>
      </section>

      <section className="flex flex-col gap-2 text-sm leading-relaxed text-gray-700">
        <h2 className="font-semibold text-gray-900">3. 개인정보의 보유 및 이용 기간</h2>
        <p>
          회원 탈퇴 시 또는 이용자가 삭제를 요청할 때까지 보유하며, 요청 시 지체 없이
          파기합니다. 관계 법령에 따라 보존이 필요한 정보는 해당 기간 동안만 별도 보관합니다.
        </p>
      </section>

      <section className="flex flex-col gap-2 text-sm leading-relaxed text-gray-700">
        <h2 className="font-semibold text-gray-900">4. 개인정보의 제3자 제공 및 처리 위탁</h2>
        <p>서비스는 다음 외부 서비스를 이용해 운영됩니다.</p>
        <ul className="list-disc pl-5">
          <li>
            <strong>네이버 검색광고 API / 검색(쇼핑) API</strong> — 이용자가 입력한 검색
            키워드 문자열만 전송되며, 이메일 등 개인 식별 정보는 전송되지 않습니다.
          </li>
          <li>
            <strong>Railway</strong> (백엔드 서버·데이터베이스 호스팅), <strong>Vercel</strong>
            {" "}(프론트엔드 호스팅) — 서비스 인프라를 제공하는 클라우드 사업자로, 이용자가
            입력한 데이터가 이들 서버에 저장됩니다.
          </li>
        </ul>
        <p>이 외의 목적으로 개인정보를 제3자에게 제공하지 않습니다.</p>
      </section>

      <section className="flex flex-col gap-2 text-sm leading-relaxed text-gray-700">
        <h2 className="font-semibold text-gray-900">5. 이용자의 권리</h2>
        <p>
          이용자는 언제든지 자신의 개인정보 열람·정정·삭제를 요청할 수 있습니다. 아래 문의처로
          연락 주시면 확인 후 지체 없이 조치합니다.
        </p>
      </section>

      <section className="flex flex-col gap-2 text-sm leading-relaxed text-gray-700">
        <h2 className="font-semibold text-gray-900">6. 로그인 정보 저장 방식</h2>
        <p>
          로그인 상태 유지를 위한 인증 토큰은 브라우저의 로컬 스토리지(localStorage)에
          저장되며, 별도의 추적용 쿠키는 사용하지 않습니다.
        </p>
      </section>

      <section className="flex flex-col gap-2 text-sm leading-relaxed text-gray-700">
        <h2 className="font-semibold text-gray-900">7. 문의처</h2>
        <p>
          개인정보 관련 문의는{" "}
          <a href="mailto:kang42000@gmail.com" className="text-primary-600 underline">
            kang42000@gmail.com
          </a>
          으로 연락해 주세요.
        </p>
      </section>
    </div>
  );
}
