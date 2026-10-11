// FILE: Code.gs
// APP_VERSION: 0.1.0-dev
// BUILD_DATE: 2026-10-11

function doGet() {
  return HtmlService.createTemplateFromFile('Index')
    .evaluate()
    .setTitle('UALP')
    .setXFrameOptionsMode(HtmlService.XFrameOptionsMode.DEFAULT);
}

function getRuntimeStatus() {
  return { appName: UALP_APP.NAME, appVersion: UALP_APP.VERSION, buildDate: UALP_APP.BUILD_DATE, environment: getUalpEnvironment_() };
}
