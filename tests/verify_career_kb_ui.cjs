/** Isolated owner-only Career KB UI smoke, no network, secrets or DB writes. */
'use strict';
const assert=require('node:assert/strict');
const fs=require('node:fs');
const vm=require('node:vm');
const file=process.argv[2]||'webapp/index.html';
const html=fs.readFileSync(file,'utf8');
const start='// CAREER_KB_009_UI_BEGIN',end='// CAREER_KB_009_UI_END';
const source=html.includes(start)&&html.includes(end)
  ?html.slice(html.indexOf(start)+start.length,html.indexOf(end)).trim()
  : (process.argv[2] ? html : (()=>{throw Error('Career KB source markers not found')})());
assert(!source.includes('innerHTML'));
class Element{
  constructor(tag='div') {this.tag=tag;this.children=[];this.textContent='';this.hidden=false;this.disabled=false;this.attrs={};}
  append(...nodes){this.children.push(...nodes)}
  replaceChildren(...nodes){this.children=[...nodes]}
  setAttribute(key,val){this.attrs[key]=String(val)}
}
const ids=Object.fromEntries(['careerItems','careerDetail','careersOpen','careerHome'].map(k=>[k,new Element()]));
const state={busy:false,authenticated:false};
const names=[
 ['2.A.1.a','Reading Comprehension','Понимание прочитанного'],
 ['2.A.1.b','Active Listening','Активное слушание'],
 ['2.A.1.c','Writing','Письменная речь'],
 ['2.A.1.d','Speaking','Устная речь'],
 ['2.A.1.e','Mathematics','Математика'],
 ['2.A.1.f','Science','Применение научных методов'],
 ['2.A.2.a','Critical Thinking','Критическое мышление'],
 ['2.A.2.b','Active Learning','Активное обучение'],
 ['2.A.2.c','Learning Strategies','Стратегии обучения'],
 ['2.A.2.d','Monitoring','Контроль результатов'],
];
const codes=['15-2051.00','15-2051.01'];
const titles=['Data Scientists','Business Intelligence Analysts'];
const listing={source:{snapshotId:'ONET_DB_31_0'},careerFitCalculated:false,
  roles:codes.map((code,i)=>({code,title:titles[i],description:'Synthetic role description '+i,skillCount:10}))};
function detail(code){
 const measurements=[];
 for(const [i,[elementId,skill]] of names.entries())for(const scaleId of ['IM','LV']){
  const missing=code===codes[0]&&i===9&&scaleId==='LV';
  measurements.push({elementId,skill,scaleId,minimum:scaleId==='IM'?'1':'0',maximum:scaleId==='IM'?'5':'7',
    evidenceStatus:missing?'SUPPRESSED':'OBSERVED',rawValue:missing?null:scaleId==='IM'?'4.0000':'4.2500',updatedAtSource:'08/2026'});
 }
 return {source:listing.source,careerFitCalculated:false,code,title:titles[codes.indexOf(code)],description:'Synthetic description',
  skillCount:10,measurementCount:20,measurements,notice:'US source; not profile or career fit'};
}
let calls=[],visible='',status='';const model={...listing};
const context={document:{createElement:tag=>new Element(tag)},el:id=>ids[id],state,
  locked:b=>{state.busy=b},setStatus:s=>{status=s},show:s=>{visible=s},home:()=>{visible='welcome'},
  api:async (url,method)=>{assert.equal(method,'GET');calls.push(url);return url==='/api/careers'?model:detail(decodeURIComponent(url.split('/').pop()))},
  Set,Map,Error,Number,Object,Array,String};
vm.createContext(context);vm.runInContext(source,context);
const collect=(root,pred)=>{const found=[];const walk=x=>{if(pred(x))found.push(x);for(const c of x.children||[])walk(c)};walk(root);return found};
(async()=>{
 await ids.careersOpen.onclick();assert.equal(calls.length,0,'Unauthorized call must not fetch');
 state.authenticated=true;await ids.careersOpen.onclick();
 assert.equal(visible,'careers');assert.equal(ids.careerItems.children.length,2);
 const second=ids.careerItems.children[1];await second.children[2].onclick();
 assert.equal(calls[1],'/api/careers/15-2051.01');
 assert.equal(ids.careerDetail.hidden,false);
 let sections=collect(ids.careerDetail,x=>x.tag==='section');assert.equal(sections.length,10);
 assert.equal(sections[0].children[0].textContent,'Понимание прочитанного');
 assert(sections[0].children[1].textContent.includes('Reading Comprehension'));
 const grid=sections[0].children[2];assert.equal(grid.children.length,2);
 let values=collect(grid,x=>x.className==='career-measure-value').map(x=>x.textContent);
 assert.deepEqual(values,['4,00 / 5','4,25 / 7']);
 let meters=collect(grid,x=>x.tag==='meter');assert.equal(meters.length,2);
 assert.deepEqual(meters.map(x=>[x.min,x.max,x.value]),[[1,5,4],[0,7,4.25]]);
 assert(meters.every(x=>x.attrs['aria-label'].includes('исходной шкале O*NET')));
 const json=JSON.stringify(ids.careerDetail);
 assert(!json.includes('4.0000')&&!json.includes('% fit')&&!json.includes('подходит'));
 await ids.careerItems.children[0].children[2].onclick();
 sections=collect(ids.careerDetail,x=>x.tag==='section');
 assert.equal(sections.length,10);
 const missing=sections[9];assert(collect(missing,x=>x.textContent.includes('SUPPRESSED')).length>0);
 assert.equal(collect(missing,x=>x.tag==='meter').length,1,'missing scale has no zero meter');
 const safe=detail(codes[0]);safe.measurements[0].skill='Untrusted skill';
 context.bad=safe;
 assert.throws(()=>vm.runInContext('careerRenderDetail(bad)',context),/Незнакомое название/);
 safe.measurements[0].skill='Reading Comprehension';safe.measurements[0].rawValue='4.00001';
 assert.throws(()=>vm.runInContext('careerRenderDetail(bad)',context),/Неверное исходное значение/);
 safe.measurements[0].rawValue='4.0000';safe.measurements[0].minimum='0';
 assert.throws(()=>vm.runInContext('careerRenderDetail(bad)',context),/несовместимую шкалу/);
 // A failed detail read does not expose stale data.
 state.authenticated=false;
 await ids.careersOpen.onclick();assert.equal(calls.length,3);
 await ids.careerHome.onclick();assert.equal(visible,'welcome');
 console.log('CAREER_KB_UI_RU_COMPACT_SYNTHETIC_SMOKE_PASS');
})().catch(e=>{console.error(e);process.exitCode=1});
