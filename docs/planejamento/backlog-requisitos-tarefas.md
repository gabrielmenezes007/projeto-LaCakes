# Backlog, requisitos e tarefas

## Backlog priorizado

| Ordem | ID | Tema | História | Pontos | Prioridade |
|---|---|---|---|---|---|
| 1 | US05 | Conta do cliente | Como visitante, quero criar uma conta informando nome, e-mail, telefone e senha, para poder fazer pedidos e acompanhar minhas compras. | 3 | A |
| 2 | US06 | Conta do cliente | Como cliente cadastrado, quero entrar com e-mail e senha, para finalizar pedidos e ver meu histórico de compras. | 2 | A |
| 3 | US19 | Administração da loja | Como proprietária da loja, quero uma área administrativa protegida por login, para que só a minha equipe consiga mexer em produtos e pedidos. | 2 | A |
| 4 | US20 | Administração da loja | Como proprietária, quero cadastrar um cupcake com nome, categoria, descrição, ingredientes, alergênicos, preço, foto e estoque do dia, para que ele apareça na vitrine. | 3 | A |
| 5 | US01 | Vitrine virtual | Como visitante, quero ver em uma única tela os cupcakes disponíveis hoje, com foto, nome e preço, para decidir rapidamente o que comprar sem precisar perguntar pelo WhatsApp. | 3 | A |
| 6 | US08 | Carrinho, pedido e entrega | Como cliente, quero escolher a quantidade de um cupcake e adicioná-lo ao carrinho, para montar meu pedido com vários sabores. | 3 | A |
| 7 | US09 | Carrinho, pedido e entrega | Como cliente, quero mudar a quantidade ou remover itens do carrinho e ver o total atualizado, para ajustar o pedido ao meu orçamento. | 2 | A |
| 8 | US10 | Carrinho, pedido e entrega | Como cliente, quero escolher se vou receber os cupcakes em casa ou retirar na loja e ver o valor do frete antes de pagar, para decidir o que sai mais em conta. | 3 | A |
| 9 | US12 | Carrinho, pedido e entrega | Como cliente, quero revisar itens, quantidades, endereço e valores antes de confirmar, para ter certeza de que o pedido está certo. | 5 | A |
| 10 | US13 | Pagamento | Como cliente, quero pagar meu pedido com cartão de crédito ou de débito sem sair do site, para concluir a compra de forma rápida e do jeito que eu preferir. | 5 | A |
| 11 | US17 | Acompanhamento do pedido | Como cliente, quero ver em que etapa meu pedido está (pago, em preparo, saiu para entrega, entregue), para saber quando os cupcakes vão chegar. | 3 | A |
| 12 | US23 | Administração da loja | Como atendente, quero ver os pedidos recebidos, filtrar por status e avançar a etapa de cada um, para organizar a produção e manter o cliente informado. | 5 | A |
| 13 | US03 | Vitrine virtual | Como cliente que tem alergia a amendoim, quero abrir a página de um cupcake e ver a descrição, os ingredientes e os alergênicos, para comprar com segurança. | 2 | B |
| 14 | US04 | Vitrine virtual | Como cliente, quero ver claramente quando um sabor esgotou no dia, para não perder tempo tentando comprar algo que a loja não tem mais. | 1 | B |
| 15 | US22 | Administração da loja | Como confeiteira, quero informar rapidamente quantas unidades de cada sabor foram produzidas hoje, para que a vitrine mostre só o que realmente existe. | 2 | B |
| 16 | US11 | Carrinho, pedido e entrega | Como cliente, quero informar meu CEP e endereço e saber na hora se a loja entrega na minha região, para não fazer um pedido que não pode ser entregue. | 3 | B |
| 17 | US15 | Pagamento | Como cliente, quero receber uma mensagem clara quando meu pagamento for recusado e poder tentar de novo ou trocar a forma de pagamento, para não perder o pedido. | 2 | B |
| 18 | US16 | Acompanhamento do pedido | Como cliente, quero ver a lista dos meus pedidos com data, valor e status, para lembrar o que comprei e acompanhar o que está em andamento. | 2 | B |
| 19 | US21 | Administração da loja | Como proprietária, quero editar dados e preço de um cupcake ou desativá-lo, para tirar da vitrine um sabor fora de época sem perder o histórico de vendas. | 2 | B |
| 20 | US07 | Conta do cliente | Como cliente, quero sair da minha conta, para que outra pessoa que use o mesmo celular ou computador não veja meus pedidos. | 1 | B |
| 21 | US02 | Vitrine virtual | Como visitante, quero filtrar a vitrine por categoria (Clássicos, Recheados, Zero açúcar e Datas especiais), para encontrar mais rápido o tipo de cupcake que procuro. | 2 | C |
| 22 | US14 | Pagamento | Como cliente, quero pagar com Pix copiando um código, para não precisar digitar dados de cartão. | 3 | C |
| 23 | US18 | Acompanhamento do pedido | Como cliente, quero cancelar um pedido que ainda não entrou em preparo, para corrigir um engano sem precisar ligar para a loja. | 3 | D |

