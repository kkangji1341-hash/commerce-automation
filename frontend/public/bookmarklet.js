(function () {
  "use strict";

  // API_BASE is injected by the trigger snippet as window.__PDC_API_BASE__ before this
  // script loads. Falls back to production if not set.
  var API_BASE = window.__PDC_API_BASE__ || "https://backend-production-bce0.up.railway.app";

  function sanitizeFilename(name) {
    return (name || "product_images").replace(/[\\/:*?"<>|]+/g, "_").trim().slice(0, 60) || "product_images";
  }

  async function run() {
    var overlay = document.createElement("div");
    overlay.style.cssText =
      "position:fixed;top:16px;right:16px;z-index:2147483647;background:#111827;color:#fff;" +
      "padding:10px 16px;border-radius:8px;font:14px/1.4 sans-serif;box-shadow:0 4px 12px rgba(0,0,0,.3)";
    overlay.textContent = "이미지 URL 수집 중...";
    document.body.appendChild(overlay);

    try {
      // 1단계: 지금 보고 있는 페이지의 <img> 태그에서 URL만 모은다.
      // (여기까진 CORS 문제 없음 — src를 읽는 건 항상 허용된다.)
      var imgs = Array.prototype.slice
        .call(document.querySelectorAll("img"))
        .filter(function (img) {
          return img.naturalWidth >= 200 && img.naturalHeight >= 200 && img.src && img.src.indexOf("data:") !== 0;
        })
        .map(function (img) {
          return img.src;
        });

      var unique = Array.from(new Set(imgs)).slice(0, 60);
      if (unique.length === 0) {
        overlay.textContent = "200px 이상 이미지를 찾지 못했습니다";
        setTimeout(function () {
          overlay.remove();
        }, 3000);
        return;
      }

      // 2단계: URL 목록만 우리 서버로 보낸다. 실제 다운로드는 서버가 대신 한다 —
      // 이미지 CDN이 대부분 CORS를 안 열어줘서 브라우저가 직접 받으면 거의 다 실패한다
      // (onch3.co.kr 이미지로 실측 확인: fetch() 전부 실패, canvas도 동일한 이유로 막힘).
      overlay.textContent = "서버에서 이미지 " + unique.length + "개 내려받는 중...";
      var res = await fetch(API_BASE + "/api/v1/scrape/zip-from-urls", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ image_urls: unique, filename: document.title }),
      });

      if (!res.ok) {
        throw new Error("서버 오류 (" + res.status + ")");
      }

      var blob = await res.blob();
      var a = document.createElement("a");
      a.href = URL.createObjectURL(blob);
      a.download = sanitizeFilename(document.title) + ".zip";
      document.body.appendChild(a);
      a.click();
      a.remove();

      overlay.textContent = "완료! ZIP 다운로드됨 (최대 " + unique.length + "개 시도)";
      setTimeout(function () {
        overlay.remove();
      }, 4000);
    } catch (err) {
      overlay.textContent = "오류: " + err.message;
      setTimeout(function () {
        overlay.remove();
      }, 5000);
    }
  }

  run();
})();
