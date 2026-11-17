// Synthetic LOCAL HTTPS Chromium regression for consent-based browser-only draft resume.
// No Neon access, no real question texts, no real respondent data.
const {chromium}=require('playwright');
const assert=require('node:assert/strict');
const ROOT='https://127.0.0.1:8843';
const PREFIX='ualp-owner-draft-v1:';
const RIASEC='ONET_SHORT_60_DIGITAL', WV='UALP_WV21_RU_LIKERT';
(async()=>{
 const browser=await chromium.launch({headless:true,
  executablePath:process.env.CHROMIUM_PATH||undefined,args:['--no-sandbox']});
 const context=await browser.newContext({ignoreHTTPSErrors:true,viewport:{width:393,height:852}});
 const page=await context.newPage(),errors=[];
 page.on('pageerror',e=>errors.push(e.message));
 let submitted=null;
 await page.route('**/api/forms/*',async route=>{
  const formKey=decodeURIComponent(route.request().url().split('/').pop());
  const n=formKey===RIASEC?60:formKey===WV?21:0;
  assert(n>0,'Unexpected form requested');
  await route.fulfill({json:{formKey,formVersion:formKey+'-synthetic-v1',
   items:Array.from({length:n},(_,i)=>({itemId:formKey+'-'+i,prompt:'Synthetic question '+i})),
   options:[{optionKey:'V1',label:'Synthetic option 1'},{optionKey:'V2',label:'Synthetic option 2'}]}});
 });
 await page.route('**/api/runs',async route=>{
  submitted=route.request().postDataJSON();
  await route.fulfill({status:201,json:{scoringAlgorithmVersion:'RIASEC-SUM-v1',
   runId:'synthetic-saved-run',formKey:'ONET_SHORT_60_DIGITAL',status:'COMPLETED',
   formVersion:'synthetic-draft-v1',validationStatus:'NOT_REVIEWED',
   recordedAt:'2026-11-17T10:00:00+00:00',
   scores:['R','I','A','S','E','C'].map(key=>({key,mean:10}))}});
 });
 await page.goto(ROOT);
 await page.locator('#access').fill('synthetic-browser-only-access-key-000000000000');
 await page.locator('#remember').check();
 await page.locator('#login').click();
 await page.locator('#signedIn').waitFor({state:'visible'});
 await page.locator('#consent').check();
 await page.locator('#draftOptIn').check();
 await page.locator('#preferencesSave').click();
 assert(await page.locator('#preferencesPanel').isHidden());
 await page.locator('#startRiasec').click();
 await page.locator('#questions').waitFor({state:'visible'});
 // Two responses and navigation; request identity persists across reload.
 await page.locator('#options input[value="V1"]').check();
 await page.locator('#next').click();
 await page.locator('#options input[value="V2"]').check();
 await page.locator('#next').click();
 let riasecDraft=await page.evaluate(k=>JSON.parse(localStorage.getItem(k)),PREFIX+RIASEC);
 assert(riasecDraft&&riasecDraft.itemIds.length===60);
 assert.equal(riasecDraft.index,2);
 assert.equal(Object.keys(riasecDraft.answers).length,2);
 assert(!JSON.stringify(riasecDraft).includes('synthetic-browser-only-access-key'));
 assert(!JSON.stringify(riasecDraft).includes('Synthetic question'));
 const requestId=riasecDraft.requestId;
 await page.reload();
 await page.locator('#signedIn').waitFor({state:'visible'});
 await page.locator('#draftResumes button').first().waitFor({state:'visible'});
 assert(await page.locator('#consent').isChecked(),'Remember the one-time consent on browser reopen');
 assert(await page.locator('#draftOptIn').isChecked(),'Remember explicit draft opt-in on browser reopen');
 assert(await page.locator('#preferencesPanel').isHidden(),'Do not return to first-time setup after reload');
 await page.getByRole('button',{name:'Продолжить RIASEC'}).click();
 await page.locator('#questions').waitFor({state:'visible'});
 assert.match(await page.locator('#position').innerText(),/Вопрос 3 из 60/);
 await page.locator('#previous').click();
 assert(await page.locator('#options input[value="V2"]').isChecked());
 await page.locator('#next').click();
 await page.locator('#questionHome').click();
 await page.locator('#welcome').waitFor({state:'visible'});
 // Independent Work Values draft must not overwrite the RIASEC draft.
 await page.locator('#consent').check();
 await page.locator('#start').click();
 await page.locator('#options input[value="V1"]').check();
 await page.locator('#questionHome').click();
 await page.locator('#welcome').waitFor({state:'visible'});
 assert(await page.getByRole('button',{name:'Продолжить Work Values'}).isVisible());
 assert(await page.getByRole('button',{name:'Продолжить RIASEC'}).isVisible());
 const wvDraft=await page.evaluate(k=>localStorage.getItem(k),PREFIX+WV);
 assert(wvDraft,'Work Values draft missing');
 // Refuse to silently restart the saved RIASEC form.
 page.once('dialog',d=>d.dismiss());
 await page.locator('#consent').check();
 await page.locator('#startRiasec').click();
 assert(await page.getByRole('button',{name:'Продолжить RIASEC'}).isVisible());
 await page.getByRole('button',{name:'Продолжить RIASEC'}).click();
 await page.locator('#questions').waitFor({state:'visible'});
 assert.match(await page.locator('#position').innerText(),/Вопрос 3 из 60/);
 for(let i=2;i<60;i++){
  await page.locator('#options input[value="V1"]').check();
  await page.locator('#next').click();
 }
 await page.locator('#results').waitFor({state:'visible'});
 assert.match(await page.locator('#resultProvenance').innerText(),/synthetic-draft-v1/);
 assert(submitted&&submitted.requestId===requestId);
 assert.equal(submitted.answers.length,60);
 assert.equal(await page.evaluate(k=>localStorage.getItem(k),PREFIX+RIASEC),null);
 assert.equal(await page.evaluate(k=>localStorage.getItem(k),PREFIX+WV),wvDraft);
 await page.locator('#resultHome').click();
 // A stale version must be rejected, not applied against changed catalog content.
 await page.evaluate(k=>{
  const d=JSON.parse(localStorage.getItem(k));d.formVersion='different-version';
  localStorage.setItem(k,JSON.stringify(d));
 },PREFIX+WV);
 await page.locator('#consent').check();
 await page.getByRole('button',{name:'Продолжить Work Values'}).click();
 await page.waitForFunction(()=>document.getElementById('status').textContent.includes('Версия вопросов изменилась'));
 assert.match(await page.locator('#status').innerText(),/Версия вопросов изменилась/);
 assert.equal(await page.evaluate(k=>localStorage.getItem(k),PREFIX+WV),null);
 // Expired draft is removed lazily when the authenticated owner next opens the app.
 await page.evaluate(({key,draft})=>{
  draft.savedAt=Date.now()-8*24*60*60*1000;
  draft.expiresAt=Date.now()-1;
  localStorage.setItem(key,JSON.stringify(draft));
 },{key:PREFIX+RIASEC,draft:riasecDraft});
 await page.reload();
 await page.locator('#signedIn').waitFor({state:'visible'});
 assert.equal(await page.evaluate(k=>localStorage.getItem(k),PREFIX+RIASEC),null);
 // Unsubmitted opt-in drafts must be wiped at logout, never stored in the session cookie.
 // Full reload must retain the one-time consent and explicit draft preference.
 assert(await page.locator('#consent').isChecked());
 assert(await page.locator('#draftOptIn').isChecked());
 await page.locator('#start').click();
 await page.locator('#options input[value="V2"]').check();
 await page.locator('#questionHome').click();
 assert(await page.evaluate(k=>localStorage.getItem(k),PREFIX+WV));
 await page.locator('#logout').click();
 await page.locator('#loginFields').waitFor({state:'visible'});
 assert.equal(await page.evaluate(k=>localStorage.getItem(k),PREFIX+WV),null);
 assert.equal(await page.evaluate(k=>localStorage.getItem(k),PREFIX+RIASEC),null);
 assert.equal(await page.evaluate(()=>localStorage.getItem('ualp-owner-settings-v1')),null);
 await page.reload();
 await page.locator('#login').waitFor({state:'visible'});
 assert(!(await page.locator('#draftResumes').isVisible()));
 assert.deepEqual(errors,[]);
 console.log('PASS: opt-in, per-form 60/21 drafts, reload, version fence, saved requestId, save cleanup, logout cleanup; synthetic local HTTPS');
 await browser.close();
})().catch(e=>{console.error(e);process.exit(1)});
