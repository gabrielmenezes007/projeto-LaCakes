# Testes com usuários

Validação do sistema com **5 pessoas** (colegas de curso ou profissionais da área), que usam o sistema como clientes
e como administradora da loja e registram o que funcionou, o que não funcionou e o que não foi testado.

## Arquivos

| Arquivo | Para que serve |
|---|---|
| [roteiro-de-teste.md](roteiro-de-teste.md) | Cenários sugeridos, com os dados de teste (CEPs, cartões, contas) |
| [formulario-de-teste.md](formulario-de-teste.md) | Campos que cada testador preenche (versão de referência) |
| `scripts/gerar_formularios_teste.py` | Gera os formulários em Word (um por testador) e a capa da consolidação |
| `scripts/consolidar_testes.py` | Junta a capa e os 5 formulários preenchidos num único PDF |

Os formulários preenchidos e o PDF consolidado ficam **fora do repositório**, porque contêm nomes e assinaturas dos
testadores. O resumo sem dados pessoais e as correções feitas entram em
[docs/desenvolvimento/testes.md](../desenvolvimento/testes.md).

## Passo a passo

1. Gerar os formulários: `python scripts/gerar_formularios_teste.py <pasta>`
2. Iniciar o sistema com `iniciar.bat --recriar` (banco limpo para cada sessão de teste, se preferir).
3. Para cada testador: entregar o roteiro e o formulário `Formulario_Teste_Testador_N.docx`, informar as senhas das
   contas de teste e deixar a pessoa usar o sistema sem ajuda (só tirar dúvidas de acesso).
4. Depois de cada sessão, salvar o formulário preenchido na mesma pasta.
5. Preencher a capa `00_Capa_Consolidacao.docx` (resumo, problemas consolidados, correções e laudo).
6. Gerar o PDF único: `python scripts/consolidar_testes.py <pasta>`
7. Corrigir os problemas pertinentes, com um commit por correção, e registrar em
   [docs/desenvolvimento/testes.md](../desenvolvimento/testes.md).
