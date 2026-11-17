-- =====================================================================
-- LaCakes Cupcakes Gourmet – projeto físico do banco de dados (SQLite)
-- Gerado automaticamente a partir dos models SQLAlchemy por
-- scripts/gerar_docs_banco.py. Não edite à mão: altere os models e gere de novo.
-- Valores em dinheiro são guardados em centavos (INTEGER).
-- =====================================================================

-- categoria: Categorias da vitrine (Clássicos, Recheados, Zero açúcar, Datas especiais).
CREATE TABLE categoria (
	id INTEGER NOT NULL, 
	nome VARCHAR(40) NOT NULL, 
	descricao VARCHAR(200), 
	PRIMARY KEY (id), 
	UNIQUE (nome)
);

-- loja: 
CREATE TABLE loja (
	id INTEGER NOT NULL, 
	endereco VARCHAR(150) NOT NULL, 
	dias_funcionamento VARCHAR(7) NOT NULL, 
	abre_as TIME NOT NULL, 
	fecha_as TIME NOT NULL, 
	atualizado_em DATETIME NOT NULL, 
	PRIMARY KEY (id), 
	CONSTRAINT ck_loja_horario CHECK (abre_as < fecha_as)
);

-- usuario: Pessoas cadastradas (clientes e administradores).
CREATE TABLE usuario (
	id INTEGER NOT NULL, 
	nome VARCHAR(80) NOT NULL, 
	email VARCHAR(120) NOT NULL, 
	senha_hash VARCHAR(255) NOT NULL, 
	telefone VARCHAR(20) NOT NULL, 
	perfil VARCHAR(7) NOT NULL, 
	criado_em DATETIME NOT NULL, 
	PRIMARY KEY (id), 
	CONSTRAINT ck_usuario_perfil CHECK (perfil IN ('CLIENTE', 'ADMIN'))
);

CREATE UNIQUE INDEX ix_usuario_email ON usuario (email);

-- pedido: Pedidos dos clientes, com modalidade, endereço de entrega e totais.
CREATE TABLE pedido (
	id INTEGER NOT NULL, 
	usuario_id INTEGER NOT NULL, 
	status VARCHAR(20) NOT NULL, 
	modalidade VARCHAR(8) NOT NULL, 
	cep VARCHAR(8), 
	logradouro VARCHAR(120), 
	numero VARCHAR(10), 
	complemento VARCHAR(60), 
	bairro VARCHAR(60), 
	subtotal_centavos INTEGER NOT NULL, 
	taxa_entrega_centavos INTEGER NOT NULL, 
	total_centavos INTEGER NOT NULL, 
	previsao_preparo DATE, 
	criado_em DATETIME NOT NULL, 
	atualizado_em DATETIME NOT NULL, 
	PRIMARY KEY (id), 
	CONSTRAINT ck_pedido_subtotal CHECK (subtotal_centavos >= 0), 
	CONSTRAINT ck_pedido_taxa CHECK (taxa_entrega_centavos >= 0), 
	CONSTRAINT ck_pedido_total CHECK (total_centavos = subtotal_centavos + taxa_entrega_centavos), 
	FOREIGN KEY(usuario_id) REFERENCES usuario (id), 
	CONSTRAINT ck_pedido_status CHECK (status IN ('AGUARDANDO_PAGAMENTO', 'PAGO', 'EM_PREPARO', 'SAIU_PARA_ENTREGA', 'PRONTO_PARA_RETIRADA', 'ENTREGUE', 'CANCELADO')), 
	CONSTRAINT ck_pedido_modalidade CHECK (modalidade IN ('ENTREGA', 'RETIRADA'))
);

CREATE INDEX ix_pedido_status ON pedido (status);
CREATE INDEX ix_pedido_usuario_id ON pedido (usuario_id);

