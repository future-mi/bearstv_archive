# 🐻 BEARS TV 2026 아카이브

두산 베어스 공식 유튜브 채널 [BEARS TV](https://www.youtube.com/@bearstv1982) 개인 큐레이션 아카이브.

**🔗 사이트 보기:** https://future-mi.github.io/bearstv_archive

## 구성

- `index.html` — GitHub Pages 배포용 (hover 효과 등 인터랙션 포함)
- `bearstv-archive-theqoo.html` — 더쿠 게시글용 (인라인 스타일, 앵커 동작)
- `generate.py` — CSV → HTML 생성 스크립트
- `data/youtube.csv` — 노션에서 export한 원본 데이터

## 업데이트 방법 (반자동)

1. 노션에서 CSV export → `data/youtube.csv` 로 덮어쓰기
2. `python generate.py` 실행
3. Git에 올리기:
   ```bash
   git add .
   git commit -m "update archive"
   git push
   ```
4. 몇 분 후 GitHub Pages에 자동 반영됨

## 카테고리 (10개)

애프터게임 · 잠실직캠 · 두런두런 · 이천일기 · 베어스티비 · 하이라이트 · 위두미 · 곰지락 · 스프링캠프 · 기타
