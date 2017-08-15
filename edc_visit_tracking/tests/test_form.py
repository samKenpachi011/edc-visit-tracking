from dateutil.relativedelta import relativedelta
from django import forms
from django.test import TestCase, tag
from edc_appointment.models import Appointment
from edc_base.utils import get_utcnow
from edc_visit_schedule.site_visit_schedules import site_visit_schedules

from ..constants import SCHEDULED
from ..form_validators import VisitFormValidator
from .helper import Helper
from .models import SubjectVisit
from .visit_schedule import visit_schedule1, visit_schedule2
from edc_constants.constants import ALIVE, YES


class SubjectVisitForm(forms.ModelForm):

    form_validator_cls = VisitFormValidator

    class Meta:
        model = SubjectVisit
        fields = '__all__'


class TestForm(TestCase):

    helper_cls = Helper

    def setUp(self):
        self.subject_identifier = '12345'
        self.helper = self.helper_cls(
            subject_identifier=self.subject_identifier)
        site_visit_schedules._registry = {}
        site_visit_schedules.register(visit_schedule=visit_schedule1)
        site_visit_schedules.register(visit_schedule=visit_schedule2)

    @tag('1')
    def test_form_validator_ok(self):
        self.helper.consent_and_enroll()
        appointment = Appointment.objects.all()[0]
        subject_visit = SubjectVisit.objects.create(
            appointment=appointment,
            reason=SCHEDULED)
        cleaned_data = dict(
            appointment=appointment,
            reason=SCHEDULED,
            is_present=YES,
            survival_status=ALIVE,
            last_alive_date=get_utcnow().date())
        form_validator = VisitFormValidator(
            cleaned_data=cleaned_data, instance=subject_visit)
        form_validator.validate()