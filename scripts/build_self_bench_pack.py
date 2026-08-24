#!/usr/bin/env python3
"""
자체 모델 테스트 프롬프트 팩 빌더 (self_bench_pack.json)
- TokenChaser 수집 84개의 구조·개념만 참고, 원문은 복사하지 않음
- 핵심 확장: 모든 산출물이 한국어+영어 이중언어(바이링궐) 출력

실행: python3 scripts/build_self_bench_pack.py
산출: packs/self-bench-pack-v1.json
"""
import json, os

# 공통 바이링궐 요구 모듈 (각 프롬프트에 조합되어 들어감)
BILINGUAL_COMMON = """
## Language Requirements (중요)
- All user-visible UI text must appear in BOTH Korean and English (한국어 + 영어).
- Default language: Korean. Include a working language toggle button (KO/EN) that switches all visible text instantly without reloading.
- No half-translated strings: when KO is active, every label/button/message must be Korean; when EN is active, every label must be English.
- Render Korean correctly: use a proper Korean font stack (e.g. 'Noto Sans KR', 'Nanum Gothic', 'Malgun Gothic', Apple SD Gothic Neo) with sensible fallbacks. UTF-8 encoding only. No mojibake (깨진 글자 금지).
- Prefer compact Korean phrasing (e.g. '저장' not '저장하기 버튼') and natural English equivalents.
- If the app shows content categories, dates, or units, localize those too (e.g. '2026년 8월 18일' ↔ 'Aug 18, 2026').
- At the end of your answer, add a short section '## 이중언어 안내 / Bilingual Note' in both Korean and English: 2-3 sentences each describing the app and how to use the language toggle.
"""

QA_COMMON = """
## Quality Bar
- Polished, modern visual design with a consistent color system and typography.
- Smooth animations and hover/active states on interactive elements.
- Responsive layout that works on desktop and mobile widths.
- No external libraries or CDNs: everything (CSS/JS/fonts) must be self-contained in the single file or served locally.
- No placeholder text ('TODO', 'lorem ipsum'). Every visible element should be real.
"""

# 에이전트 자기개선 루프 — 모든 프롬프트에 포함 (단발 생성이 아닌 스스로 테스트·검증·수정)
SELF_TEST_COMMON = """
## Self-Test & Verification Loop (필수 — 이 지시는 절대 건너뛰지 마세요)
당신은 AI 에이전트입니다. 위 산출물을 만든 뒤 **반드시 스스로 테스트하고 검증한 다음, 문제가 있으면 고쳐서 다시 제출**해야 합니다. 한 번에 응답만 주고 끝내는 방식은 금지입니다.

1. **생성 → 테스트 사이클**: 산출물(HTML 파일 등)을 실제 파일로 만든다.
2. **스스로 실행해보기**: 가능하면 헤드리스 브라우저(Playwright/Chrome) 또는 로컬 서버(`python3 -m http.server`)로 직접 열어서 동작을 확인한다. 도구가 없으면 최소한 코드를 정적 분석하고 실행 가능한 문법인지 확인한다.
3. **검증 체크리스트** (모두 확인):
   - [ ] 페이지/앱이 에러 없이 로드되는가 (콘솔 오류 0건)
   - [ ] 요구된 기능이 전부 구현되고 실제로 동작하는가 (버튼 클릭, 입력, 토글, 게임 플레이)
   - [ ] 이중언어: 모든 UI 텍스트에 한국어·영어가 모두 있고, KO/EN 토글 버튼이 즉시 동작하는가 (반쪽 번역 없음)
   - [ ] 한글이 깨지지 않는가 (폰트/UTF-8, � 문자가 없어야 함)
   - [ ] 외부 CDN/라이브러리를 쓰지 않았는가 (자체 포함)
   - [ ] 모바일/데스크톱 너비에서 레이아웃이 깨지지 않는가
4. **문제 발견 시**: 코드를 수정하고 다시 테스트한다. 최대 5회 반복. 그래도 안 되면 남은 문제를 마지막에 명확히 보고한다.
5. **최종 제출**: 고친 최종 결과물 + 간단한 자기 검증 보고서(테스트한 항목, 발견·수정한 버그, 남은 문제)를 응답 끝에 함께 제출한다. 보고서는 한국어로 쓴다.
"""

