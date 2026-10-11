// FILE: Config.gs
// APP_VERSION: 0.1.0-dev
// BUILD_DATE: 2026-10-11

var UALP_APP = Object.freeze({
  NAME: 'UALP',
  VERSION: '0.1.0-dev',
  BUILD_DATE: '2026-10-11',
  RUNTIME_SCHEMA_VERSION: '0.1.0',
  DEFAULT_LOCALE: 'ru',
  CONTENT_MAX_ROWS_PER_TABLE: 5000,
  SCRIPT_PROPERTY_CONTENT_DB_ID: 'UALP_CONTENT_SPREADSHEET_ID',
  SCRIPT_PROPERTY_RUNTIME_DB_ID: 'UALP_RUNTIME_SPREADSHEET_ID',
  SCRIPT_PROPERTY_ENVIRONMENT: 'UALP_ENVIRONMENT'
});

function getUalpEnvironment_() {
  return PropertiesService.getScriptProperties().getProperty(UALP_APP.SCRIPT_PROPERTY_ENVIRONMENT) || 'DEV';
}

function getContentSpreadsheet_() {
  var ctx = typeof ualpContext_ === 'function' ? ualpContext_() : null;
  if (ctx && ctx.contentSpreadsheet) return ctx.contentSpreadsheet;
  var id = PropertiesService.getScriptProperties().getProperty(UALP_APP.SCRIPT_PROPERTY_CONTENT_DB_ID);
  if (!id) throw ualpError_('CONFIG_CONTENT_DB_MISSING', 'UALP content spreadsheet is not configured.');
  var ss = SpreadsheetApp.openById(id);
  if (ctx) ctx.contentSpreadsheet = ss;
  return ss;
}

function getRuntimeSpreadsheet_() {
  var ctx = typeof ualpContext_ === 'function' ? ualpContext_() : null;
  if (ctx && ctx.runtimeSpreadsheet) return ctx.runtimeSpreadsheet;
  var id = PropertiesService.getScriptProperties().getProperty(UALP_APP.SCRIPT_PROPERTY_RUNTIME_DB_ID);
  if (!id) throw ualpError_('CONFIG_RUNTIME_DB_MISSING', 'UALP runtime spreadsheet is not configured.');
  var ss = SpreadsheetApp.openById(id);
  if (ctx) ctx.runtimeSpreadsheet = ss;
  return ss;
}

function configureUalpScript(contentSpreadsheetId, runtimeSpreadsheetId, environment) {
  if (!contentSpreadsheetId || !runtimeSpreadsheetId) {
    throw ualpError_('CONFIG_INVALID', 'Both contentSpreadsheetId and runtimeSpreadsheetId are required.');
  }
  var env = String(environment || 'DEV').toUpperCase();
  if (['DEV', 'TEST', 'STAGING', 'PROD'].indexOf(env) === -1) {
    throw ualpError_('CONFIG_ENV_INVALID', 'Environment must be DEV, TEST, STAGING, or PROD.');
  }
  PropertiesService.getScriptProperties().setProperties({
    UALP_CONTENT_SPREADSHEET_ID: String(contentSpreadsheetId),
    UALP_RUNTIME_SPREADSHEET_ID: String(runtimeSpreadsheetId),
    UALP_ENVIRONMENT: env
  });
  return { ok: true, environment: env };
}
