ALTER TABLE pagamentos_simulados
    DROP CONSTRAINT IF EXISTS pagamentos_status_check;

ALTER TABLE pagamentos_simulados
    ADD CONSTRAINT pagamentos_status_check CHECK (
        status_pagamento IN ('simulado', 'pendente', 'aprovado', 'cancelado')
    );

ALTER TABLE repasses
    DROP CONSTRAINT IF EXISTS repasses_status_check;

ALTER TABLE repasses
    ADD CONSTRAINT repasses_status_check CHECK (
        status_repasse IN ('pendente', 'simulado', 'aprovado', 'cancelado')
    );

CREATE INDEX IF NOT EXISTS idx_pagamentos_status
    ON pagamentos_simulados(status_pagamento)
    WHERE deleted_at IS NULL;

CREATE INDEX IF NOT EXISTS idx_repasses_status
    ON repasses(status_repasse)
    WHERE deleted_at IS NULL;

CREATE INDEX IF NOT EXISTS idx_repasses_destinatario
    ON repasses(destinatario_usuario_id)
    WHERE deleted_at IS NULL;
