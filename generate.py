"""
BEARS TV 2026 아카이브 생성 스크립트

사용법:
1. 노션에서 CSV export → data/youtube.csv 로 저장
2. python generate.py 실행
3. index.html (GitHub Pages용) + bearstv-archive-theqoo.html (더쿠용) 두 파일 생성됨
"""

import pandas as pd
import re
import html
from pathlib import Path

# ===== 경로 설정 =====
BASE_DIR = Path(__file__).parent
CSV_PATH = BASE_DIR / "data" / "youtube.csv"
OUT_INDEX = BASE_DIR / "index.html"
OUT_THEQOO = BASE_DIR / "bearstv-archive-theqoo.html"

# ===== 섹션 설정 =====
SECTIONS = [
    ('애프터게임', 'user_content_0'),
    ('잠실직캠', 'user_content_1'),
    ('두런두런', 'user_content_2'),
    ('이천일기', 'user_content_3'),
    ('베어스티비', 'user_content_4'),
    ('하이라이트', 'user_content_5'),
    ('위두미', 'user_content_6'),
    ('곰지락', 'user_content_7'),
    ('스프링캠프', 'user_content_8'),
    ('기타', 'user_content_9'),
]

# ===== 유틸 함수 =====
def parse_date(date_str):
    m = re.match(r'(\d{4})년\s*(\d{1,2})월\s*(\d{1,2})일', str(date_str))
    if m:
        return int(m.group(1)) * 10000 + int(m.group(2)) * 100 + int(m.group(3))
    return 0

def parse_tags(tag_str):
    if pd.isna(tag_str):
        return []
    return [t.strip() for t in str(tag_str).split(',') if t.strip()]

def get_video_id(url):
    m = re.search(r'watch\?v=([^&]+)', str(url))
    return m.group(1) if m else None

def format_title(title):
    t = html.escape(str(title))
    t = re.sub(r'\[([^\]]+)\]', 
               r'<span style="color:#0A1330;font-weight:700;">[\1]</span>', t)
    t = re.sub(r'\((\d{1,2}\.\d{1,2})\)', 
               r'<span style="font-family:\'IBM Plex Mono\',Consolas,monospace;font-size:13px;color:#5C5651;">(\1)</span>', t)
    return t

# ===== 데이터 로드 =====
print(f"CSV 로딩: {CSV_PATH}")
df = pd.read_csv(CSV_PATH)
df['sort_key'] = df['게시일'].apply(parse_date)
df['tags_list'] = df['태그'].apply(parse_tags)
df['video_id'] = df['URL'].apply(get_video_id)
print(f"총 {len(df)}개 영상 로드됨")

# ===== 카드 HTML 생성 =====
def video_card_html(video):
    vid = video['video_id']
    url = video['URL']
    title = format_title(video['제목'])
    thumb = f"https://img.youtube.com/vi/{vid}/hqdefault.jpg"
    return f'''          <td style="width:50%; vertical-align:top; padding:8px;">
            <a href="{url}" target="_blank" rel="noreferrer noopener" style="text-decoration:none; color:#1A1512; display:block;">
              <img src="{thumb}" alt="{html.escape(str(video['제목'])[:40])}" width="480" height="360" style="width:100%; height:auto; aspect-ratio:4/3; display:block; border-radius:2px; border:0;">
              <div style="font-family:'Gowun Batang',serif; font-size:15px; line-height:1.55; color:#1A1512; font-weight:500; letter-spacing:-0.005em; word-break:keep-all; padding:10px 4px 0;">
                {title}
              </div>
            </a>
          </td>'''

# ===== 섹션 HTML 조립 =====
section_html_parts = []
section_counts = {}
total_cards = 0

