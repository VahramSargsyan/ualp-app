/* UALP-MVP-001 | 0.1.0-dev | owner-only Apps Script TEST.
 * The canonical Assessment Library is read-only. Runtime writes use another spreadsheet.
 * Never publish as "Anyone" and never paste spreadsheet IDs or assessment keys into code.
 */
var UALP_APP_VERSION = '0.1.0-dev';
var UALP_RUNTIME_SCHEMA_VERSION = 'UALP-RUNTIME-v0.1';

var UALP_RUNTIME_HEADERS = {
  Users: ['userId','displayName','locale','status','createdAt','updatedAt'],
  AssessmentRuns: ['assessmentRunId','userId','assessmentFormId','formKey','formVersion','locale','status','startedAt','submittedAt','algorithmVersion','clientStartRequestId','clientSubmitRequestId','contentSchemaVersion','createdAt','updatedAt'],
  Responses: ['responseId','assessmentRunId','itemId','responseOptionId','itemOptionId','responseValue','answeredAt','createdAt'],
  ScaleScores: ['scaleScoreId','assessmentRunId','scaleId','rawScore','answeredItems','expectedItems','algorithmVersion','createdAt'],
  RequestDedup: ['clientRequestId','operation','entityType','entityId','status','responseJson','createdAt','updatedAt'],
  EntityRowIndex: ['entityType','entityId','sheetName','rowNumber','updatedAt'],
  ErrorLog: ['errorId','operation','code','message','contextJson','createdAt'],
  RuntimeSchema: ['schemaKey','schemaVersion','installedAt','environment']
};

function ualpFail_(code, message) {
  throw new Error(code + ': ' + message);
}
function ualpString_(value) { return String(value === null || value === undefined ? '' : value).trim(); }
function ualpNow_() { return new Date().toISOString(); }
function ualpId_(prefix) { return prefix + '-' + Utilities.getUuid(); }
function ualpSame_(a, b) { return ualpString_(a) === ualpString_(b); }

