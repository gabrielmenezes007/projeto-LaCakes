# Registro de decisões

Decisões de projeto e o motivo de cada uma.

## Planejamento

| # | Decisão | Motivo |
|---|---|---|
| D01 | Loja fictícia chamada **LaCakes Cupcakes Gourmet**, com a confeiteira **Laysa** como dona e administradora. | Um nome e uma persona concretos deixam as histórias de usuário mais claras. |
| D02 | Aplicação **web responsiva (mobile first)** em vez de app nativo. | O cliente quer um "aplicativo"; uma web app responsiva funciona no celular e cabe no prazo e na stack escolhida (Flask). |
| D03 | 23 histórias de usuário. | Cobrem os quatro pilares (vitrine, pedido, pagamento e entrega) mais conta e administração, sem funcionalidades além do escopo. |
| D04 | Escopo: cadastro/login, vitrine, carrinho, pedido, pagamento simulado, acompanhamento e admin, incluindo **atualização de status pelo admin** e **cancelamento pelo cliente**. | Sem a atualização de status pelo admin, o acompanhamento do pedido não teria como mudar. O cancelamento é pequeno e ficou com a menor prioridade (D). |
| D05 | Pagamento **simulado** por cartão de crédito, cartão de débito ou Pix. Cartões terminados em 0000 são recusados (crédito e débito). | Não há gateway real no escopo; a regra do final 0000 permite testar o cenário de recusa. Nenhum número de cartão completo é guardado (só a modalidade e os 4 últimos dígitos). |
| D06 | Carrinho guardado na **sessão** (não no banco). | Mais simples, permite que o visitante monte o carrinho antes do login e não precisa de tabela extra. |
| D07 | Endereço de entrega gravado **dentro do pedido** (não em tabela separada de endereços). | Funciona como "foto" do endereço no momento da compra e mantém o escopo enxuto. |
| D08 | Loja em **Jaú/SP** (Rua das Flores, 120; seg. a sáb., 9h às 19h). Entrega só para CEPs de Jaú (**17200-001 a 17229-999**). | Não há integração com serviço de CEP no escopo; a faixa oficial da cidade é simples de validar e testar. |
| D09 | Prioridade dos cartões de A a E; pontos em Fibonacci (1, 2, 3, 5). No backlog, a prioridade é a ordem de execução seguida da letra. | A letra mostra a importância; o número mostra a sequência de trabalho. |
| D10 | Diagramas feitos em **Mermaid** (código em `docs/planejamento/diagramas/`) e renderizados com Playwright usando o Microsoft Edge instalado. O diagrama de caso de uso é um **SVG** gerado por script. | O Mermaid não tem diagrama de caso de uso UML; o restante fica versionado como texto. |
| D11 | Wireframes e mockups gerados do **mesmo HTML/CSS** (`docs/planejamento/prototipo/`), com um modo "wireframe" em tons de cinza. | Garante que wireframe e mockup mostram as mesmas telas, e o CSS pode ser reaproveitado no front-end. |
| D12 | Paleta: Roxo Amora `#5D2452` (ações principais), Verde Profundo `#112F24` (títulos e admin), Creme Amêndoa `#FAF4ED` (fundo), Menta Sálvia `#29604C` (confirmações e pagamento). | Identidade própria da marca. Contraste do texto branco: 11,4:1 (amora), 14,4:1 (verde), 7,3:1 (menta), todos acima do mínimo da WCAG AA. |
| D13 | Débito usa o **mesmo formulário do crédito** (abas Crédito / Débito / Pix); a modalidade fica registrada no campo `metodo` do pagamento (`CREDITO`, `DEBITO`, `PIX`). | Mesmas validações e mesma regra de recusa; a modalidade aparece no resumo do pedido. |
| D14 | Tons derivados da paleta: `#F3E8F1` (seleção), `#EADBE6` (cabeçalhos de tabela e telas públicas no mapa navegacional), `#DDEBE4` (etiquetas de categoria), `#E6D2E2` (destaque da etapa atual), `#451A3D` (amora escura) e borda `#E6DCD3`. | Variações claras/escuras das quatro cores principais, para fundos e bordas. Cores de status (vermelho de erro, amarelo de aviso) e os fundos das ilustrações dos cupcakes são independentes da paleta. |
| D15 | Conteúdo do planejamento em uma **fonte única** (`scripts/conteudo_planejamento.py`), da qual saem os Markdown de `docs/planejamento` e o documento Word. | Evita que documentos diferentes fiquem com informações diferentes. |
| D16 | Documentos Word/PDF e dados pessoais ficam **fora do repositório** (`.gitignore`); os dados de identificação são lidos de `scripts/dados_aluno.json`, que não é versionado. | O repositório é público; ele guarda só o projeto e sua documentação técnica. |

