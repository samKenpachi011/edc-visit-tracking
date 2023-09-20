from dateutil.relativedelta import relativedelta
from django.test import TestCase
from edc_appointment.models import Appointment
from edc_base import get_utcnow
from edc_facility.import_holidays import import_holidays
from edc_visit_schedule.site_visit_schedules import site_visit_schedules

from ..constants import SCHEDULED
from ..model_mixins import PreviousVisitError
from ..visit_sequence import VisitSequence, VisitSequenceError
from .helper import Helper
from .models import SubjectVisit
from .visit_schedule import visit_schedule1, visit_schedule2


class DisabledVisitSequence(VisitSequence):
    def enforce_sequence(self):
        return None


class TestPreviousVisit(TestCase):

    helper_cls = Helper

    def setUp(self):
        import_holidays()
        SubjectVisit.visit_sequence_cls = VisitSequence
        self.subject_identifier = '12345'
        self.helper = self.helper_cls(
            subject_identifier=self.subject_identifier)
        site_visit_schedules._registry = {}
        site_visit_schedules.register(visit_schedule=visit_schedule1)
        site_visit_schedules.register(visit_schedule=visit_schedule2)
        self.helper.consent_and_put_on_schedule()

    def tearDown(self):
        SubjectVisit.visit_sequence_cls = VisitSequence

    def test_visit_sequence_enforcer_on_first_visit_in_sequence(self):
        appointments = Appointment.objects.all().order_by('timepoint_datetime')
        SubjectVisit.visit_sequence_cls = DisabledVisitSequence
        visit = SubjectVisit.objects.create(
            appointment=appointments[0],
            report_datetime=get_utcnow() - relativedelta(months=10),
            reason=SCHEDULED)
        visit_sequence = VisitSequence(appointment=visit.appointment)
        try:
            visit_sequence.enforce_sequence()
        except VisitSequenceError as e:
            self.fail(f'VisitSequenceError unexpectedly raised. Got \'{e}\'')

    def test_visit_sequence_enforcer_without_first_visit_in_sequence(self):
        appointments = Appointment.objects.all().order_by('timepoint_datetime')
        SubjectVisit.visit_sequence_cls = DisabledVisitSequence
        visit = SubjectVisit.objects.create(
            appointment=appointments[1],
            report_datetime=get_utcnow() - relativedelta(months=10),
            reason=SCHEDULED)
        visit_sequence = VisitSequence(appointment=visit.appointment)
        self.assertRaises(VisitSequenceError, visit_sequence.enforce_sequence)

    def test_requires_previous_visit_thru_model(self):
        """Asserts requires previous visit to exist on create.
        """
        appointments = Appointment.objects.all().order_by('timepoint_datetime')

        SubjectVisit.objects.create(
            appointment=appointments[0],
            report_datetime=get_utcnow() - relativedelta(months=10),
            reason=SCHEDULED)

        self.assertRaises(
            PreviousVisitError, SubjectVisit.objects.create,
            appointment=appointments[2],
            report_datetime=get_utcnow() - relativedelta(months=8),
            reason=SCHEDULED)

        SubjectVisit.objects.create(
            appointment=appointments[1],
            report_datetime=get_utcnow() - relativedelta(months=10),
            reason=SCHEDULED)

        self.assertRaises(
            PreviousVisitError, SubjectVisit.objects.create,
            appointment=appointments[3],
            report_datetime=get_utcnow() - relativedelta(months=8),
            reason=SCHEDULED)