function ualpConfig_() {
  var props = PropertiesService.getScriptProperties();
  var cfg = {
    env: ualpString_(props.getProperty('UALP_ENV')),
    ownerEmail: ualpString_(props.getProperty('UALP_OWNER_EMAIL')).toLowerCase(),
    userId: ualpString_(props.getProperty('UALP_DEV_USER_ID')),
    formKey: ualpString_(props.getProperty('UALP_ENABLED_FORM_KEY')),
    contentId: ualpString_(props.getProperty('UALP_ASSESSMENT_LIBRARY_ID')),
    runtimeId: ualpString_(props.getProperty('UALP_RUNTIME_DB_ID'))
  };
  if (cfg.env !== 'TEST') ualpFail_('UALP_TEST_ONLY', 'Only TEST is permitted in this build');
  if (!cfg.ownerEmail || !cfg.userId || !cfg.formKey || !cfg.contentId || !cfg.runtimeId) {
    ualpFail_('UALP_CONFIG_MISSING', 'Required TEST Script Properties are missing');
  }
  if (cfg.contentId === cfg.runtimeId) ualpFail_('UALP_DB_ISOLATION', 'Content and Runtime DB must differ');
  return cfg;
}
function ualpOwner_(cfg) {
  var email = ualpString_(Session.getActiveUser().getEmail()).toLowerCase();
  if (!email || email !== cfg.ownerEmail) {
    ualpFail_('UALP_OWNER_ONLY', 'Owner identity was not confirmed; use owner-only TEST deployment');
  }
}
function ualpConnect_(cfg) {
  return { content: SpreadsheetApp.openById(cfg.contentId), runtime: SpreadsheetApp.openById(cfg.runtimeId) };
}
function ualpRead_(ss, name, cache) {
  cache = cache || {};
  if (cache[name]) return cache[name];
  var sheet = ss.getSheetByName(name);
  if (!sheet || sheet.getLastRow() < 1) ualpFail_('UALP_TABLE_MISSING', 'Required table: ' + name);
  var values = sheet.getDataRange().getValues();
  var header = values[0].map(ualpString_);
  if (!header.length || !header[0]) ualpFail_('UALP_BAD_HEADER', name);
  var seen = {};
  header.forEach(function(h){ if (h) { if (seen[h]) ualpFail_('UALP_DUPLICATE_HEADER', name + '.' + h); seen[h] = true; } });
  var rows = values.slice(1).filter(function(r){ return r.some(function(v){ return v !== '' && v !== null; }); }).map(function(r) {
    var rec = {}; header.forEach(function(h,i){ if (h) rec[h] = r[i]; }); return rec;
  });
  cache[name] = rows;
  return rows;
}
function ualpBundle_(content, names) {
  var cache = {}, out = {};
  names.forEach(function(n){ out[n] = ualpRead_(content, n, cache); });
  return out;
}
function ualpActive_(row) { return row && ualpString_(row.recordStatus).toUpperCase() !== 'ARCHIVED'; }
function ualpFindOne_(rows, field, val) {
  return (rows || []).filter(function(r){ return ualpActive_(r) && ualpSame_(r[field], val); })[0] || null;
}
function ualpLocalized_(rows, idField, id, locale, field) {
  var exact = (rows || []).filter(function(r){ return ualpActive_(r) && ualpSame_(r[idField], id) && ualpSame_(r.locale, locale); })[0];
  return exact ? ualpString_(exact[field]) : '';
}
function ualpSafeFormFromBundle_(data, formKey, locale) {
  var f = ualpFindOne_(data.AssessmentForms, 'formKey', formKey);
  if (!f) ualpFail_('UALP_FORM_NOT_FOUND', 'Unavailable assessment');
  var language = ualpString_(locale) || ualpString_(f.originalLanguage) || 'ru';
  var memberships = (data.AssessmentFormItems || []).filter(function(r){ return ualpActive_(r) && ualpSame_(r.assessmentFormId, f.assessmentFormId); });
  memberships.sort(function(a,b){ return Number(a.displayOrder)-Number(b.displayOrder); });
  if (!memberships.length || memberships.length !== Number(f.itemCount)) ualpFail_('UALP_FORM_COUNT', 'Incomplete form membership');
  var used = {}, fallbacks = [];
  var items = memberships.map(function(m) {
    if (used[m.itemId]) ualpFail_('UALP_FORM_DUPLICATE_ITEM', 'Duplicate item ID');
    used[m.itemId] = true;
    var item = ualpFindOne_(data.Items, 'itemId', m.itemId);
    if (!item) ualpFail_('UALP_ITEM_MISSING', 'Missing item');
    var prompt = ualpLocalized_(data.ItemTranslations, 'itemId', m.itemId, language, 'promptText');
    var canonical = ualpString_(item.canonicalPrompt);
    if (!prompt) {
      prompt = canonical;
      if (language !== ualpString_(item.canonicalLanguage)) fallbacks.push(m.itemId);
    }
    if (!prompt) ualpFail_('UALP_PROMPT_MISSING', 'Unresolved item prompt');
    var itemOptions = (data.ItemOptions || []).filter(function(o){ return ualpActive_(o) && ualpSame_(o.itemId,m.itemId); });
    var options, type;
    if (itemOptions.length) {
      type = 'ITEM_OPTION';
      options = itemOptions.sort(function(a,b){ return Number(a.displayOrder)-Number(b.displayOrder); }).map(function(o) {
        var lbl = ualpLocalized_(data.ItemOptionTranslations, 'itemOptionId', o.itemOptionId, language, 'optionText') || ualpString_(o.optionText);
        if (!lbl) ualpFail_('UALP_OPTION_LABEL', 'Missing item option label');
        return { id: ualpString_(o.itemOptionId), label: lbl };
      });
    } else {
      type = 'RESPONSE_OPTION';
      var setId = ualpString_(m.responseSetOverrideId) || ualpString_(item.responseSetId) || ualpString_(f.defaultResponseSetId);
      options = (data.ResponseOptions || []).filter(function(o){ return ualpActive_(o) && ualpSame_(o.responseSetId, setId); })
        .sort(function(a,b){ return Number(a.displayOrder)-Number(b.displayOrder); }).map(function(o) {
          var lbl = ualpLocalized_(data.ResponseOptionTranslations, 'responseOptionId', o.responseOptionId, language, 'labelText')
            || ualpLocalized_(data.ResponseOptionTranslations, 'responseOptionId', o.responseOptionId, ualpString_(f.originalLanguage), 'labelText')
            || ualpString_(o.optionKey);
          return { id: ualpString_(o.responseOptionId), label: lbl };
        });
    }
    if (!options.length) ualpFail_('UALP_OPTIONS_MISSING', 'Missing response options');
    // Unapproved required visual stimuli must not silently disappear in the pilot.
    var assignedAssets = (data.ItemAssets || []).filter(function(a){ return ualpActive_(a) && ualpSame_(a.itemId,m.itemId); });
    var assetUrls = assignedAssets.map(function(link) {
      var asset = ualpFindOne_(data.Assets, 'assetId', link.assetId);
      if (!asset || !ualpSame_(asset.storageMode, 'LOCAL_COPY') || !ualpSame_(asset.validationStatus,'SOURCE_VERIFIED')
          || !/^https:\/\//.test(ualpString_(asset.uri))) {
        if (link.required === true || ualpSame_(link.required, 'TRUE')) {
          ualpFail_('UALP_ASSET_NOT_APPROVED', 'Required visual material is not approved for TEST');
        }
        return null;
      }
      return ualpString_(asset.uri);
    }).filter(Boolean);
    return {
      itemId: ualpString_(m.itemId),
      displayOrder: Number(m.displayOrder),
      prompt: prompt,
      required: m.required === true || ualpSame_(m.required, 'TRUE'),
      optionType: type,
      options: options,
      assetUrls: assetUrls
    };
  });
  // Strict allow-list. Do not return the source bundle, answer keys, weights or scoring rules.
  return {
    assessmentFormId: ualpString_(f.assessmentFormId),
    formKey: ualpString_(f.formKey),
    formVersion: ualpString_(f.formVersion),
    contentSchemaVersion: ualpString_(f.schemaVersion),
    title: ualpString_(f.name),
    locale: language,
    pilotOnly: true,
    localizationFallbackCount: fallbacks.length,
    items: items
  };
}
function ualpScoringFromBundle_(data, safeForm, responses) {
  if (!Array.isArray(responses) || responses.length !== safeForm.items.length) {
    ualpFail_('UALP_INCOMPLETE_FORM', 'Every item must be answered once');
  }
  var byItem = {}, items = {};
  safeForm.items.forEach(function(it){ items[it.itemId] = it; });
  responses.forEach(function(r) {
    if (!r || !r.itemId || !items[r.itemId] || byItem[r.itemId]) ualpFail_('UALP_RESPONSE_SET', 'Unexpected or duplicate item');
    var safeItem = items[r.itemId];
    var chosen = (safeItem.options || []).filter(function(o){ return ualpSame_(o.id, r.optionId); })[0];
    if (!chosen) ualpFail_('UALP_INVALID_OPTION', 'Option does not belong to this item');
    byItem[r.itemId] = { itemId: r.itemId, optionId: chosen.id, optionType: safeItem.optionType };
  });
  safeForm.items.forEach(function(it){ if (!byItem[it.itemId]) ualpFail_('UALP_INCOMPLETE_FORM', 'Missing required item'); });
  var f = ualpFindOne_(data.AssessmentForms, 'assessmentFormId', safeForm.assessmentFormId);
  if (!f || !ualpSame_(f.formVersion, safeForm.formVersion)) ualpFail_('UALP_VERSION_CHANGED', 'The assessment form version changed');
  var versions = (data.AssessmentVersions || []).filter(function(v){ return ualpActive_(v) && ualpSame_(v.assessmentId, f.assessmentId); });
  if (versions.length !== 1) ualpFail_('UALP_VERSION_AMBIGUOUS', 'Expected exactly one assessment-version mapping');
  var links = (data.ItemScaleLinks || []).filter(function(l){ return ualpActive_(l) && ualpSame_(l.assessmentVersionId, versions[0].assessmentVersionId) && !!byItem[l.itemId]; });
  var rules = (data.FormScoringRules || []).filter(function(r){ return ualpActive_(r) && ualpSame_(r.assessmentFormId, safeForm.assessmentFormId); });
  if (!rules.length) ualpFail_('UALP_SCORING_RULES_MISSING', 'No scoring rules');
  var versionsSeen={}, scores=[];
  rules.forEach(function(rule) {
    if (ualpSame_(rule.validationStatus, 'BLOCKED')) ualpFail_('UALP_SCORING_BLOCKED', 'Scoring validation has not passed');
    var rel = links.filter(function(l){ return ualpSame_(l.scaleId, rule.scaleId); });
    if (rel.length < Number(rule.minAnsweredItems) || !rel.length) ualpFail_('UALP_SCALE_COVERAGE', 'Not enough items for scale');
    var sum = 0;
    rel.forEach(function(l) {
      var chosen = byItem[l.itemId], value, opt;
      if (chosen.optionType === 'ITEM_OPTION') {
        opt = ualpFindOne_(data.ItemOptions, 'itemOptionId', chosen.optionId);
        if (!opt || !ualpSame_(opt.itemId, l.itemId)) ualpFail_('UALP_OPTION_MISMATCH', 'Item option mismatch');
      } else {
        opt = ualpFindOne_(data.ResponseOptions, 'responseOptionId', chosen.optionId);
        if (!opt) ualpFail_('UALP_OPTION_MISMATCH', 'Response option not found');
      }
      if (ualpSame_(l.contributionRule,'CORRECT_1_ELSE_0')) {
        if (chosen.optionType !== 'ITEM_OPTION') ualpFail_('UALP_SCORING_RULE', 'Objective scoring requires item options');
        value = opt.isCorrect === true || ualpSame_(opt.isCorrect,'TRUE') ? 1 : 0;
      } else if (ualpSame_(l.contributionRule,'OPTION_SCORE_VALUE')) {
        value = Number(opt.scoreValue);
      } else {
        ualpFail_('UALP_UNSUPPORTED_CONTRIBUTION', 'Unsupported contribution type');
      }
      if (!isFinite(value)) ualpFail_('UALP_INVALID_SCORE', 'Non-numeric scoring value');
      var weight = l.weight === '' || l.weight == null ? 1 : Number(l.weight);
      if (!isFinite(weight)) ualpFail_('UALP_INVALID_WEIGHT', 'Invalid scoring weight');
      if (!ualpSame_(l.direction,'POSITIVE')) ualpFail_('UALP_UNSUPPORTED_DIRECTION','Direction needs a reviewed scoring adapter');
      sum += value * weight;
    });
    var method = ualpString_(rule.aggregationMethod);
    var raw;
    if (method === 'SUM' || method === 'COUNT') raw = sum;
    else if (method === 'MEAN') raw = sum / rel.length;
    else ualpFail_('UALP_AGGREGATION_UNKNOWN','Unsupported aggregation');
    raw = Math.round(raw * 100000000) / 100000000;
    if ((rule.rawMin !== '' && rule.rawMin != null && raw < Number(rule.rawMin) - 1e-8)
        || (rule.rawMax !== '' && rule.rawMax != null && raw > Number(rule.rawMax) + 1e-8)) {
      ualpFail_('UALP_SCORE_OUT_OF_RANGE','Score is outside the canonical rule range');
    }
    var scale = ualpFindOne_(data.Scales, 'scaleId', rule.scaleId);
    if (!scale) ualpFail_('UALP_SCALE_MISSING','Unknown scale');
    var alg = ualpString_(rule.algorithmVersion);
    versionsSeen[alg] = true;
    scores.push({scaleId: ualpString_(rule.scaleId), scaleKey: ualpString_(scale.scaleKey),
      scaleName: ualpString_(scale.name), rawScore: raw, answeredItems: rel.length,
      expectedItems: rel.length, algorithmVersion: alg});
  });
  var algorithms = Object.keys(versionsSeen);
  if (algorithms.length !== 1 || !algorithms[0]) ualpFail_('UALP_ALGORITHM_CONFLICT','Inconsistent algorithm version');
  return { algorithmVersion: algorithms[0], scores: scores, responses: Object.keys(byItem).map(function(k){return byItem[k];}) };
}

