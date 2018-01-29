[![Build Status](https://travis-ci.org/botswana-harvard/edc-visit-tracking.svg?branch=develop)](https://travis-ci.org/botswana-harvard/edc-visit-tracking) [![Coverage Status](https://coveralls.io/repos/botswana-harvard/edc-visit-tracking/badge.svg?branch=develop&service=github)](https://coveralls.io/github/botswana-harvard/edc-visit-tracking?branch=develop)

# edc-visit-tracking

Track study participant visit reports.


### Declaring a visit model

For a subject that requires ICF would look like this:

    class SubjectVisit(VisitModelMixin, OffstudyMixin, CreatesMetadataModelMixin, RequiresConsentModelMixin, BaseUuidModel):
    
        class Meta(VisitModelMixin.Meta):
            consent_model = 'edc_example.subjectconsent'
            app_label = 'edc_example'


If the subject does not require ICF, such as an infant, just don't include the `RequiresConsentModelMixin`:

    class InfantVisit(VisitModelMixin, OffstudyMixin, CreatesMetadataModelMixin, BaseUuidModel):
    
        class Meta(VisitModelMixin.Meta):
            app_label = 'edc_example'

In both cases a `OneToOneField` attr to `edc_example.Appointment` is added through the `VisitModelMixin` mixin, so `edc_example.Appointment` must exist.

### Declaring a CRF

The `CrfModelMixin` is required for all CRF models. CRF models have a key to the visit model.

    class CrfOne(CrfModelMixin, OffstudyMixin, RequiresConsentModelMixin, UpdatesCrfMetadataModelMixin, BaseUuidModel):
    
        subject_visit = models.OneToOneField(SubjectVisit)
    
        f1 = models.CharField(max_length=10, default='erik')
    
        vl = models.CharField(max_length=10, default=NO)
    
        rdb = models.CharField(max_length=10, default=NO)
    
        class Meta:
            consent_model = 'edc_example.subjectconsent'
            app_label = 'edc_example'
            offstudy_model = 'edc_example.subjectoffstudy'

### Declaring forms:

The `VisitFormMixin` includes a number of common validations in the `clean` method:

    class SubjectVisitForm(VisitFormMixin, forms.ModelForm):
    
        class Meta:
            model = SubjectVisit

### `PreviousVisitModelMixin`

The `PreviousVisitModelMixin` ensures that visits are entered in sequence. It is included with the `VisitModelMixin`.
