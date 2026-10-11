// FILE: RuntimeRepository.gs
// APP_VERSION: 0.1.0-dev

function ensureAnonymousUser_(userId, locale) {
  var existing = findRowByIndexedId_('Users', 'userId', userId, 'USER');
  if (existing) return existing.record;
  var now = new Date();
  var record = { userId: userId, displayName: '', locale: locale, status: 'ACTIVE', createdAt: now, updatedAt: now };
  appendIndexedRecord_('Users', record, 'USER', userId);
  return record;
}

function appendIndexedRecord_(sheetName, record, entityType, entityId) {
  var ss = getRuntimeSpreadsheet_();
  var table = readRuntimeHeaders_(ss, sheetName);
  var values = table.headers.map(function(h) { return Object.prototype.hasOwnProperty.call(record, h) ? record[h] : ''; });
  var rowNumber = table.sheet.getLastRow() + 1;
  table.sheet.getRange(rowNumber, 1, 1, values.length).setValues([values]);
  var idx = ss.getSheetByName('EntityRowIndex');
  idx.getRange(idx.getLastRow() + 1, 1, 1, 5).setValues([[entityType, entityId, sheetName, rowNumber, new Date()]]);
  return rowNumber;
}

function readRuntimeHeaders_(ss, sheetName) {
  var sheet = ss.getSheetByName(sheetName);
  if (!sheet) throw ualpError_('RUNTIME_SHEET_MISSING', 'Runtime sheet missing: ' + sheetName);
  var lastCol = sheet.getLastColumn();
  if (lastCol < 1) throw ualpError_('RUNTIME_HEADERS_MISSING', 'Runtime sheet headers missing: ' + sheetName);
  return { sheet: sheet, headers: sheet.getRange(1,1,1,lastCol).getValues()[0].map(String) };
}

function findRowByIndexedId_(sheetName, idColumn, entityId, entityType) {
  var ss = getRuntimeSpreadsheet_();
  var idx = ss.getSheetByName('EntityRowIndex');
  if (!idx) throw ualpError_('RUNTIME_INDEX_MISSING', 'EntityRowIndex sheet missing.');
  var finder = idx.getRange(2, 2, Math.max(idx.getLastRow()-1,1), 1).createTextFinder(String(entityId)).matchEntireCell(true);
  var cell = finder.findNext();
  if (!cell) return null;
  var row = idx.getRange(cell.getRow(), 1, 1, 5).getValues()[0];
  if (String(row[0]) !== String(entityType) || String(row[2]) !== String(sheetName)) return null;
  var rowNumber = Number(row[3]);
  var table = readRuntimeHeaders_(ss, sheetName);
  var values = table.sheet.getRange(rowNumber, 1, 1, table.headers.length).getValues()[0];
  var record = {};
  table.headers.forEach(function(h,i){ record[h] = values[i]; });
  if (String(record[idColumn]) !== String(entityId)) throw ualpError_('RUNTIME_INDEX_STALE', 'EntityRowIndex points to a different ID.', { entityId: entityId, rowNumber: rowNumber });
  return { rowNumber: rowNumber, record: record, headers: table.headers, sheet: table.sheet };
}

function updateIndexedRecord_(sheetName, idColumn, entityId, entityType, patch) {
  var found = findRowByIndexedId_(sheetName, idColumn, entityId, entityType);
  if (!found) throw ualpError_('RUNTIME_RECORD_NOT_FOUND', 'Runtime record not found.', { sheetName: sheetName, entityId: entityId });
  var row = found.headers.map(function(h){ return Object.prototype.hasOwnProperty.call(patch,h) ? patch[h] : found.record[h]; });
  found.sheet.getRange(found.rowNumber,1,1,row.length).setValues([row]);
  return true;
}

function findDedup_(clientRequestId, operation) {
  var ss = getRuntimeSpreadsheet_();
  var sheet = ss.getSheetByName('RequestDedup');
  if (!sheet || sheet.getLastRow() < 2) return null;
  var finder = sheet.getRange(2,1,sheet.getLastRow()-1,1).createTextFinder(String(clientRequestId)).matchEntireCell(true);
  var cells = finder.findAll();
  for (var i=0;i<cells.length;i++) {
    var row = sheet.getRange(cells[i].getRow(),1,1,8).getValues()[0];
    if (String(row[1]) === String(operation)) {
      return { clientRequestId: row[0], operation: row[1], entityType: row[2], entityId: row[3], status: row[4], responseJson: row[5], createdAt: row[6], updatedAt: row[7] };
    }
  }
  return null;
}

function appendDedup_(clientRequestId, operation, entityType, entityId, response) {
  var ss = getRuntimeSpreadsheet_();
  var sheet = ss.getSheetByName('RequestDedup');
  var now = new Date();
  sheet.getRange(sheet.getLastRow()+1,1,1,8).setValues([[clientRequestId, operation, entityType, entityId, 'COMPLETED', JSON.stringify(response), now, now]]);
}

function appendRowsByHeader_(sheetName, records) {
  if (!records.length) return;
  var ss = getRuntimeSpreadsheet_();
  var table = readRuntimeHeaders_(ss, sheetName);
  var matrix = records.map(function(record){ return table.headers.map(function(h){ return Object.prototype.hasOwnProperty.call(record,h) ? record[h] : ''; }); });
  table.sheet.getRange(table.sheet.getLastRow()+1,1,matrix.length,table.headers.length).setValues(matrix);
}

function existingRowsForRun_(sheetName, runId) {
  var ss = getRuntimeSpreadsheet_();
  var sheet = ss.getSheetByName(sheetName);
  if (!sheet || sheet.getLastRow() < 2) return [];
  var headers = sheet.getRange(1,1,1,sheet.getLastColumn()).getValues()[0].map(String);
  var runCol = headers.indexOf('assessmentRunId') + 1;
  if (!runCol) return [];
  var cells = sheet.getRange(2,runCol,sheet.getLastRow()-1,1).createTextFinder(String(runId)).matchEntireCell(true).findAll();
  return cells.map(function(cell){
    var vals = sheet.getRange(cell.getRow(),1,1,headers.length).getValues()[0];
    var o={}; headers.forEach(function(h,i){o[h]=vals[i];}); return o;
  });
}
