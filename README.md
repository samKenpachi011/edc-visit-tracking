[![Build Status](https://app.travis-ci.com/samKenpachi011/edc-visit-tracking.svg?branch=develop)](https://app.travis-ci.com/samKenpachi011/edc-visit-tracking)

[![Coverage Status](https://coveralls.io/repos/github/samKenpachi011/edc-visit-tracking/badge.svg?branch=develop)](https://coveralls.io/github/samKenpachi011/edc-visit-tracking?branch=develop)


[![Language](https://img.shields.io/badge/Language-Python-blue.svg)](https://www.python.org/)
[![License](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Version](https://img.shields.io/badge/Version-1.0.0-blue.svg)](https://github.com/samKenpachi011/edc-visit-tracking/releases/tag/v1.0.0)
[![Log Scan Status](https://img.shields.io/badge/Log%20Scan-Passing-brightgreen.svg)](https://app.travis-ci.com/github/samKenpachi011/edc-visit-tracking/logscans)

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
