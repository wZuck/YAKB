(() => {
  'use strict';
  const data = window.YAKB_GUIDE;
  if (!data) return;
  const $ = id => document.getElementById(id);
  const esc = s => String(s).replace(/[&<>"']/g, c => ({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]));
  const key = 'yakb-a0-soldering-v1';
  let checked = new Set(), phase = '', ascending = true;
  try { checked = new Set(JSON.parse(localStorage.getItem(key) || '[]')); } catch { /* private/local mode */ }
  const valid = new Set(data.steps.map(s=>s.id));
  checked = new Set([...checked].filter(id=>valid.has(id)));
  function toast(message) { $('toast').textContent=message;$('toast').classList.add('visible');setTimeout(()=>$('toast').classList.remove('visible'),2200); }
  function save() { try { localStorage.setItem(key,JSON.stringify([...checked])); } catch { toast('当前浏览器无法保存进度；本次操作仍可继续。'); } }
  function progress() { $('progressText').textContent=`${checked.size} / ${data.steps.length}`;$('bar').style.width=`${checked.size/data.steps.length*100}%`; }
  function phases() {
    $('phases').innerHTML=[{id:'',code:'ALL',title:'全部步骤'},...data.phases].map(p=>`<button type="button" data-phase="${esc(p.id)}" class="${phase===p.id?'active':''}" aria-pressed="${phase===p.id}"><b>${esc(p.code)}</b>${esc(p.title)}</button>`).join('');
  }
  function steps() {
    $('steps').innerHTML=data.steps.map(s=>`<article class="step ${checked.has(s.id)?'is-done':''}" id="${s.id}" style="--phase:${s.color}" ${phase&&phase!==s.phase?'hidden':''}><div class="step-side"><span class="step-number">${s.code}</span><small>${esc(s.phaseTitle)}</small></div><figure><button type="button" data-image="${esc(s.image)}" data-caption="${esc(s.title)}" aria-label="放大：${esc(s.title)}"><img src="${esc(s.image)}" alt="${esc(s.title)}：当前位号高亮位置图" loading="lazy" width="1400" height="800"></button><figcaption>${esc(s.imageNote)}</figcaption></figure><div class="step-copy"><div class="step-meta"><span>${esc(s.subtitle)}</span><span>${esc(s.count)}</span></div><h3>${esc(s.title)}</h3><p class="summary">${esc(s.summary)}</p><div class="parts">${s.parts.map(p=>`<span>${esc(p)}</span>`).join('')}</div><ol>${s.instructions.map(t=>`<li>${esc(t)}</li>`).join('')}</ol><div class="checkpoint">${esc(s.checkpoint)}</div><label class="done-label"><input type="checkbox" data-step="${s.id}" ${checked.has(s.id)?'checked':''}>本步骤已检查完成</label></div></article>`).join('');
  }
  function inventory() {
    const term=$('search').value.trim().toLowerCase(), p=$('phaseFilter').value, type=$('typeFilter').value;
    let rows=data.inventory.filter(r=>(!p||r.phase===p)&&(!type||r.type===type)&&(!term||Object.values(r).join(' ').toLowerCase().includes(term)));
    rows.sort((a,b)=>(ascending?1:-1)*a.ref.localeCompare(b.ref,'en',{numeric:true}));
    $('rows').innerHTML=rows.map(r=>`<tr><td>${esc(r.ref)}</td><td>${esc(r.step)}</td><td>${esc(r.value)}</td><td>${esc(r.footprint)}</td><td>${esc(r.side)}</td><td>${Number(r.x).toFixed(3)}</td><td>${Number(r.y).toFixed(3)}</td><td>${esc(r.note)}</td></tr>`).join('');
    $('rowCount').textContent=`${rows.length} / ${data.inventory.length} 条`;$('empty').hidden=rows.length!==0;
  }
  $('phaseFilter').insertAdjacentHTML('beforeend',data.phases.map(p=>`<option value="${p.id}">${esc(p.title)}</option>`).join(''));
  $('phases').addEventListener('click',e=>{const b=e.target.closest('[data-phase]');if(!b)return;phase=b.dataset.phase;phases();steps();});
  $('steps').addEventListener('change',e=>{const id=e.target.dataset.step;if(!id)return;e.target.checked?checked.add(id):checked.delete(id);e.target.closest('.step').classList.toggle('is-done',e.target.checked);save();progress();});
  $('steps').addEventListener('click',e=>{const b=e.target.closest('[data-image]');if(!b)return;$('zoomImage').src=b.dataset.image;$('zoomImage').alt=b.dataset.caption;$('zoomCaption').textContent=b.dataset.caption;$('viewer').showModal();});
  $('closeViewer').addEventListener('click',()=>$('viewer').close());
  $('viewer').addEventListener('click',e=>{if(e.target===$('viewer'))$('viewer').close();});
  $('reset').addEventListener('click',()=>{if(!checked.size)return;if(window.confirm('清除本浏览器保存的所有 YAKB 焊接进度？')){checked.clear();save();steps();progress();toast('进度已重置');}});
  ['search','phaseFilter','typeFilter'].forEach(id=>$(id).addEventListener(id==='search'?'input':'change',inventory));
  $('sortRef').addEventListener('click',()=>{ascending=!ascending;inventory();});
  $('print').addEventListener('click',()=>window.print());
  phases();steps();inventory();progress();
})();