def P(pid, cat, title, body):
    return {
        "id": pid,
        "title": title,
        "category": cat,
        "text": body + "\n" + SELF_TEST_COMMON,
        "source": "SELF (design 2026-08-18, inspired by tokenchaser.net structure)",
        "source_video": "자체 설계 — TokenChaser 84개 패턴 분석 기반"
    }

prompts = []

# ================= UI (9) =================
ui_prompts = [
    P("self-ui-01", "ui", "한국 주식 대시보드",
      "Create a Korean stock market dashboard in a single HTML file. It shows a fictional but realistic KOSPI/KOSDAQ watchlist: 8 stocks with Korean company names (삼성전자, SK하이닉스, LG에너지솔루션, NAVER, 카카오, 현대차, 기아, 셀트리온), current price, change %, and a 7-day sparkline for each. Include a market summary header (지수/등락), a searchable filter, and a detail view modal when clicking a stock (open/high/low/volume + a 30-day mini chart drawn with canvas or SVG).\n\n"
      + BILINGUAL_COMMON + "\n" + QA_COMMON),

    P("self-ui-02", "ui", "인터랙티브 서울 지하철 노선도",
      "Build an interactive Seoul subway line map in a single HTML file. Render at least 4 real lines (숭실대입구 스타일의 실제 역 이름 사용: 1호선 서울역·시청, 2호선 강남·홍대입구, 3호선 고속터미널·잠실, 4호선 혜화·사당) as colored lines with stations as draggable-map nodes. Clicking a station shows transfer info, nearby landmarks, and estimated travel time to another selected station. Support drag-to-pan and pinch/scroll zoom. All station names and tooltips bilingual.\n\n"
      + BILINGUAL_COMMON + "\n" + QA_COMMON),

    P("self-ui-03", "ui", "한식당 디지털 메뉴판",
      "Create a digital menu app for a Korean restaurant in a single HTML file. Menu categories: 김치찌개, 비빔밥, 불고기, 삼겹살, 잡채, 떡볶이, 순대국, 갈비탕. Each item card shows an emoji-based dish illustration, price in KRW (₩), spice level (🌶🌶🌶), and a short description. Features: category tabs, cart with quantity controls, order summary with total (합계/부가세), and a '주문하기' checkout flow with a fake payment success screen. Bilingual everywhere.\n\n"
      + BILINGUAL_COMMON + "\n" + QA_COMMON),

    P("self-ui-04", "ui", "한국어 단어장 플래시카드",
      "Build a Korean vocabulary flashcard web app in a single HTML file: a deck of 20 essential Korean words with English translations (e.g. 사과/apple, 책/book, 학교/school, 시간/time, 친구/friend), example sentences, and TTS-free pronunciation guide (romanization). Study modes: flip card, multiple-choice quiz (사지선다), and spaced-repetition progress bars per word. Track correct/incorrect counts and show a completion screen when all words are mastered. Include a small stats section (정답률/진행률).\n\n"
      + BILINGUAL_COMMON + "\n" + QA_COMMON),

    P("self-ui-05", "ui", "대한민국 관광 브로슈어 웹사이트",
      "Design a responsive travel brochure website for South Korea in a single HTML file. Sections: hero with a Seoul skyline scene (pure CSS/SVG), 4 destination cards (제주도, 부산, 경주, 강원도) with weather-friendly color themes, a food highlight strip, a culture section (한복, 한옥, 다도), and a contact/booking footer. Eye-catching hero animation on load, smooth scroll navigation with an always-visible top nav, and a back-to-top button.\n\n"
      + BILINGUAL_COMMON + "\n" + QA_COMMON),

    P("self-ui-06", "ui", "전통시장 중고거래 마켓플레이스",
      "Create a Korean flea-market marketplace app UI in a single HTML file. Listings show used items (중고 가구, 전자기기, LP판, 수제공예) with photos simulated by CSS art or gradients, seller nickname, price in ₩, and a '희망 가격' badge. Features: search bar with category filter chips, sort by price/newest, wishlist heart toggle with a counter, and a chat-style inquire modal. Aisle-style layout inspired by traditional markets (남대문 느낌의 warm color palette).\n\n"
      + BILINGUAL_COMMON + "\n" + QA_COMMON),

    P("self-ui-07", "ui", "K-POP 차트 뮤직 플레이어",
      "Build a K-POP chart music player in a single HTML file. A top-10 chart list with fictional but plausible song/artist names (e.g. '밤하늘 Dance', 'City Pop Drive', '겨울 편지'), each row with rank, title, artist, and play button. Clicking play shows a full player: rotating vinyl/CD cover art (CSS), progress bar, play/pause, next/prev, shuffle, loop, and volume. Add an animated audio visualizer (canvas bars) that reacts to a Web Audio API synthesized tone. Chart can be filtered by genre tabs (댄스/발라드/R&B/인디).\n\n"
      + BILINGUAL_COMMON + "\n" + QA_COMMON),

    P("self-ui-08", "ui", "실시간 날씨 대시보드 (국내 6개 도시)",
      "Create a weather dashboard for 6 South Korean cities (서울, 부산, 인천, 대구, 대전, 광주) in a single HTML file. Show current temperature, condition with animated icons (sunny/rain/snow/cloudy — CSS keyframe animations, no images), humidity, wind, and a 5-day forecast strip. A large city card switches with a temperature unit toggle (°C/°F) and a light/dark theme toggle. Simulated live 'now' data with smooth updates every 5 seconds (gently varying values), clearly labeled as simulated.\n\n"
      + BILINGUAL_COMMON + "\n" + QA_COMMON),

    P("self-ui-09", "ui", "아이폰 홈화면 스타일 커스텀 런처 대시보드",
      "Build an iOS-style home screen launcher in a single HTML file: wallpaper with a subtle animated gradient, app grid with 12 fictional Korean apps (메모, 달력, 사진, 지도, 날씨, 계산기, 설정, 음악, 메일, 카메라, 지갑, 건강) with custom SVG/emoji icons, a dock with 4 apps, a status bar (time, battery, signal), and notifications badges. Tapping an app opens a smooth animated modal with icon-bounce and a back gesture. Includes Ambient Light/Dark auto theme and a haptic-like press animation.\n\n"
      + BILINGUAL_COMMON + "\n" + QA_COMMON),
]
prompts += ui_prompts

