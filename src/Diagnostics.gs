// FILE: Diagnostics.gs
// APP_VERSION: 0.1.0-dev

function runDiagnostics() {
  var result = { appVersion: UALP_APP.VERSION, buildDate: UALP_APP.BUILD_DATE, environment: getUalpEnvironment_(), checks: [], ok: true };
  try {
    var content = getContentSpreadsheet_();
    ['AssessmentForms','AssessmentFormItems','Items','FormScoringRules','ItemScaleLinks'].forEach(function(name){
      var s=content.getSheetByName(name); var ok=!!s; result.checks.push({check:'content_sheet',name:name,ok:ok}); if(!ok) result.ok=false;
    });
  } catch(e) { result.ok=false; result.checks.push({check:'content_db',ok:false,code:e.ualpCode||'ERROR',message:e.message}); }
  try {
    var runtime = getRuntimeSpreadsheet_();
    Object.keys(UALP_RUNTIME_SCHEMA_).forEach(function(name){
      var s=runtime.getSheetByName(name); var ok=!!s; result.checks.push({check:'runtime_sheet',name:name,ok:ok}); if(!ok) result.ok=false;
    });
  } catch(e2) { result.ok=false; result.checks.push({check:'runtime_db',ok:false,code:e2.ualpCode||'ERROR',message:e2.message}); }
  return result;
}

function logRuntimeError_(operation, error, context) {
  try {
    var ss=getRuntimeSpreadsheet_(); var sheet=ss.getSheetByName('ErrorLog'); if(!sheet) return;
    sheet.getRange(sheet.getLastRow()+1,1,1,6).setValues([['ERR-'+Utilities.getUuid(),operation,String(error.ualpCode||'UNEXPECTED'),String(error.message||error),JSON.stringify(context||{}),new Date()]]);
  } catch(ignore) {}
}