for cat, anchor_id in SECTIONS:
    cat_videos = df[df['tags_list'].apply(lambda tags: cat in tags)].sort_values('sort_key', ascending=False)
    count = len(cat_videos)
    section_counts[cat] = count
    total_cards += count
    count_str = f"{count:02d}"
    unit = "video" if count == 1 else "videos"
    
    section_html_parts.append(f'''
  <tr>
    <td style="padding:24px 24px 8px;">
      <a href="#{anchor_id}" name="{anchor_id}" id="{anchor_id}" style="font-family:'IBM Plex Mono',Consolas,monospace; font-size:11px; letter-spacing:0.24em; color:#5C5651; text-transform:uppercase; padding-bottom:10px; border-bottom:1px solid #D9CFB7; display:block; text-decoration:none;">
        {cat} &nbsp;/&nbsp; <b style="color:#0A1330;">{count_str}</b> {unit}
      </a>
    </td>
  </tr>''')
    
    videos_list = cat_videos.to_dict('records')
    rows_html = []
    for i in range(0, len(videos_list), 2):
        left = video_card_html(videos_list[i])
        right = video_card_html(videos_list[i+1]) if i + 1 < len(videos_list) else '          <td style="width:50%; padding:8px;">&nbsp;</td>'
        rows_html.append(f'''
      <table cellpadding="0" cellspacing="0" border="0" style="width:100%; border-collapse:separate; border-spacing:8px;">
        <tr>
{left}
{right}
        </tr>
      </table>''')
    
    grid_html = '\n'.join(rows_html)
    section_html_parts.append(f'''
  <tr>
    <td style="padding:8px 16px 16px;">{grid_html}
    </td>
  </tr>''')

# 상단 칩 (5개마다 줄바꿈)
chip_htmls = []
for i, (cat, anchor_id) in enumerate(SECTIONS):
    chip_htmls.append(f'<a href="#{anchor_id}" title="{cat} 섹션으로 이동" style="text-decoration:none; display:inline-block; padding:6px 14px; margin:3px; background:transparent; border:1px solid #B89B5E; border-radius:999px; font-size:11px; color:#5C5651; letter-spacing:0.02em;">{cat}</a>')
    if (i + 1) % 5 == 0 and i < len(SECTIONS) - 1:
        chip_htmls.append('<br>')
chip_row = '\n      '.join(chip_htmls)

# 공통 콘텐츠 (paste_content)
paste_content = f'''
<table cellpadding="0" cellspacing="0" border="0" style="width:100%; max-width:860px; margin:0 auto; border-collapse:collapse; background:#F4EFE1;">

  <tr>
    <td style="background:#0A1330; padding:32px 24px 28px; text-align:center;">
      <div style="font-family:'IBM Plex Mono',Consolas,monospace; font-size:10px; letter-spacing:0.32em; color:#B89B5E; text-transform:uppercase; margin-bottom:12px;">Doosan Bears &nbsp;·&nbsp; Season 2026</div>
      <div style="font-family:'Gowun Batang',serif; font-size:42px; font-weight:400; line-height:1; color:#F4EFE1; letter-spacing:-0.03em; margin-bottom:10px;">
        BEARS TV
      </div>
      <div style="height:2px; background:#C8102E; width:226px; margin:16px auto 0;"></div>
    </td>
  </tr>

  <tr>
    <td style="background:#EAE0C9; padding:14px 20px; text-align:center; border-bottom:1px solid #D9CFB7;">
      {chip_row}
    </td>
  </tr>
{"".join(section_html_parts)}

  <tr>
    <td style="background:#0A1330; padding:20px 20px; text-align:center;">
      <div style="font-family:'IBM Plex Mono',Consolas,monospace; font-size:10px; letter-spacing:0.2em; text-transform:uppercase; color:#7A7565;">
        Doosan Bears <span style="color:#C8102E; margin:0 6px;">·</span> 무명의 더쿠 박곰 <span style="color:#C8102E; margin:0 6px;">·</span> Fan Made
      </div>
    </td>
  </tr>

</table>
'''