# ================= GAME (8) =================
game_prompts = [
    P("self-game-01", "game", "한국어 오목 (인공지능 대전)",
      "Create a playable Omok (오목, five-in-a-row) game in a single HTML file: a 15x15 board rendered on canvas, playable vs a simple AI opponent (or 2-player local hotseat toggle). Stone placement with smooth drop animation and captured-point counting (흑돌/백돌). Win detection for 5 in a row with a highlighted winning line, win/lose/draw screens with score history (전적). Include game options: board theme (나무/다크), sound effects via Web Audio beeps, and an undo-last-move button.\n\n"
      + BILINGUAL_COMMON + "\n" + QA_COMMON),

    P("self-game-02", "game", "제주 감귤 수확 캐치 게임",
      "Build a Jeju tangerine harvest catch game in a single HTML file: tangerines (감귤) fall from the top with varying speed, the player moves a basket (바구니) with mouse/touch/keyboard to catch them. Catch counting with combo multiplier, occasional bonus items (곶감, 한라봉) and penalty items (돌멩이). Three difficulty stages by score threshold with a stage-up animation. Game over screen with final score, best score saved to localStorage, and a cheerful Jeju color palette (tangerine orange + sea green).\n\n"
      + BILINGUAL_COMMON + "\n" + QA_COMMON),

    P("self-game-03", "game", "한글 타자 연습 게임",
      "Create a Korean typing tutor game in a single HTML file: Korean words (가나다라... level-based: 2-자 낱말 → 4-자 단어 → 속담/문장) fall like comets from the top; the player types them with the keyboard using Korean IME mapping, and correct typing destroys the comet with a particle explosion. Show typing accuracy, WPM-equivalent in 글자/분, and a live error counter. A virtual Korean keyboard display highlights the next key to press. Leaderboard of best scores in localStorage.\n\n"
      + BILINGUAL_COMMON + "\n" + QA_COMMON),

    P("self-game-04", "game", "매트릭스 스타일 한글 낙하 코드 워즈",
      "Build a Matrix-style falling-code word game in a single HTML file: green falling columns of Hangul syllables (가나다라마바사아자차카타파하 + random compounds) with a hacker terminal aesthetic. The player types the glowing highlighted syllable before it reaches the bottom. Increasing speed and multi-column spawn. Score with streak multiplier, lives (3 생명), and a 'SYSTEM FAILURE' game-over screen with restart. Digital rain background effect, monospace font, scanline overlay.\n\n"
      + BILINGUAL_COMMON + "\n" + QA_COMMON),

    P("self-game-05", "game", "한국 전통 설날 민속놀이 번들",
      "Create a Korean folk-game bundle in a single HTML file with 3 playable mini-games: ① 윷놀이 (Yut Nori) — 4-stick toss simulation with a board path and 2 player markers, ② 제기차기 (Jegichagi) — timing-based kick game with combo counter, ③ 투호 (Tuho) — arrow-into-jar aiming game with wind physics. A hub screen with three doors styled like a traditional hanok (한옥) entrance. Overall cozy seollal (설날) theme with 랜덤 상품상자 reward animation after each game.\n\n"
      + BILINGUAL_COMMON + "\n" + QA_COMMON),

    P("self-game-06", "game", "호랑이 달리기 러너 (장수풍뎅이 스타일)",
      "Build a side-scrolling runner game in a single HTML file starring a friendly Korean tiger (호랑이) character drawn with pure CSS/SVG: run/jump/double-jump over obstacles (바위, 나무, 연못) with gravity physics. Collect coin-like golden persimmons (감) for score and a special mask-rescue item. Parallax mountain/hanok background, day-night cycle every 60 seconds. Increasing speed to a sunset 'golden hour' finale at 500 points. Game over with distance traveled and best-distance record.\n\n"
      + BILINGUAL_COMMON + "\n" + QA_COMMON),

    P("self-game-07", "game", "기억력 카드 뒤집기 (한국 문화 테마)",
      "Create a memory-matching card game in a single HTML file: a 4x4 grid of cards showing 8 pairs of Korean cultural symbols (한복, 탈춤, 사물놀이, 김치, 불국사, 한옥, 다도, 태권도) drawn as CSS/SVG art. Flip animation with 3D rotation; match two cards for a pair; mismatches cost time; a 90-second timer with a tension soundtrack (Web Audio chiptune). Score by pairs + remaining time bonus. Difficulty select (4x4 / 6x4) and a victory screen with confetti.\n\n"
      + BILINGUAL_COMMON + "\n" + QA_COMMON),

    P("self-game-08", "game", "KTX 타이쿤 티켓 발권 시뮬레이터",
      "Create a KTX train ticket simulator game in a single HTML file: the player queues passengers and prints the correct ticket based on their spoken needs (displayed as speech bubbles): destination city (서울/부산/대전/광주/목포), seat class (일반/특실), and departure time. Select the right route+seat on a ticketing console UI, hit 발권, and earn coins per correct ticket; wrong ones cost a life. 10 customers per day, 3 days to beat the high score. Coin shop to unlock console skins. Retro CRT-ticket printer animation.\n\n"
      + BILINGUAL_COMMON + "\n" + QA_COMMON),
]
prompts += game_prompts

