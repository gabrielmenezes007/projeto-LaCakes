# Testes – verificação e validação

Este documento mostra como foi conferido que o sistema faz o que foi especificado (**verificação**) e que ele atende
às necessidades de quem vai usar (**validação**).

## 1. Estratégia (Modelo V)

| Lado do desenvolvimento | Artefato | Teste correspondente | Como foi feito |
|---|---|---|---|
| Requisitos | Histórias de usuário e critérios de aceitação | **Teste de aceitação** | Critérios de aceitação ligados a testes automatizados (item 3.1), teste manual no navegador (3.2) e teste com 5 usuários (3.3) |
| Análise | Casos de uso, regras de negócio | **Teste de sistema** | Fluxos completos pelas rotas: cadastro → carrinho → checkout → pagamento → acompanhamento → admin |
| Arquitetura | MVC, modelo de dados | **Teste de integração** | `test_rotas_cliente.py`, `test_rotas_admin_e_erros.py` e `test_banco.py` |
| Código | Models e serviços | **Teste unitário** | `test_models.py` e `test_servicos.py` |

## 2. Verificação

### 2.1 Revisões

| Revisão | Resultado |
|---|---|
| Cada regra de negócio (RN01 a RN15) conferida contra o código dos serviços | Todas implementadas; cada uma tem pelo menos um teste (item 3.1) |
| Telas implementadas comparadas com os mockups | Diferenças registradas em [revisao-do-planejamento.md](revisao-do-planejamento.md#3-interface-ihc) |
| Script SQL físico comparado com os models | Feito por teste automatizado (`test_banco.py`), para os dois nunca ficarem diferentes |
| Varredura antes de cada commit | Nenhum dado pessoal ou arquivo de entrega no repositório |

### 2.2 Testes automatizados (pytest)

**Resultado: 123 testes, 123 aprovados, 0 falhas. Cobertura de código: 95%.**
Saída completa da execução: [evidencias/resultado-testes.txt](evidencias/resultado-testes.txt).

| Arquivo | Tipo | Testes | O que cobre |
|---|---|---|---|
| `tests/test_models.py` | Unitário | 15 | Senha com hash, e-mail único, disponibilidade e estoque, totais do pedido, máquina de status, regra de cancelamento |
| `tests/test_servicos.py` | Unitário | 39 | Taxa de entrega, área de entrega de Jaú (inclusive os limites da faixa), pedido mínimo, validação de cartão, recusa do final 0000, senha forte, conversão de valores, proteção de redirecionamento |
| `tests/test_rotas_cliente.py` | Integração | 43 | Vitrine, filtros, detalhe, 404, cadastro, login/logout, carrinho, checkout, pagamento (crédito, débito, Pix, recusa, estoque), acompanhamento, permissões, cancelamento |
| `tests/test_rotas_admin_e_erros.py` | Integração | 23 | Acesso restrito, cadastro e edição de produto, upload, estoque do dia, avanço de status, filtro, páginas de erro 404/500/400(CSRF)/413 |
| `tests/test_banco.py` | Integração (dados) | 3 | Script SQL cria as mesmas tabelas e colunas dos models, CHECK funcionando, dados iniciais |

Cobertura por camada (resumo da execução):

| Camada | Cobertura |
|---|---|
| Models (`app/models`) | 92% a 100% |
| Services (`app/services`) | 89% a 100% |
| Controllers (`app/controllers`) | 95% a 100% |
| **Total** | **95%** |

Como rodar:

```bash
.venv\Scripts\python -m pytest --cov=app        # Linux/macOS: .venv/bin/python -m pytest --cov=app
```

### 2.3 Defeitos encontrados na verificação

Defeitos achados pelos testes e revisões durante o desenvolvimento, todos corrigidos antes dos testes com usuários:

| # | Defeito | Como foi encontrado | Correção |
|---|---|---|---|
| V1 | Na tela de checkout, a mensagem de pedido mínimo não aparecia: o macro de alerta tinha o mesmo nome da variável da mensagem e a escondia. | Revisão de código | Macro importado com outro nome (`caixa_alerta`) |
| V2 | Teste de "desativar produto" falhava porque o nome do produto aparecia na mensagem de sucesso. | Teste automatizado | Verificação passou a olhar o card da vitrine, não a página inteira |
| V3 | Aviso do SQLAlchemy ao montar pedidos nos testes (objeto fora da sessão). | Execução dos testes | Pedido adicionado à sessão antes de receber itens |
| V4 | Valores longos no resumo (ex.: "Cartão de débito •••• 1111") quebravam a linha desalinhados. | Teste manual no navegador | Coluna de valores alinhada à direita |
| V5 | Ícone de conta quase invisível sobre o roxo do topo. | Revisão visual dos mockups | Troca por círculo branco com iniciais |

## 3. Validação

### 3.1 Critérios de aceitação ligados aos testes (rastreabilidade)

| História | Testes que validam os critérios de aceitação |
|---|---|
| US01 Ver a vitrine | `test_mostra_produtos_ativos_e_esconde_inativos`, `test_vitrine_vazia` |
| US02 Filtrar por categoria | `test_filtro_por_categoria`, `test_categoria_sem_produtos` |
| US03 Detalhes e alergênicos | `test_detalhe_mostra_alergenicos`, `test_produto_inexistente_ou_inativo_404` |
| US04 Sabor esgotado | `test_selos_esgotado_e_ultimas_unidades`, `test_nao_adiciona_esgotado`, `test_disponivel_e_esgotado`, `test_ultimas_unidades` |
| US05 Criar conta | `test_cadastro_com_sucesso_ja_entra_logado`, `test_cadastro_email_duplicado_mantem_campos`, `test_cadastro_senha_fraca_e_senhas_diferentes`, `test_senha_forte`, `test_cadastro_valida_todos_os_campos` |
| US06 Entrar | `test_login_valido_e_invalido`, `test_login_volta_para_pagina_de_origem`, `test_carrinho_mantido_apos_login`, `test_login_nao_redireciona_para_outro_site` |
| US07 Sair | `test_logout_encerra_sessao` |
| US08 Adicionar ao carrinho | `test_adicionar_e_somar`, `test_nao_passa_do_estoque`, `test_limite_de_24_por_sabor` |
| US09 Alterar/remover itens | `test_atualizar_e_remover`, `test_atualizar_para_zero_remove` |
| US10 Entrega ou retirada | `test_taxa_de_entrega`, `test_entrega_gratis_a_partir_de_120`, `test_retirada_sem_taxa`, `test_retirada_sem_endereco_e_sem_taxa`, `test_entrega_gratis_acima_de_120` |
| US11 Endereço e área de entrega | `test_area_de_entrega_jau` (9 casos), `test_cep_fora_de_jau`, `test_endereco_incompleto` |
| US12 Revisar e confirmar | `test_exige_login`, `test_pedido_minimo`, `test_cria_pedido_com_taxa_e_precos_congelados`, `test_carrinho_vazio_volta_para_carrinho`, `test_aviso_de_pedido_minimo_no_carrinho` |
| US13 Cartão de crédito ou débito | `test_credito_aprovado_baixa_estoque`, `test_debito_registra_modalidade`, `test_dados_do_cartao_invalidos`, `test_estoque_acabou_antes_de_pagar`, `test_cartao_vencido`, `test_cartao_com_erros` |
| US14 Pix | `test_pix`, `test_pix_sempre_aprovado` |
| US15 Pagamento recusado | `test_cartao_recusado_mantem_aguardando`, `test_final_0000_e_recusado` |
| US16 Histórico de pedidos | `test_lista_vazia`, `test_lista_e_detalhe_com_linha_do_tempo`, `test_cliente_nao_ve_pedido_de_outro` |
| US17 Acompanhar o pedido | `test_lista_e_detalhe_com_linha_do_tempo`, `test_cliente_ve_mudanca_de_status`, `test_fluxo_de_status_entrega`, `test_fluxo_de_status_retirada` |
| US18 Cancelar antes do preparo | `test_cancelar_pedido_pago_estorna_e_repoe_estoque`, `test_nao_cancela_em_preparo`, `test_pode_cancelar_so_antes_do_preparo` |
| US19 Área administrativa | `test_visitante_vai_para_login`, `test_cliente_recebe_403`, `test_admin_acessa` |
| US20 Cadastrar cupcake | `test_cadastrar_produto_aparece_na_vitrine`, `test_nome_duplicado_e_preco_fora_da_faixa`, `test_upload_de_foto`, `test_upload_com_extensao_invalida` |
| US21 Editar e desativar | `test_editar_preco_e_desativar`, `test_editar_produto_inexistente` |
| US22 Estoque do dia | `test_atualizar_estoque_do_dia`, `test_estoque_invalido_nao_salva_nada` |
| US23 Pedidos e status | `test_avancar_ate_entregue`, `test_nao_avanca_pedido_sem_pagamento`, `test_filtro_por_status` |

### 3.2 Teste de aceitação manual (desenvolvedor)

Executado em 15/11/2026, no Microsoft Edge, em tamanho de celular (375 px) e de computador (1280 px):

| # | Cenário | Resultado |
|---|---|---|
| M1 | Instalação do zero com `iniciar.bat` numa cópia nova do repositório | ✅ Ambiente criado, dependências instaladas, banco criado e vitrine no ar |
| M2 | Login com a conta de cliente de teste | ✅ Mensagem "Olá, Ana!" e iniciais no topo |
| M3 | Adicionar cupcakes pela vitrine e pela página do produto; alterar quantidade no carrinho | ✅ Contador e totais atualizados; aviso de pedido mínimo |
| M4 | Checkout com CEP de outra cidade (13010-000) | ✅ Mensagem "Ainda não entregamos neste CEP" no campo |
| M5 | Checkout com CEP de Jaú (17201-000) | ✅ Pedido criado e redirecionamento para pagamento |
| M6 | Pagamento no débito com cartão final 0000 | ✅ Tela "Pagamento recusado"; pedido continua aguardando |
| M7 | Pagamento no débito com cartão válido | ✅ "Pedido confirmado" com "Cartão de débito •••• 1111" |
| M8 | Acompanhamento do pedido | ✅ Linha do tempo com Aguardando pagamento e Pago com data e hora |
| M9 | Cliente tentando abrir a área admin | ✅ Página 403 "Acesso negado" |
| M10 | Admin avançando o pedido para "Em preparo" | ✅ Status atualizado e visível para o cliente |
| M11 | Estoque baixado após a compra | ✅ Quantidades corretas na lista do admin |

Os cenários M1 a M5, M7, M8 e M11 foram feitos clicando no navegador; M6, M9 e M10 foram percorridos no mesmo
navegador pelo script `scripts/capturar_telas.py`, que também gerou as capturas de tela: [img/telas](img/telas).

O sistema também foi instalado e usado pelo autor no próprio computador, com `iniciar.bat`, sem erros.

### 3.3 Validação com usuários (5 testadores)

**Situação: a preencher.** Os testes com usuários ainda não foram realizados.

- Cada testador segue o [roteiro de teste](../testes-usuarios/roteiro-de-teste.md) (15 tarefas, em linguagem do dia a
  dia) e registra o resultado no seu quadro do documento de entrega: nome, data, o que funcionou, o que não funcionou
  e o que deve ser corrigido, e o que não foi testado e por quê.
- Resumo das 5 avaliações, correções feitas e laudo de qualidade: a preencher depois dos testes.

| Testador | Data | Funcionou | Não funcionou | Não testado |
|---|---|---|---|---|
| Testador 1 | a preencher | a preencher | a preencher | a preencher |
| Testador 2 | a preencher | a preencher | a preencher | a preencher |
| Testador 3 | a preencher | a preencher | a preencher | a preencher |
| Testador 4 | a preencher | a preencher | a preencher | a preencher |
| Testador 5 | a preencher | a preencher | a preencher | a preencher |
