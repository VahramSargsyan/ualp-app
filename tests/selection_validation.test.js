const fs=require('fs'),vm=require('vm'),assert=require('assert');
const ctx={console,Number,Math,isFinite};vm.createContext(ctx);
for(const f of ['src/SheetDb.gs','src/ScoringService.gs'])vm.runInContext(fs.readFileSync(f,'utf8'),ctx,{filename:f});
function code(fn){try{fn();return null}catch(e){return e.ualpCode}}
const form={defaultResponseSetId:'RS1'};
const formItems=[{itemId:'i1',responseSetOverrideId:''},{itemId:'i2',responseSetOverrideId:''}];
const items={i1:{itemId:'i1',responseSetId:'RS1'},i2:{itemId:'i2',responseSetId:'OBJ'}};
const ro={r1:{responseOptionId:'r1',responseSetId:'RS1'},r2:{responseOptionId:'r2',responseSetId:'RS2'}};
const io={o1:{itemOptionId:'o1',itemId:'i2',scoreValue:1},oX:{itemOptionId:'oX',itemId:'other',scoreValue:1}};
ctx.validateResponseSelections_(form,formItems,[{itemId:'i1',responseOptionId:'r1'},{itemId:'i2',itemOptionId:'o1'}],items,ro,io);
assert.equal(code(()=>ctx.validateResponseSelections_(form,formItems,[{itemId:'i1',responseOptionId:'r2'}],items,ro,io)),'RESPONSE_OPTION_NOT_ALLOWED');
assert.equal(code(()=>ctx.validateResponseSelections_(form,formItems,[{itemId:'i2',itemOptionId:'oX'}],items,ro,io)),'ITEM_OPTION_NOT_ALLOWED');
assert.equal(code(()=>ctx.validateResponseSelections_(form,formItems,[{itemId:'outside',responseOptionId:'r1'}],items,ro,io)),'RESPONSE_ITEM_NOT_IN_FORM');
console.log('selection_validation.test.js: PASS');
