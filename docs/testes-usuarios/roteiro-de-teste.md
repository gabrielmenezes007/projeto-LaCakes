# Roteiro de teste – LaCakes Cupcakes Gourmet

Obrigado por testar! Use o sistema como se fosse comprar cupcakes de verdade. Não existe resposta certa ou errada:
o importante é contar com sinceridade o que deu certo, o que deu errado e o que ficou confuso.

> Nada é cobrado de verdade: os pagamentos são apenas uma simulação.

## Dados para usar no teste

| Para quê | O que digitar |
|---|---|
| Entrar como dona da loja (parte 2) | E-mail `admin@lacakes.test` · senha `Admin@2026` |
| CEP de Jaú (a loja entrega) | `17201-000` |
| CEP de outra cidade (a loja não entrega) | `13010-000` |
| Cartão que será **recusado** | `4111 1111 1111 0000` |
| Cartão que será **aprovado** | `4111 1111 1111 1111` |
| Validade e código do cartão | validade `12/30` · código `123` |

## Parte 1 – Como cliente

| # | O que fazer | O que deve acontecer |
|---|---|---|
| 1 | Na página inicial, clique nos botões de tipo (Clássicos, Recheados…) e depois em "Todos". | Aparecem só os cupcakes daquele tipo; "Todos" mostra tudo de novo. |
| 2 | Clique em um cupcake para ver os detalhes. | Aparecem a descrição, os ingredientes e o aviso "Contém:". |
| 3 | Clique em **Entrar** e depois em **Criar conta**. Primeiro tente a senha `abc`; depois crie sua conta com uma senha de verdade (letras e números). | Primeiro aparece um aviso explicando a senha; depois a conta é criada e você já entra. |
| 4 | Clique no círculo com as suas iniciais (no alto) e em **Sair**. Entre de novo, errando a senha uma vez. | Aviso de senha errada; com a senha certa, você entra. |
| 5 | Coloque cupcakes no carrinho (pelo menos R$ 25,00, que é o pedido mínimo) e mude as quantidades com os botões − e +. | O total muda na hora. |
| 6 | Na página inicial, clique 5 vezes em **+ Adicionar** no **Limão Siciliano**. | Na 5ª vez, aviso de que só existem 4 unidades. |
| 7 | No carrinho, clique em **Finalizar pedido**, escolha **Entrega**, invente um endereço com o CEP `13010-000` e clique em **Confirmar pedido**. | Aviso de que a loja não entrega nesse CEP. |
| 8 | Troque para o CEP `17201-000` e confirme de novo. | Aparece a tela de pagamento. |
| 9 | Escolha **Débito** e pague com o cartão que será recusado. Depois clique em **Tentar novamente** e use o cartão aprovado. | Primeiro "Pagamento recusado" (sem cobrança); depois "Pedido confirmado". |
| 10 | Faça outro pedido escolhendo **Retirar na loja** e pague com **Pix** (botão **Já paguei**). | Pedido confirmado, sem taxa de entrega. |
| 11 | Clique em **Pedidos** e abra um dos seus pedidos. | Aparece o andamento do pedido, etapa por etapa. |
| 12 | Em um dos pedidos, clique em **Cancelar pedido**. | O pedido aparece como cancelado. |

## Parte 2 – Como dona da loja

Saia da sua conta e entre com o e-mail e a senha da dona da loja (tabela acima).

| # | O que fazer | O que deve acontecer |
|---|---|---|
| 13 | Em **Pedidos**, clique em **Avançar** em um pedido até ele ficar "Entregue". | O andamento muda a cada clique. |
| 14 | Em **Produtos**, mude a quantidade de um sabor e clique em **Salvar estoques do dia**. | Aviso de que o estoque foi salvo. |
| 15 | Clique em **Novo cupcake**. Primeiro tente o preço `250,00`; depois cadastre um cupcake inventado com um preço normal e estoque `10`. | Primeiro um aviso sobre o preço; depois o cupcake aparece na loja. |

## Como registrar a sua opinião

Use um dos quadros em branco (um para cada pessoa) e escreva com as suas palavras:

- seu **nome** e a **data** do teste;
- **o que funcionou**;
- **o que não funcionou**: o que aconteceu, o que você esperava e o que deveria ser corrigido;
- **o que você não testou** e por quê (faltou tempo, não encontrou, não entendeu como fazer…).

Sugestões e coisas que ficaram confusas também são muito bem-vindas.
