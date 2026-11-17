# Dicionário de dados – LaCakes Cupcakes Gourmet

Gerado automaticamente a partir dos models (`scripts/gerar_docs_banco.py`). Valores em dinheiro ficam em **centavos** (inteiro) para evitar erros de arredondamento.

## Tabela `categoria`

Categorias da vitrine (Clássicos, Recheados, Zero açúcar, Datas especiais).

| Coluna | Tipo | Nulo? | Padrão | Restrições | Descrição |
|---|---|---|---|---|---|
| `id` | INTEGER | não |  | PK | Identificador da categoria |
| `nome` | VARCHAR(40) | não |  | UNIQUE | Nome exibido no filtro da vitrine |
| `descricao` | VARCHAR(200) | sim |  |  | Descrição curta da categoria |

## Tabela `loja`



| Coluna | Tipo | Nulo? | Padrão | Restrições | Descrição |
|---|---|---|---|---|---|
| `id` | INTEGER | não |  | PK | Identificador (a loja tem um único registro) |
| `endereco` | VARCHAR(150) | não |  |  | Endereço da loja, usado na retirada |
| `dias_funcionamento` | VARCHAR(7) | não |  |  | Dias abertos: dígitos de 0 (segunda) a 6 (domingo), ex.: 012345 |
| `abre_as` | TIME | não |  | CHECK: abre_as < fecha_as | Horário de abertura |
| `fecha_as` | TIME | não |  | CHECK: abre_as < fecha_as | Horário de fechamento (depois da abertura) |
| `atualizado_em` | DATETIME | não | data/hora atual |  | Última alteração |

## Tabela `usuario`

Pessoas cadastradas (clientes e administradores).

| Coluna | Tipo | Nulo? | Padrão | Restrições | Descrição |
|---|---|---|---|---|---|
| `id` | INTEGER | não |  | PK | Identificador do usuário |
| `nome` | VARCHAR(80) | não |  |  | Nome completo do usuário |
| `email` | VARCHAR(120) | não |  | UNIQUE | E-mail de login, único por conta (RN01) |
| `senha_hash` | VARCHAR(255) | não |  |  | Hash da senha; a senha nunca é gravada (RNF02) |
| `telefone` | VARCHAR(20) | não |  |  | Telefone/WhatsApp para contato sobre o pedido |
| `perfil` | VARCHAR(7) | não | CLIENTE | CHECK: CLIENTE, ADMIN | CLIENTE ou ADMIN (RN13) |
| `criado_em` | DATETIME | não | data/hora atual |  | Data e hora do cadastro |

## Tabela `pedido`

Pedidos dos clientes, com modalidade, endereço de entrega e totais.

| Coluna | Tipo | Nulo? | Padrão | Restrições | Descrição |
|---|---|---|---|---|---|
| `id` | INTEGER | não |  | PK | Número do pedido |
| `usuario_id` | INTEGER | não |  | FK → usuario.id; índice | Cliente dono do pedido (FK usuario.id) |
| `status` | VARCHAR(20) | não | AGUARDANDO_PAGAMENTO | índice; CHECK: AGUARDANDO_PAGAMENTO, PAGO, EM_PREPARO, SAIU_PARA_ENTREGA, PRONTO_PARA_RETIRADA, ENTREGUE, CANCELADO | Situação atual (RN10) |
| `modalidade` | VARCHAR(8) | não |  | CHECK: ENTREGA, RETIRADA | ENTREGA ou RETIRADA |
| `cep` | VARCHAR(8) | sim |  |  | CEP de entrega, só dígitos (vazio na retirada) |
| `logradouro` | VARCHAR(120) | sim |  |  | Rua/avenida de entrega |
| `numero` | VARCHAR(10) | sim |  |  | Número do endereço |
| `complemento` | VARCHAR(60) | sim |  |  | Complemento (opcional) |
| `bairro` | VARCHAR(60) | sim |  |  | Bairro de entrega |
| `subtotal_centavos` | INTEGER | não |  | CHECK: total_centavos = subtotal_centavos + taxa_entrega_centavos; CHECK: subtotal_centavos >= 0 | Soma dos itens, em centavos |
| `taxa_entrega_centavos` | INTEGER | não | 0 | CHECK: total_centavos = subtotal_centavos + taxa_entrega_centavos; CHECK: taxa_entrega_centavos >= 0 | Taxa de entrega (RN06) |
| `total_centavos` | INTEGER | não |  | CHECK: total_centavos = subtotal_centavos + taxa_entrega_centavos; CHECK: subtotal_centavos >= 0 | Subtotal + taxa de entrega |
| `previsao_preparo` | DATE | sim |  |  | Dia de preparo e entrega quando foi pago com a loja fechada (vazio = mesmo dia) |
| `criado_em` | DATETIME | não | data/hora atual |  | Data e hora do pedido |
| `atualizado_em` | DATETIME | não | data/hora atual |  | Última alteração |