# ===== 검색바 + 맨 위로 버튼 (index.html 전용, 더쿠용에는 넣지 않음) =====
# f-string 밖에 따로 둬서 CSS/JS 중괄호를 이스케이프할 필요 없음
ENHANCE_HTML = r'''
<!-- ===== BEARS TV 아카이브: 검색 + 맨 위로 버튼 (GitHub Pages 전용, 더쿠용 HTML에는 넣지 말 것) ===== -->
<style>
  .bt-head { width:100%; max-width:860px; margin:0 auto; border-collapse:collapse; background:#F4EFE1; }
  .bt-search {
    position: sticky; top: 0; z-index: 20;
    max-width: 860px; margin: 0 auto; box-sizing: border-box;
    padding: 12px 20px; background: rgba(244,239,225,0.96);
    -webkit-backdrop-filter: blur(6px); backdrop-filter: blur(6px);
    border-bottom: 1px solid #D9CFB7;
  }
  .bt-search-row { display:flex; align-items:center; gap:10px; }
  .bt-field { position:relative; flex:1; min-width:0; }
  .bt-field svg { position:absolute; left:14px; top:50%; transform:translateY(-50%); width:15px; height:15px; color:#8A7A55; pointer-events:none; }
  .bt-input {
    width:100%; box-sizing:border-box; height:40px; padding:0 38px 0 38px;
    border:1px solid #B89B5E; border-radius:999px; background:#FBF8F0;
    font: 14px 'Pretendard Variable', Pretendard, -apple-system, sans-serif; color:#1A1512;
    outline:none; -webkit-appearance:none; appearance:none;
  }
  .bt-input::placeholder { color:#9A9283; }
  .bt-input:focus { border-color:#0A1330; box-shadow:0 0 0 3px rgba(10,19,48,0.08); }
  .bt-input::-webkit-search-cancel-button { display:none; }
  .bt-clear {
    position:absolute; right:8px; top:50%; transform:translateY(-50%);
    width:26px; height:26px; border:0; border-radius:50%; background:transparent;
    color:#5C5651; font-size:16px; line-height:26px; cursor:pointer; display:none;
  }
  .bt-clear:hover { background:#EAE0C9; }
  .bt-count {
    flex:none; font-family:'IBM Plex Mono', Consolas, monospace; font-size:11px;
    letter-spacing:0.12em; color:#5C5651; white-space:nowrap;
  }
  .bt-count b { color:#0A1330; }
  .bt-empty {
    max-width:860px; margin:0 auto; box-sizing:border-box; padding:56px 20px; text-align:center;
    background:#F4EFE1; font-family:'Gowun Batang', serif; font-size:15px; color:#5C5651; display:none;
  }
  .bt-grid {
    display:grid; grid-template-columns:1fr 1fr; column-gap:24px; row-gap:32px;
    padding:16px 16px 16px;
  }
  .bt-grid > div { min-width:0; }
  .bt-hide { display:none !important; }
  .bt-chip-off { opacity:0.35; }
  [id^="user_content_"] { scroll-margin-top: 72px; }

  .bt-top {
    position:fixed; right:20px; bottom:24px; z-index:30;
    width:46px; height:46px; border-radius:50%;
    border:1px solid #B89B5E; background:#0A1330; color:#F4EFE1;
    display:flex; align-items:center; justify-content:center; cursor:pointer;
    box-shadow:0 6px 18px rgba(10,19,48,0.25);
    opacity:0; visibility:hidden; transform:translateY(8px);
    transition:opacity .2s ease, transform .2s ease, visibility .2s;
  }
  .bt-top.show { opacity:1; visibility:visible; transform:none; }
  .bt-top:hover { background:#C8102E; border-color:#C8102E; }
  .bt-top svg { width:18px; height:18px; }

  @media (max-width:640px) {
    .bt-search { padding:10px 12px; }
    .bt-grid { column-gap:14px; row-gap:24px; padding:12px 8px 12px; }
    .bt-top { right:14px; bottom:18px; width:42px; height:42px; }
  }
</style>

<button type="button" class="bt-top" aria-label="맨 위로" title="맨 위로">
  <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round"><path d="M12 19V5M5 12l7-7 7 7"/></svg>
</button>

<script>
(function () {
  var archive = document.getElementById('archive');
  if (!archive) return;
  var table = archive.querySelector('table');
  if (!table) return;
  var rows = Array.prototype.slice.call(table.rows);

  // 1) 히어로 + 칩 줄을 별도 테이블로 빼고, 그 아래에 sticky 검색바 삽입
  var head = document.createElement('table');
  head.className = 'bt-head';
  head.setAttribute('cellpadding', '0'); head.setAttribute('cellspacing', '0'); head.setAttribute('border', '0');
  var headBody = document.createElement('tbody');
  head.appendChild(headBody);
  headBody.appendChild(rows[0]);
  headBody.appendChild(rows[1]);
  archive.insertBefore(head, table);

  var bar = document.createElement('div');
  bar.className = 'bt-search';
  bar.innerHTML =
    '<div class="bt-search-row">' +
      '<div class="bt-field">' +
        '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.2" stroke-linecap="round"><circle cx="11" cy="11" r="7"/><path d="M20 20l-3.5-3.5"/></svg>' +
        '<input class="bt-input" type="search" enterkeyhint="search" autocomplete="off" placeholder="선수 · 제목 · 날짜 검색" aria-label="영상 검색">' +
        '<button type="button" class="bt-clear" aria-label="검색어 지우기">×</button>' +
      '</div>' +
      '<div class="bt-count"></div>' +
    '</div>';
  archive.insertBefore(bar, table);

  var empty = document.createElement('div');
  empty.className = 'bt-empty';
  empty.textContent = '검색 결과가 없어요';
  archive.insertBefore(empty, table.nextSibling);

  var input = bar.querySelector('.bt-input');
  var clearBtn = bar.querySelector('.bt-clear');
  var countEl = bar.querySelector('.bt-count');

  // 2) 섹션별 카드 테이블들을 하나의 그리드로 변환 (빈칸 없이 필터링하기 위해)
  var sections = [];
  var items = [];
  var chips = {};
  Array.prototype.forEach.call(head.querySelectorAll('a[href^="#user_content_"]'), function (a) {
    chips[a.getAttribute('href').slice(1)] = a;
  });

  Array.prototype.forEach.call(table.querySelectorAll('a[id^="user_content_"]'), function (hdr) {
    var hdrRow = hdr.closest('tr');
    var bodyRow = hdrRow && hdrRow.nextElementSibling;
    if (!bodyRow) return;
    var cell = bodyRow.cells[0];
    var cards = Array.prototype.slice.call(cell.querySelectorAll('a[target="_blank"]'));
    var grid = document.createElement('div');
    grid.className = 'bt-grid';
    var catName = hdr.textContent.split('/')[0].replace(/\s+/g, ' ').trim();
    var countB = hdr.querySelector('b');
    var sec = { id: hdr.id, hdrRow: hdrRow, bodyRow: bodyRow, countB: countB,
                total: countB ? countB.textContent : '', items: [] };
    cards.forEach(function (a) {
      var wrap = document.createElement('div');
      wrap.appendChild(a);
      grid.appendChild(wrap);
      var img = a.querySelector('img');
      var text = (catName + ' ' + a.textContent + ' ' + (img ? img.alt : ''))
        .normalize('NFC').toLowerCase().replace(/\s+/g, ' ');
      var it = { el: wrap, text: text, textNs: text.replace(/\s/g, '') };
      sec.items.push(it); items.push(it);
    });
    cell.innerHTML = '';
    cell.appendChild(grid);
    sections.push(sec);
  });

  var total = items.length;

  function pad(n, ref) { var s = String(n); return ref && ref.length === 2 && s.length < 2 ? '0' + s : s; }

  // 3) 검색
  function apply(q) {
    var terms = q.normalize('NFC').toLowerCase().trim().split(/\s+/).filter(Boolean);
    var shown = 0;
    sections.forEach(function (sec) {
      var n = 0;
      sec.items.forEach(function (it) {
        var ok = terms.every(function (t) { return it.text.indexOf(t) > -1 || it.textNs.indexOf(t) > -1; });
        it.el.classList.toggle('bt-hide', !ok);
        if (ok) n++;
      });
      var off = terms.length && n === 0;
      sec.hdrRow.classList.toggle('bt-hide', off);
      sec.bodyRow.classList.toggle('bt-hide', off);
      if (sec.countB) sec.countB.textContent = terms.length ? pad(n, sec.total) : sec.total;
      if (chips[sec.id]) chips[sec.id].classList.toggle('bt-chip-off', off);
      shown += n;
    });
    clearBtn.style.display = q ? 'block' : 'none';
    empty.style.display = terms.length && !shown ? 'block' : 'none';
    countEl.innerHTML = terms.length ? '<b>' + shown + '</b> / ' + total : '<b>' + total + '</b> videos';
    try {
      var url = new URL(location.href);
      if (q.trim()) url.searchParams.set('q', q.trim()); else url.searchParams.delete('q');
      history.replaceState(null, '', url);
    } catch (e) {}
  }

  var raf = 0;
  input.addEventListener('input', function () {
    cancelAnimationFrame(raf);
    raf = requestAnimationFrame(function () {
      apply(input.value);
      // 아래쪽에서 검색하면 결과 맨 앞이 보이게 검색바 위치로
      var barTop = head.getBoundingClientRect().bottom + window.pageYOffset;
      if (window.pageYOffset > barTop) window.scrollTo(0, barTop);
    });
  });
  clearBtn.addEventListener('click', function () { input.value = ''; apply(''); input.focus(); });
  input.addEventListener('keydown', function (e) {
    if (e.key === 'Escape') { input.value = ''; apply(''); }
    if (e.key === 'Enter') input.blur();
  });
  document.addEventListener('keydown', function (e) {
    if (e.key === '/' && document.activeElement !== input && !/INPUT|TEXTAREA/.test(document.activeElement.tagName)) {
      e.preventDefault(); input.focus();
    }
  });

  var q0 = '';
  try { q0 = new URL(location.href).searchParams.get('q') || ''; } catch (e) {}
  input.value = q0;
  apply(q0);

  // 4) 맨 위로 버튼
  var topBtn = document.querySelector('.bt-top');
  function onScroll() { topBtn.classList.toggle('show', window.pageYOffset > 600); }
  window.addEventListener('scroll', onScroll, { passive: true });
  onScroll();
  topBtn.addEventListener('click', function () {
    window.scrollTo({ top: 0, behavior: 'smooth' });
    if (location.hash) history.replaceState(null, '', location.pathname + location.search);
  });
})();
</script>
<!-- ===== /검색 + 맨 위로 버튼 ===== -->
'''

