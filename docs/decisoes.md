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
