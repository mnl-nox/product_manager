'use strict';
(() => {
  const status = document.querySelector('#status');
  let csrfToken = '';
  const money = cents => new Intl.NumberFormat('pt-BR', {style:'currency', currency:'BRL'}).format(cents / 100);
  async function api(path, options = {}) {
    const headers = {'Accept':'application/json', ...(options.body ? {'Content-Type':'application/json'} : {}), ...(options.method && options.method !== 'GET' ? {'X-CSRF-Token':csrfToken} : {}), ...options.headers};
    const response = await fetch(path, {...options, headers, credentials:'same-origin'});
    const body = await response.json().catch(() => ({}));
    if (!response.ok) throw new Error(body.error || 'Falha na requisição.');
    return body;
  }
  function cell(value) { const td = document.createElement('td'); td.textContent = value == null ? '' : String(value); return td; }
  async function load() {
    try {
      const [suppliers, requests, products, orders] = await Promise.all([
        api('/api/purchasing/suppliers'), api('/api/purchasing/requests'), api('/api/products'), api('/api/purchasing/orders')
      ]);
      const supplierBody = document.querySelector('#suppliers-body'); supplierBody.replaceChildren();
      suppliers.forEach(s => { const tr = document.createElement('tr'); [s.name,s.tax_id,s.email,s.phone,s.status].forEach(v => tr.append(cell(v))); supplierBody.append(tr); });
      if (!suppliers.length) supplierBody.append(rowMessage(5, 'Nenhum fornecedor cadastrado.'));
      const requestBody = document.querySelector('#requests-body'); requestBody.replaceChildren();
      requests.forEach(r => {
        const tr = document.createElement('tr');
        [r.id,r.description,r.requester,money(r.estimated_total_cents),r.status].forEach(v => tr.append(cell(v)));
        const action = document.createElement('td');
        if (r.status === 'requested') {
          const quote = document.createElement('button'); quote.type='button'; quote.textContent='Registrar cotação'; quote.addEventListener('click', () => addQuote(r.id, suppliers)); action.append(quote);
        } else if (r.status === 'quoted' && ['admin','finance'].includes(window.productManagerRole)) {
          const approve = document.createElement('button'); approve.type='button'; approve.textContent='Aprovar'; approve.addEventListener('click', () => approveRequest(r.id)); action.append(approve);
        } else if (r.status === 'approved' && ['admin','operator'].includes(window.productManagerRole)) {
          const order = document.createElement('button'); order.type='button'; order.textContent='Emitir pedido'; order.addEventListener('click', () => createOrder(r.id)); action.append(order);
        }
        tr.append(action); requestBody.append(tr);
      });
      if (!requests.length) requestBody.append(rowMessage(6, 'Nenhuma solicitação cadastrada.'));
      const ordersBody = document.querySelector('#orders-body'); ordersBody.replaceChildren();
      orders.forEach(o => {
        const tr=document.createElement('tr');
        [o.id,o.supplier_name,money(o.total_cents),o.status].forEach(v=>tr.append(cell(v)));
        const action=document.createElement('td');
        if(['ordered','partially_received'].includes(o.status) && ['admin','operator'].includes(window.productManagerRole)){
          const receive=document.createElement('button');receive.type='button';receive.textContent='Registrar recebimento';receive.addEventListener('click',()=>receiveOrder(o.id));action.append(receive);
        }
        tr.append(action);ordersBody.append(tr);
      });
      if(!orders.length)ordersBody.append(rowMessage(5,'Nenhum pedido emitido.'));
      const select = document.querySelector('#product-id');
      products.forEach(p => { const opt = document.createElement('option'); opt.value = p.id; opt.textContent = p.name + ' (' + p.sku + ')'; select.append(opt); });
      status.textContent = 'Dados de compras atualizados.';
    } catch (error) { status.textContent = error.message; }
  }
  function rowMessage(span, message) { const tr=document.createElement('tr'); const td=cell(message); td.colSpan=span; tr.append(td); return tr; }
  async function addQuote(requestId, suppliers) {
    if (!suppliers.length) { status.textContent='Cadastre um fornecedor antes de registrar cotações.'; return; }
    const supplierId = prompt('ID do fornecedor disponível: ' + suppliers.map(s => s.id + ' — ' + s.name).join(', '));
    if (!supplierId) return;
    const total = prompt('Valor total da cotação em reais (ex.: 1250,00):');
    if (total === null) return;
    const cents = Math.round(Number(total.replace(',','.')) * 100);
    const days = Number(prompt('Prazo em dias corridos (0 se desconhecido):','0') || 0);
    try { await api('/api/purchasing/quotes',{method:'POST',body:JSON.stringify({request_id:requestId,supplier_id:Number(supplierId),total_cents:cents,lead_days:days})}); status.textContent='Cotação registrada.'; await load(); }
    catch(error) { status.textContent=error.message; }
  }
  async function createOrder(requestId) {
    try {
      const detail=await api('/api/purchasing/requests/'+requestId);
      if(!detail.quotes.length){status.textContent='Registre uma cotação antes de emitir o pedido.';return;}
      const selected=prompt('Escolha o ID da cotação: '+detail.quotes.map(q=>q.id+' — '+q.supplier_name+' — '+money(q.total_cents)+' — '+q.lead_days+' dia(s)').join('; '));
      if(!selected)return;
      await api('/api/purchasing/requests/'+requestId+'/order',{method:'POST',body:JSON.stringify({quote_id:Number(selected)})});
      status.textContent='Pedido emitido.';await load();
    } catch(error){status.textContent=error.message;}
  }
  async function receiveOrder(orderId) {
    try {
      const detail=await api('/api/purchasing/orders/'+orderId);
      const items=[];
      for(const item of detail.items){
        const remaining=item.ordered_quantity-item.received_quantity;
        if(remaining<=0)continue;
        const raw=prompt('Item '+item.id+' — '+item.description+'; restante '+remaining+'. Quantidade recebida agora (0 para ignorar):','0');
        if(raw===null)return;
        const quantity=Number(raw);
        if(!Number.isInteger(quantity)||quantity<0||quantity>remaining){status.textContent='Quantidade inválida para o item '+item.id+'.';return;}
        if(quantity>0)items.push({item_id:item.id,quantity});
      }
      if(!items.length){status.textContent='Nenhuma quantidade informada.';return;}
      await api('/api/purchasing/orders/'+orderId+'/receive',{method:'POST',body:JSON.stringify({items})});
      status.textContent='Recebimento registrado; estoque atualizado.';await load();
    } catch(error){status.textContent=error.message;}
  }
  async function approveRequest(id) {
    if (!confirm('Aprovar esta solicitação?')) return;
    try { await api('/api/purchasing/requests/'+id+'/approve',{method:'POST',body:JSON.stringify({decision:'approved'})}); status.textContent='Solicitação aprovada.'; await load(); }
    catch(error) { status.textContent=error.message; }
  }
  document.querySelector('#supplier-form').addEventListener('submit', async event => {
    event.preventDefault(); const data=Object.fromEntries(new FormData(event.currentTarget));
    try { await api('/api/purchasing/suppliers',{method:'POST',body:JSON.stringify(data)}); event.currentTarget.reset(); status.textContent='Fornecedor cadastrado.'; await load(); }
    catch(error) { status.textContent=error.message; }
  });
  document.querySelector('#request-form').addEventListener('submit', async event => {
    event.preventDefault(); const data=Object.fromEntries(new FormData(event.currentTarget));
    const productId=data.product_id ? Number(data.product_id) : null;
    const unitCents=Math.round(Number(data.unit_price.replace(',','.'))*100);
    try { await api('/api/purchasing/requests',{method:'POST',body:JSON.stringify({description:data.description,items:[{product_id:productId,description:data.item_description,quantity:Number(data.quantity),estimated_unit_cents:unitCents}]})}); event.currentTarget.reset(); status.textContent='Solicitação criada.'; await load(); }
    catch(error) { status.textContent=error.message; }
  });
  document.querySelector('#refresh').addEventListener('click', load);
  api('/api/auth/me').then(data => { csrfToken=data.csrfToken; window.productManagerRole=data.user.role; return load(); }).catch(error => { status.textContent=error.message; });
})();
