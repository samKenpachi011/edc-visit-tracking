[![Build Status](https://travis-ci.org/botswana-harvard/edc-visit-tracking.svg?branch=develop)](https://travis-ci.org/botswana-harvard/edc-visit-tracking) [![Coverage Status](https://coveralls.io/repos/botswana-harvard/edc-visit-tracking/badge.svg?branch=develop&service=github)](https://coveralls.io/github/botswana-harvard/edc-visit-tracking?branch=develop)

# edc-visit-tracking

Track study participant visits


### Declaring a visit model

There are variations on how to do this but a typical example for a subject that requires ICF would look like this:

    from edc_base.audit_trail import AuditTrail
    from edc_base.model.models import BaseUuidModel
    from edc_consent.models import RequiresConsentMixin
    from edc_meta_data.models import CrfMetaDataMixin
    from edc_offstudy.models import OffStudyMixin
    from edc_sync.models import SyncModelMixin
    from edc_visit_tracking.constants import VISIT_REASON_NO_FOLLOW_UP_CHOICES
    from edc_visit_tracking.models import VisitModelMixin, PreviousVisitMixin, CaretakerFieldsMixin
    
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

### Declaring a CRF

    from edc_meta_data.managers import CrfMetaDataManager
    from edc_base.audit_trail import AuditTrail
    from edc_base.model.models import BaseUuidModel
    from edc_consent.models import RequiresConsentMixin
    from edc_offstudy.models import OffStudyMixin
    from edc_sync.models import SyncModelMixin
    from edc_visit_tracking.managers import CrfModelManager
    from edc_visit_tracking.models import CrfModelMixin

    class MyCrfModel(CrfModelMixin, SyncModelMixin, OffStudyMixin,
                       RequiresConsentMixin, BaseUuidModel
    
        consent_model = SubjectConsent
        off_study_model = ('my_app', 'SubjectOffStudy')
        subject_visit = models.OneToOneField(SubjectVisit)

        question_one = models.CharField(
            max_lenght-10)
        question_two = models.CharField(
            max_lenght-10)
        question_three = models.CharField(
            max_lenght-10)
        ...
        objects = CrfModelManager()
        history = AuditTrail()
        entry_meta_data_manager = CrfMetaDataManager(MaternalVisit)
    
        def natural_key(self):
            return (self.subject_visit.natural_key(), )
        natural_key.dependencies = ['my_app.subject_visit']
    
        def __str__(self):
            return str(self.get_visit())

        class Meta:
            app_label = 'my_app'

### Declaring forms:

The `VisitFormMixin` includes a number of common validations in the `clean` method:

    class SubjectVisitForm(VisitFormMixin, forms.ModelForm):
    
        class Meta:
            model = SubjectVisit

## `CrfModelMixin`

The `CrfModelMixin` is required for all CRF models. CRF models have a key to the visit model.

## `PreviousVisitMixin`

The `PreviousVisitMixin` ensures that visits are entered in sequence.
