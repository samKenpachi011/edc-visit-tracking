from dateutil.relativedelta import relativedelta
from django.core.exceptions import ImproperlyConfigured
from django.test import TestCase, tag
from edc_appointment.models import Appointment
from edc_base import get_utcnow
from edc_facility.import_holidays import import_holidays
from edc_visit_schedule.site_visit_schedules import site_visit_schedules
from edc_visit_tracking.constants import SCHEDULED

from .models import SubjectVisit, CrfOneInline, OtherModel
from .models import CrfOne, BadCrfOneInline
from .helper import Helper
from .visit_schedule import visit_schedule1, visit_schedule2


class TestVisit(TestCase):

    helper_cls = Helper

    def setUp(self):
        import_holidays()
        self.subject_identifier = '12345'
        self.helper = self.helper_cls(
            subject_identifier=self.subject_identifier)
        site_visit_schedules._registry = {}
        site_visit_schedules.register(visit_schedule=visit_schedule1)
        site_visit_schedules.register(visit_schedule=visit_schedule2)

    def test_crf_visit_model_attrs(self):
        """Assert models using the CrfModelMixin can determine which
        attribute points to the visit model foreignkey.
        """
        self.assertEqual(CrfOne().visit_model_attr(), 'subject_visit')
        self.assertEqual(CrfOne.objects.all().count(), 0)

    def test_crf_visit_model(self):
        """Assert models using the CrfModelMixin can determine which
        visit model is in use for the app_label.
        """
        self.assertEqual(CrfOne().visit_model(), SubjectVisit)
        self.assertEqual(CrfOne.objects.all().count(), 0)

    def test_crf_inline_model_attrs(self):
        """Assert inline model can find visit instance from parent.
        """
        self.helper.consent_and_put_on_schedule()
        appointment = Appointment.objects.all().order_by(
            'timepoint_datetime')[0]
        subject_visit = SubjectVisit.objects.create(
            appointment=appointment, reason=SCHEDULED)
        crf_one = CrfOne.objects.create(subject_visit=subject_visit)
        other_model = OtherModel.objects.create()
        crf_one_inline = CrfOneInline.objects.create(
            crf_one=crf_one, other_model=other_model)
        self.assertEqual(crf_one_inline.visit.pk, subject_visit.pk)

    def test_crf_inline_model_parent_model(self):
        """Assert inline model cannot find parent, raises exception.
        """
        self.helper.consent_and_put_on_schedule()
        appointment = Appointment.objects.all()[0]
        subject_visit = SubjectVisit.objects.create(
            appointment=appointment,
            reason=SCHEDULED)
        crf_one = CrfOne.objects.create(subject_visit=subject_visit)
        other_model = OtherModel.objects.create()
        self.assertRaises(
            ImproperlyConfigured,
            BadCrfOneInline.objects.create,
            crf_one=crf_one,
            other_model=other_model)

    def test_crf_inline_model_attrs2(self):
        """Assert inline model can find visit instance from parent.
        """
        self.helper.consent_and_put_on_schedule()
        appointment = Appointment.objects.all()[0]
        subject_visit = SubjectVisit.objects.create(
            appointment=appointment,
            reason=SCHEDULED)
        crf_one = CrfOne.objects.create(subject_visit=subject_visit)
        other_model = OtherModel.objects.create()
        crf_one_inline = CrfOneInline.objects.create(
            crf_one=crf_one,
            other_model=other_model)
        self.assertIsInstance(crf_one_inline.visit, SubjectVisit)

    def test_get_previous_model_instance(self):
        """Assert model can determine the previous.
        """

        self.helper.consent_and_put_on_schedule()
        for index, appointment in enumerate(Appointment.objects.all().order_by(
                'visit_code')):
            SubjectVisit.objects.create(
                appointment=appointment,
                report_datetime=(
                    get_utcnow() - relativedelta(months=10 - index)),
                reason=SCHEDULED)
        subject_visits = SubjectVisit.objects.all().order_by(
            'appointment__timepoint_datetime')
        self.assertEqual(subject_visits.count(), 4)
        subject_visit = subject_visits[0]
        self.assertIsNone(subject_visit.previous_visit)
        subject_visit = subject_visits[1]
        self.assertEqual(subject_visit.previous_visit.pk, subject_visits[0].pk)
        subject_visit = subject_visits[2]
        self.assertEqual(subject_visit.previous_visit.pk, subject_visits[1].pk)
        subject_visit = subject_visits[3]
        self.assertEqual(subject_visit.previous_visit.pk, subject_visits[2].pk)
