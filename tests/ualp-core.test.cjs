'use strict';
const test = require('node:test');
const assert = require('node:assert/strict');
const fs = require('node:fs');
const vm = require('node:vm');
const path = require('node:path');

const js = fs.readFileSync(path.join(__dirname,'../apps-script/Code.gs'),'utf8');
const sandbox = { console, Date, Math, JSON, Object, Array, Number, String, Error, isFinite };
vm.createContext(sandbox);
vm.runInContext(js,sandbox,{filename:'Code.gs'});
const call = (name,...args) => sandbox[name](...args);

function fixture(kind='RIASEC'){
  const objective=kind==='ICAR', values=kind==='WORKVALUES';
  const data={
    AssessmentForms:[{assessmentFormId:'FORM1',assessmentId:'AS1',formKey:'PILOT',
      formVersion:'v1',itemCount:2,defaultResponseSetId:'SET1',originalLanguage:'ru',
      name:'PILOT',schemaVersion:'v0.4',recordStatus:'DRAFT'}],
    AssessmentFormItems:[{assessmentFormId:'FORM1',itemId:'I1',displayOrder:1,required:true},
      {assessmentFormId:'FORM1',itemId:'I2',displayOrder:2,required:true}],
    Items:[{itemId:'I1',canonicalLanguage:'ru',canonicalPrompt:'Prompt one',responseSetId:'SET1'},
      {itemId:'I2',canonicalLanguage:'ru',canonicalPrompt:'Prompt two',responseSetId:'SET1'}],
    ItemTranslations:[],
    ResponseOptions:objective?[]:[
      {responseOptionId:'R0',responseSetId:'SET1',displayOrder:1,scoreValue:0,optionKey:'LOW'},
      {responseOptionId:'R1',responseSetId:'SET1',displayOrder:2,scoreValue:1,optionKey:'ONE'},
      {responseOptionId:'R3',responseSetId:'SET1',displayOrder:3,scoreValue:3,optionKey:'THREE'},
      {responseOptionId:'R4',responseSetId:'SET1',displayOrder:4,scoreValue:4,optionKey:'HIGH'}],
    ResponseOptionTranslations:[],
    ItemOptions:objective?[
      {itemOptionId:'I1A',itemId:'I1',optionKey:'A',displayOrder:1,optionText:'A',isCorrect:true,scoreValue:1},
      {itemOptionId:'I1B',itemId:'I1',optionKey:'B',displayOrder:2,optionText:'B',isCorrect:false,scoreValue:0},
      {itemOptionId:'I2A',itemId:'I2',optionKey:'A',displayOrder:1,optionText:'A',isCorrect:false,scoreValue:0},
      {itemOptionId:'I2B',itemId:'I2',optionKey:'B',displayOrder:2,optionText:'B',isCorrect:true,scoreValue:1}]:[],
    ItemOptionTranslations:[],ItemAssets:[],Assets:[],
    AssessmentVersions:[{assessmentVersionId:'AV1',assessmentId:'AS1',scoringAlgorithmVersion:'A-v1'}],
    ItemScaleLinks:[
      {assessmentVersionId:'AV1',itemId:'I1',scaleId:'S1',weight:1,direction:'POSITIVE',
        contributionRule:objective?'CORRECT_1_ELSE_0':'OPTION_SCORE_VALUE'},
      {assessmentVersionId:'AV1',itemId:'I2',scaleId:'S1',weight:1,direction:'POSITIVE',
        contributionRule:objective?'CORRECT_1_ELSE_0':'OPTION_SCORE_VALUE'}],
    FormScoringRules:[{assessmentFormId:'FORM1',scaleId:'S1',aggregationMethod:values?'MEAN':'SUM',
      minAnsweredItems:2,rawMin:0,rawMax:values?4:objective?2:8,algorithmVersion:'A-v1',
      validationStatus:'SOURCE_VERIFIED'}],
    Scales:[{scaleId:'S1',scaleKey:'S',name:'Scale S'}]
  };
  return data;
}
function answers(kind){
  return kind==='ICAR'?[{itemId:'I1',optionId:'I1A'},{itemId:'I2',optionId:'I2A'}]:
    [{itemId:'I1',optionId:kind==='WORKVALUES'?'R1':'R0'},
     {itemId:'I2',optionId:kind==='WORKVALUES'?'R3':'R4'}];
}
const safe = (d)=>call('ualpSafeFormFromBundle_',d,'PILOT','ru');
const score = (d,a)=>call('ualpScoringFromBundle_',d,safe(d),a);
const err = (fn,code)=>assert.throws(fn,new RegExp(code));

