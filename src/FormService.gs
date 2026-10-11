// FILE: FormService.gs
// APP_VERSION: 0.1.0-dev

function getAssessmentForm(formKey, locale) {
  resetUalpRequestContext_();
  return buildAssessmentFormPayload_(String(formKey || ''), locale || UALP_APP.DEFAULT_LOCALE);
}

function buildAssessmentFormPayload_(formKey, locale) {
  var ss = getContentSpreadsheet_();
  var forms = tableByName_(ss, 'AssessmentForms');
  var form = forms.find(function(x) { return String(x.formKey) === formKey; });
  if (!form) throw ualpError_('FORM_NOT_FOUND', 'Unknown assessment form: ' + formKey);

  var formItems = tableByName_(ss, 'AssessmentFormItems')
    .filter(function(x) { return String(x.assessmentFormId) === String(form.assessmentFormId); })
    .sort(function(a, b) { return Number(a.displayOrder) - Number(b.displayOrder); });

  if (formItems.length !== Number(form.itemCount)) {
    throw ualpError_('FORM_ITEM_COUNT_MISMATCH', 'Assessment form membership does not match declared itemCount.', {
      formKey: formKey,
      declared: Number(form.itemCount),
      actual: formItems.length
    });
  }

  var itemsById = indexBy_(tableByName_(ss, 'Items'), 'itemId');
  var itemTranslations = groupBy_(tableByName_(ss, 'ItemTranslations'), 'itemId');
  var responseOptionsBySet = groupBy_(tableByName_(ss, 'ResponseOptions'), 'responseSetId');
  var responseOptionTranslations = groupBy_(tableByName_(ss, 'ResponseOptionTranslations'), 'responseOptionId');
  var itemOptionsByItem = groupBy_(tableByName_(ss, 'ItemOptions'), 'itemId');
  var itemOptionTranslations = groupBy_(tableByName_(ss, 'ItemOptionTranslations'), 'itemOptionId');
  var entityTranslations = tableByName_(ss, 'EntityTranslations');
  var assetsById = indexBy_(tableByName_(ss, 'Assets'), 'assetId');
  var itemAssetsByItem = groupBy_(tableByName_(ss, 'ItemAssets'), 'itemId');

  var formTr = findEntityTranslation_(entityTranslations, 'ASSESSMENT_FORM', String(form.assessmentFormId), locale);
  var questions = formItems.map(function(fi) {
    var item = itemsById[String(fi.itemId)];
    if (!item) throw ualpError_('FORM_ITEM_MISSING', 'Form references unknown item.', { itemId: fi.itemId });
    var responseSetId = String(fi.responseSetOverrideId || item.responseSetId || form.defaultResponseSetId || '');
    return buildPublicQuestion_({
      item: item,
      formItem: fi,
      locale: locale,
      itemTranslations: itemTranslations[String(item.itemId)] || [],
      responseOptions: responseOptionsBySet[responseSetId] || [],
      responseOptionTranslations: responseOptionTranslations,
      itemOptions: itemOptionsByItem[String(item.itemId)] || [],
      itemOptionTranslations: itemOptionTranslations,
      itemAssets: itemAssetsByItem[String(item.itemId)] || [],
      assetsById: assetsById
    });
  });

  return {
    app: { name: UALP_APP.NAME, version: UALP_APP.VERSION, buildDate: UALP_APP.BUILD_DATE, environment: getUalpEnvironment_() },
    form: {
      assessmentFormId: String(form.assessmentFormId),
      assessmentId: String(form.assessmentId),
      formKey: String(form.formKey),
      formVersion: String(form.formVersion),
      name: formTr && formTr.name ? String(formTr.name) : String(form.name),
      instructions: formTr && formTr.instructionsText ? String(formTr.instructionsText) : '',
      itemCount: Number(form.itemCount),
      locale: locale,
      originalLanguage: String(form.originalLanguage || ''),
      validationStatus: String(form.validationStatus || ''),
      exploratory: String(form.recordStatus || '').toUpperCase() !== 'RELEASED' || String(form.validationStatus || '').toUpperCase() !== 'VALIDATED'
    },
    questions: questions
  };
}

function buildPublicQuestion_(ctx) {
  var item = ctx.item;
  var tr = findLocaleRow_(ctx.itemTranslations, ctx.locale, 'locale');
  var prompt = tr && tr.promptText ? String(tr.promptText) : String(item.canonicalPrompt || '');
  var localizationFallback = !(tr && tr.promptText);
  if (!prompt) {
    throw ualpError_('PROMPT_UNAVAILABLE', 'No prompt is available for requested locale or canonical fallback.', { itemId: item.itemId, locale: ctx.locale });
  }

  var itemSpecific = (ctx.itemOptions || []).length > 0;
  var options = itemSpecific
    ? ctx.itemOptions.slice().sort(byDisplayOrder_).map(function(opt) {
        var otr = findLocaleRow_(ctx.itemOptionTranslations[String(opt.itemOptionId)] || [], ctx.locale, 'locale');
        return {
          itemOptionId: String(opt.itemOptionId),
          optionKey: String(opt.optionKey),
          label: otr && otr.optionText ? String(otr.optionText) : String(opt.optionText || opt.optionKey)
        };
      })
    : (ctx.responseOptions || []).slice().sort(byDisplayOrder_).map(function(opt) {
        var otr = findLocaleRow_(ctx.responseOptionTranslations[String(opt.responseOptionId)] || [], ctx.locale, 'locale');
        return {
          responseOptionId: String(opt.responseOptionId),
          optionKey: String(opt.optionKey),
          label: otr && (otr.label || otr.optionText) ? String(otr.label || otr.optionText) : humanizeOptionKey_(String(opt.optionKey))
        };
      });

  var assets = (ctx.itemAssets || []).slice().sort(byDisplayOrder_).map(function(link) {
    var asset = ctx.assetsById[String(link.assetId)];
    if (!asset) return null;
    return { assetId: String(asset.assetId), role: String(link.assetRole || ''), uri: String(asset.uri || ''), mimeType: String(asset.mimeType || '') };
  }).filter(Boolean);

  // Deliberately whitelist safe fields. Do not spread source rows here.
  return {
    itemId: String(item.itemId),
    displayOrder: Number(ctx.formItem.displayOrder),
    itemType: String(item.itemType),
    required: truthyCell_(ctx.formItem.required),
    prompt: prompt,
    localizationFallback: localizationFallback,
    answerKind: itemSpecific ? 'ITEM_OPTION' : 'RESPONSE_OPTION',
    options: options,
    assets: assets
  };
}

function findLocaleRow_(rows, locale, localeField) {
  return (rows || []).find(function(x) { return String(x[localeField] || '') === String(locale); }) || null;
}

function findEntityTranslation_(rows, entityType, entityId, locale) {
  return (rows || []).find(function(x) {
    return String(x.entityType) === entityType && String(x.entityId) === entityId && String(x.locale) === String(locale);
  }) || null;
}

function byDisplayOrder_(a, b) { return Number(a.displayOrder) - Number(b.displayOrder); }

function humanizeOptionKey_(key) {
  return key.toLowerCase().split('_').map(function(x) { return x ? x.charAt(0).toUpperCase() + x.slice(1) : x; }).join(' ');
}