# ================= SERVICE (4) — VPS 개념을 GB10 로컬 배포로 변형 =================
# 시크릿 없음, 로컬 포트/디렉토리는 [LOCAL] 토큰으로 마스킹
SVC_COMMON = """
## Execution Rules
- Run all commands on the LOCAL development machine (주어진 로컬 서버, Ubuntu Linux) — not a cloud VPS.
- Use [LOCAL_PORT] for the web port and [LOCAL_DIR] for the project directory. Do not hardcode real secrets.
- Deliverables: URL to open, files changed, how you verified it works (실행 명령 포함).
"""
svc_prompts = [
    P("self-svc-01", "service", "로컬 GPU 상태 모니터링 대시보드",
      "You have access to a local Ubuntu machine with an NVIDIA GPU. Build and deploy a live web dashboard on this machine that shows real GPU/CPU stats: nvidia-smi output (GPU name, utilization %, VRAM used/total, temperature, power draw), CPU load average, RAM usage, disk usage, and uptime. The dashboard must poll live data (or auto-refresh) and update its charts without manual reload. Requirements: accessible from [LOCAL_PORT] in a browser, clean dashboard UI with both gauges and sparkline history, dark theme. Don't overengineer it. Verify it works end-to-end.\n\n"
      + BILINGUAL_COMMON + "\n" + SVC_COMMON),

    P("self-svc-02", "service", "로컬 한글 블로그/메모 서버",
      "Set up a local-first blog & memo web server on this machine: serves markdown files from [LOCAL_DIR] as a read-friendly blog with a post list, tag filtering, and a simple write flow (new post creation via web form that saves a .md file). Features: syntax-highlighted code blocks, dark/light toggle, RSS feed endpoint, and a lightweight full-text search over post contents. Deploy it as a background service that survives terminal close and restarts on boot (systemd or equivalent). Verify: create a sample post titled '첫 번째 글' through the web UI and confirm it appears in the list and RSS.\n\n"
      + BILINGUAL_COMMON + "\n" + SVC_COMMON),

    P("self-svc-03", "service", "로컬 미디어 파일 인덱서 + 검색 웹앱",
      "Build a local media-file indexer web app: scans [LOCAL_DIR] for images/videos/audio, builds a searchable index (filename, type, size, modified date, dimensions/hash where feasible), and serves a browse UI with grid/table views, filters by extension, and instant search-as-you-type. Clicking an item shows metadata and a preview (media element or image thumbnail) served locally. Auto-rescan trigger button plus a scheduled rescan every hour. Expose a JSON API at /api/search?q= for automation. Verify: index at least 50 files in a sample folder and show search results for 'mp4'.\n\n"
      + BILINGUAL_COMMON + "\n" + SVC_COMMON),

    P("self-svc-04", "service", "로컬 RSS 뉴스 리더 + 요약 서버",
      "Create a local RSS news reader with a summary server: fetches a configured list of Korean tech RSS feeds (한국어 기술 뉴스 3개 피드), shows a unified feed list with unread counts per source, marks items as read, and caches articles locally. Add a '요약' (summarize) button per article that calls a local LLM endpoint (OpenAI-compatible at [LOCAL_LLM_ENDPOINT]) and displays a 3-sentence Korean summary with a regenerate option. Deploy on [LOCAL_PORT] as a background service. Verify: feeds load, at least one summary is generated and displayed.\n\n"
      + BILINGUAL_COMMON + "\n" + SVC_COMMON),
]
prompts += svc_prompts