# ===== index.html (GitHub Pages용) =====
from datetime import datetime
build_time = datetime.now().strftime('%Y-%m-%d %H:%M')

index_html = f'''<!DOCTYPE html>
<html lang="ko">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>BEARS TV · 2026 아카이브</title>
<meta name="description" content="두산 베어스 공식 유튜브 채널 큐레이션 아카이브 · {total_cards}개 영상">
<meta property="og:title" content="BEARS TV · 2026 아카이브">
<meta property="og:description" content="두산 베어스 공식 유튜브 채널 큐레이션 아카이브">
<meta property="og:type" content="website">
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Gowun+Batang:wght@400;700&family=IBM+Plex+Mono:wght@400;500&display=swap" rel="stylesheet">
<link rel="stylesheet" as="style" crossorigin href="https://cdn.jsdelivr.net/gh/orioncactus/pretendard@v1.3.9/dist/web/variable/pretendardvariable.min.css">
<style>
  html {{ scroll-behavior: smooth; }}
  body {{
    margin: 0;
    background: #E5DEC8;
    font-family: 'Pretendard Variable', Pretendard, -apple-system, BlinkMacSystemFont, sans-serif;
    color: #1A1512;
    -webkit-font-smoothing: antialiased;
  }}
  /* 카드 hover 효과 */
  #archive td a[target="_blank"] {{
    transition: transform 0.18s ease, opacity 0.18s ease;
  }}
  #archive td a[target="_blank"]:hover {{
    transform: translateY(-2px);
    opacity: 0.92;
  }}
  #archive td a[target="_blank"]:hover img {{
    box-shadow: 0 6px 16px rgba(10, 19, 48, 0.15);
  }}
  /* 상단 칩 hover 효과 */
  #archive a[href^="#user_content_"] {{
    transition: all 0.15s ease;
  }}
  #archive a[href^="#user_content_"]:hover {{
    background: #0A1330 !important;
    color: #F4EFE1 !important;
    border-color: #0A1330 !important;
  }}
  /* 빌드 정보 */
  .build-info {{
    max-width: 860px;
    margin: 0 auto;
    padding: 12px 20px;
    text-align: center;
    font-family: 'IBM Plex Mono', monospace;
    font-size: 10px;
    letter-spacing: 0.2em;
    text-transform: uppercase;
    color: rgba(26, 21, 18, 0.4);
  }}
  @media (max-width: 640px) {{
    body {{ padding: 0; }}
  }}
</style>
</head>
<body>

<div id="archive">
{paste_content}
</div>

<div class="build-info">Last Updated · {build_time}</div>

{ENHANCE_HTML}

</body>
</html>
'''

