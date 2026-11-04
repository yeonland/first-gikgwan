"""rule/ 폴더의 규칙서 PDF를 rule/md/*.md로 바꿔요. 룰 카드 조항 번호를 대조할 때 읽기 쉽게 하려는 것.

rule/은 .gitignore에 들어 있어서 만든 md도 저장소에 올라가지 않아요 (규칙서 저작권).

    pip install pypdf
    python scripts/rules_to_md.py            # rule/*.pdf 전부
    python scripts/rules_to_md.py 야구        # 파일 이름에 '야구'가 들어간 것만

md 모양: 맨 위에 원본 파일 이름·쪽수, 쪽마다 '## p.N', 조항 번호로 시작하는 줄은 '### '를 붙여 찾기 쉽게.
"""
import logging
import re
import sys
from pathlib import Path

from pypdf import PdfReader

logging.getLogger('pypdf').setLevel(logging.ERROR)  # 깨진 PDF 구조 경고는 결과와 상관없어서 숨김

ROOT = Path(__file__).resolve().parent.parent
SRC = ROOT / 'rule'
OUT = SRC / 'md'

# 조항 번호로 시작하는 줄: 5.09 / 26.1.1 / 16.2. (IIHF) / 8:11 (핸드볼) / 제12조 / Rule 2
ARTICLE = re.compile(r'^(제\s?\d+\s?조|Rule \d+\b|\d{1,3}(\.\d{1,2}){1,3}\.?(?=\s|$|\()|\d{1,2}:\d{1,2}[a-z]?(?=\s|$))')


def page_text(page):
    text = page.extract_text() or ''
    lines = []
    for line in text.splitlines():
        line = re.sub(r'\s+', ' ', line).strip()
        if not line:
            continue
        lines.append('### ' + line if ARTICLE.match(line) else line)
    return '\n'.join(lines)


def convert(pdf):
    reader = PdfReader(pdf)
    parts = [f'# {pdf.stem}', '', f'원본: rule/{pdf.name} · {len(reader.pages)}쪽', '']
    empty = 0
    for i, page in enumerate(reader.pages, 1):
        body = page_text(page)
        if not body:
            empty += 1
        parts += [f'## p.{i}', '', body, '']
    out = OUT / (pdf.stem + '.md')
    out.write_text('\n'.join(parts), encoding='utf-8')
    note = f' (글자 없는 쪽 {empty}개: 그림이거나 스캔본)' if empty else ''
    print(f'{pdf.name} → md/{out.name}{note}')


def main():
    if not SRC.is_dir():
        sys.exit('rule/ 폴더가 없어요. 저장소 맨 위에 rule/을 만들고 규칙서 PDF를 넣어 주세요.')
    OUT.mkdir(exist_ok=True)
    pick = sys.argv[1] if len(sys.argv) > 1 else ''
    pdfs = sorted(p for p in SRC.glob('*.pdf') if pick in p.name)
    if not pdfs:
        sys.exit('바꿀 PDF가 없어요.')
    for pdf in pdfs:
        convert(pdf)


if __name__ == '__main__':
    main()