# ================= PROGRESSIVE (3) — Phase 확장, 재구축 금지 =================
PROG_COMMON = """
## Expansion Rule
- Start from Phase 1 only. You will be asked to extend it in later phases WITHOUT rebuilding from scratch — keep the existing code structure, styles, and data, and add features on top. If a feature requires refactoring, do it minimally and preserve the app's visual identity.
"""
prog_prompts = [
    P("self-prog-01", "progressive", "한국어 학습 플랫폼 (Phase 1→2→3)",
      "Phase 1: Create a Korean language learning platform in a single HTML file: a landing page with hero ('한국어를 배워봐요 — Learn Korean') and a lesson list of 5 units (한글 자모, 인사말, 음식, 쇼핑, 길찾기), each showing progress 0%. Clicking a unit opens a lesson screen with vocab flashcards. Data in a simple JS object, clean educational design.\n\n"
      + PROG_COMMON + "\n"
      + BILINGUAL_COMMON + "\n" + QA_COMMON),

    P("self-prog-02", "progressive", "한국어 학습 플랫폼 (2단계 확장)",
      "Phase 2: Expand the existing Korean learning platform from Phase 1. Do NOT rebuild from scratch. Add: a quiz engine per unit (multiple-choice + fill-in-the-blank), scoring with immediate feedback (정답/오답 애니메이션), a progress system that persists to localStorage and updates lesson progress %, and a dashboard view with overall completion ring chart. Also add a review mode that re-quizzes only the questions answered wrong.\n\n"
      + PROG_COMMON + "\n"
      + BILINGUAL_COMMON + "\n" + QA_COMMON),

    P("self-prog-03", "progressive", "한국어 학습 플랫폼 (3단계 확장)",
      "Phase 3: Expand the existing Korean learning platform from Phases 1-2. Do NOT rebuild from scratch. Add: a gamified streak system (연속 학습 일수 with a flame icon), daily goals, achievement badges (badge collection screen), a simple leaderboard mock, and a speaking practice section using Web Speech API (read a word, the app checks basic audio is detected and shows encouragement). Final polish: consistent animation language, empty-state illustrations, and a full app walkthrough guide modal on first visit.\n\n"
      + PROG_COMMON + "\n"
      + BILINGUAL_COMMON + "\n" + QA_COMMON),
]
prompts += prog_prompts

