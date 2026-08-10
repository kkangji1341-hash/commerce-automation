export default function TermsPage() {
  return (
    <div className="mx-auto flex max-w-2xl flex-col gap-6 p-4 pb-20 sm:p-6">
      <div>
        <h1 className="text-2xl font-bold text-gray-900">이용약관</h1>
        <p className="mt-1 text-sm text-gray-500">시행일: 2026년 8월 11일</p>
      </div>

      <section className="flex flex-col gap-2 text-sm leading-relaxed text-gray-700">
        <h2 className="font-semibold text-gray-900">제1조 (목적)</h2>
        <p>
          이 약관은 상품선정 & 키워드분석(이하 "서비스")이 제공하는 키워드 분석, 상품명 자동
          생성, 마진 계산, 상세페이지 이미지 수집 등의 기능 이용과 관련해 서비스와 이용자의
          권리·의무 및 책임사항을 정합니다.
        </p>
      </section>

      <section className="flex flex-col gap-2 text-sm leading-relaxed text-gray-700">
        <h2 className="font-semibold text-gray-900">제2조 (서비스의 내용)</h2>
        <p>서비스는 다음 기능을 제공합니다.</p>
        <ul className="list-disc pl-5">
          <li>네이버 검색광고/검색 API 기반 키워드 검색량·경쟁도 분석</li>
          <li>세부 키워드 조합 기반 상품명 자동 생성</li>
          <li>원가 입력 기반 판매가·마진 계산</li>
          <li>온채널(onch3.co.kr) 상세페이지 이미지 수집 도구 및 브라우저 북마크렛</li>
        </ul>
        <p>
          검색량·경쟁도·평균가 등 데이터는 네이버 등 외부 API가 제공하는 값을 그대로 표시하며,
          서비스가 임의로 만들어내지 않습니다. 다만 외부 API의 응답 지연·오류·정책 변경으로
          일부 데이터가 일시적으로 제공되지 않을 수 있습니다.
        </p>
      </section>

      <section className="flex flex-col gap-2 text-sm leading-relaxed text-gray-700">
        <h2 className="font-semibold text-gray-900">제3조 (회원가입 및 계정)</h2>
        <p>
          이용자는 이메일과 비밀번호로 회원가입할 수 있으며, 회원가입 시 기재한 정보는
          정확해야 합니다. 계정 정보(비밀번호 등)의 관리 책임은 이용자 본인에게 있으며,
          제3자에 의한 부정 이용에 대해 서비스는 책임지지 않습니다.
        </p>
      </section>

      <section className="flex flex-col gap-2 text-sm leading-relaxed text-gray-700">
        <h2 className="font-semibold text-gray-900">제4조 (이용자의 의무)</h2>
        <p>이용자는 다음 행위를 해서는 안 됩니다.</p>
        <ul className="list-disc pl-5">
          <li>
            상세페이지 수집기 및 북마크렛으로 수집한 이미지를, <strong>판매 승인을 받지 않은
            상품</strong>에 무단으로 사용하는 행위 — 온채널 등 공급사는 상세페이지 이미지에
            대한 저작권을 보유하며, 승인된 판매자만 사용할 수 있습니다. 이를 위반해 발생하는
            법적 책임은 전적으로 이용자 본인에게 있습니다.
          </li>
          <li>서비스가 제공하지 않는 방식(자동화된 대량 요청, 인증 우회 등)으로 시스템에 부하를
            주거나 다른 이용자의 이용을 방해하는 행위</li>
          <li>타인의 계정을 무단으로 사용하는 행위</li>
          <li>관계 법령을 위반하는 목적으로 서비스를 이용하는 행위</li>
        </ul>
      </section>

      <section className="flex flex-col gap-2 text-sm leading-relaxed text-gray-700">
        <h2 className="font-semibold text-gray-900">제5조 (책임의 제한)</h2>
        <p>
          서비스가 제공하는 검색량·마진·상품명 등은 참고용 정보이며, 실제 판매 성과나 수익을
          보장하지 않습니다. 이용자는 서비스가 제공하는 정보를 참고해 최종 판단과 결정을
          스스로 내려야 하며, 그로 인해 발생하는 결과에 대해 서비스는 책임을 지지 않습니다.
        </p>
        <p>
          서비스는 무료로 제공되며, 관련 법령이 허용하는 범위에서 서비스 중단·데이터 손실 등에
          대한 책임을 지지 않습니다.
        </p>
      </section>

      <section className="flex flex-col gap-2 text-sm leading-relaxed text-gray-700">
        <h2 className="font-semibold text-gray-900">제6조 (약관의 변경)</h2>
        <p>
          서비스는 필요한 경우 이 약관을 변경할 수 있으며, 변경 시 서비스 내 공지 또는 이
          페이지 갱신을 통해 안내합니다.
        </p>
      </section>

      <section className="flex flex-col gap-2 text-sm leading-relaxed text-gray-700">
        <h2 className="font-semibold text-gray-900">제7조 (문의)</h2>
        <p>
          서비스 이용과 관련한 문의는{" "}
          <a href="mailto:kang42000@gmail.com" className="text-primary-600 underline">
            kang42000@gmail.com
          </a>
          으로 연락해 주세요.
        </p>
      </section>
    </div>
  );
}