-- produto: Cupcakes vendidos, com preço e estoque do dia.
CREATE TABLE produto (
	id INTEGER NOT NULL, 
	categoria_id INTEGER NOT NULL, 
	nome VARCHAR(80) NOT NULL, 
	descricao TEXT, 
	ingredientes TEXT, 
	alergenicos VARCHAR(200), 
	preco_centavos INTEGER NOT NULL, 
	estoque INTEGER NOT NULL, 
	imagem VARCHAR(200), 
	ativo BOOLEAN NOT NULL, 
	criado_em DATETIME NOT NULL, 
	PRIMARY KEY (id), 
	CONSTRAINT ck_produto_preco CHECK (preco_centavos BETWEEN 100 AND 20000), 
	CONSTRAINT ck_produto_estoque CHECK (estoque BETWEEN 0 AND 500), 
	FOREIGN KEY(categoria_id) REFERENCES categoria (id), 
	UNIQUE (nome)
);

CREATE INDEX ix_produto_categoria_id ON produto (categoria_id);

-- historico_status: Linha do tempo das mudanças de status de cada pedido.
CREATE TABLE historico_status (
	id INTEGER NOT NULL, 
	pedido_id INTEGER NOT NULL, 
	status VARCHAR(20) NOT NULL, 
	observacao VARCHAR(200), 
	criado_em DATETIME NOT NULL, 
	PRIMARY KEY (id), 
	FOREIGN KEY(pedido_id) REFERENCES pedido (id), 
	CONSTRAINT ck_historico_status CHECK (status IN ('AGUARDANDO_PAGAMENTO', 'PAGO', 'EM_PREPARO', 'SAIU_PARA_ENTREGA', 'PRONTO_PARA_RETIRADA', 'ENTREGUE', 'CANCELADO'))
);

CREATE INDEX ix_historico_status_pedido_id ON historico_status (pedido_id);

-- item_pedido: Itens de cada pedido, com o preço congelado no momento da compra.
CREATE TABLE item_pedido (
	id INTEGER NOT NULL, 
	pedido_id INTEGER NOT NULL, 
	produto_id INTEGER NOT NULL, 
	quantidade INTEGER NOT NULL, 
	preco_unitario_centavos INTEGER NOT NULL, 
	PRIMARY KEY (id), 
	CONSTRAINT ck_item_quantidade CHECK (quantidade BETWEEN 1 AND 24), 
	CONSTRAINT ck_item_preco CHECK (preco_unitario_centavos > 0), 
	CONSTRAINT uq_item_pedido_produto UNIQUE (pedido_id, produto_id), 
	FOREIGN KEY(pedido_id) REFERENCES pedido (id), 
	FOREIGN KEY(produto_id) REFERENCES produto (id)
);

CREATE INDEX ix_item_pedido_pedido_id ON item_pedido (pedido_id);
CREATE INDEX ix_item_pedido_produto_id ON item_pedido (produto_id);

-- pagamento: Tentativas de pagamento (simulado) de cada pedido.
CREATE TABLE pagamento (
	id INTEGER NOT NULL, 
	pedido_id INTEGER NOT NULL, 
	metodo VARCHAR(7) NOT NULL, 
	status VARCHAR(9) NOT NULL, 
	valor_centavos INTEGER NOT NULL, 
	cartao_final VARCHAR(4), 
	codigo_transacao VARCHAR(40), 
	criado_em DATETIME NOT NULL, 
	PRIMARY KEY (id), 
	CONSTRAINT ck_pagamento_valor CHECK (valor_centavos > 0), 
	FOREIGN KEY(pedido_id) REFERENCES pedido (id), 
	CONSTRAINT ck_pagamento_metodo CHECK (metodo IN ('CREDITO', 'DEBITO', 'PIX')), 
	CONSTRAINT ck_pagamento_status CHECK (status IN ('APROVADO', 'RECUSADO', 'ESTORNADO'))
);

CREATE INDEX ix_pagamento_pedido_id ON pagamento (pedido_id);