test('safe form payload excludes scoring keys and internal fields',()=>{
  const d=fixture('ICAR'); const p=safe(d), out=JSON.stringify(p);
  assert.equal(p.items.length,2);
  for(const secret of ['scoreValue','isCorrect','weight','FormScoringRules','correctOptionId']){
    assert.ok(!out.includes(secret),secret);
  }
  assert.equal(p.pilotOnly,true);
});
test('RIASEC type scoring uses canonical 0..4 SUM (not client transport)',()=>{
  const d=fixture('RIASEC'),result=score(d,answers('RIASEC'));
  assert.equal(result.scores[0].rawScore,4);
  assert.equal(result.algorithmVersion,'A-v1');
});
test('Work Values type scoring uses canonical MEAN',()=>{
  const result=score(fixture('WORKVALUES'),answers('WORKVALUES'));
  assert.equal(result.scores[0].rawScore,2);
});
test('objective ICAR-type scoring counts correct options server-side',()=>{
  const d=fixture('ICAR'); const r=score(d,answers('ICAR'));
  assert.equal(r.scores[0].rawScore,1);
  assert.equal(r.scores[0].answeredItems,2);
});
test('required items and unknown choices fail before writes',()=>{
  const d=fixture();
  err(()=>score(d,[answers('RIASEC')[0]]),'UALP_INCOMPLETE_FORM');
  err(()=>score(d,[{itemId:'I1',optionId:'R0'},{itemId:'I2',optionId:'NOT-IN-SET'}]),'UALP_INVALID_OPTION');
  err(()=>score(d,[{itemId:'I1',optionId:'R0'},{itemId:'I1',optionId:'R4'}]),'UALP_RESPONSE_SET');
});
test('blocked scoring keys cannot be used for runtime scoring',()=>{
  const d=fixture('ICAR');d.FormScoringRules[0].validationStatus='BLOCKED';
  err(()=>score(d,answers('ICAR')),'UALP_SCORING_BLOCKED');
});
test('required unpublished visual assets block form rather than silently disappearing',()=>{
  const d=fixture('ICAR');d.ItemAssets=[{itemId:'I1',assetId:'A1',required:true}];
  d.Assets=[{assetId:'A1',uri:'https://example.com/a.png',storageMode:'EXTERNAL_DEV_REFERENCE',
    validationStatus:'NOT_REVIEWED'}];
  err(()=>safe(d),'UALP_ASSET_NOT_APPROVED');
});
test('TEST config refuses same content and runtime DB and defaults to no PROD',()=>{
  const props={
    UALP_ENV:'TEST',UALP_OWNER_EMAIL:'owner@example.com',UALP_DEV_USER_ID:'U1',
    UALP_ENABLED_FORM_KEY:'PILOT',UALP_ASSESSMENT_LIBRARY_ID:'SAME',UALP_RUNTIME_DB_ID:'SAME'
  };
  sandbox.PropertiesService={getScriptProperties(){return {getProperty:(k)=>props[k]||''};}};
  err(()=>call('ualpConfig_'),'UALP_DB_ISOLATION');
  props.UALP_RUNTIME_DB_ID='RUNTIME';assert.equal(call('ualpConfig_').env,'TEST');
  props.UALP_ENV='PROD';err(()=>call('ualpConfig_'),'UALP_TEST_ONLY');
  props.UALP_ENV='TEST';
  sandbox.Session={getActiveUser(){return {getEmail:()=>''};}};
  err(()=>call('ualpOwner_',call('ualpConfig_')),'UALP_OWNER_ONLY');
});

