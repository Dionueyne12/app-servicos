from sqlalchemy.orm import Session

from models import MonitoramentoSistema


def registrar_alerta_monitoramento(
    db: Session,
    tipo_alerta: str,
    nivel_alerta: str,
    mensagem: str,
    origem: str,
) -> None:
    alerta = MonitoramentoSistema(
        tipo_alerta=tipo_alerta,
        nivel_alerta=nivel_alerta,
        mensagem=mensagem,
        origem=origem,
        status="ativo",
    )
    db.add(alerta)
    db.commit()
