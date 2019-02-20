from django import forms
from django.core.exceptions import ValidationError
from django.test import TestCase, tag
from edc_appointment.models import Appointment
from edc_base.utils import get_utcnow
from edc_constants.constants import ALIVE, YES, NO, DEAD
from edc_constants.constants import PARTICIPANT
from edc_facility.import_holidays import import_holidays
from edc_visit_schedule.site_visit_schedules import site_visit_schedules

from ..constants import SCHEDULED, MISSED_VISIT
from ..form_validators import VisitFormValidator
from .helper import Helper
from .models import SubjectVisit
from .visit_schedule import visit_schedule1, visit_schedule2


class SubjectVisitForm(forms.ModelForm):

    form_validator_cls = VisitFormValidator

    class Meta:
        model = SubjectVisit
        fields = '__all__'


@tag('sv')
class TestForm(TestCase):

    helper_cls = Helper

    def setUp(self):
        import_holidays()
        self.subject_identifier = '12345'
        self.helper = self.helper_cls(
            subject_identifier=self.subject_identifier)
        site_visit_schedules._registry = {}
        site_visit_schedules.register(visit_schedule=visit_schedule1)
        site_visit_schedules.register(visit_schedule=visit_schedule2)

    def test_form_validator_ok(self):
        self.helper.consent_and_put_on_schedule()
        appointment = Appointment.objects.all()[0]
        subject_visit = SubjectVisit.objects.create(
            appointment=appointment,
            reason=SCHEDULED)
        cleaned_data = dict(
            appointment=appointment,
            reason=SCHEDULED,
            is_present=YES,
            survival_status=ALIVE,
            info_source=PARTICIPANT,
            last_alive_date=get_utcnow().date())
        form_validator = VisitFormValidator(
            cleaned_data=cleaned_data, instance=subject_visit)
        form_validator.validate()

    def test_info_source_invalid(self):
        self.helper.consent_and_put_on_schedule()
        appointment = Appointment.objects.all()[0]
        subject_visit = SubjectVisit.objects.create(
            appointment=appointment,
            reason=SCHEDULED)
        cleaned_data = dict(
            appointment=appointment,
            reason=SCHEDULED,
            info_source=None,
            is_present=YES,
            survival_status=ALIVE,
            last_alive_date=get_utcnow().date())
        form_validator = VisitFormValidator(
            cleaned_data=cleaned_data, instance=subject_visit)
        self.assertRaises(ValidationError, form_validator.validate)
        self.assertIn('info_source', form_validator._errors)

    def test_info_source_valid(self):
        self.helper.consent_and_put_on_schedule()
        appointment = Appointment.objects.all()[0]
        subject_visit = SubjectVisit.objects.create(
            appointment=appointment,
            reason=SCHEDULED)
        cleaned_data = dict(
            appointment=appointment,
            reason=MISSED_VISIT,
            info_source=None,
            is_present=NO,
            survival_status=ALIVE,
            reason_missed='blahblah',
            last_alive_date=get_utcnow().date())
        form_validator = VisitFormValidator(
            cleaned_data=cleaned_data, instance=subject_visit)
        try:
            form_validator.validate()
        except ValidationError as e:
            self.fail(f'ValidationError unexpectedly raised. Got{e}')

    def test_is_present_invalid(self):
        self.helper.consent_and_put_on_schedule()
        appointment = Appointment.objects.all()[0]
        subject_visit = SubjectVisit.objects.create(
            appointment=appointment,
            reason=SCHEDULED)
        cleaned_data = dict(
            appointment=appointment,
            reason=MISSED_VISIT,
            info_source=None,
            is_present=YES,
            reason_missed='blahblah',
            survival_status=ALIVE,
            last_alive_date=get_utcnow().date())
        form_validator = VisitFormValidator(
            cleaned_data=cleaned_data, instance=subject_visit)
        self.assertRaises(ValidationError, form_validator.validate)
        self.assertIn('reason', form_validator._errors)

    def test_reason_missed_invalid(self):
        self.helper.consent_and_put_on_schedule()
        appointment = Appointment.objects.all()[0]
        subject_visit = SubjectVisit.objects.create(
            appointment=appointment,
            reason=SCHEDULED)
        cleaned_data = dict(
            appointment=appointment,
            reason=MISSED_VISIT,
            info_source=None,
            is_present=NO,
            reason_missed=None,
            survival_status=ALIVE,
            last_alive_date=get_utcnow().date())
        form_validator = VisitFormValidator(
            cleaned_data=cleaned_data, instance=subject_visit)
        self.assertRaises(ValidationError, form_validator.validate)
        self.assertIn('reason_missed', form_validator._errors)

    def test_last_alive_date_invalid(self):
        self.helper.consent_and_put_on_schedule()
        appointment = Appointment.objects.all()[0]
        subject_visit = SubjectVisit.objects.create(
            appointment=appointment,
            reason=SCHEDULED)
        cleaned_data = dict(
            appointment=appointment,
            reason=MISSED_VISIT,
            info_source=None,
            is_present=NO,
            reason_missed='blahblah',
            survival_status=ALIVE,
            last_alive_date=None)
        form_validator = VisitFormValidator(
            cleaned_data=cleaned_data, instance=subject_visit)
        self.assertRaises(ValidationError, form_validator.validate)
        self.assertIn('last_alive_date', form_validator._errors)

    def test_survival_status_invalid(self):
        self.helper.consent_and_put_on_schedule()
        appointment = Appointment.objects.all()[0]
        subject_visit = SubjectVisit.objects.create(
            appointment=appointment,
            reason=SCHEDULED)
        cleaned_data = dict(
            appointment=appointment,
            reason=MISSED_VISIT,
            info_source=None,
            is_present=YES,
            reason_missed='blahblah',
            survival_status=DEAD,
            last_alive_date=get_utcnow().date())
        form_validator = VisitFormValidator(
            cleaned_data=cleaned_data, instance=subject_visit)
        self.assertRaises(ValidationError, form_validator.validate)
        self.assertIn('survival_status', form_validator._errors)

    def test_reason_invalid(self):
        self.helper.consent_and_put_on_schedule()
        appointment = Appointment.objects.all()[0]
        subject_visit = SubjectVisit.objects.create(
            appointment=appointment,
            reason=SCHEDULED)
        cleaned_data = dict(
            appointment=appointment,
            reason=MISSED_VISIT,
            info_source=None,
            is_present=YES,
            reason_missed='blahblah',
            survival_status=ALIVE,
            last_alive_date=get_utcnow().date())
        form_validator = VisitFormValidator(
            cleaned_data=cleaned_data, instance=subject_visit)
        self.assertRaises(ValidationError, form_validator.validate)
        self.assertIn('reason', form_validator._errors)

    def test_is_present_no_info_source_invalid(self):
        self.helper.consent_and_put_on_schedule()
        appointment = Appointment.objects.all()[0]
        subject_visit = SubjectVisit.objects.create(
            appointment=appointment,
            reason=SCHEDULED)
        cleaned_data = dict(
            appointment=appointment,
            reason=MISSED_VISIT,
            info_source=PARTICIPANT,
            is_present=NO,
            reason_missed='blahblah',
            survival_status=DEAD,
            last_alive_date=get_utcnow().date())
        form_validator = VisitFormValidator(
            cleaned_data=cleaned_data, instance=subject_visit)
        self.assertRaises(ValidationError, form_validator.validate)
        self.assertIn('info_source', form_validator._errors)
