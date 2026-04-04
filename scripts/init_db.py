from sqlalchemy.orm import Session

from src.db.init_db import create_tables, seed_roles
from src.db.session import SessionLocal
from src.models.user import User
from src.repositories.role_repository import RoleRepository


def main() -> None:
    create_tables()
    db: Session = SessionLocal()
    try:
        seed_roles(db)
        role_repo = RoleRepository(db)
        admin_role = role_repo.get_by_name("Admin")
        if admin_role and not db.query(User).filter(User.username == "admin").first():
            db.add(User(username="admin", password="admin123", role_id=admin_role.id, status="ACTIVE"))
            db.commit()
            print("Created default admin user: admin/admin123")
    finally:
        db.close()


if __name__ == "__main__":
    main()
