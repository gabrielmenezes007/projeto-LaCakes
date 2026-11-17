# Testes com usuários

Validação do sistema com **5 pessoas**, que usam o sistema como clientes e como dona da loja e contam o que
funcionou, o que não funcionou e o que não foi testado.

- [roteiro-de-teste.md](roteiro-de-teste.md): o que cada pessoa faz, com os dados de teste e como registrar a opinião.
  O mesmo roteiro aparece no documento de entrega, logo antes dos quadros que os testadores preenchem.

## Passo a passo

1. Iniciar o sistema com `iniciar.bat --recriar` (banco limpo antes de cada sessão, se preferir).
2. Cada testador segue o roteiro sem ajuda (só tirar dúvidas de acesso) e preenche o seu quadro no documento de
   entrega (nome, data, o que funcionou, o que não funcionou e o que deve ser corrigido, o que não foi testado e por quê).
3. Depois das 5 sessões, juntar os problemas iguais, corrigir os pertinentes (um commit por correção) e registrar o
   resultado em [docs/desenvolvimento/testes.md](../desenvolvimento/testes.md) e no laudo de qualidade.

As respostas com os nomes dos testadores ficam só no documento de entrega, fora do repositório.

## Resultado (16/11/2026)

As 15 tarefas do roteiro funcionaram para os 5 testadores. Eles pediram 5 melhorias (tela inicial, rua e bairro
pelo CEP, estatísticas de vendas, aviso de loja fechada e cadastro dos dados da loja), todas implementadas no mesmo
dia. Os detalhes estão em [docs/desenvolvimento/testes.md](../desenvolvimento/testes.md#33-validação-com-usuários-5-testadores).
