# 📊 실시간 시세 자동 추적 보고서

> 비트코인(BTC/KRW) & 테슬라(TSLA) 시세를 **5분마다 자동 업데이트**합니다.

---

## 📈 최신 시세 보고서

👉 **[REPORT.md](./REPORT.md)** 에서 최신 데이터를 확인하세요.

---

## 🔄 자동화 방식

- **GitHub Actions** 스케줄러 (`*/5 * * * *`) 로 5분마다 실행
- **CoinGecko API** → BTC/KRW 현재가, 변화율, 거래량, 시가총액
- **Yahoo Finance API** → TSLA 현재가, 변화율, 52주 고/저

## 📁 파일 구조

```
bitcoin/
├── REPORT.md              # 최신 시세 보고서 (자동 업데이트)
├── data/
│   └── history.json       # 시세 히스토리 (최근 24시간 / 288개)
├── scripts/
│   └── update_report.py   # 데이터 수집 & 보고서 생성 스크립트
└── .github/workflows/
    └── update.yml         # GitHub Actions 워크플로우
```

## ⚠️ GitHub Actions 활성화 방법

레포지토리를 포크한 경우 **Actions 탭**에서 워크플로우를 수동으로 활성화해야 합니다.
