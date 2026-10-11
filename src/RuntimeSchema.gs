// FILE: RuntimeSchema.gs
// APP_VERSION: 0.1.0-dev

var UALP_RUNTIME_SCHEMA_ = Object.freeze({
  Users: ['userId','displayName','locale','status','createdAt','updatedAt'],
  AssessmentRuns: ['assessmentRunId','userId','assessmentFormId','formKey','formVersion','locale','status','startedAt','submittedAt','algorithmVersion','clientStartRequestId','clientSubmitRequestId','contentSchemaVersion','createdAt','updatedAt'],
  Responses: ['responseId','assessmentRunId','itemId','responseOptionId','itemOptionId','responseValue','answeredAt','createdAt'],
  ScaleScores: ['scaleScoreId','assessmentRunId','scaleId','rawScore','answeredItems','expectedItems','algorithmVersion','createdAt'],
  RequestDedup: ['clientRequestId','operation','entityType','entityId','status','responseJson','createdAt','updatedAt'],
  EntityRowIndex: ['entityType','entityId','sheetName','rowNumber','updatedAt'],
  ErrorLog: ['errorId','operation','code','message','contextJson','createdAt'],
  RuntimeSchema: ['schemaKey','schemaVersion','installedAt','environment']
});

function installRuntimeSchema() {
  var env = getUalpEnvironment_();
  if (env === 'PROD') throw ualpError_('PROD_SCHEMA_DIRECT_INSTALL_FORBIDDEN', 'Direct PROD schema installation is forbidden. Use a repository-owned migration path.');
  var ss = getRuntimeSpreadsheet_();
  Object.keys(UALP_RUNTIME_SCHEMA_).forEach(function(sheetName) {
    ensureFreshSchemaSheet_(ss, sheetName, UALP_RUNTIME_SCHEMA_[sheetName]);
  });
  var schemaSheet = ss.getSheetByName('RuntimeSchema');
  if (schemaSheet.getLastRow() === 1) {
    schemaSheet.getRange(2, 1, 1, 4).setValues([['UALP_RUNTIME', UALP_APP.RUNTIME_SCHEMA_VERSION, new Date(), env]]);
  }
  return runDiagnostics();
}

function ensureFreshSchemaSheet_(ss, sheetName, headers) {
  var sheet = ss.getSheetByName(sheetName);
  if (!sheet) sheet = ss.insertSheet(sheetName);
  var lastRow = sheet.getLastRow();
  var lastCol = sheet.getLastColumn();
  if (lastRow === 0 || lastCol === 0) {
    sheet.getRange(1, 1, 1, headers.length).setValues([headers]);
    sheet.setFrozenRows(1);
    return;
  }
  var existing = sheet.getRange(1, 1, 1, Math.max(lastCol, headers.length)).getValues()[0].slice(0, headers.length).map(String);
  if (existing.join('\u001f') !== headers.join('\u001f')) {
    throw ualpError_('RUNTIME_SCHEMA_HEADER_MISMATCH', 'Existing runtime sheet headers differ from expected fresh schema.', { sheetName: sheetName, expected: headers, actual: existing });
  }
}
