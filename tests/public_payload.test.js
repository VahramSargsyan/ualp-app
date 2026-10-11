const fs=require('fs'),vm=require('vm'),assert=require('assert');
const ctx={console, Number, Math, isFinite}; vm.createContext(ctx);
for(const f of ['src/SheetDb.gs','src/FormService.gs']) vm.runInContext(fs.readFileSync(f,'utf8'),ctx,{filename:f});
const q=ctx.buildPublicQuestion_({
 item:{itemId:'ITEM-1',itemType:'OBJECTIVE',canonicalPrompt:'Prompt',scoreValue:99,isCorrect:true},
 formItem:{displayOrder:1,required:true},locale:'ru',itemTranslations:[],responseOptions:[],responseOptionTranslations:{},
 itemOptions:[{itemOptionId:'O1',optionKey:'A',displayOrder:1,optionText:'One',scoreValue:1,isCorrect:true},{itemOptionId:'O2',optionKey:'B',displayOrder:2,optionText:'Two',scoreValue:0,isCorrect:false}],
 itemOptionTranslations:{},itemAssets:[],assetsById:{}
});
const text=JSON.stringify(q);
assert.ok(!text.includes('isCorrect'));
assert.ok(!text.includes('scoreValue'));
assert.equal(q.options[0].itemOptionId,'O1');
console.log('public_payload.test.js: PASS');
