# Manual de uso – LaCakes Cupcakes Gourmet

Este manual explica como instalar o sistema e como usar cada parte dele, como cliente e como administradora da loja.

> **Ambiente de demonstração:** os pagamentos são **simulados**. Nenhum valor é cobrado e nenhum dado de cartão é
> guardado (só os 4 últimos dígitos).

## 1. Instalação

### Requisitos
- Windows 10/11, Linux ou macOS
- **Python 3.10 ou mais novo** ([python.org/downloads](https://www.python.org/downloads/)). No Windows, marque a opção
  **"Add python.exe to PATH"** durante a instalação.
- Conexão com a internet só na primeira vez (para baixar as bibliotecas).

### Subir com um comando
1. Baixe o projeto (botão **Code → Download ZIP** no GitHub) e descompacte, ou faça `git clone`.
2. Na pasta do projeto:
   - **Windows:** dê dois cliques em `iniciar.bat`.
   - **Linux/macOS:** rode `./iniciar.sh` no terminal.
3. Na primeira vez o script cria o ambiente virtual, instala as dependências e cria o banco com dados de exemplo
   (leva de 1 a 3 minutos). Nas próximas vezes é bem mais rápido.
4. O navegador abre em **http://127.0.0.1:5000**. Para parar o sistema, feche a janela do terminal ou tecle `Ctrl+C`.

Para **voltar o banco ao estado inicial** (apagando pedidos e cadastros de teste): dois cliques em
`iniciar-com-banco-limpo.bat` (ou, no terminal, `iniciar.bat --recriar` / `./iniciar.sh --recriar`).

### Instalação manual (alternativa)
```bash
python -m venv .venv
.venv\Scripts\activate          # Linux/macOS: source .venv/bin/activate
pip install -r requirements.txt
python -m app.seed
python run.py
```

### Contas de teste
| Perfil | E-mail | Senha |
|---|---|---|
| Administradora (Laysa) | `admin@lacakes.test` | `Admin@2026` |
| Cliente de exemplo (Ana Souza) | `cliente@lacakes.test` | `Cliente@2026` |

Também é possível criar uma conta nova pela tela **Criar conta**.

### Dados úteis para testar
| O que testar | Dado |
|---|---|
| CEP **dentro** da área de entrega (Jaú/SP) | `17201-000` (qualquer CEP de 17200-001 a 17229-999) |
| CEP **fora** da área de entrega | `13010-000` |
| Cartão (crédito ou débito) **aprovado** | `4111 1111 1111 1111`, validade futura (ex.: `12/30`), CVV `123` |
| Cartão **recusado** | qualquer número terminado em `0000`, ex.: `4111 1111 1111 0000` |
| Produto com **poucas unidades** | Limão Siciliano (4 em estoque) |
| Produto **esgotado** | Morango com Chantilly |

## 2. Usando como cliente

| Tela | Como usar |
|---|---|
| **Vitrine** (página inicial) | Mostra os cupcakes do dia. Toque numa categoria para filtrar. "Esgotado" indica que o sabor acabou hoje; "Últimas unidades" indica que restam 5 ou menos. |
| **Detalhes do cupcake** | Toque no cupcake para ver descrição, ingredientes e alergênicos ("Contém:"). Escolha a quantidade com − e + e toque em **Adicionar ao carrinho**. |
| **Carrinho** (ícone 🛒) | Altere quantidades com − e + (o total é recalculado na hora) ou toque em **Remover**. O pedido mínimo é de R$ 25,00. |
| **Entrar / Criar conta** | Não é preciso conta para montar o carrinho; ela só é pedida na hora de finalizar. O carrinho continua lá depois do login. |
| **Entrega e resumo** | Escolha **Entrega** (R$ 8,00; grátis a partir de R$ 120,00; só em Jaú) ou **Retirar na loja** (sem taxa). Na entrega, informe CEP, rua, número e bairro. Confira o resumo e toque em **Confirmar pedido**. |
| **Pagamento** | Escolha **Crédito**, **Débito** ou **Pix**. No cartão, preencha nome, número, validade e CVV. No Pix, copie o código e toque em **Já paguei**. Se o cartão for recusado, nada é cobrado e você pode tentar de novo. |
| **Pedido confirmado** | Mostra o número do pedido, o total pago e a forma de pagamento. |
| **Meus pedidos** (📦) | Lista seus pedidos. Toque em um pedido para ver a **linha do tempo**: Aguardando pagamento → Pago → Em preparo → Saiu para entrega (ou Pronto para retirada) → Entregue. |
| **Cancelar pedido** | Disponível nos detalhes do pedido enquanto ele está "Aguardando pagamento" ou "Pago". Se já estava pago, o valor é estornado (simulação) e o estoque volta. |
| **Sair** | Toque nas suas iniciais no topo e depois em **Sair**. O carrinho também é limpo. |

## 3. Usando como administradora

Entre com a conta de administradora. O menu **Administração** aparece no topo (ou no menu das iniciais, no celular).

| Tela | Como usar |
|---|---|
| **Produtos e estoque do dia** | Lista todos os cupcakes. Para informar a produção do dia, digite a quantidade no campo **Estoque** de cada sabor e toque em **Salvar estoques do dia**. Se algum valor for inválido, nada é salvo e o campo fica destacado. |
| **Novo cupcake / Editar** | Preencha nome, categoria, preço (ex.: `14,90`) e estoque (obrigatórios), além de descrição, ingredientes, alergênicos e foto (JPG, PNG ou WEBP de até 2 MB). Desmarque **Produto ativo** para tirar um sabor da vitrine sem apagar o histórico. |
| **Pedidos** | Mostra primeiro os pedidos pagos, que precisam de preparo. Use **Filtrar por status** e toque em **Avançar → próxima etapa** para atualizar o andamento; o cliente vê a mudança na hora. Pedidos aguardando pagamento não podem avançar. |

## 4. Mensagens de erro

| Situação | O que aparece |
|---|---|
| E-mail ou senha errados | "E-mail ou senha inválidos" (sem dizer qual dos dois, por segurança) |
| Cadastro com dados inválidos | Mensagem embaixo de cada campo com problema |
| Quantidade maior que o estoque | "Só temos X unidades deste sabor hoje" |
| CEP fora de Jaú | "Ainda não entregamos neste CEP. Você pode escolher Retirar na loja." |
| Pedido abaixo de R$ 25,00 | "O pedido mínimo é de R$ 25,00" |
| Cartão recusado | Tela "Pagamento recusado", com a opção de tentar novamente |
| Estoque acabou durante o pagamento | "Estoque insuficiente para: [sabor]. Nenhum valor foi cobrado." |
| Página inexistente | Tela 404 "Página não encontrada" |
| Cliente tentando abrir área restrita ou pedido de outra pessoa | Tela 403 "Acesso negado" |

## 5. Trocar o banco de dados (opcional)

Por padrão o sistema usa SQLite (arquivo `instance/lacakes.db`). Para usar PostgreSQL ou MySQL, instale o driver
(veja `requirements.txt`) e defina a variável de ambiente antes de iniciar:

```bash
set DATABASE_URL=postgresql://usuario:senha@localhost:5432/lacakes      # Windows (cmd)
export DATABASE_URL=postgresql://usuario:senha@localhost:5432/lacakes   # Linux/macOS
```

## 6. Rodar os testes automatizados

No Windows, dê dois cliques em `rodar-testes.bat`. Pelo terminal:

```bash
.venv\Scripts\python -m pytest --cov=app
```
