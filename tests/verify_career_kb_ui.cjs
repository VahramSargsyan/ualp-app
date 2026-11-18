/** Standalone synthetic DOM/browser smoke; no network, server or credentials. */
'use strict';
const assert=require('node:assert/strict');
const fs=require('node:fs');
const vm=require('node:vm');
const source=fs.readFileSync(process.argv[2]||'webapp/career_ui_snippet.js','utf8');
assert(!source.includes('innerHTML'));
class Element {
  constructor(tag='div') {this.tag=tag;this.children=[];this.textContent='';this.hidden=false;this.disabled=false;this.onclick=null;}
  append(node){this.children.push(node);}
  replaceChildren(...nodes){this.children=[...nodes];}
}
const ids=Object.fromEntries(['careerItems','careerDetail','careersOpen','careerHome'].map(x=>[x,new Element()]));
const state={busy:false,authenticated:true};
const codes=['15-2051.00','15-2051.01'];
const titles=['Data Scientists','Business Intelligence Analysts'];
let calls=[];let opened='';let latestStatus='';
const model={
  source:{snapshotId:'ONET_DB_31_0'},careerFitCalculated:false,
  roles:codes.map((code,i)=>({code,title:titles[i],description:'Synthetic test role '+i,skillCount:10})),
};
function detail(code){
  const measurements=[];
  for(let i=0;i<10;i++)for(const scaleId of ['IM','LV']){
    const suppressed=(code===codes[1]&&i===9&&scaleId==='LV');
    measurements.push({elementId:'2.A.1.'+String.fromCharCode(97+i),skill:'Synthetic skill '+i,
      scaleId,minimum:scaleId==='IM'?'1':'0',maximum:scaleId==='IM'?'5':'7',
      evidenceStatus:suppressed?'SUPPRESSED':'OBSERVED',rawValue:suppressed?null:'3.2500',updatedAtSource:'08/2026'});
  }
  return {source:model.source,careerFitCalculated:false,code,title:titles[codes.indexOf(code)],
    description:'Synthetic detail',skillCount:10,measurementCount:20,measurements,notice:'O*NET US; no fit'};
}
const context={
  document:{createElement:tag=>new Element(tag)},
  el:id=>ids[id], state,
  locked:flag=>{state.busy=flag},
  setStatus:txt=>{latestStatus=txt},
  show:id=>{opened=id},
  home:()=>{opened="welcome"},
  api:async (url,method)=>{assert.equal(method,'GET');calls.push(url);return url==='/api/careers'?model:detail(decodeURIComponent(url.slice('/api/careers/'.length)))},
  console,Set,Map,Error,Number,Object,Array,String,
};
vm.createContext(context);
vm.runInContext(source,context,{filename:'career_ui_snippet.js'});
(async()=>{
  state.authenticated=false;
  await ids.careersOpen.onclick();
  assert.equal(calls.length,0,'No catalog network calls before authorization');
  state.authenticated=true;
  await ids.careersOpen.onclick();
  assert.equal(opened,'careers');
  assert.equal(calls[0],'/api/careers');
  assert.equal(ids.careerItems.children.length,2);
  assert.equal(ids.careerItems.children[1].children.length,3);
  await ids.careerItems.children[1].children[2].onclick();
  assert.equal(calls[1],'/api/careers/15-2051.01');
  assert.equal(ids.careerDetail.hidden,false);
  const all=JSON.stringify(ids.careerDetail);
  assert(all.includes('SUPPRESSED'));
  assert(!all.includes('0.0000'));
  assert(!all.includes('подходит')&&!all.includes('% fit'));
  await ids.careerHome.onclick();
  assert.equal(state.busy,false);
  console.log('CAREER_KB_UI_SYNTHETIC_SMOKE_PASS');
})().catch(e=>{console.error(e);process.exitCode=1});
