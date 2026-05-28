from sqlalchemy import select
from sqlalchemy.orm import Session

from auth.security import hash_password
from models import Usuario
from models import CategoriaServico


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


def ensure_default_service_categories(db: Session, usuario_id=None) -> None:
    defaults = [
        ("Eletrica", "Chuveiro, tomada, ventilador, resistencia e pequenos reparos eletricos."),
        ("Hidraulica", "Torneira, registro, sifao, vazamento, vaso sanitario e caixa acoplada."),
        ("Desentupimento", "Vaso, pia, ralo, esgoto, caixa de gordura e encanamento entupido."),
        ("Jardinagem", "Cortar grama, poda simples, limpeza de jardim e manutencao externa."),
        ("Instalacao", "Suporte de TV, prateleira, varal, cortina, ventilador e montagem simples."),
        ("Limpeza", "Limpeza pos-obra, caixa d'agua, area externa e higienizacao geral."),
        ("Manutencao geral", "Pequenos reparos residenciais que nao se encaixam nas outras categorias."),
    ]
    for nome, descricao in defaults:
        categoria = db.scalar(
            select(CategoriaServico).where(
                CategoriaServico.nome == nome,
                CategoriaServico.deleted_at.is_(None),
            )
        )
        if categoria is None:
            db.add(
                CategoriaServico(
                    nome=nome,
                    descricao=descricao,
                    ativo=True,
                    created_by_usuario_id=usuario_id,
                )
            )
        elif not categoria.ativo:
            categoria.ativo = True
            categoria.updated_by_usuario_id = usuario_id
    db.commit()
