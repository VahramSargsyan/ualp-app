// FILE: AssessmentService.gs
// APP_VERSION: 0.1.0-dev

function startAssessment(input) {
  resetUalpRequestContext_();
  input = input || {};
  var formKey = String(input.formKey || '');
  var locale = String(input.locale || UALP_APP.DEFAULT_LOCALE);
  var userId = String(input.userId || '');
  var clientRequestId = String(input.clientRequestId || '');
  if (!formKey || !userId || !clientRequestId) throw ualpError_('START_INPUT_INVALID', 'formKey, userId and clientRequestId are required.');
  var payload = buildAssessmentFormPayload_(formKey, locale);

  var lock = LockService.getScriptLock();
  lock.waitLock(10000);
  try {
    var dedup = findDedup_(clientRequestId, 'START_ASSESSMENT');
    if (dedup) return JSON.parse(String(dedup.responseJson));
    ensureAnonymousUser_(userId, locale);
    var runId = 'RUN-' + Utilities.getUuid();
    var now = new Date();
    var run = {
      assessmentRunId: runId,
      userId: userId,
      assessmentFormId: payload.form.assessmentFormId,
      formKey: payload.form.formKey,
      formVersion: payload.form.formVersion,
      locale: locale,
      status: 'STARTED',
      startedAt: now,
      submittedAt: '',
      algorithmVersion: '',
      clientStartRequestId: clientRequestId,
      clientSubmitRequestId: '',
      contentSchemaVersion: 'UALP-ASSESSMENT-LIBRARY-SCHEMA-v0.4',
      createdAt: now,
      updatedAt: now
    };
    appendIndexedRecord_('AssessmentRuns', run, 'ASSESSMENT_RUN', runId);
    var response = { assessmentRunId: runId, form: payload.form, questions: payload.questions, app: payload.app };
    appendDedup_(clientRequestId, 'START_ASSESSMENT', 'ASSESSMENT_RUN', runId, response);
    return response;
  } finally {
    lock.releaseLock();
  }
}

function submitAssessment(input) {
  resetUalpRequestContext_();
  input = input || {};
  var runId = String(input.assessmentRunId || '');
  var clientRequestId = String(input.clientRequestId || '');
  var responses = input.responses || [];
  if (!runId || !clientRequestId || !Array.isArray(responses)) throw ualpError_('SUBMIT_INPUT_INVALID', 'assessmentRunId, clientRequestId and responses[] are required.');

  var found = findRowByIndexedId_('AssessmentRuns', 'assessmentRunId', runId, 'ASSESSMENT_RUN');
  if (!found) throw ualpError_('RUN_NOT_FOUND', 'Assessment run not found.', { assessmentRunId: runId });
  var run = found.record;
  if (String(run.status) === 'CANCELLED') throw ualpError_('RUN_CANCELLED', 'Assessment run is cancelled.');
  if (String(run.status) === 'COMPLETED') {
    var existingDedup = findDedup_(clientRequestId, 'SUBMIT_ASSESSMENT');
    if (existingDedup) return JSON.parse(String(existingDedup.responseJson));
    return rebuildCompletedResult_(runId, String(run.locale || UALP_APP.DEFAULT_LOCALE));
  }

  // Compute before mutation. Correct-answer material remains server-side.
  var scores = scoreAssessmentForm_(String(run.assessmentFormId), responses);
  var clientScores = enrichScoresForClient_(scores, String(run.locale || UALP_APP.DEFAULT_LOCALE));
  var result = { assessmentRunId: runId, status: 'COMPLETED', scores: clientScores, exploratory: true };

  var lock = LockService.getScriptLock();
  lock.waitLock(10000);
  try {
    var dedup = findDedup_(clientRequestId, 'SUBMIT_ASSESSMENT');
    if (dedup) return JSON.parse(String(dedup.responseJson));

    var fresh = findRowByIndexedId_('AssessmentRuns', 'assessmentRunId', runId, 'ASSESSMENT_RUN');
    if (!fresh) throw ualpError_('RUN_NOT_FOUND_AFTER_LOCK', 'Assessment run disappeared during submit.');
    if (String(fresh.record.status) === 'COMPLETED') throw ualpError_('RUN_ALREADY_COMPLETED_DIFFERENT_REQUEST', 'Run was completed by another request.');

    updateIndexedRecord_('AssessmentRuns','assessmentRunId',runId,'ASSESSMENT_RUN',{status:'SUBMITTING',clientSubmitRequestId:clientRequestId,updatedAt:new Date()});

    // Repair-aware: on retry after a partial write, append only missing item/scale records.
    var existingResponses = existingRowsForRun_('Responses', runId);
    var existingItemIds = {}; existingResponses.forEach(function(x){ existingItemIds[String(x.itemId)] = true; });
    var responseRows = responses.filter(function(x){ return !existingItemIds[String(x.itemId)]; }).map(function(x){
      return {
        responseId: 'RESP-' + Utilities.getUuid(), assessmentRunId: runId, itemId: String(x.itemId),
        responseOptionId: x.responseOptionId ? String(x.responseOptionId) : '', itemOptionId: x.itemOptionId ? String(x.itemOptionId) : '',
        responseValue: '', answeredAt: new Date(), createdAt: new Date()
      };
    });
    appendRowsByHeader_('Responses', responseRows);

    var existingScores = existingRowsForRun_('ScaleScores', runId);
    var existingScaleIds = {}; existingScores.forEach(function(x){ existingScaleIds[String(x.scaleId)] = true; });
    var scoreRows = scores.filter(function(x){ return !existingScaleIds[String(x.scaleId)]; }).map(function(x){
      return {
        scaleScoreId: 'SCORE-' + Utilities.getUuid(), assessmentRunId: runId, scaleId: String(x.scaleId), rawScore: x.rawScore,
        answeredItems: x.answeredItems, expectedItems: x.expectedItems, algorithmVersion: x.algorithmVersion, createdAt: new Date()
      };
    });
    appendRowsByHeader_('ScaleScores', scoreRows);

    var algorithmVersions = {};
    scores.forEach(function(x){ if (x.algorithmVersion) algorithmVersions[x.algorithmVersion]=true; });
    updateIndexedRecord_('AssessmentRuns','assessmentRunId',runId,'ASSESSMENT_RUN',{
      status:'COMPLETED', submittedAt:new Date(), algorithmVersion:Object.keys(algorithmVersions).sort().join(';'), clientSubmitRequestId:clientRequestId, updatedAt:new Date()
    });
    appendDedup_(clientRequestId,'SUBMIT_ASSESSMENT','ASSESSMENT_RUN',runId,result);
    return result;
  } catch (e) {
    logRuntimeError_('submitAssessment', e, { assessmentRunId: runId, clientRequestId: clientRequestId });
    throw e;
  } finally {
    lock.releaseLock();
  }
}

function rebuildCompletedResult_(runId, locale) {
  var rows = existingRowsForRun_('ScaleScores', runId);
  if (!rows.length) throw ualpError_('COMPLETED_RUN_SCORES_MISSING', 'Completed run has no persisted ScaleScores.', { assessmentRunId: runId });
  var scores = rows.map(function(x) {
    return { scaleId: String(x.scaleId), rawScore: Number(x.rawScore), answeredItems: Number(x.answeredItems), expectedItems: Number(x.expectedItems), algorithmVersion: String(x.algorithmVersion || '') };
  });
  return { assessmentRunId: runId, status: 'COMPLETED', scores: enrichScoresForClient_(scores, locale), exploratory: true };
}
