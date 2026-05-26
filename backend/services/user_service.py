import re

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.schemas import CadastroUsuarioRequest
from auth.security import hash_password, verify_password
from models import Cliente, Prestador, PrestadorValidacao, Usuario
from utils.exceptions import BadRequestError, ConflictError, UnauthorizedError


def cadastrar_usuario(db: Session, payload: CadastroUsuarioRequest) -> Usuario:
    _validar_cadastro(payload)

    email = payload.email.strip().lower()
    usuario_existente = db.scalar(
        select(Usuario).where(Usuario.email == email, Usuario.deleted_at.is_(None))
    )
    if usuario_existente is not None:
        raise ConflictError("E-mail ja cadastrado.")

    usuario = Usuario(
        nome=payload.nome.strip(),
        email=email,
        telefone=_somente_numeros(payload.telefone),
        senha_hash=hash_password(payload.senha),
        tipo_usuario=payload.tipo_usuario,
    )
    db.add(usuario)
    db.flush()

    if payload.tipo_usuario == "cliente":
        db.add(
            Cliente(
                usuario_id=usuario.id,
                documento=payload.documento,
                endereco_principal=payload.endereco.strip(),
                bairro=payload.bairro.strip(),
                cidade=payload.cidade.strip(),
                estado=payload.estado.strip().upper(),
            )
        )
    elif payload.tipo_usuario == "prestador":
        prestador = Prestador(
            usuario_id=usuario.id,
            documento=payload.documento,
            endereco_principal=payload.endereco.strip(),
            bairro=payload.bairro.strip(),
            cidade=payload.cidade.strip(),
            estado=payload.estado.strip().upper(),
            ativo=False,
        )
        db.add(prestador)
        db.flush()
        db.add(PrestadorValidacao(prestador_id=prestador.id, status_validacao="pendente"))

    db.commit()
    db.refresh(usuario)
    return usuario


def autenticar_usuario(db: Session, email: str, senha: str) -> Usuario:
    usuario = db.scalar(
        select(Usuario).where(
            Usuario.email == email.strip().lower(),
            Usuario.deleted_at.is_(None),
        )
    )
    if usuario is None or not usuario.ativo:
        raise UnauthorizedError("E-mail ou senha invalidos.")

    if not verify_password(senha, usuario.senha_hash):
        raise UnauthorizedError("E-mail ou senha invalidos.")

    return usuario


def _validar_cadastro(payload: CadastroUsuarioRequest) -> None:
    nome = payload.nome.strip()
    if len(nome) < 3 or any(char.isdigit() for char in nome):
        raise BadRequestError("Nome deve ter pelo menos 3 caracteres e nao conter numeros.")

    if not re.fullmatch(r"[^@\s]+@[^@\s]+\.[^@\s]+", payload.email.strip()):
        raise BadRequestError("E-mail invalido.")

    telefone = _somente_numeros(payload.telefone)
    if not re.fullmatch(r"\d{10,11}", telefone):
        raise BadRequestError("Telefone deve estar no formato brasileiro com DDD.")

    if not payload.endereco.strip():
        raise BadRequestError("Endereco obrigatorio.")

    if not payload.bairro.strip():
        raise BadRequestError("Bairro obrigatorio.")

    if not payload.cidade.strip():
        raise BadRequestError("Cidade obrigatoria.")

    if not re.fullmatch(r"[A-Za-z]{2}", payload.estado.strip()):
        raise BadRequestError("Estado obrigatorio. Use UF com 2 letras.")

    if not re.search(r"[A-Za-z]", payload.senha) or not re.search(r"\d", payload.senha):
        raise BadRequestError("Senha deve conter letra e numero.")


def _somente_numeros(value: str) -> str:
    return re.sub(r"\D", "", value)
