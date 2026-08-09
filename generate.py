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
        BEARS<span style="color:#B89B5E; font-style:italic; font-weight:300; margin:0 4px;">·</span>TV
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
  <h2>🐻 BEARS TV 2026 · ''' + str(total_cards) + '''개 (더쿠 붙여넣기용)</h2>
  <ol>
    <li>아래 <b>[코드 복사]</b> 클릭</li>
    <li>더쿠 글쓰기 → 우측상단 <code>소스</code> 클릭</li>
    <li>빈 창에 붙여넣기 (Ctrl+V)</li>
    <li>다시 <code>소스</code> 눌러서 확인 → 등록</li>
  </ol>
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
