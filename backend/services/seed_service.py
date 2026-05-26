from sqlalchemy import select
from sqlalchemy.orm import Session

from auth.security import hash_password
from models import Usuario


DEFAULT_ADMIN_EMAIL = "admin@app.com"
DEFAULT_ADMIN_PASSWORD = "Admin@123"


def ensure_default_admin(db: Session) -> None:
    admin = db.scalar(
        select(Usuario).where(
            Usuario.email == DEFAULT_ADMIN_EMAIL,
            Usuario.deleted_at.is_(None),
        )
    )
    if admin is not None:
        return

    db.add(
        Usuario(
            nome="Administrador",
            email=DEFAULT_ADMIN_EMAIL,
            telefone="11999999999",
            senha_hash=hash_password(DEFAULT_ADMIN_PASSWORD),
            tipo_usuario="admin",
            ativo=True,
        )
    )
    db.commit()