## Tabela `produto`

Cupcakes vendidos, com preço e estoque do dia.

| Coluna | Tipo | Nulo? | Padrão | Restrições | Descrição |
|---|---|---|---|---|---|
| `id` | INTEGER | não |  | PK | Identificador do produto |
| `categoria_id` | INTEGER | não |  | FK → categoria.id; índice | Categoria do produto (FK categoria.id) |
| `nome` | VARCHAR(80) | não |  | UNIQUE | Nome do cupcake, único (RN14) |
| `descricao` | TEXT | sim |  |  | Descrição exibida na página do produto |
| `ingredientes` | TEXT | sim |  |  | Lista de ingredientes |
| `alergenicos` | VARCHAR(200) | sim |  |  | Alergênicos (ex.: glúten, leite, ovos) |
| `preco_centavos` | INTEGER | não |  | CHECK: preco_centavos BETWEEN 100 AND 20000 | Preço em centavos, de 100 a 20000 (R$ 1,00 a R$ 200,00) |
| `estoque` | INTEGER | não | 0 | CHECK: estoque BETWEEN 0 AND 500 | Unidades disponíveis hoje, de 0 a 500 |
| `imagem` | VARCHAR(200) | sim |  |  | Caminho da imagem dentro de /static; vazio usa a imagem padrão |
| `ativo` | BOOLEAN | não | True |  | Se falso, o produto não aparece na vitrine |
| `criado_em` | DATETIME | não | data/hora atual |  | Data e hora do cadastro |

## Tabela `historico_status`

Linha do tempo das mudanças de status de cada pedido.

| Coluna | Tipo | Nulo? | Padrão | Restrições | Descrição |
|---|---|---|---|---|---|
| `id` | INTEGER | não |  | PK | Identificador do registro |
| `pedido_id` | INTEGER | não |  | FK → pedido.id; índice | Pedido (FK pedido.id) |
| `status` | VARCHAR(20) | não |  | CHECK: AGUARDANDO_PAGAMENTO, PAGO, EM_PREPARO, SAIU_PARA_ENTREGA, PRONTO_PARA_RETIRADA, ENTREGUE, CANCELADO | Status que o pedido assumiu |
| `observacao` | VARCHAR(200) | sim |  |  | Observação da mudança |
| `criado_em` | DATETIME | não | data/hora atual |  | Momento da mudança |

## Tabela `item_pedido`

Itens de cada pedido, com o preço congelado no momento da compra.

| Coluna | Tipo | Nulo? | Padrão | Restrições | Descrição |
|---|---|---|---|---|---|
| `id` | INTEGER | não |  | PK; CHECK: quantidade BETWEEN 1 AND 24 | Identificador do item |
| `pedido_id` | INTEGER | não |  | FK → pedido.id; índice | Pedido ao qual o item pertence (FK pedido.id) |
| `produto_id` | INTEGER | não |  | FK → produto.id; índice | Cupcake comprado (FK produto.id) |
| `quantidade` | INTEGER | não |  | CHECK: quantidade BETWEEN 1 AND 24 | Quantidade, de 1 a 24 (RN04) |
| `preco_unitario_centavos` | INTEGER | não |  | CHECK: preco_unitario_centavos > 0 | Preço unitário congelado na compra (RN15) |

Restrição de unicidade `uq_item_pedido_produto`: (pedido_id, produto_id).

## Tabela `pagamento`

Tentativas de pagamento (simulado) de cada pedido.

| Coluna | Tipo | Nulo? | Padrão | Restrições | Descrição |
|---|---|---|---|---|---|
| `id` | INTEGER | não |  | PK | Identificador da tentativa de pagamento |
| `pedido_id` | INTEGER | não |  | FK → pedido.id; índice | Pedido pago (FK pedido.id) |
| `metodo` | VARCHAR(7) | não |  | CHECK: CREDITO, DEBITO, PIX | CREDITO, DEBITO ou PIX |
| `status` | VARCHAR(9) | não |  | CHECK: APROVADO, RECUSADO, ESTORNADO | APROVADO, RECUSADO ou ESTORNADO |
| `valor_centavos` | INTEGER | não |  | CHECK: valor_centavos > 0 | Valor cobrado, em centavos |
| `cartao_final` | VARCHAR(4) | sim |  |  | 4 últimos dígitos do cartão (vazio no Pix) |
| `codigo_transacao` | VARCHAR(40) | sim |  |  | Código devolvido pelo serviço simulado |
| `criado_em` | DATETIME | não | data/hora atual |  | Momento da tentativa |