function ualpContentTables_() {
  return ['AssessmentForms','AssessmentFormItems','Items','ItemTranslations','ResponseOptions',
    'ResponseOptionTranslations','ItemOptions','ItemOptionTranslations','ItemAssets','Assets',
    'AssessmentVersions','ItemScaleLinks','FormScoringRules','Scales'];
}
function ualpFormBundle_(content) { return ualpBundle_(content, ualpContentTables_()); }
function ualpGetForm_() {
  var cfg=ualpConfig_(); ualpOwner_(cfg);
  var db=ualpConnect_(cfg), data=ualpFormBundle_(db.content);
  return ualpSafeFormFromBundle_(data,cfg.formKey,'ru');
}
function getAssessmentForm() {
  return ualpGetForm_();
}

function ualpRuntimeSheet_(runtime, name) {
  var sheet = runtime.getSheetByName(name), headers = UALP_RUNTIME_HEADERS[name];
  if (!sheet || !headers) ualpFail_('UALP_RUNTIME_TABLE_MISSING','Missing runtime table ' + name);
  if (sheet.getLastRow() < 1) ualpFail_('UALP_RUNTIME_SCHEMA_MISSING','Missing runtime header ' + name);
  var current = sheet.getRange(1,1,1,headers.length).getValues()[0].map(ualpString_);
  if (headers.some(function(h,i){return h !== current[i];})) {
    ualpFail_('UALP_RUNTIME_SCHEMA_DRIFT','Runtime table header mismatch: '+name);
  }
  return sheet;
}
function ualpAppend_(runtime, name, records) {
  if (!records.length) return [];
  var sheet=ualpRuntimeSheet_(runtime,name), headers=UALP_RUNTIME_HEADERS[name];
  var rowStart=sheet.getLastRow()+1;
  sheet.getRange(rowStart,1,records.length,headers.length).setValues(records.map(function(rec) {
    return headers.map(function(k){return rec[k] === undefined || rec[k] === null ? '' : rec[k];});
  }));
  return records.map(function(r,i){return rowStart+i;});
}
function ualpFindRuntime_(runtime, table, field, value) {
  var sheet=ualpRuntimeSheet_(runtime,table), header=UALP_RUNTIME_HEADERS[table];
  var col=header.indexOf(field)+1;
  if (!col) ualpFail_('UALP_FIND_FIELD','Unexpected runtime lookup field');
  var last=sheet.getLastRow();
  if (last < 2) return null;
  var match=sheet.getRange(2,col,last-1,1).createTextFinder(ualpString_(value)).matchEntireCell(true).findNext();
  if (!match) return null;
  var rowNumber=match.getRow(), values=sheet.getRange(rowNumber,1,1,header.length).getValues()[0];
  var record={};header.forEach(function(k,i){record[k]=values[i];});
  if (!ualpSame_(record[field],value)) ualpFail_('UALP_STALE_LOCATOR','Runtime lookup verification failed');
  return { row:rowNumber, value:record };
}
function ualpFindAllRuntime_(runtime, table, field, value) {
  var sheet=ualpRuntimeSheet_(runtime,table), header=UALP_RUNTIME_HEADERS[table];
  var col=header.indexOf(field)+1, last=sheet.getLastRow();
  if (!col) ualpFail_('UALP_FIND_FIELD','Unexpected runtime relation field');
  if (last<2) return [];
  return sheet.getRange(2,col,last-1,1).createTextFinder(ualpString_(value)).matchEntireCell(true).findAll().map(function(m) {
    var vals=sheet.getRange(m.getRow(),1,1,header.length).getValues()[0],rec={};
    header.forEach(function(k,i){rec[k]=vals[i];});
    return {row:m.getRow(),value:rec};
  });
}
function ualpUpdateRuntimeRow_(runtime,table,row,patch) {
  var sheet=ualpRuntimeSheet_(runtime,table),header=UALP_RUNTIME_HEADERS[table];
  var vals=sheet.getRange(row,1,1,header.length).getValues()[0];
  header.forEach(function(k,i){ if (Object.prototype.hasOwnProperty.call(patch,k)) vals[i]=patch[k]; });
  sheet.getRange(row,1,1,header.length).setValues([vals]);
}
function ualpFindRun_(runtime,id) {
  var index=ualpFindRuntime_(runtime,'EntityRowIndex','entityId',id);
  if (index && ualpSame_(index.value.entityType,'AssessmentRun') && ualpSame_(index.value.sheetName,'AssessmentRuns')) {
    var sheet=ualpRuntimeSheet_(runtime,'AssessmentRuns'),header=UALP_RUNTIME_HEADERS.AssessmentRuns;
    var n=Number(index.value.rowNumber);
    if (Number.isInteger(n) && n>=2 && n<=sheet.getLastRow()) {
      var vals=sheet.getRange(n,1,1,header.length).getValues()[0],rec={};
      header.forEach(function(k,i){rec[k]=vals[i];});
      if (ualpSame_(rec.assessmentRunId,id)) return {row:n,value:rec};
    }
  }
  return ualpFindRuntime_(runtime,'AssessmentRuns','assessmentRunId',id);
}
function ualpTestRuntimeInstaller() {
  var cfg=ualpConfig_();ualpOwner_(cfg);
  var db=ualpConnect_(cfg),rt=db.runtime;
  // Preflight all existing tables BEFORE making structural writes.
  Object.keys(UALP_RUNTIME_HEADERS).forEach(function(name){
    var sheet=rt.getSheetByName(name);
    if (sheet && sheet.getLastRow()>0) ualpRuntimeSheet_(rt,name);
  });
  Object.keys(UALP_RUNTIME_HEADERS).forEach(function(name){
    var sheet=rt.getSheetByName(name);
    if (!sheet) sheet=rt.insertSheet(name);
    if (sheet.getLastRow()===0) sheet.getRange(1,1,1,UALP_RUNTIME_HEADERS[name].length).setValues([UALP_RUNTIME_HEADERS[name]]);
  });
  var installed=ualpFindRuntime_(rt,'RuntimeSchema','schemaKey','runtime');
  if (installed && !ualpSame_(installed.value.schemaVersion,UALP_RUNTIME_SCHEMA_VERSION)) ualpFail_('UALP_RUNTIME_SCHEMA_VERSION','Migration required');
  if (!installed) ualpAppend_(rt,'RuntimeSchema',[{schemaKey:'runtime',schemaVersion:UALP_RUNTIME_SCHEMA_VERSION,
    installedAt:ualpNow_(),environment:'TEST'}]);
  return {ok:true,environment:'TEST',version:UALP_RUNTIME_SCHEMA_VERSION,tables:Object.keys(UALP_RUNTIME_HEADERS).length};
}
function ualpEnsureRuntime_(runtime) {
  Object.keys(UALP_RUNTIME_HEADERS).forEach(function(n){ualpRuntimeSheet_(runtime,n);});
  var marker=ualpFindRuntime_(runtime,'RuntimeSchema','schemaKey','runtime');
  if (!marker || !ualpSame_(marker.value.schemaVersion,UALP_RUNTIME_SCHEMA_VERSION)
      || !ualpSame_(marker.value.environment,'TEST')) ualpFail_('UALP_RUNTIME_NOT_READY','TEST installer has not completed');
}
function ualpDedup_(runtime,id,operation) {
  var match=ualpFindRuntime_(runtime,'RequestDedup','clientRequestId',id);
  if (match && !ualpSame_(match.value.operation,operation)) ualpFail_('UALP_REQUEST_COLLISION','Request ID already used');
  return match;
}
function ualpCheckRequest_(value) {
  var id=ualpString_(value);
  if (!/^[a-zA-Z0-9_-]{12,100}$/.test(id)) ualpFail_('UALP_REQUEST_ID','Invalid request ID');
  return id;
}
function ualpPublicResult_(runId, scores) {
  return {assessmentRunId:runId,status:'COMPLETED',pilotOnly:true,algorithmVersion:scores[0] ? scores[0].algorithmVersion : '',
    scores:scores.map(function(s){return {scaleId:s.scaleId,scaleKey:s.scaleKey,scaleName:s.scaleName,
      rawScore:Number(s.rawScore),answeredItems:Number(s.answeredItems),expectedItems:Number(s.expectedItems)};})};
}
function ualpReadStoredScores_(runtime,runId,content) {
  var rows=ualpFindAllRuntime_(runtime,'ScaleScores','assessmentRunId',runId);
  var names={};
  (content.Scales||[]).forEach(function(s){names[s.scaleId]=s;});
  return rows.map(function(r){ var s=r.value, scale=names[s.scaleId]||{};return {
    scaleId:s.scaleId,scaleKey:scale.scaleKey||'',scaleName:scale.name||'',rawScore:Number(s.rawScore),
    answeredItems:Number(s.answeredItems),expectedItems:Number(s.expectedItems),algorithmVersion:s.algorithmVersion
  }; });
}
function ualpWithLock_(cb) {
  var lock=LockService.getScriptLock(); lock.waitLock(20000);
  try { return cb(); } finally { lock.releaseLock(); }
}
function startAssessment(input) {
  var cfg=ualpConfig_();ualpOwner_(cfg);
  input=input||{};
  var requestId=ualpCheckRequest_(input.clientRequestId);
  var db=ualpConnect_(cfg),bundle=ualpFormBundle_(db.content);
  var form=ualpSafeFormFromBundle_(bundle,cfg.formKey,'ru'),now=ualpNow_();
  ualpEnsureRuntime_(db.runtime);
  return ualpWithLock_(function(){
    var old=ualpDedup_(db.runtime,requestId,'START');
    if (old && ualpSame_(old.value.status,'COMPLETED')) return JSON.parse(old.value.responseJson);
    // If a start was interrupted before dedup append, recover its existing canonical run.
    var existing=ualpFindRuntime_(db.runtime,'AssessmentRuns','clientStartRequestId',requestId);
    if (existing && !ualpSame_(existing.value.userId,cfg.userId)) ualpFail_('UALP_USER_COLLISION','Unexpected request owner');
    var runId=existing ? existing.value.assessmentRunId : ualpId_('RUN');
    if (!existing) {
      var user=ualpFindRuntime_(db.runtime,'Users','userId',cfg.userId);
      if (!user) ualpAppend_(db.runtime,'Users',[{userId:cfg.userId,displayName:'Pilot owner',locale:'ru',
        status:'active',createdAt:now,updatedAt:now}]);
      var rows=ualpAppend_(db.runtime,'AssessmentRuns',[{assessmentRunId:runId,userId:cfg.userId,
        assessmentFormId:form.assessmentFormId,formKey:form.formKey,formVersion:form.formVersion,
        locale:form.locale,status:'STARTED',startedAt:now,algorithmVersion:'',
        clientStartRequestId:requestId,contentSchemaVersion:form.contentSchemaVersion,createdAt:now,updatedAt:now}]);
      ualpAppend_(db.runtime,'EntityRowIndex',[{entityType:'AssessmentRun',entityId:runId,sheetName:'AssessmentRuns',
        rowNumber:rows[0],updatedAt:now}]);
    }
    var ack={assessmentRunId:runId,status:existing?existing.value.status:'STARTED',form:form};
    if (!old) ualpAppend_(db.runtime,'RequestDedup',[{clientRequestId:requestId,operation:'START',entityType:'AssessmentRun',
      entityId:runId,status:'COMPLETED',responseJson:JSON.stringify(ack),createdAt:now,updatedAt:now}]);
    return ack;
  });
}
function submitAssessment(input) {
  var cfg=ualpConfig_();ualpOwner_(cfg);
  input=input||{};
  var requestId=ualpCheckRequest_(input.clientRequestId);
  var runId=ualpString_(input.assessmentRunId);
  if (!/^RUN-[a-f0-9-]{36}$/i.test(runId)) ualpFail_('UALP_RUN_ID','Invalid run identifier');
  var db=ualpConnect_(cfg),bundle=ualpFormBundle_(db.content);
  var form=ualpSafeFormFromBundle_(bundle,cfg.formKey,'ru');
  var computed=ualpScoringFromBundle_(bundle,form,input.responses);
  var now=ualpNow_();
  ualpEnsureRuntime_(db.runtime);
  return ualpWithLock_(function(){
    var old=ualpDedup_(db.runtime,requestId,'SUBMIT');
    if (old) {
      if (!ualpSame_(old.value.entityId,runId)) ualpFail_('UALP_REQUEST_COLLISION','Request belongs to another run');
      if (ualpSame_(old.value.status,'COMPLETED')) return JSON.parse(old.value.responseJson);
    }
    var rec=ualpFindRun_(db.runtime,runId);
    if (!rec || !ualpSame_(rec.value.userId,cfg.userId)) ualpFail_('UALP_RUN_NOT_FOUND','Unknown run or owner');
    if (!ualpSame_(rec.value.assessmentFormId,form.assessmentFormId)
        || !ualpSame_(rec.value.formVersion,form.formVersion)) ualpFail_('UALP_VERSION_CHANGED','Run uses another form version');
    if (ualpSame_(rec.value.status,'COMPLETED')) {
      var previous=ualpReadStoredScores_(db.runtime,runId,bundle);
      if (previous.length !== computed.scores.length) ualpFail_('UALP_INCOMPLETE_COMMIT','Stored score count mismatch');
      return ualpPublicResult_(runId,previous);
    }
    if (!ualpSame_(rec.value.status,'STARTED') && !ualpSame_(rec.value.status,'SUBMITTING')) {
      ualpFail_('UALP_RUN_STATE','Run is not open for submission');
    }
    if (ualpSame_(rec.value.status,'SUBMITTING')
        && !ualpSame_(rec.value.clientSubmitRequestId,requestId)) ualpFail_('UALP_RUN_BUSY','Another submission is in progress');
    if (ualpSame_(rec.value.status,'STARTED')) {
      ualpUpdateRuntimeRow_(db.runtime,'AssessmentRuns',rec.row,
        {status:'SUBMITTING',clientSubmitRequestId:requestId,algorithmVersion:computed.algorithmVersion,updatedAt:now});
    }
    var existingResponses=ualpFindAllRuntime_(db.runtime,'Responses','assessmentRunId',runId);
    var responseMap={};existingResponses.forEach(function(x){
      if (responseMap[x.value.itemId]) ualpFail_('UALP_DUPLICATE_PERSISTED_RESPONSE','Duplicate persisted response');
      responseMap[x.value.itemId]=x.value;
    });
    var newResponses=[];
    computed.responses.forEach(function(r){
      var prior=responseMap[r.itemId];
      if (prior) {
        if (!ualpSame_(prior.responseOptionId, r.optionType==='RESPONSE_OPTION'?r.optionId:'')
            || !ualpSame_(prior.itemOptionId,r.optionType==='ITEM_OPTION'?r.optionId:'')) {
          ualpFail_('UALP_RETRY_MISMATCH','Existing response does not match retry');
        }
      } else {
        newResponses.push({responseId:ualpId_('RESP'),assessmentRunId:runId,itemId:r.itemId,
          responseOptionId:r.optionType==='RESPONSE_OPTION'?r.optionId:'',
          itemOptionId:r.optionType==='ITEM_OPTION'?r.optionId:'',
          responseValue:'',answeredAt:now,createdAt:now});
      }
    });
    ualpAppend_(db.runtime,'Responses',newResponses);
    var existingScores=ualpFindAllRuntime_(db.runtime,'ScaleScores','assessmentRunId',runId);
    var scoreMap={};existingScores.forEach(function(x){
      if (scoreMap[x.value.scaleId]) ualpFail_('UALP_DUPLICATE_PERSISTED_SCORE','Duplicate persisted score');
      scoreMap[x.value.scaleId]=x.value;
    });
    var newScores=[];
    computed.scores.forEach(function(s){
      var prior=scoreMap[s.scaleId];
      if (prior) {
        if (Math.abs(Number(prior.rawScore)-s.rawScore)>1e-7
            || !ualpSame_(prior.algorithmVersion,s.algorithmVersion)) ualpFail_('UALP_RETRY_SCORE_MISMATCH','Persisted score differs');
      } else {
        newScores.push({scaleScoreId:ualpId_('SCORE'),assessmentRunId:runId,scaleId:s.scaleId,
          rawScore:s.rawScore,answeredItems:s.answeredItems,expectedItems:s.expectedItems,
          algorithmVersion:s.algorithmVersion,createdAt:now});
      }
    });
    ualpAppend_(db.runtime,'ScaleScores',newScores);
    ualpUpdateRuntimeRow_(db.runtime,'AssessmentRuns',rec.row,{status:'COMPLETED',submittedAt:now,
      algorithmVersion:computed.algorithmVersion,updatedAt:now});
    var result=ualpPublicResult_(runId,computed.scores);
    if (!old) ualpAppend_(db.runtime,'RequestDedup',[{clientRequestId:requestId,operation:'SUBMIT',
      entityType:'AssessmentRun',entityId:runId,status:'COMPLETED',responseJson:JSON.stringify(result),
      createdAt:now,updatedAt:now}]);
    return result;
  });
}
function ualpDiagnostics() {
  var cfg=ualpConfig_();ualpOwner_(cfg);
  var db=ualpConnect_(cfg);
  var missing=[];
  Object.keys(UALP_RUNTIME_HEADERS).forEach(function(n){
    try { ualpRuntimeSheet_(db.runtime,n); } catch(e) { missing.push(n); }
  });
  return {appVersion:UALP_APP_VERSION,environment:'TEST',runtimeTablesOk:missing.length===0,
    missingOrDriftedRuntimeTables:missing,contentDbIsSeparate:cfg.contentId!==cfg.runtimeId,
    enabledFormKey:cfg.formKey,prodConfigured:false};
}
function doGet() {
  var cfg=ualpConfig_();ualpOwner_(cfg);
  return HtmlService.createHtmlOutputFromFile('Index').setTitle('UALP — закрытый TEST');
}