## Escala de prioridade

- **A** – Essencial: sem ela o sistema não vende (entra no MVP).
- **B** – Importante: melhora muito a experiência; entra logo depois do essencial.
- **C** – Desejável: agrega valor, mas a loja consegue operar sem.
- **D** – Pode esperar: baixa frequência de uso.
- **E** – Futuro: ideias anotadas para versões seguintes (ex.: cupom de desconto, avaliações, notificações por WhatsApp).

## Requisitos funcionais

| ID | Requisito | Histórias |
|---|---|---|
| RF01 | Listar produtos ativos na vitrine com foto, nome, preço, categoria e disponibilidade. | US01, US04 |
| RF02 | Filtrar a vitrine por categoria. | US02 |
| RF03 | Exibir detalhes do produto (descrição, ingredientes, alergênicos, estoque). | US03 |
| RF04 | Cadastrar cliente com validação de e-mail único e senha forte. | US05 |
| RF05 | Autenticar e encerrar sessão de usuários. | US06, US07 |
| RF06 | Manter carrinho de compras na sessão (adicionar, alterar, remover, calcular totais). | US08, US09 |
| RF07 | Calcular taxa de entrega conforme modalidade e subtotal. | US10 |
| RF08 | Validar CEP da área de entrega e endereço obrigatório. | US11 |
| RF09 | Criar pedido a partir do carrinho, validando pedido mínimo e congelando preços. | US12 |
| RF10 | Processar pagamento simulado por cartão de crédito, cartão de débito e Pix, registrando cada tentativa. | US13, US14, US15 |
| RF11 | Baixar estoque na aprovação e devolver no cancelamento de pedido pago. | US13, US18 |
| RF12 | Listar pedidos do cliente e exibir linha do tempo de status. | US16, US17 |
| RF13 | Permitir cancelamento pelo cliente antes do preparo. | US18 |
| RF14 | Restringir a área administrativa ao perfil Administrador. | US19 |
| RF15 | Cadastrar, editar, ativar e desativar produtos. | US20, US21 |
| RF16 | Atualizar estoque diário dos produtos. | US22 |
| RF17 | Listar pedidos no admin, filtrar por status e avançar o status. | US23 |

## Requisitos não funcionais

| ID | Nome | Descrição |
|---|---|---|
| RNF01 | Responsividade | Todas as telas devem funcionar em celulares a partir de 360 px de largura, tablets e computadores, sem rolagem horizontal. |
| RNF02 | Segurança de senha | Senhas são guardadas apenas como hash (algoritmo seguro do Werkzeug), nunca em texto puro. |
| RNF03 | Desempenho | A vitrine deve carregar em até 2 segundos em rede local com até 100 produtos cadastrados. |
| RNF04 | Usabilidade das mensagens | Mensagens de erro em português, perto do campo com problema, dizendo o que fazer para corrigir. |
| RNF05 | Acessibilidade | Contraste mínimo AA (WCAG 2.1), texto alternativo em todas as imagens, rótulos em todos os campos e navegação por teclado. |
| RNF06 | Segurança de sessão e formulários | Formulários protegidos contra CSRF; sessão de login com cookie HttpOnly; rotas privadas exigem autenticação. |
| RNF07 | Portabilidade do banco | A conexão com o banco é definida pela variável de ambiente DATABASE_URL, permitindo SQLite, PostgreSQL ou MySQL sem mudar o código. |
| RNF08 | Manutenibilidade | Código organizado em MVC, com testes automatizados (pytest) cobrindo modelos, rotas e erros. |
| RNF09 | Privacidade (LGPD) | Não armazenar número completo de cartão nem CVV; coletar apenas dados necessários para o pedido. |
| RNF10 | Tratamento de erros | Páginas amigáveis para erros 403, 404 e 500, sempre com um caminho de volta para a vitrine. |

