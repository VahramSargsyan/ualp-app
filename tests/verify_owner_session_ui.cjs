// Browser regression against a LOCAL HTTPS server with a synthetic access key.
// Catalog/results are mocked: this is not evidence of Neon/Preview persistence.
const {chromium}=require('playwright');
const assert=require('node:assert/strict');
(async()=>{
 const browser=await chromium.launch({headless:true,executablePath:process.env.CHROMIUM_PATH||undefined,args:['--no-sandbox']});
 const errors=[];
 let ctx=await browser.newContext({ignoreHTTPSErrors:true,viewport:{width:393,height:852}});
 let page=await ctx.newPage();
 page.on('pageerror',e=>errors.push(e.message));
 await page.goto('https://127.0.0.1:8843');
 await page.locator('#login').waitFor({state:'visible'});
 assert(await page.locator('#remember').isChecked(), 'Private owner TEST must offer persistent sign-in by default');
 const key='synthetic-browser-only-access-key-000000000000';
 // Distinguish rejected key from a server-accepted login whose browser loses the session cookie.
 await page.locator('#access').fill('wrong-synthetic-key');
 await page.locator('#login').click();
 await page.waitForFunction(()=>document.getElementById('status').textContent.includes('LOGIN_REQUEST_FAILED'));
 assert.equal(await page.locator('#access').inputValue(),'wrong-synthetic-key');
 // Simulate an otherwise successful server cookie issue followed by a blocked/absent cookie on verification.
 await page.route('**/api/session',async route=>{
   if(route.request().method()==='GET')
     return route.fulfill({status:401,contentType:'application/json',body:JSON.stringify({detail:'Access denied'})});
   return route.continue();
 });
 await page.locator('#access').fill(key);
 await page.locator('#login').click();
 await page.waitForFunction(()=>document.getElementById('status').textContent.includes('SESSION_COOKIE_CHECK_FAILED'));
 assert.equal(await page.locator('#access').inputValue(),key,'Never discard key before cookie check');
 assert(!(await page.locator('#signedIn').isVisible()),'Do not claim authenticated when cookie check fails');
 await page.unroute('**/api/session');
 await page.locator('#login').click();
 await page.locator('#signedIn').waitFor({state:'visible'});
 assert(await page.locator('#preferencesPanel').isVisible(),'Initial owner preference setup must be offered');
 assert.equal(await page.locator('#access').inputValue(),'');
 let cookies=await ctx.cookies();
 const session=cookies.find(c=>c.name==='__Host-ualp_session');
 assert(session&&session.httpOnly&&session.secure&&session.sameSite==='Strict');
 assert(session.expires>Date.now()/1000+29*24*60*60,'Cookie should persist for about 30 days, not the browser session');
 assert.match(await page.locator('#status').innerText(),/Вход сохранён на 30 дней/);
 assert(!session.value.includes('synthetic-browser'));
 const storage=await ctx.storageState();
 assert(storage.origins.every(o=>o.localStorage.length===0));
 await ctx.close();
 ctx=await browser.newContext({ignoreHTTPSErrors:true,viewport:{width:393,height:852},storageState:storage});
 page=await ctx.newPage();page.on('pageerror',e=>errors.push(e.message));
 await page.route('**/api/profile',route=>route.fulfill({json:{methods:[],methodCount:0,completedRuns:0,hasMoreMethods:false}}));
 await page.route('**/api/forms/*',route=>route.fulfill({json:{formKey:'ONET_SHORT_60_DIGITAL',items:Array.from({length:60},(_,i)=>({itemId:'synthetic-'+i,prompt:'Synthetic item '+i})),options:[{optionKey:'V1',label:'Synthetic answer'}]}}));
 await page.route('**/api/runs',route=>route.fulfill({status:201,json:{scoringAlgorithmVersion:'RIASEC-SUM-v1',runId:'synthetic-run',scores:['R','I','A','S','E','C'].map(key=>({key,mean:10}))}}));
 // Synthetic history responses only; session endpoint still uses real local HTTPS backend.
 const historyRows=[
  {runId:'synthetic-history-wv-old',formKey:'UALP_WV21_RU_LIKERT',
   formVersion:'synthetic-work-values-v1',scoringAlgorithmVersion:'WORKVALUES-MEAN-v1',
   status:'COMPLETED',completedAt:'2026-11-14T11:00:00Z'},
  {runId:'synthetic-history-wv-new',formKey:'UALP_WV21_RU_LIKERT',
   formVersion:'synthetic-work-values-v1',scoringAlgorithmVersion:'WORKVALUES-MEAN-v1',
   status:'COMPLETED',completedAt:'2026-11-16T11:00:00Z'},
  {runId:'synthetic-history-wv-different',formKey:'UALP_WV21_RU_LIKERT',
   formVersion:'synthetic-work-values-v2',scoringAlgorithmVersion:'WORKVALUES-MEAN-v1',
   status:'COMPLETED',completedAt:'2026-11-17T11:00:00Z'},
  {runId:'synthetic-history-riasec',formKey:'ONET_SHORT_60_DIGITAL',
   formVersion:'synthetic-riasec',scoringAlgorithmVersion:'RIASEC-SUM-v1',
   status:'COMPLETED',completedAt:'2026-11-15T11:00:00Z'}
 ];
 await page.route('**/api/history**',route=>{
  const u=new URL(route.request().url()),filter=u.searchParams.get('formKey');
  assert(['ALL','UALP_WV21_RU_LIKERT','ONET_SHORT_60_DIGITAL'].includes(filter));
  const entries=historyRows.filter(x=>filter==='ALL'||x.formKey===filter);
  return route.fulfill({json:{formKeyFilter:filter,items:entries,pageSize:10,nextCursor:null}});
 });
 await page.route('**/api/runs/synthetic-history-*',route=>{
  const runId=route.request().url().split('/').pop();
  const isRiasec=runId==='synthetic-history-riasec';
  const isNewest=runId==='synthetic-history-wv-new';
  return route.fulfill({json:{
    runId,status:'COMPLETED',
    scoringAlgorithmVersion:isRiasec?'RIASEC-SUM-v1':'WORKVALUES-MEAN-v1',
    scores:['R','I','A','S','E','C'].map(k=>({
      scaleId:'synthetic-scale-'+k,key:k,label:'Synthetic scale '+k,
      answered:isRiasec?10:3,
      mean:isRiasec?20:isNewest?2.75:2.25
    }))
  }});
 });
 await page.goto('https://127.0.0.1:8843');
 await page.locator('#signedIn').waitFor({state:'visible'});
 await page.locator('#historyOpen').click();
 await page.locator('#history').waitFor({state:'visible'});
 await page.waitForFunction(()=>document.querySelectorAll('#historyList li').length===4);
 assert((await page.locator('#historyList').innerText()).includes('RIASEC'));
 assert((await page.locator('#historyList').innerText()).includes('Work Values'));
 await page.locator('#historyFilter').selectOption('ONET_SHORT_60_DIGITAL');
 await page.waitForFunction(()=>document.querySelectorAll('#historyList li').length===1&&
   document.querySelector('#historyList').textContent.includes('RIASEC'));
 await page.locator('#historyList li button:not([data-compare-run])').click();
 await page.locator('#results').waitFor({state:'visible'});
 assert.match(await page.locator('#resultExplain').innerText(),/Шесть независимых сумм интересов/);
 await page.locator('#resultHistory').click();
 await page.locator('#history').waitFor({state:'visible'});
 await page.locator('#historyFilter').selectOption('UALP_WV21_RU_LIKERT');
 await page.waitForFunction(()=>document.querySelectorAll('#historyList li').length===3&&
   document.querySelector('#historyList').textContent.includes('Work Values'));
 // One pass is not enough; do not compare different form versions or RIASEC vs Work Values.
 assert(await page.locator('#historyCompare').isDisabled());
 await page.locator('button[data-compare-run="synthetic-history-wv-old"]').click();
 assert.match(await page.locator('#compareSelectionStatus').innerText(),/1 из 2/);
 await page.locator('button[data-compare-run="synthetic-history-wv-different"]').click();
 assert.match(await page.locator('#status').innerText(),/одной методики с одинаковой версией/);
 assert.match(await page.locator('#compareSelectionStatus').innerText(),/1 из 2/);
 await page.locator('button[data-compare-run="synthetic-history-wv-new"]').click();
 assert(await page.locator('#historyCompare').isEnabled());
 await page.locator('#historyCompare').click();
 await page.locator('#compare').waitFor({state:'visible'});
 assert.match(await page.locator('#compareContext').innerText(),/synthetic-work-values-v1/);
 assert.equal(await page.locator('#compareRows .compare-row').count(),7);
 assert.match(await page.locator('#compareRows').innerText(),/\+0\.50/);
 assert.match(await page.locator('#compare').innerText(),/не подтверждение развития навыков/);
 await page.locator('#compareHistory').click();
 await page.locator('#history').waitFor({state:'visible'});
 await page.locator('#historyFilter').selectOption('ONET_SHORT_60_DIGITAL');
 await page.waitForFunction(()=>document.querySelectorAll('#historyList li').length===1);
 assert(await page.locator('#historyCompare').isDisabled(),'Filter change clears selections');
 assert.match(await page.locator('#compareSelectionStatus').innerText(),/0 из 2/);
 await page.locator('#historyHome').click();
 await page.locator('#profileOpen').click();await page.locator('#profile').waitFor({state:'visible'});
 await page.locator('#profileHome').click();
 assert(await page.locator('#signedIn').isVisible());
 assert(await page.locator('#preferencesPanel').isVisible(),'First login setup remains until explicitly saved');
 await page.locator('#consent').check();
 await page.locator('#draftOptIn').check();
 await page.locator('#preferencesSave').click();
 assert(await page.locator('#preferencesPanel').isHidden(),'After one-time setup, detailed checkboxes should be hidden');
 assert(await page.locator('#preferencesSummary').isVisible(),'Summary/settings control remains available');
 assert.equal(await page.locator('#welcomeTitle').innerText(),'Главная · UALP');
 assert(await page.locator('#welcomeIntro').isHidden(),'Long onboarding copy not on authenticated dashboard');
 // Repeated navigation to Home must NOT uncheck consent or redisplay setup.
 for(let i=0;i<2;i++){
   await page.locator('#profileOpen').click();
   await page.locator('#profile').waitFor({state:'visible'});
   await page.locator('#profileHome').click();
   assert(await page.locator('#consent').isChecked(),'Home must preserve consent');
   assert(await page.locator('#draftOptIn').isChecked(),'Home must preserve draft preference');
   assert(await page.locator('#preferencesPanel').isHidden(),'Do not re-display onboarding on Home');
 }
 await page.locator('#preferencesEdit').click();
 assert(await page.locator('#preferencesPanel').isVisible(),'Owner can edit preferences on demand');
 await page.locator('#preferencesSave').click();
 assert(await page.locator('#preferencesPanel').isHidden());
 await page.locator('#startRiasec').click();
 for(let i=0;i<60;i++){
   await page.locator('#options input').check();await page.locator('#next').click();
 }
 await page.locator('#results').waitFor({state:'visible'});
 await page.locator('#resultHome').click();
 assert(await page.locator('#signedIn').isVisible());
 await page.reload();await page.locator('#signedIn').waitFor({state:'visible'});
 assert(await page.locator('#consent').isChecked(),'Consent restored on the same authenticated device');
 assert(await page.locator('#draftOptIn').isChecked(),'Opt-in restored on the same authenticated device');
 assert(await page.locator('#preferencesPanel').isHidden(),'Do not show prior one-time setup on browser reopen');
 assert(await page.locator('#preferencesSummary').isVisible());
 await page.screenshot({path:'/tmp/ualp-session-mobile.png',fullPage:true});
 await page.locator('#logout').click();await page.locator('#loginFields').waitFor({state:'visible'});
 await page.reload();await page.locator('#login').waitFor({state:'visible'});
 assert.equal(await page.locator('#signedIn').isVisible(),false);
 assert.equal((await ctx.cookies()).some(c=>c.name==='__Host-ualp_session'),false);
 assert.equal(await page.evaluate(()=>localStorage.getItem('ualp-owner-settings-v1')),null,
   'Explicit logout clears saved one-time consent and draft preference');
 assert(await page.locator('#remember').isChecked(),'Preference should default to remembered after logout');
 // Shared-device opt-out remains supported; it must issue a non-persistent session cookie.
 await page.locator('#remember').uncheck();
 await page.locator('#access').fill('synthetic-browser-only-access-key-000000000000');
 await page.locator('#login').click();
 await page.locator('#signedIn').waitFor({state:'visible'});
 const temporary=(await ctx.cookies()).find(c=>c.name==='__Host-ualp_session');
 assert(temporary&&temporary.expires===-1,'Opt-out should produce a browser-session cookie');
 assert.match(await page.locator('#status').innerText(),/без запоминания/);
 await page.locator('#logout').click();
 await page.locator('#loginFields').waitFor({state:'visible'});
 assert.deepEqual(errors,[]);
 console.log('PASS: same-form same-version raw comparison, incompatible version rejection, filter reset, one-time consent, Home, login/history/profile; local HTTPS synthetic');
 await browser.close();
})().catch(e=>{console.error(e);process.exit(1)});