## Desenvolvimento

| # | Decisão | Motivo |
|---|---|---|
| D17 | Valores em dinheiro guardados em **centavos (inteiro)** no banco e no código. | Evita erros de arredondamento de ponto flutuante e funciona igual em SQLite, PostgreSQL e MySQL. |
| D18 | Regras de negócio em uma camada de **serviços** (`app/services`), separada dos controllers. | Os controllers ficam só com HTTP; as regras podem ser testadas sem navegador. |
| D19 | Enumerações gravadas como **VARCHAR + CHECK** (não ENUM nativo). | Portável entre os três bancos suportados e ainda bloqueia valores inválidos. |
| D20 | Validação de formulários feita à mão nos serviços (sem WTForms); proteção **CSRF** pelo Flask-WTF. | Menos dependências e mensagens de erro exatamente como planejadas nos protótipos. |
| D21 | Ilustrações SVG geradas por script para os cupcakes de exemplo; fotos reais podem ser enviadas pelo admin. | Evita problemas de direitos autorais com fotos da internet. |
| D22 | Contas de teste com domínio reservado **`.test`** (`admin@lacakes.test`, `cliente@lacakes.test`). | Domínio reservado para testes, que não pertence a ninguém. |
| D23 | Logout limpa a sessão inteira (inclusive o carrinho). | US07: outra pessoa pode usar o mesmo aparelho. |
| D24 | Cartões de crédito/débito em formulário único; `iniciar.bat`/`iniciar.sh` sobem tudo com um comando. | Escopo enxuto e instalação simples para quem vai testar. |

## Melhorias após os testes com usuários (16/11/2026)

| # | Decisão | Motivo |
|---|---|---|
| D25 | **Tela inicial** em `/`, com a frase "Feitos hoje, fresquinhos 💜", botão "Ver cupcakes", situação da loja (aberta/fechada), 3 destaques, "Como funciona" e dados da loja. A vitrine passou para `/vitrine`. Destaques: os cupcakes disponíveis mais vendidos (sem vendas, ordem alfabética). | Pedido dos testadores. Formato e frase escolhidos pelo autor entre as opções apresentadas. |
| D26 | **Busca de CEP** pelo serviço público ViaCEP, feita pelo servidor (rota `/cep/<cep>`, só para quem está logado), com limite de 4 segundos. CEP fora de Jaú nem é consultado. Se o serviço falhar, o cliente digita o endereço normalmente. Revisa a D08. | Preencher rua e bairro como em outros sites, sem impedir a compra quando não houver internet. |
| D27 | **Dados da loja** numa tabela `loja` com um único registro (endereço, dias de funcionamento, abertura e fechamento), editada pela administradora na tela "Dados da loja". O nome da loja continua na configuração. | Os horários deixam de ficar fixos no código e passam a controlar o aviso de loja fechada. |
| D28 | **Loja fechada**: o pedido continua sendo aceito. Com a loja fechada, o status continua "Pago" e a data de preparo é gravada em `pedido.previsao_preparo`. Enquanto o pedido estiver "Pago", aparece o selo "Preparado e entregue amanhã (ter., 17/11)" ou "Preparado e entregue segunda-feira (23/11)". Antes da abertura, o pedido é para o mesmo dia. Depois do fechamento, vai para o próximo dia de funcionamento. Feriados não são tratados. | Escolha do autor entre "selo com data" e "novo status". O selo não muda a máquina de status (RN10) e a data gravada mantém o texto certo nos dias seguintes. |
| D29 | **Estatísticas de vendas** na aba "Vendas" da administração, com um resumo do dia no topo de "Pedidos". Conta como venda o pedido pago e não cancelado, pelo dia em que foi feito. | Pedido dos testadores. A regra simples e explícita evita contar pedidos estornados ou não pagos. |
| D30 | Horário pela **hora local do computador** (mesma função `agora()` dos models). As regras recebem o momento por parâmetro, e os testes fixam o relógio em `app.services.loja.relogio`. | A loja atende uma única cidade. Fixar o relógio deixa os testes independentes da hora em que rodam. |
| D31 | O `seed` **atualiza bancos de versões anteriores** sem apagar dados: cria a tabela nova, adiciona a coluna `previsao_preparo` com `ALTER TABLE` e grava os dados padrão da loja. | Quem já usava o sistema não perde pedidos ao atualizar. Uma ferramenta de migração seria exagero para uma coluna. |