# ===== bearstv-archive-theqoo.html (더쿠용 - 기존 그대로) =====
stats_html = '\n'.join([f'    <div class="stat"><b>{section_counts[cat]}</b>{cat}</div>' for cat, _ in SECTIONS])

theqoo_html = '''<!DOCTYPE html>
<html lang="ko">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>BEARS TV · 2026 아카이브 (더쿠 붙여넣기용)</title>
<link rel="preconnect" href="https://fonts.googleapis.com">
<link href="https://fonts.googleapis.com/css2?family=Gowun+Batang:wght@400;700&family=IBM+Plex+Mono:wght@400;500&display=swap" rel="stylesheet">
<style>
  html { scroll-behavior: smooth; }
  body { margin:0; padding:2rem 1rem 4rem; background:#E5DEC8; font-family:-apple-system,BlinkMacSystemFont,sans-serif; color:#1A1512; }
  .guide { max-width:860px; margin:0 auto 2rem; padding:1.5rem 1.75rem; background:#fffbe6; border-left:3px solid #B89B5E; line-height:1.65; font-size:0.9rem; }
  .guide h2 { margin:0 0 0.75rem; font-size:1.1rem; color:#0A1330; font-weight:700; }
  .guide ol { margin:0.5rem 0 1rem 1.25rem; padding:0; }
  .guide li { margin-bottom:0.35rem; }
  .guide code { background:rgba(10,19,48,0.06); padding:0.1em 0.4em; font-family:'IBM Plex Mono',monospace; font-size:0.88em; }
  .copy-btn { padding:0.7rem 1.3rem; background:#0A1330; color:#F4EFE1; border:none; font-size:0.9rem; font-weight:500; cursor:pointer; letter-spacing:0.02em; }
  .copy-btn:hover { background:#C8102E; }
  .copy-btn.done { background:#4a6b3d; }
  .copy-status { display:inline-block; margin-left:0.75rem; font-size:0.85rem; color:#5C5651; }
  .stats { display:grid; grid-template-columns:repeat(auto-fit,minmax(110px,1fr)); gap:0.5rem; margin-top:1rem; font-family:'IBM Plex Mono',monospace; font-size:0.75rem; }
  .stat { padding:0.6rem 0.75rem; background:rgba(184,155,94,0.1); text-align:center; }
  .stat b { display:block; font-size:1.1rem; color:#0A1330; margin-bottom:2px; }
</style>
</head>
<body>

<div class="guide">
  <h2>🐻 BEARS TV 2026 · ''' + str(total_cards) + '''개 </h2>
  <button class="copy-btn" id="copyBtn">📋 코드 복사</button>
  <span class="copy-status" id="copyStatus"></span>
  <div class="stats">
''' + stats_html + '''
  </div>
</div>

<div id="paste-content">''' + paste_content + '''</div>

<script>
document.getElementById('copyBtn').addEventListener('click', async function() {
  const content = document.getElementById('paste-content').innerHTML.trim();
  const btn = this, status = document.getElementById('copyStatus');
  try {
    await navigator.clipboard.writeText(content);
    btn.textContent = '✓ 복사 완료 (' + Math.round(content.length/1024) + 'KB)';
    btn.classList.add('done');
    status.textContent = '더쿠 소스 모드에 붙여넣기!';
    setTimeout(() => { btn.textContent='📋 코드 복사'; btn.classList.remove('done'); status.textContent=''; }, 4000);
  } catch(e) {
    const ta = document.createElement('textarea');
    ta.value = content; document.body.appendChild(ta); ta.select();
    document.execCommand('copy'); document.body.removeChild(ta);
    btn.textContent = '✓ 복사 완료'; btn.classList.add('done');
  }
});
</script>

</body>
</html>'''

# ===== 파일 저장 =====
OUT_INDEX.write_text(index_html, encoding='utf-8')
OUT_THEQOO.write_text(theqoo_html, encoding='utf-8')

print(f"\n✅ index.html 생성 ({OUT_INDEX.stat().st_size / 1024:.1f} KB) - GitHub Pages용")
print(f"✅ bearstv-archive-theqoo.html 생성 ({OUT_THEQOO.stat().st_size / 1024:.1f} KB) - 더쿠용")
print(f"\n총 {total_cards}개 영상")
for cat, aid in SECTIONS:
    print(f"  {cat}: {section_counts[cat]}개")
