[![Build Status](https://travis-ci.org/botswana-harvard/edc-visit-tracking.svg?branch=develop)](https://travis-ci.org/botswana-harvard/edc-visit-tracking) [![Coverage Status](https://coveralls.io/repos/botswana-harvard/edc-visit-tracking/badge.svg?branch=develop&service=github)](https://coveralls.io/github/botswana-harvard/edc-visit-tracking?branch=develop)

# edc-visit-tracking

Track study participant visits


### Declaring a visit model

There are variations on how to do this but a typical example for a subject that requires ICF would look like this:

    class SubjectVisit(OffStudyMixin, SyncModelMixin, PreviousVisitMixin, CrfMetaDataMixin,
                  RequiresConsentMixin, CaretakerFieldsMixin, VisitModelMixin, BaseUuidModel):
    
        consent_model = SubjectConsent
    
        off_study_model = ('my_app', 'SubjectOffStudy')
    
        death_report_model = ('my_app', 'SubjectDeathReport')
    
        history = AuditTrail()
    
        def get_visit_reason_choices(self):
            return VISIT_REASON
    
        def get_visit_reason_no_follow_up_choices(self):
            """ Returns the visit reasons that do not imply any data
            collection; that is, the subject is not available. """
            dct = {}
            for item in VISIT_REASON_NO_FOLLOW_UP_CHOICES:
                dct.update({item: item})
            return dct
    
        class Meta:
            app_label = 'my_app'

If the subject does not require ICF, such as an infant, any form that has the DOB will do for `consent_model`:

    class InfantVisit(OffStudyMixin, SyncModelMixin, PreviousVisitMixin, CrfMetaDataMixin,
                  RequiresConsentMixin, CaretakerFieldsMixin, VisitModelMixin, BaseUuidModel):
    
        consent_model = InfantBirthModel
    
        off_study_model = ('my_app', 'InfantOffStudy')
    
        death_report_model = ('my_app', 'InfantDeathReport')
    
        history = AuditTrail()
    
        def get_visit_reason_choices(self):
            return VISIT_REASON
    
        def get_visit_reason_no_follow_up_choices(self):
            """ Returns the visit reasons that do not imply any data
            collection; that is, the subject is not available. """
            dct = {}
            for item in VISIT_REASON_NO_FOLLOW_UP_CHOICES:
                dct.update({item: item})
            return dct
    
        class Meta:
            app_label = 'my_app'

            
## Declaring forms:
    
The `VisitFormMixin` includes a number of common validations in the `clean` method:

    class SubjectVisitForm(VisitFormMixin, forms.ModelForm):
    
        class Meta:
            model = SubjectVisit

## `CrfModelMixin`

The `CrfModelMixin` is required for all CRF models. CRF models have a key to the visit model.

## `PreviousVisitMixin`

The `PreviousVisitMixin` ensures that visits are entered in sequence.