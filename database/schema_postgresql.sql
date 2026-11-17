-- =====================================================================
-- LaCakes Cupcakes Gourmet – projeto físico do banco de dados (PostgreSQL)
-- Gerado automaticamente a partir dos models SQLAlchemy por
-- scripts/gerar_docs_banco.py. Não edite à mão: altere os models e gere de novo.
-- Valores em dinheiro são guardados em centavos (INTEGER).
-- =====================================================================

-- categoria: Categorias da vitrine (Clássicos, Recheados, Zero açúcar, Datas especiais).
CREATE TABLE categoria (
	id SERIAL NOT NULL, 
	nome VARCHAR(40) NOT NULL, 
	descricao VARCHAR(200), 
	PRIMARY KEY (id), 
	UNIQUE (nome)
);

COMMENT ON TABLE categoria IS 'Categorias da vitrine (Clássicos, Recheados, Zero açúcar, Datas especiais).';
COMMENT ON COLUMN categoria.id IS 'Identificador da categoria';
COMMENT ON COLUMN categoria.nome IS 'Nome exibido no filtro da vitrine';
COMMENT ON COLUMN categoria.descricao IS 'Descrição curta da categoria';

-- loja: 
CREATE TABLE loja (
	id SERIAL NOT NULL, 
	endereco VARCHAR(150) NOT NULL, 
	dias_funcionamento VARCHAR(7) NOT NULL, 
	abre_as TIME WITHOUT TIME ZONE NOT NULL, 
	fecha_as TIME WITHOUT TIME ZONE NOT NULL, 
	atualizado_em TIMESTAMP WITHOUT TIME ZONE NOT NULL, 
	PRIMARY KEY (id), 
	CONSTRAINT ck_loja_horario CHECK (abre_as < fecha_as)
);

COMMENT ON TABLE loja IS '';
COMMENT ON COLUMN loja.id IS 'Identificador (a loja tem um único registro)';
COMMENT ON COLUMN loja.endereco IS 'Endereço da loja, usado na retirada';
COMMENT ON COLUMN loja.dias_funcionamento IS 'Dias abertos: dígitos de 0 (segunda) a 6 (domingo), ex.: 012345';
COMMENT ON COLUMN loja.abre_as IS 'Horário de abertura';
COMMENT ON COLUMN loja.fecha_as IS 'Horário de fechamento (depois da abertura)';
COMMENT ON COLUMN loja.atualizado_em IS 'Última alteração';

-- usuario: Pessoas cadastradas (clientes e administradores).
CREATE TABLE usuario (
	id SERIAL NOT NULL, 
	nome VARCHAR(80) NOT NULL, 
	email VARCHAR(120) NOT NULL, 
	senha_hash VARCHAR(255) NOT NULL, 
	telefone VARCHAR(20) NOT NULL, 
	perfil VARCHAR(7) NOT NULL, 
	criado_em TIMESTAMP WITHOUT TIME ZONE NOT NULL, 
	PRIMARY KEY (id), 
	CONSTRAINT ck_usuario_perfil CHECK (perfil IN ('CLIENTE', 'ADMIN'))
);

CREATE UNIQUE INDEX ix_usuario_email ON usuario (email);

COMMENT ON TABLE usuario IS 'Pessoas cadastradas (clientes e administradores).';
COMMENT ON COLUMN usuario.id IS 'Identificador do usuário';
COMMENT ON COLUMN usuario.nome IS 'Nome completo do usuário';
COMMENT ON COLUMN usuario.email IS 'E-mail de login, único por conta (RN01)';
COMMENT ON COLUMN usuario.senha_hash IS 'Hash da senha; a senha nunca é gravada (RNF02)';
COMMENT ON COLUMN usuario.telefone IS 'Telefone/WhatsApp para contato sobre o pedido';
COMMENT ON COLUMN usuario.perfil IS 'CLIENTE ou ADMIN (RN13)';
COMMENT ON COLUMN usuario.criado_em IS 'Data e hora do cadastro';

