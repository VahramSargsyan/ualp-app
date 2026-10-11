const fs=require('fs'), vm=require('vm'), assert=require('assert');
const ctx={console, Number, Math, isFinite}; vm.createContext(ctx);
for(const f of ['src/SheetDb.gs','src/ScoringCore.gs']) vm.runInContext(fs.readFileSync(f,'utf8'),ctx,{filename:f});

function throwsCode(fn,code){let ok=false;try{fn()}catch(e){ok=e.ualpCode===code}assert.ok(ok,`expected ${code}`)}

// RIASEC-like SUM
{
 const out=ctx.computeScaleScores_({
  formItems:[{itemId:'i1',required:true},{itemId:'i2',required:true}],
  responses:[{itemId:'i1',responseOptionId:'r4'},{itemId:'i2',responseOptionId:'r2'}],
  responseOptionsById:{r4:{scoreValue:4},r2:{scoreValue:2}}, itemOptionsById:{},
  scaleLinks:[{itemId:'i1',scaleId:'R',weight:1,direction:'POSITIVE'},{itemId:'i2',scaleId:'R',weight:1,direction:'POSITIVE'}],
  scoringRules:[{scaleId:'R',aggregationMethod:'SUM',minAnsweredItems:2,minCompletionPct:100,rawMin:0,rawMax:8,algorithmVersion:'RIASEC-SUM-v1'}]
 });
 assert.equal(out[0].rawScore,6);
}

// Work-values-like MEAN
{
 const out=ctx.computeScaleScores_({
  formItems:[{itemId:'i1',required:true},{itemId:'i2',required:true}],
  responses:[{itemId:'i1',responseOptionId:'a'},{itemId:'i2',responseOptionId:'b'}],
  responseOptionsById:{a:{scoreValue:4},b:{scoreValue:2}}, itemOptionsById:{},
  scaleLinks:[{itemId:'i1',scaleId:'WV',weight:1,direction:'POSITIVE'},{itemId:'i2',scaleId:'WV',weight:1,direction:'POSITIVE'}],
  scoringRules:[{scaleId:'WV',aggregationMethod:'MEAN',minAnsweredItems:2,minCompletionPct:100,rawMin:0,rawMax:4,algorithmVersion:'WORKVALUES-MEAN-v1'}]
 });
 assert.equal(out[0].rawScore,3);
}

// ICAR-like binary objective item options
{
 const out=ctx.computeScaleScores_({
  formItems:[{itemId:'i1',required:true},{itemId:'i2',required:true}],
  responses:[{itemId:'i1',itemOptionId:'correct'},{itemId:'i2',itemOptionId:'wrong'}],
  responseOptionsById:{}, itemOptionsById:{correct:{scoreValue:1},wrong:{scoreValue:0}},
  scaleLinks:[{itemId:'i1',scaleId:'TOTAL',weight:1,direction:'POSITIVE'},{itemId:'i2',scaleId:'TOTAL',weight:1,direction:'POSITIVE'}],
  scoringRules:[{scaleId:'TOTAL',aggregationMethod:'SUM',minAnsweredItems:2,minCompletionPct:100,rawMin:0,rawMax:2,algorithmVersion:'ICAR16-BINARY-v1'}]
 });
 assert.equal(out[0].rawScore,1);
}

throwsCode(()=>ctx.computeScaleScores_({formItems:[{itemId:'i1',required:true}],responses:[],responseOptionsById:{},itemOptionsById:{},scaleLinks:[],scoringRules:[]}), 'FORM_INCOMPLETE');
console.log('scoring_core.test.js: PASS');
