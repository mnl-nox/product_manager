'use strict';
(() => {
 let csrfToken='';
 const status=document.querySelector('#status');
 const money=c=>new Intl.NumberFormat('pt-BR',{style:'currency',currency:'BRL'}).format(c/100);
 async function api(path,options={}){const headers={'Accept':'application/json',...(options.body?{'Content-Type':'application/json'}:{}),...(options.method&&options.method!=='GET'?{'X-CSRF-Token':csrfToken}:{})};const res=await fetch(path,{...options,headers,credentials:'same-origin'});const body=await res.json().catch(()=>({}));if(!res.ok)throw new Error(body.error||'Falha na requisição.');return body;}
 const td=v=>{const e=document.createElement('td');e.textContent=v==null?'':String(v);return e;};
 function row(body,values){const tr=document.createElement('tr');values.forEach(v=>tr.append(td(v)));body.append(tr);}
 function card(label,value){const article=document.createElement('article');article.className='panel';const title=document.createElement('p');title.className='eyebrow muted';title.textContent=label;const strong=document.createElement('h2');strong.textContent=value;article.append(title,strong);document.querySelector('#summary-cards').append(article);}
 async function load(){
  try{
   const from=document.querySelector('#from-date').value,to=document.querySelector('#to-date').value;
   const data=await api('/api/reports/summary?from='+encodeURIComponent(from)+'&to='+encodeURIComponent(to));
   const t=data.totals;const cards=document.querySelector('#summary-cards');cards.replaceChildren();
   card('Receita realizada',money(t.revenue_cents));card('Despesas realizadas',money(t.expenses_cents));card('Resultado',money(t.profit_cents));card('Margem de resultado',t.profit_margin_percent===null?'—':t.profit_margin_percent+'%');card('Caixa projetado',money(t.projected_cash_cents));card('Proxy de giro de estoque',t.stock_turnover_proxy===null?'—':String(t.stock_turnover_proxy));
   const top=document.querySelector('#top-products');top.replaceChildren();data.topProducts.forEach(p=>row(top,[p.name,p.sku,p.units_sold,money(p.revenue_cents)]));if(!data.topProducts.length)row(top,['Sem vendas registradas','','','']);
   const monthly=document.querySelector('#monthly');monthly.replaceChildren();data.monthly.forEach(m=>row(monthly,[m.period,money(m.revenue_cents),money(m.expenses_cents),money(m.revenue_cents-m.expenses_cents)]));if(!data.monthly.length)row(monthly,['Sem lançamentos','','','']);
   const cats=document.querySelector('#categories');cats.replaceChildren();data.byCategory.forEach(c=>row(cats,[c.category,money(c.revenue_cents),money(c.expenses_cents)]));if(!data.byCategory.length)row(cats,['Sem lançamentos','','']);
   const overdue=document.querySelector('#overdue');overdue.replaceChildren();for(const type of ['income','expense']){const item=data.overdue[type]||{count:0,amount_cents:0};const p=document.createElement('p');p.textContent=(type==='income'?'Receitas vencidas: ':'Despesas vencidas: ')+item.count+' conta(s), '+money(item.amount_cents);overdue.append(p);}
   status.textContent='Relatório atualizado para '+from+' até '+to+'.';
  }catch(error){status.textContent=error.message;}
 }
 document.querySelector('#filter-form').addEventListener('submit',e=>{e.preventDefault();load();});
 document.querySelector('#sale-form').addEventListener('submit',async e=>{e.preventDefault();const d=Object.fromEntries(new FormData(e.currentTarget));try{await api('/api/reports/sales',{method:'POST',body:JSON.stringify({product_id:Number(d.product_id),quantity:Number(d.quantity),unit_price:Number(d.unit_price),sale_date:d.sale_date,status:d.status})});status.textContent='Venda registrada.';await load();}catch(error){status.textContent=error.message;}});
 const today=new Date();const iso=d=>{const date=new Date(d.getTime()-d.getTimezoneOffset()*60000);return date.toISOString().slice(0,10);};
 document.querySelector('#to-date').value=iso(today);document.querySelector('#sale-date').value=iso(today);document.querySelector('#from-date').value=iso(new Date(today.getFullYear(),today.getMonth(),1));
 api('/api/auth/me').then(async me=>{csrfToken=me.csrfToken;const products=await api('/api/products');const select=document.querySelector('#product-id');products.forEach(p=>select.add(new Option(p.name+' ('+p.sku+') — estoque '+p.quantity,p.id)));await load();}).catch(error=>{status.textContent=error.message;});
})();
