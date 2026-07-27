from Back_end.database.database import SessionLocal
from Back_end.models.category import Category

db = SessionLocal()
rows = db.query(Category).all()
print(rows)
for r in rows:
    print(r.cid, r.category)