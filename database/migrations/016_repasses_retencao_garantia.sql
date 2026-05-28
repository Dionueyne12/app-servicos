ALTER TABLE repasses
    DROP CONSTRAINT IF EXISTS repasses_status_check;

ALTER TABLE repasses
    ADD CONSTRAINT repasses_status_check CHECK (
        status_repasse IN ('pendente', 'simulado', 'aprovado', 'cancelado', 'retido_garantia')
    );

ALTER TABLE repasses
    DROP CONSTRAINT IF EXISTS repasses_tipo_check;

ALTER TABLE repasses
    ADD CONSTRAINT repasses_tipo_check CHECK (
        tipo_repasse IN ('prestador', 'empresa', 'plataforma', 'garantia')
    );