## Regras de negócio

| ID | Regra | Descrição |
|---|---|---|
| RN01 | Conta única por e-mail | Cada e-mail só pode ter uma conta. A senha precisa ter no mínimo 8 caracteres, com pelo menos uma letra e um número. |
| RN02 | Compra exige login | Visitantes podem ver a vitrine e montar o carrinho, mas só clientes autenticados podem finalizar um pedido. |
| RN03 | Disponibilidade do produto | Produto inativo não aparece na vitrine. Produto ativo com estoque do dia igual a zero aparece com o selo "Esgotado" e não pode ser adicionado ao carrinho. |
| RN04 | Limite de quantidade | A quantidade de cada item no carrinho vai de 1 a 24 unidades e nunca pode passar do estoque disponível do produto. |
| RN05 | Pedido mínimo | O subtotal mínimo de um pedido é R$ 25,00, em qualquer modalidade (entrega ou retirada). |
| RN06 | Taxa de entrega | Entrega custa R$ 8,00 (taxa fixa). Para subtotal a partir de R$ 120,00 a entrega é grátis. Retirada na loja não tem taxa. |
| RN07 | Área de entrega | A loja fica em Jaú/SP (Rua das Flores, 120) e só entrega dentro da cidade: CEPs de 17200-001 a 17229-999. Fora dessa faixa, o cliente só pode escolher retirada na loja. |
| RN08 | Baixa de estoque | O estoque só é baixado quando o pagamento é aprovado. Antes de aprovar, o sistema confere de novo se ainda há estoque de cada item. |
| RN09 | Pagamento simulado | O pagamento é simulado e aceita cartão de crédito, cartão de débito ou Pix. Cartão (crédito ou débito): número com 16 dígitos, validade futura e CVV de 3 dígitos. Para fins de teste, cartões terminados em 0000 são recusados nas duas modalidades. Pix: um código "copia e cola" é gerado e o pagamento é aprovado quando o cliente confirma. |
| RN10 | Fluxo de status do pedido | Status possíveis: Aguardando pagamento → Pago → Em preparo → Saiu para entrega (ou Pronto para retirada) → Entregue. O pedido só avança uma etapa por vez. Cancelado é um status final. |
| RN11 | Cancelamento pelo cliente | O cliente só pode cancelar enquanto o pedido estiver Aguardando pagamento ou Pago. Se já estava pago, o estoque volta e o pagamento é marcado como estornado (simulado). |
| RN12 | Privacidade dos pedidos | Cada cliente só pode ver os próprios pedidos. |
| RN13 | Área administrativa restrita | Telas e ações de administração só podem ser acessadas por usuários com perfil Administrador. |
| RN14 | Dados do produto | Nome é obrigatório e único. Preço entre R$ 1,00 e R$ 200,00. Estoque do dia entre 0 e 500. Toda vez que um produto é cadastrado ele precisa ter uma categoria. |
| RN15 | Preço congelado | O preço de cada item é gravado no pedido no momento da compra. Se o preço do produto mudar depois, os pedidos antigos não mudam. |

## Tarefas (2 a 12 h)

