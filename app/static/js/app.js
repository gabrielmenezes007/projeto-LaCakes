// LaCakes – pequenos comportamentos de interface. Tudo funciona sem JavaScript; aqui só melhora a experiência.
document.documentElement.classList.add('js');

// Botões − e + dos campos de quantidade. Com data-auto, envia o formulário ao mudar (carrinho).
document.querySelectorAll('[data-stepper]').forEach(function (caixa) {
  var campo = caixa.querySelector('input[type=number]');
  var form = caixa.tagName === 'FORM' ? caixa : caixa.closest('form');
  function mudar(delta) {
    var min = parseInt(campo.min || '0', 10), max = parseInt(campo.max || '99', 10);
    var valor = Math.min(max, Math.max(min, (parseInt(campo.value, 10) || 0) + delta));
    campo.value = valor;
    if (caixa.hasAttribute('data-auto')) form.submit();
  }
  caixa.querySelector('[data-menos]').addEventListener('click', function () { mudar(-1); });
  caixa.querySelector('[data-mais]').addEventListener('click', function () { mudar(1); });
  if (caixa.hasAttribute('data-auto')) campo.addEventListener('change', function () { form.submit(); });
});

// Checkout: mostra endereço ou dados da loja e recalcula a taxa conforme a modalidade.
var checkout = document.querySelector('[data-checkout]');
if (checkout) {
  var subtotal = parseInt(checkout.dataset.subtotal, 10);
  var taxaEntrega = parseInt(checkout.dataset.taxaEntrega, 10);
  var moeda = function (c) { return 'R$ ' + (c / 100).toFixed(2).replace('.', ',').replace(/\B(?=(\d{3})+(?!\d))/g, '.'); };
  var atualizar = function () {
    var entrega = checkout.querySelector('input[name=modalidade]:checked').value === 'ENTREGA';
    checkout.querySelector('[data-endereco]').hidden = !entrega;
    checkout.querySelector('[data-retirada]').hidden = entrega;
    checkout.querySelectorAll('.opcao').forEach(function (o) { o.classList.toggle('sel', o.querySelector('input').checked); });
    var taxa = entrega ? taxaEntrega : 0;
    checkout.querySelector('[data-valor-taxa]').textContent = taxa === 0 ? 'Grátis' : moeda(taxa);
    checkout.querySelector('[data-valor-total]').textContent = moeda(subtotal + taxa);
  };
  checkout.querySelectorAll('input[name=modalidade]').forEach(function (r) { r.addEventListener('change', atualizar); });
  // máscara simples de CEP: 00000-000
  var cep = checkout.querySelector('#cep');
  if (cep) cep.addEventListener('input', function () {
    var d = cep.value.replace(/\D/g, '').slice(0, 8);
    cep.value = d.length > 5 ? d.slice(0, 5) + '-' + d.slice(5) : d;
    if (d.length === 8) buscarCep(d);
  });

  // Busca do endereço pelo CEP: preenche rua e bairro (o cliente confere e informa o número).
  var statusCep = checkout.querySelector('[data-cep-status]');
  var ultimoCep = '';
  function avisarCep(texto, classe) {
    statusCep.textContent = texto;
    statusCep.className = classe;
  }
  function preencher(seletor, valor) {
    var campo = checkout.querySelector(seletor);
    if (campo && valor) {
      campo.value = valor;
      campo.classList.remove('invalido');
    }
  }
  function buscarCep(digitos) {
    if (!statusCep || digitos === ultimoCep) return;
    ultimoCep = digitos;
    avisarCep('Buscando o endereço…', 'dica');
    fetch(checkout.dataset.urlCep.replace('00000000', digitos), { headers: { 'Accept': 'application/json' } })
      .then(function (r) { if (!r.ok) throw new Error(r.status); return r.json(); })
      .then(function (res) {
        if (cep.value.replace(/\D/g, '') !== digitos) return;  // o cliente já mudou o CEP
        if (!res.ok) {
          avisarCep('⚠ ' + res.mensagem, res.fora_da_area ? 'msg-campo' : 'dica');
          return;
        }
        preencher('#logradouro', res.logradouro);
        preencher('#bairro', res.bairro);
        avisarCep('✔ Endereço encontrado (' + res.cidade + '/' + res.uf + '). Confira e informe o número.', 'dica ok-texto');
        checkout.querySelector(res.logradouro ? '#numero' : '#logradouro').focus();
      })
      .catch(function () {
        ultimoCep = '';
        avisarCep('Não foi possível buscar o CEP agora. Preencha a rua e o bairro.', 'dica');
      });
  }
}

// Número do cartão em grupos de 4 e validade MM/AA.
var numero = document.querySelector('#numero_cartao');
if (numero) numero.addEventListener('input', function () {
  numero.value = numero.value.replace(/\D/g, '').slice(0, 16).replace(/(\d{4})(?=\d)/g, '$1 ');
});
var validade = document.querySelector('#validade');
if (validade) validade.addEventListener('input', function () {
  var d = validade.value.replace(/\D/g, '').slice(0, 4);
  validade.value = d.length > 2 ? d.slice(0, 2) + '/' + d.slice(2) : d;
});

// Copiar código Pix.
document.querySelectorAll('[data-copiar]').forEach(function (botao) {
  botao.addEventListener('click', function () {
    var texto = document.querySelector(botao.dataset.copiar).textContent.trim();
    var ok = function () { botao.textContent = 'Código copiado ✔'; };
    if (navigator.clipboard) navigator.clipboard.writeText(texto).then(ok, ok); else ok();
  });
});

// Confirmação antes de ações irreversíveis (cancelar pedido).
document.querySelectorAll('form[data-confirmar]').forEach(function (form) {
  form.addEventListener('submit', function (e) {
    if (!window.confirm(form.dataset.confirmar)) e.preventDefault();
  });
});

// Filtro do admin envia ao trocar a opção.
document.querySelectorAll('form[data-auto-envio] select').forEach(function (s) {
  s.addEventListener('change', function () { s.form.submit(); });
});
