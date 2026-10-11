// FILE: ScoringCore.gs
// APP_VERSION: 0.1.0-dev

function computeScaleScores_(input) {
  var responses = input.responses || [];
  var formItems = input.formItems || [];
  var responseOptionsById = input.responseOptionsById || {};
  var itemOptionsById = input.itemOptionsById || {};
  var scaleLinks = input.scaleLinks || [];
  var scoringRules = input.scoringRules || [];

  validateCompleteResponses_(formItems, responses);

  var responseByItem = {};
  responses.forEach(function(r) {
    var itemId = String(r.itemId || '');
    if (!itemId) throw ualpError_('RESPONSE_ITEM_MISSING', 'Response itemId is required.');
    if (responseByItem[itemId]) throw ualpError_('RESPONSE_DUPLICATE_ITEM', 'Only one response per item is allowed.', { itemId: itemId });
    responseByItem[itemId] = r;
  });

  var itemScoreById = {};
  Object.keys(responseByItem).forEach(function(itemId) {
    itemScoreById[itemId] = resolveItemScore_(responseByItem[itemId], responseOptionsById, itemOptionsById);
  });

  var linksByScale = groupBy_(scaleLinks, 'scaleId');
  return scoringRules.map(function(rule) {
    var scaleId = String(rule.scaleId);
    var links = (linksByScale[scaleId] || []).filter(function(link) {
      return Object.prototype.hasOwnProperty.call(responseByItem, String(link.itemId));
    });
    var expectedLinks = linksByScale[scaleId] || [];
    var minAnswered = Number(rule.minAnsweredItems || expectedLinks.length || 0);
    var minPct = Number(rule.minCompletionPct || 100);
    var completionPct = expectedLinks.length ? (links.length / expectedLinks.length) * 100 : 0;
    if (links.length < minAnswered || completionPct + 1e-9 < minPct) {
      throw ualpError_('SCALE_INCOMPLETE', 'Scale does not meet completion requirements.', {
        scaleId: scaleId,
        answered: links.length,
        expected: expectedLinks.length,
        minAnswered: minAnswered,
        minCompletionPct: minPct
      });
    }

    var contributions = links.map(function(link) {
      var direction = String(link.direction || 'POSITIVE').toUpperCase();
      if (direction !== 'POSITIVE') throw ualpError_('SCORING_DIRECTION_UNSUPPORTED', 'Only POSITIVE direction is supported in MVP.', { scaleId: scaleId, direction: direction });
      var weight = numberOrNull_(link.weight);
      if (weight === null) weight = 1;
      return itemScoreById[String(link.itemId)] * weight;
    });

    var method = String(rule.aggregationMethod || '').toUpperCase();
    var rawScore;
    if (method === 'SUM') rawScore = contributions.reduce(function(a, b) { return a + b; }, 0);
    else if (method === 'MEAN') rawScore = contributions.reduce(function(a, b) { return a + b; }, 0) / contributions.length;
    else throw ualpError_('SCORING_METHOD_UNSUPPORTED', 'Unsupported aggregation method: ' + method, { scaleId: scaleId });

    rawScore = roundScore_(rawScore);
    var rawMin = numberOrNull_(rule.rawMin);
    var rawMax = numberOrNull_(rule.rawMax);
    if (rawMin !== null && rawScore < rawMin - 1e-9) throw ualpError_('SCORE_BELOW_RANGE', 'Score below configured range.', { scaleId: scaleId, rawScore: rawScore, rawMin: rawMin });
    if (rawMax !== null && rawScore > rawMax + 1e-9) throw ualpError_('SCORE_ABOVE_RANGE', 'Score above configured range.', { scaleId: scaleId, rawScore: rawScore, rawMax: rawMax });

    return {
      scaleId: scaleId,
      rawScore: rawScore,
      answeredItems: links.length,
      expectedItems: expectedLinks.length,
      algorithmVersion: String(rule.algorithmVersion || '')
    };
  });
}

function resolveItemScore_(response, responseOptionsById, itemOptionsById) {
  if (response.responseOptionId) {
    var ro = responseOptionsById[String(response.responseOptionId)];
    if (!ro) throw ualpError_('RESPONSE_OPTION_INVALID', 'Unknown responseOptionId.', { responseOptionId: response.responseOptionId });
    var rv = numberOrNull_(ro.scoreValue);
    if (rv === null) throw ualpError_('RESPONSE_OPTION_SCORE_MISSING', 'Response option has no scoreValue.');
    return rv;
  }
  if (response.itemOptionId) {
    var io = itemOptionsById[String(response.itemOptionId)];
    if (!io) throw ualpError_('ITEM_OPTION_INVALID', 'Unknown itemOptionId.', { itemOptionId: response.itemOptionId });
    var iv = numberOrNull_(io.scoreValue);
    if (iv === null) throw ualpError_('ITEM_OPTION_SCORE_MISSING', 'Item option has no scoreValue.');
    return iv;
  }
  throw ualpError_('RESPONSE_VALUE_MISSING', 'Each response must select a responseOptionId or itemOptionId.');
}

function validateCompleteResponses_(formItems, responses) {
  var requiredIds = (formItems || []).filter(function(x) { return truthyCell_(x.required); }).map(function(x) { return String(x.itemId); });
  var submittedIds = {};
  (responses || []).forEach(function(x) { submittedIds[String(x.itemId)] = true; });
  var missing = requiredIds.filter(function(id) { return !submittedIds[id]; });
  if (missing.length) throw ualpError_('FORM_INCOMPLETE', 'All required items must be answered.', { missingItemIds: missing });
}

function roundScore_(n) { return Math.round((n + Number.EPSILON) * 1000000) / 1000000; }
