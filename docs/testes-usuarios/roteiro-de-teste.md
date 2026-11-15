# Roteiro de teste – LaCakes Cupcakes Gourmet

Use o sistema como um cliente faria e, depois, como a dona da loja. Para cada cenário, marque no formulário se
**funcionou**, **não funcionou** ou se você **não testou**. Ao encontrar um problema, tire uma captura de tela
(Windows: tecla Windows + Shift + S) e anote o número dela no formulário.

> Os pagamentos são **simulados**: nenhum valor é cobrado e nenhum dado de cartão é guardado.

## Dados de teste

| O quê | Valor |
|---|---|
| Endereço do sistema | http://127.0.0.1:5000 |
| Conta de cliente | `cliente@lacakes.test` (ou crie a sua) |
| Conta de administradora | `admin@lacakes.test` |
| Senhas | informadas pelo responsável pelo teste (também estão no README) |
| CEP dentro da área de entrega (Jaú/SP) | `17201-000` |
| CEP fora da área de entrega | `13010-000` |
| Cartão aprovado (crédito ou débito) | `4111 1111 1111 1111`, validade `12/30`, CVV `123` |
| Cartão recusado | `4111 1111 1111 0000` |

## Cenários

| # | Cenário | Como testar | Resultado esperado |
|---|---|---|---|
| 1 | Vitrine e filtro | Abrir a página inicial e tocar nas categorias | Só aparecem os cupcakes da categoria; "Todos" volta a lista completa |
| 2 | Detalhes do cupcake | Abrir um cupcake | Descrição, ingredientes e bloco "Contém:" com alergênicos |
| 3 | Criar conta | Tela Criar conta; testar senha fraca e e-mail já cadastrado | Conta criada; erros aparecem embaixo de cada campo |
| 4 | Entrar e sair | Senha errada, depois a certa; sair pelo menu das iniciais | "E-mail ou senha inválidos"; depois "Olá, …"; ao sair, "Você saiu da sua conta" |
| 5 | Montar o carrinho | Adicionar sabores, usar − e +, remover | Total atualizado; aviso de pedido mínimo abaixo de R$ 25,00 |
| 6 | Limite de estoque | Tentar mais de 4 Limão Siciliano | "Só temos 4 unidades deste sabor hoje" |
| 7 | Entrega em Jaú | Finalizar com CEP 17201-000 | Taxa de R$ 8,00 (grátis a partir de R$ 120,00) e ida para o pagamento |
| 8 | CEP de outra cidade | Usar o CEP 13010-000 | "Ainda não entregamos neste CEP…" |
| 9 | Retirar na loja | Escolher Retirar na loja | Taxa R$ 0,00 e endereço da loja |
| 10 | Crédito | Aba Crédito, cartão aprovado | "Pedido confirmado" |
| 11 | Débito | Aba Débito, cartão aprovado | "Pedido confirmado" com "Cartão de débito •••• 1111" |
| 12 | Pix | Aba Pix, copiar código, Já paguei | "Pedido confirmado" com "Pix" |
| 13 | Pagamento recusado | Cartão terminado em 0000 | Tela "Pagamento recusado"; "Tentar novamente" volta ao pagamento |
| 14 | Acompanhar o pedido | Meus pedidos → abrir o pedido | Linha do tempo com a etapa atual destacada |
| 15 | Cancelar | Cancelar um pedido pago ou aguardando pagamento | "Pedido cancelado" (e estorno, se estava pago) |
| 16 | Admin: novo cupcake | Entrar como administradora → Novo cupcake; testar preço 250,00 | Erro de preço; com dados certos, o cupcake aparece na vitrine |
| 17 | Admin: estoque e desativar | Mudar estoques e salvar; desmarcar "Produto ativo" | Vitrine reflete o estoque; produto inativo some da vitrine |
| 18 | Admin: status do pedido | Pedidos → Avançar | Status muda; o cliente vê a nova etapa |
| 19 | Celular (opcional) | Navegador em tela estreita (F12 → modo celular) | Telas se ajustam, sem rolagem lateral |
