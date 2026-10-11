// FILE: ScoringService.gs
// APP_VERSION: 0.1.0-dev

function scoreAssessmentForm_(assessmentFormId, responses) {
  var ss = getContentSpreadsheet_();
  var formItems = tableByName_(ss, 'AssessmentFormItems').filter(function(x) { return String(x.assessmentFormId) === String(assessmentFormId); });
  var scoringRules = tableByName_(ss, 'FormScoringRules').filter(function(x) { return String(x.assessmentFormId) === String(assessmentFormId); });
  if (!scoringRules.length) throw ualpError_('SCORING_RULES_MISSING', 'No FormScoringRules found for form.', { assessmentFormId: assessmentFormId });
  var formsById = indexBy_(tableByName_(ss, 'AssessmentForms'), 'assessmentFormId');
  var form = formsById[String(assessmentFormId)];
  if (!form) throw ualpError_('FORM_NOT_FOUND', 'Assessment form not found during scoring.', { assessmentFormId: assessmentFormId });
  var itemsById = indexBy_(tableByName_(ss, 'Items'), 'itemId');
  var responseOptionsById = indexBy_(tableByName_(ss, 'ResponseOptions'), 'responseOptionId');
  var itemOptionsById = indexBy_(tableByName_(ss, 'ItemOptions'), 'itemOptionId');
  validateResponseSelections_(form, formItems, responses, itemsById, responseOptionsById, itemOptionsById);

  var scaleIds = {};
  scoringRules.forEach(function(x) { scaleIds[String(x.scaleId)] = true; });
  var itemIds = {};
  formItems.forEach(function(x) { itemIds[String(x.itemId)] = true; });
  var scaleLinks = tableByName_(ss, 'ItemScaleLinks').filter(function(x) { return itemIds[String(x.itemId)] && scaleIds[String(x.scaleId)]; });

  return computeScaleScores_({
    responses: responses,
    formItems: formItems,
    responseOptionsById: responseOptionsById,
    itemOptionsById: itemOptionsById,
    scaleLinks: scaleLinks,
    scoringRules: scoringRules
  });
}

function enrichScoresForClient_(scores, locale) {
  var ss = getContentSpreadsheet_();
  var scales = indexBy_(tableByName_(ss, 'Scales'), 'scaleId');
  var entityTranslations = tableByName_(ss, 'EntityTranslations');
  return scores.map(function(score) {
    var scale = scales[String(score.scaleId)] || {};
    var tr = findEntityTranslation_(entityTranslations, 'SCALE', String(score.scaleId), locale);
    return {
      scaleId: String(score.scaleId),
      scaleKey: String(scale.scaleKey || ''),
      name: tr && tr.name ? String(tr.name) : String(scale.name || score.scaleId),
      rawScore: score.rawScore,
      rawMin: null,
      rawMax: null,
      answeredItems: score.answeredItems,
      expectedItems: score.expectedItems,
      algorithmVersion: score.algorithmVersion
    };
  });
}

function validateResponseSelections_(form, formItems, responses, itemsById, responseOptionsById, itemOptionsById) {
  var formItemByItemId = indexBy_(formItems, 'itemId');
  (responses || []).forEach(function(r) {
    var itemId = String(r.itemId || '');
    var fi = formItemByItemId[itemId];
    if (!fi) throw ualpError_('RESPONSE_ITEM_NOT_IN_FORM', 'Response references an item outside this form.', { itemId: itemId });
    var item = itemsById[itemId];
    if (!item) throw ualpError_('RESPONSE_ITEM_UNKNOWN', 'Response references unknown item.', { itemId: itemId });
    var itemOptionsExist = Object.keys(itemOptionsById).some(function(k) { return String(itemOptionsById[k].itemId) === itemId; });
    if (itemOptionsExist) {
      if (!r.itemOptionId || r.responseOptionId) throw ualpError_('RESPONSE_KIND_INVALID', 'Objective item requires itemOptionId only.', { itemId: itemId });
      var io = itemOptionsById[String(r.itemOptionId)];
      if (!io || String(io.itemId) !== itemId) throw ualpError_('ITEM_OPTION_NOT_ALLOWED', 'Selected item option does not belong to this item.', { itemId: itemId, itemOptionId: r.itemOptionId });
    } else {
      if (!r.responseOptionId || r.itemOptionId) throw ualpError_('RESPONSE_KIND_INVALID', 'Scale-response item requires responseOptionId only.', { itemId: itemId });
      var ro = responseOptionsById[String(r.responseOptionId)];
      var expectedSet = String(fi.responseSetOverrideId || item.responseSetId || form.defaultResponseSetId || '');
      if (!ro || String(ro.responseSetId) !== expectedSet) throw ualpError_('RESPONSE_OPTION_NOT_ALLOWED', 'Selected response option does not belong to the expected response set.', { itemId: itemId, responseOptionId: r.responseOptionId, expectedResponseSetId: expectedSet });
    }
  });
}