-- pedido: Pedidos dos clientes, com modalidade, endereço de entrega e totais.
CREATE TABLE pedido (
	id SERIAL NOT NULL, 
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
	criado_em TIMESTAMP WITHOUT TIME ZONE NOT NULL, 
	atualizado_em TIMESTAMP WITHOUT TIME ZONE NOT NULL, 
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

COMMENT ON TABLE pedido IS 'Pedidos dos clientes, com modalidade, endereço de entrega e totais.';
COMMENT ON COLUMN pedido.id IS 'Número do pedido';
COMMENT ON COLUMN pedido.usuario_id IS 'Cliente dono do pedido (FK usuario.id)';
COMMENT ON COLUMN pedido.status IS 'Situação atual (RN10)';
COMMENT ON COLUMN pedido.modalidade IS 'ENTREGA ou RETIRADA';
COMMENT ON COLUMN pedido.cep IS 'CEP de entrega, só dígitos (vazio na retirada)';
COMMENT ON COLUMN pedido.logradouro IS 'Rua/avenida de entrega';
COMMENT ON COLUMN pedido.numero IS 'Número do endereço';
COMMENT ON COLUMN pedido.complemento IS 'Complemento (opcional)';
COMMENT ON COLUMN pedido.bairro IS 'Bairro de entrega';
COMMENT ON COLUMN pedido.subtotal_centavos IS 'Soma dos itens, em centavos';
COMMENT ON COLUMN pedido.taxa_entrega_centavos IS 'Taxa de entrega (RN06)';
COMMENT ON COLUMN pedido.total_centavos IS 'Subtotal + taxa de entrega';
COMMENT ON COLUMN pedido.previsao_preparo IS 'Dia de preparo e entrega quando foi pago com a loja fechada (vazio = mesmo dia)';
COMMENT ON COLUMN pedido.criado_em IS 'Data e hora do pedido';
COMMENT ON COLUMN pedido.atualizado_em IS 'Última alteração';

-- produto: Cupcakes vendidos, com preço e estoque do dia.
CREATE TABLE produto (
	id SERIAL NOT NULL, 
	categoria_id INTEGER NOT NULL, 
	nome VARCHAR(80) NOT NULL, 
	descricao TEXT, 
	ingredientes TEXT, 
	alergenicos VARCHAR(200), 
	preco_centavos INTEGER NOT NULL, 
	estoque INTEGER NOT NULL, 
	imagem VARCHAR(200), 
	ativo BOOLEAN NOT NULL, 
	criado_em TIMESTAMP WITHOUT TIME ZONE NOT NULL, 
	PRIMARY KEY (id), 
	CONSTRAINT ck_produto_preco CHECK (preco_centavos BETWEEN 100 AND 20000), 
	CONSTRAINT ck_produto_estoque CHECK (estoque BETWEEN 0 AND 500), 
	FOREIGN KEY(categoria_id) REFERENCES categoria (id), 
	UNIQUE (nome)
);

CREATE INDEX ix_produto_categoria_id ON produto (categoria_id);

COMMENT ON TABLE produto IS 'Cupcakes vendidos, com preço e estoque do dia.';
COMMENT ON COLUMN produto.id IS 'Identificador do produto';
COMMENT ON COLUMN produto.categoria_id IS 'Categoria do produto (FK categoria.id)';
COMMENT ON COLUMN produto.nome IS 'Nome do cupcake, único (RN14)';
COMMENT ON COLUMN produto.descricao IS 'Descrição exibida na página do produto';
COMMENT ON COLUMN produto.ingredientes IS 'Lista de ingredientes';
COMMENT ON COLUMN produto.alergenicos IS 'Alergênicos (ex.: glúten, leite, ovos)';
COMMENT ON COLUMN produto.preco_centavos IS 'Preço em centavos, de 100 a 20000 (R$ 1,00 a R$ 200,00)';
COMMENT ON COLUMN produto.estoque IS 'Unidades disponíveis hoje, de 0 a 500';
COMMENT ON COLUMN produto.imagem IS 'Caminho da imagem dentro de /static; vazio usa a imagem padrão';
COMMENT ON COLUMN produto.ativo IS 'Se falso, o produto não aparece na vitrine';
COMMENT ON COLUMN produto.criado_em IS 'Data e hora do cadastro';

-- historico_status: Linha do tempo das mudanças de status de cada pedido.
CREATE TABLE historico_status (
	id SERIAL NOT NULL, 
	pedido_id INTEGER NOT NULL, 
	status VARCHAR(20) NOT NULL, 
	observacao VARCHAR(200), 
	criado_em TIMESTAMP WITHOUT TIME ZONE NOT NULL, 
	PRIMARY KEY (id), 
	FOREIGN KEY(pedido_id) REFERENCES pedido (id), 
	CONSTRAINT ck_historico_status CHECK (status IN ('AGUARDANDO_PAGAMENTO', 'PAGO', 'EM_PREPARO', 'SAIU_PARA_ENTREGA', 'PRONTO_PARA_RETIRADA', 'ENTREGUE', 'CANCELADO'))
);

CREATE INDEX ix_historico_status_pedido_id ON historico_status (pedido_id);

COMMENT ON TABLE historico_status IS 'Linha do tempo das mudanças de status de cada pedido.';
COMMENT ON COLUMN historico_status.id IS 'Identificador do registro';
COMMENT ON COLUMN historico_status.pedido_id IS 'Pedido (FK pedido.id)';
COMMENT ON COLUMN historico_status.status IS 'Status que o pedido assumiu';
COMMENT ON COLUMN historico_status.observacao IS 'Observação da mudança';
COMMENT ON COLUMN historico_status.criado_em IS 'Momento da mudança';

-- item_pedido: Itens de cada pedido, com o preço congelado no momento da compra.
CREATE TABLE item_pedido (
	id SERIAL NOT NULL, 
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

COMMENT ON TABLE item_pedido IS 'Itens de cada pedido, com o preço congelado no momento da compra.';
COMMENT ON COLUMN item_pedido.id IS 'Identificador do item';
COMMENT ON COLUMN item_pedido.pedido_id IS 'Pedido ao qual o item pertence (FK pedido.id)';
COMMENT ON COLUMN item_pedido.produto_id IS 'Cupcake comprado (FK produto.id)';
COMMENT ON COLUMN item_pedido.quantidade IS 'Quantidade, de 1 a 24 (RN04)';
COMMENT ON COLUMN item_pedido.preco_unitario_centavos IS 'Preço unitário congelado na compra (RN15)';

-- pagamento: Tentativas de pagamento (simulado) de cada pedido.
CREATE TABLE pagamento (
	id SERIAL NOT NULL, 
	pedido_id INTEGER NOT NULL, 
	metodo VARCHAR(7) NOT NULL, 
	status VARCHAR(9) NOT NULL, 
	valor_centavos INTEGER NOT NULL, 
	cartao_final VARCHAR(4), 
	codigo_transacao VARCHAR(40), 
	criado_em TIMESTAMP WITHOUT TIME ZONE NOT NULL, 
	PRIMARY KEY (id), 
	CONSTRAINT ck_pagamento_valor CHECK (valor_centavos > 0), 
	FOREIGN KEY(pedido_id) REFERENCES pedido (id), 
	CONSTRAINT ck_pagamento_metodo CHECK (metodo IN ('CREDITO', 'DEBITO', 'PIX')), 
	CONSTRAINT ck_pagamento_status CHECK (status IN ('APROVADO', 'RECUSADO', 'ESTORNADO'))
);

CREATE INDEX ix_pagamento_pedido_id ON pagamento (pedido_id);

COMMENT ON TABLE pagamento IS 'Tentativas de pagamento (simulado) de cada pedido.';
COMMENT ON COLUMN pagamento.id IS 'Identificador da tentativa de pagamento';
COMMENT ON COLUMN pagamento.pedido_id IS 'Pedido pago (FK pedido.id)';
COMMENT ON COLUMN pagamento.metodo IS 'CREDITO, DEBITO ou PIX';
COMMENT ON COLUMN pagamento.status IS 'APROVADO, RECUSADO ou ESTORNADO';
COMMENT ON COLUMN pagamento.valor_centavos IS 'Valor cobrado, em centavos';
COMMENT ON COLUMN pagamento.cartao_final IS '4 últimos dígitos do cartão (vazio no Pix)';
COMMENT ON COLUMN pagamento.codigo_transacao IS 'Código devolvido pelo serviço simulado';
COMMENT ON COLUMN pagamento.criado_em IS 'Momento da tentativa';

