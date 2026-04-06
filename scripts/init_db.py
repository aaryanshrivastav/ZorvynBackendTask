import sys
from pathlib import Path

from sqlalchemy.orm import Session

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from src.db.init_db import create_tables, seed_roles
from src.db.session import SessionLocal
from src.core.passwords import hash_password
from src.models.user import User
from src.repositories.role_repository import RoleRepository


def main() -> None:
    create_tables()
    db: Session = SessionLocal()
    try:
        seed_roles(db)
        role_repo = RoleRepository(db)
        demo_users = [
            ("admin", "admin123", "Admin"),
            ("analyst", "analyst123", "Analyst"),
            ("approver", "approver123", "Approver"),
            ("viewer", "viewer123", "Viewer"),
        ]

        created_users: list[str] = []
        for username, password, role_name in demo_users:
            role = role_repo.get_by_name(role_name)
            if not role:
                continue

            user = db.query(User).filter(User.username == username).first()
            if user is None:
                db.add(
                    User(
                        username=username,
                        password=hash_password(password),
                        role_id=role.id,
                        status="ACTIVE",
                    )
                )
                created_users.append(f"{username}/{password}")

        if created_users:
            db.commit()
            print("Created demo users: " + ", ".join(created_users))
    finally:
        db.close()


if __name__ == "__main__":
    main()