| História | Tarefa | Horas |
|---|---|---|
| US05 | Criar modelo Usuario com hash de senha | 3 |
| US05 | Criar formulário e validações de cadastro (RN01) | 4 |
| US05 | Criar template de cadastro com mensagens por campo | 3 |
| US05 | Testes de cadastro (sucesso, e-mail duplicado, senha fraca) | 3 |
| US06 | Implementar login com Flask-Login e redirecionamento 'next' | 4 |
| US06 | Criar template de login e mensagens de erro | 2 |
| US06 | Testes de login (válido, inválido, carrinho mantido) | 2 |
| US19 | Decorator de acesso admin e páginas 403 | 2 |
| US19 | Script para criar o primeiro administrador | 2 |
| US19 | Testes de acesso restrito | 2 |
| US20 | Formulário de produto com validações (RN14) | 4 |
| US20 | Upload de foto com imagem padrão | 3 |
| US20 | Template do formulário no admin | 3 |
| US20 | Testes de cadastro de produto | 3 |
| US01 | Criar modelo Produto e Categoria (ORM) e dados de exemplo | 4 |
| US01 | Criar rota e controller da vitrine | 3 |
| US01 | Criar template da vitrine com cards responsivos | 5 |
| US01 | Escrever testes da vitrine (ativos x inativos) | 2 |
| US08 | Criar serviço de carrinho em sessão (adicionar e somar) | 4 |
| US08 | Validar quantidade x estoque (RN04) e mensagens | 2 |
| US08 | Contador do carrinho no cabeçalho | 2 |
| US08 | Testes do carrinho (adicionar e limites) | 3 |
| US09 | Rotas de alterar quantidade e remover item | 3 |
| US09 | Template do carrinho com totais e estado vazio | 4 |
| US09 | Testes de alteração, remoção e carrinho vazio | 2 |
| US10 | Implementar cálculo de taxa de entrega (RN06) | 2 |
| US10 | Seletor de modalidade no checkout | 2 |
| US10 | Testes unitários da taxa de entrega | 2 |
| US12 | Criar modelos Pedido, ItemPedido e HistoricoStatus | 5 |
| US12 | Rota de checkout com resumo e pedido mínimo (RN05) | 4 |
| US12 | Criar pedido congelando preços (RN15) | 3 |
| US12 | Testes de criação de pedido e regras | 4 |
| US13 | Criar modelo Pagamento e serviço de pagamento simulado | 4 |
| US13 | Formulário de cartão com escolha crédito/débito e validações (RN09) | 4 |
| US13 | Baixa de estoque com reverificação (RN08) | 3 |
| US13 | Tela de pedido confirmado | 2 |
| US13 | Testes de pagamento aprovado e estoque insuficiente | 4 |
| US17 | Template de detalhe do pedido com linha do tempo | 4 |
| US17 | Implementar máquina de status do pedido (RN10) | 3 |
| US17 | Testes da máquina de status | 2 |
| US23 | Lista de pedidos do admin com filtro por status | 4 |
| US23 | Ação de avançar status com validação | 3 |
| US23 | Testes do fluxo de status no admin | 3 |
| US03 | Criar rota de detalhe do produto com erro 404 | 2 |
| US03 | Criar template de detalhe com bloco de alergênicos | 3 |
| US03 | Testes da página de detalhe e do 404 | 2 |
| US04 | Implementar regra de disponibilidade (selo Esgotado e Últimas unidades) | 2 |
| US04 | Bloquear adição de produto esgotado no back-end e testar | 2 |
| US22 | Edição rápida de estoque na lista do admin | 3 |
| US22 | Validação de estoque e testes | 2 |
| US11 | Formulário de endereço com validação de CEP (RN07) | 3 |
| US11 | Tela de erro de CEP fora da área e testes | 2 |
| US15 | Tela de pagamento recusado com nova tentativa | 2 |
| US15 | Registrar tentativas recusadas e testar | 2 |
| US16 | Rota e template 'Meus pedidos' (somente do usuário) | 3 |
| US16 | Testes de acesso ao pedido de outro cliente (403) | 2 |
| US21 | Edição e ativar/desativar produto | 3 |
| US21 | Testes de edição e preço congelado | 2 |
| US07 | Implementar logout e proteger rotas privadas | 2 |
| US02 | Adicionar filtro por categoria na consulta da vitrine | 2 |
| US02 | Criar barra de categorias rolável no celular | 3 |
| US14 | Gerar código Pix simulado e tela com botão copiar | 3 |
| US14 | Confirmação 'Já paguei' e testes | 2 |
| US18 | Implementar cancelamento com estorno simulado (RN11) | 3 |
| US18 | Botão e confirmação de cancelamento + testes | 3 |

**Total:** 185 horas