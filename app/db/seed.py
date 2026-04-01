import os
from sqlalchemy.orm import Session
from app.db.models import WordlistEntry

def seed_from_file(db: Session, filepath: str) -> int:
    """从 CSV 文件导入词表。格式：word,category,risk_level（每行）。返回导入数量。"""
    count = 0
    with open(filepath, encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith("#"):
                continue
            parts = line.split(",")
            if len(parts) < 3:
                continue
            word, category, risk_level_str = parts[0].strip(), parts[1].strip(), parts[2].strip()
            try:
                risk_level = int(risk_level_str)
            except ValueError:
                continue
            if db.query(WordlistEntry).filter_by(word=word).first():
                continue
            db.add(WordlistEntry(word=word, category=category, risk_level=risk_level, source="词库"))
            count += 1
    db.commit()
    return count

def run_seed():
    from app.db.database import SessionLocal, init_db
    init_db()
    db = SessionLocal()
    base_path = os.path.join(os.path.dirname(__file__), "../../wordlist/词库.txt")
    n = seed_from_file(db, os.path.abspath(base_path))
    print(f"Seeded {n} words.")
    db.close()

if __name__ == "__main__":
    run_seed()