# ================= 패킹 =================
by_cat = {}
for p in prompts:
    by_cat.setdefault(p["category"], []).append(p)

pack = {
    "meta": {
        "name": "Self Bench Pack (KO/EN Bilingual) — GB10 로컬 LLM",
        "description": "TokenChaser 84개 수집 프롬프트의 구조·개념만 참고해 자체 설계한 24개 프롬프트. "
                       "모든 산출물이 한국어+영어 이중언어 출력을 요구 (언어 토글·한글 폰트·UTF-8). "
                       "원문 복사 없음, 전 항목 자체 작성.",
        "source": "SELF-DESIGNED (2026-08-18) — inspired by tokenchaser.net prompt structure",
        "collected": "2026-08-18",
        "localized": True,
        "model_token": "MODEL_NAME",
        "usage": "오픈코드 에이전트(백본: 8080 qwen3.5-35b)가 각 프롬프트를 받아 스스로 생성→테스트→검증→수정 루프를 돌린다. "
                 "단발 1회 생성이 아니라, 전 프롬프트에 내장된 'Self-Test & Verification Loop' 지시로 에이전트가 "
                 "헤드리스 브라우저/로컬 서버로 직접 동작을 검증하고 버그를 고쳐 최종 결과물 + 한국어 검증 보고서를 제출한다. "
                 "평가 축: ①이중언어 완성도(KO/EN 커버리지·토글 동작) ②한글 렌더링(폰트·인코딩 깨짐) "
                 "③지시 준수율 ④UI/시각 완성도 ⑤기능 동작·버그 수 ⑥자기검증 충실도(루프 수행 여부·보고서 품질) ⑦(프로그레시브) 확장 유지력.",
        "scoring_axes": [
            "bilingual_coverage", "korean_rendering", "instruction_compliance",
            "ui_quality", "functionality", "self_verification", "progressive_retention"
        ],
    },
    "categories": {
        "ui": {"label": "단일 HTML UI/앱 (한영 이중언어)", "prompts": by_cat["ui"]},
        "game": {"label": "단일 HTML 게임 (한영 이중언어)", "prompts": by_cat["game"]},
        "service": {"label": "로컬 배포 서비스 (VPS 변형, 한영 이중언어)", "prompts": by_cat["service"]},
        "progressive": {"label": "점진적 확장 (Phase 1→2→3, 재구축 금지)", "prompts": by_cat["progressive"]},
    },
    "all": prompts,
}

out = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "packs", "self-bench-pack-v1.json")
with open(out, "w", encoding="utf-8") as f:
    json.dump(pack, f, ensure_ascii=False, indent=1)

# 검증
assert len(prompts) == 24, f"expected 24, got {len(prompts)}"
ids = [p["id"] for p in prompts]
assert len(set(ids)) == len(ids), "duplicate ids"
for p in prompts:
    assert "Language Requirements" in p["text"] or "이중언어" in p["text"], p["id"]
    assert "Self-Test & Verification Loop" in p["text"], f"self-test missing in {p['id']}"
    assert "모델" not in p["text"] or True  # MODEL_NAME 토큰은 이번 팩에선 미사용(자체설계이므로)
    # 원문 복사 여부 스팟 체크: 수집 팩의 독특한 문구가 들어있는지
    for banned in ["Windows-style desktop", "iPhone frame", "re.split prompt-block", "CLAUDE/GPT"]:
        assert banned.lower() not in p["text"].lower(), f"copied content in {p['id']}: {banned}"
print(f"OK: {len(prompts)} prompts -> {out}")
from collections import Counter
print("categories:", dict(Counter(p["category"] for p in prompts)))
print("len range:", min(len(p["text"]) for p in prompts), "~", max(len(p["text"]) for p in prompts))