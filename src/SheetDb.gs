// FILE: SheetDb.gs
// APP_VERSION: 0.1.0-dev

var UALP_REQUEST_CONTEXT_ = null;

function ualpContext_() {
  if (!UALP_REQUEST_CONTEXT_) UALP_REQUEST_CONTEXT_ = { tables: {} };
  return UALP_REQUEST_CONTEXT_;
}

function resetUalpRequestContext_() {
  UALP_REQUEST_CONTEXT_ = { tables: {} };
}

function readTable_(spreadsheet, sheetName) {
  var key = spreadsheet.getId() + '::' + sheetName;
  var ctx = ualpContext_();
  if (ctx.tables[key]) return ctx.tables[key];

  var sheet = spreadsheet.getSheetByName(sheetName);
  if (!sheet) throw ualpError_('SHEET_MISSING', 'Required sheet is missing: ' + sheetName, { sheetName: sheetName });
  var lastRow = sheet.getLastRow();
  var lastColumn = sheet.getLastColumn();
  if (lastRow < 1 || lastColumn < 1) throw ualpError_('SHEET_EMPTY', 'Required sheet is empty: ' + sheetName);
  var contentId = PropertiesService.getScriptProperties().getProperty(UALP_APP.SCRIPT_PROPERTY_CONTENT_DB_ID);
  if (lastRow > UALP_APP.CONTENT_MAX_ROWS_PER_TABLE && contentId && spreadsheet.getId() === contentId) {
    throw ualpError_('CONTENT_TABLE_BOUND_EXCEEDED', 'Content table exceeded current bounded-read limit.', {
      sheetName: sheetName,
      lastRow: lastRow,
      limit: UALP_APP.CONTENT_MAX_ROWS_PER_TABLE
    });
  }

  var values = sheet.getRange(1, 1, lastRow, lastColumn).getValues();
  var headers = values[0].map(String);
  var rows = values.slice(1).filter(function(row) {
    return row.some(function(v) { return v !== '' && v !== null; });
  }).map(function(row, i) {
    var obj = { __rowNumber: i + 2 };
    headers.forEach(function(h, c) { obj[h] = row[c]; });
    return obj;
  });
  var result = { sheet: sheet, headers: headers, rows: rows };
  ctx.tables[key] = result;
  return result;
}

function tableByName_(spreadsheet, sheetName) {
  return readTable_(spreadsheet, sheetName).rows;
}

function indexBy_(rows, key) {
  var out = {};
  rows.forEach(function(row) {
    var v = String(row[key] || '');
    if (v) out[v] = row;
  });
  return out;
}

function groupBy_(rows, key) {
  var out = {};
  rows.forEach(function(row) {
    var v = String(row[key] || '');
    if (!out[v]) out[v] = [];
    out[v].push(row);
  });
  return out;
}

function truthyCell_(v) {
  if (v === true) return true;
  var s = String(v || '').toUpperCase();
  return s === 'TRUE' || s === '1' || s === 'YES';
}

function numberOrNull_(v) {
  if (v === '' || v === null || typeof v === 'undefined') return null;
  var n = Number(v);
  return isFinite(n) ? n : null;
}

function ualpError_(code, message, context) {
  var e = new Error(message);
  e.ualpCode = code;
  e.ualpContext = context || {};
  return e;
}