class FakeSheet{
  constructor(name,rows){this.name=name;this.rows=rows.map(r=>r.slice());this.writes=0;}
  getLastRow(){return this.rows.length;}
  getRange(row,col,height=1,width=1){
    const me=this;
    return {
      getValues(){return Array.from({length:height},(_,i)=>Array.from({length:width},(_,j)=>me.rows[row-1+i]?.[col-1+j]??''));},
      setValues(v){
        assert.equal(v.length,height);v.forEach(rowVals=>assert.equal(rowVals.length,width));
        for(let i=0;i<height;i++){
          if(!me.rows[row-1+i])me.rows[row-1+i]=[];
          for(let j=0;j<width;j++)me.rows[row-1+i][col-1+j]=v[i][j];
        }
        me.writes++;return this;
      },
      createTextFinder(q){
        return {
          matchEntireCell(){return this;},
          findAll(){
            const results=[];
            for(let i=0;i<height;i++){
              const value=me.rows[row-1+i]?.[col-1];
              if(String(value??'')===String(q))results.push({getRow:()=>row+i});
            }
            return results;
          },
          findNext(){return this.findAll()[0]||null;}
        };
      }
    };
  }
  getDataRange(){const width=Math.max(1,...this.rows.map(r=>r.length));return this.getRange(1,1,this.rows.length,width);}
}
class FakeDb{
  constructor(tables){this.sheets={};for(const [k,v] of Object.entries(tables)){this.sheets[k]=new FakeSheet(k,v);}}
  getSheetByName(n){return this.sheets[n]||null;}
  insertSheet(n){this.sheets[n]=new FakeSheet(n,[]);return this.sheets[n];}
  writes(){return Object.values(this.sheets).reduce((a,s)=>a+s.writes,0);}
}
function asRows(records){
  const header=[...new Set(records.flatMap(x=>Object.keys(x)))];
  if(!header.length) return [['recordStatus']];
  return [header,...records.map(r=>header.map(k=>r[k]??''))];
}
function fakeSystem(kind='WORKVALUES'){
  const data=fixture(kind),tables={};
  for(const [k,v] of Object.entries(data))tables[k]=asRows(v);
  const content=new FakeDb(tables),runtimeTables={};
  for(const [k,v] of Object.entries(sandbox.UALP_RUNTIME_HEADERS))runtimeTables[k]=[v.slice()];
  runtimeTables.RuntimeSchema.push(['runtime',sandbox.UALP_RUNTIME_SCHEMA_VERSION,'now','TEST']);
  const runtime=new FakeDb(runtimeTables);
  const props={
    UALP_ENV:'TEST',UALP_OWNER_EMAIL:'owner@example.com',UALP_DEV_USER_ID:'U1',
    UALP_ENABLED_FORM_KEY:'PILOT',UALP_ASSESSMENT_LIBRARY_ID:'CONTENT',UALP_RUNTIME_DB_ID:'RUNTIME'
  };
  sandbox.PropertiesService={getScriptProperties(){return {getProperty:(k)=>props[k]||''};}};
  sandbox.Session={getActiveUser(){return {getEmail:()=> 'owner@example.com'};}};
  sandbox.SpreadsheetApp={openById(id){return id==='CONTENT'?content:id==='RUNTIME'?runtime:null;}};
  let counter=0;
  sandbox.Utilities={getUuid(){counter++;return '11111111-1111-4111-8111-'+String(counter).padStart(12,'0');}};
  sandbox.LockService={getScriptLock(){return {waitLock(){},releaseLock(){}};}};
  return {content,runtime,props};
}
test('start/submit/retry preserve one run, two responses, one score, content read-only',()=>{
  const sys=fakeSystem();
  const started=call('startAssessment',{clientRequestId:'start_request_1234567890'});
  assert.equal(started.form.items.length,2);
  const again=call('startAssessment',{clientRequestId:'start_request_1234567890'});
  assert.equal(again.assessmentRunId,started.assessmentRunId);
  const args={assessmentRunId:started.assessmentRunId,clientRequestId:'submit_request_1234567890',
    responses:answers('WORKVALUES')};
  const result=call('submitAssessment',args);
  assert.equal(result.scores[0].rawScore,2);
  assert.equal(call('submitAssessment',args).assessmentRunId,result.assessmentRunId);
  assert.equal(sys.runtime.getSheetByName('AssessmentRuns').getLastRow(),2);
  assert.equal(sys.runtime.getSheetByName('Responses').getLastRow(),3);
  assert.equal(sys.runtime.getSheetByName('ScaleScores').getLastRow(),2);
  assert.equal(sys.content.writes(),0);
});
test('invalid submission does not mutate runtime canonical records',()=>{
  const sys=fakeSystem();
  const st=call('startAssessment',{clientRequestId:'start_request_0000000001'});
  const before=sys.runtime.writes();
  err(()=>call('submitAssessment',{assessmentRunId:st.assessmentRunId,
    clientRequestId:'submit_request_0000000001',responses:[answers('WORKVALUES')[0]]}),'UALP_INCOMPLETE_FORM');
  assert.equal(sys.runtime.writes(),before);
});
test('same submit request ID cannot be reused for a different run',()=>{
  const sys=fakeSystem();
  const a=call('startAssessment',{clientRequestId:'start_request_2222222222'});
  const b=call('startAssessment',{clientRequestId:'start_request_3333333333'});
  call('submitAssessment',{assessmentRunId:a.assessmentRunId,clientRequestId:'submit_request_2222222222',
    responses:answers('WORKVALUES')});
  err(()=>call('submitAssessment',{assessmentRunId:b.assessmentRunId,clientRequestId:'submit_request_2222222222',
    responses:answers('WORKVALUES')}),'UALP_REQUEST_COLLISION');
});
