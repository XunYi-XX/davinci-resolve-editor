"""Local, read-only PDF/text reference indexing. Never executes indexed content."""
import argparse
import json
import sqlite3
import sys
from pathlib import Path


def main():
    if hasattr(sys.stdout, 'reconfigure'):
        sys.stdout.reconfigure(encoding='utf-8')
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--db', required=True)
    sub = p.add_subparsers(dest='command', required=True)
    build = sub.add_parser('index')
    build.add_argument('paths', nargs='+')
    search = sub.add_parser('search')
    search.add_argument('query', help='SQLite FTS5 query; quote phrases')
    search.add_argument('--limit', type=int, default=8)
    read = sub.add_parser('read')
    read.add_argument('path')
    read.add_argument('--page', type=int, default=1, help='1-based PDF page, not printed page')
    a = p.parse_args()
    if a.command == 'read':
        path = Path(a.path)
        if path.suffix.lower() == '.pdf':
            import pymupdf
            with pymupdf.open(path) as doc:
                print(doc[a.page - 1].get_text())
        else:
            print(path.read_text(encoding='utf-8', errors='replace'))
        return
    if a.command == 'search':
        db = sqlite3.connect(Path(a.db).resolve().as_uri() + '?mode=ro', uri=True)
        rows = db.execute("SELECT path,page,snippet(pages,2,'[',']',' … ',65) FROM pages WHERE pages MATCH ? ORDER BY rank LIMIT ?", (a.query, a.limit)).fetchall()
        print(json.dumps([dict(path=r[0], page=r[1], excerpt=r[2]) for r in rows], ensure_ascii=False, indent=2))
        return
    Path(a.db).parent.mkdir(parents=True, exist_ok=True)
    db = sqlite3.connect(a.db)
    db.execute('CREATE VIRTUAL TABLE IF NOT EXISTS pages USING fts5(path UNINDEXED,page UNINDEXED,body)')
    files = []
    for root in map(Path, a.paths):
        if not root.exists():
            raise FileNotFoundError(root)
        files.extend(root.rglob('*') if root.is_dir() else [root])
    count = 0
    for path in sorted(set(files)):
        if not path.is_file() or path.suffix.lower() not in {'.pdf', '.txt', '.md', '.pyi', '.h', '.dctl', '.fuse'}:
            continue
        db.execute('DELETE FROM pages WHERE path=?', (str(path),))
        if path.suffix.lower() == '.pdf':
            import pymupdf
            with pymupdf.open(path) as doc:
                for i, page in enumerate(doc):
                    db.execute('INSERT INTO pages VALUES(?,?,?)', (str(path), i + 1, page.get_text()))
        else:
            db.execute('INSERT INTO pages VALUES(?,?,?)', (str(path), 1, path.read_text(encoding='utf-8', errors='replace')))
        count += 1
        db.commit()
    print(json.dumps({'indexed_files': count, 'indexed_units': db.execute('SELECT count(*) FROM pages').fetchone()[0]}))


if __name__ == '__main__':
    main()
