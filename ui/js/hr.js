'use strict';
(() => {
  let csrfToken = '';
  const status = document.querySelector('#status');
  async function api(path, options={}) {
    const headers={'Accept':'application/json',...(options.body?{'Content-Type':'application/json'}:{}),...(options.method&&options.method!=='GET'?{'X-CSRF-Token':csrfToken}:{})};
    const response=await fetch(path,{...options,headers,credentials:'same-origin'});
    const body=await response.json().catch(()=>({}));
    if(!response.ok) throw new Error(body.error||'Falha na requisição.');
    return body;
  }
  const td = value => {const node=document.createElement('td');node.textContent=value==null?'':String(value);return node;};
  async function load() {
    try {
      const [departments,employees,absences]=await Promise.all([api('/api/hr/departments'),api('/api/hr/employees'),api('/api/hr/absences')]);
      const ds=document.querySelector('#department-id');ds.replaceChildren(new Option('Sem departamento',''));departments.filter(d=>d.active).forEach(d=>ds.add(new Option(d.name,d.id)));
      const es=document.querySelector('#absence-employee');es.replaceChildren();employees.filter(e=>e.status!=='inactive').forEach(e=>es.add(new Option(e.full_name+' ('+e.employee_code+')',e.id)));
      const eb=document.querySelector('#employees-body');eb.replaceChildren();employees.forEach(e=>{const tr=document.createElement('tr');[e.employee_code,e.full_name,e.job_title,e.department_name,e.hire_date,e.status].forEach(v=>tr.append(td(v)));eb.append(tr);});
      const ab=document.querySelector('#absences-body');ab.replaceChildren();absences.forEach(a=>{const tr=document.createElement('tr');[a.employee_name,a.absence_type,a.start_date+' a '+a.end_date,a.status].forEach(v=>tr.append(td(v)));const actions=td('');if(a.status==='requested'){for(const decision of ['approved','rejected']){const b=document.createElement('button');b.type='button';b.textContent=decision==='approved'?'Aprovar':'Rejeitar';b.addEventListener('click',()=>decide(a.id,decision));actions.append(b,' ');}}tr.append(actions);ab.append(tr);});
      status.textContent='Dados de RH atualizados.';
    } catch(error) {status.textContent=error.message;}
  }
  async function submitForm(event,path,convert=x=>x) {
    event.preventDefault();const data=convert(Object.fromEntries(new FormData(event.currentTarget)));
    try {await api(path,{method:'POST',body:JSON.stringify(data)});event.currentTarget.reset();status.textContent='Registro salvo.';await load();}
    catch(error){status.textContent=error.message;}
  }
  async function decide(id,decision){try{await api('/api/hr/absences/'+id+'/decision',{method:'POST',body:JSON.stringify({decision})});status.textContent='Decisão registrada.';await load();}catch(error){status.textContent=error.message;}}
  document.querySelector('#department-form').addEventListener('submit',e=>submitForm(e,'/api/hr/departments'));
  document.querySelector('#employee-form').addEventListener('submit',e=>submitForm(e,'/api/hr/employees',d=>({...d,department_id:d.department_id?Number(d.department_id):null})));
  document.querySelector('#absence-form').addEventListener('submit',e=>submitForm(e,'/api/hr/absences',d=>({...d,employee_id:Number(d.employee_id)})));
  document.querySelector('#refresh').addEventListener('click',load);
  api('/api/auth/me').then(data=>{csrfToken=data.csrfToken;if(data.user.role!=='admin')throw new Error('Acesso restrito ao administrador.');return load();}).catch(error=>{status.textContent=error.message;});
})();
