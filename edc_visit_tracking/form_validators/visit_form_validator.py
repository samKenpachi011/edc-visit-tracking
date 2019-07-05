from django import forms
from edc_constants.constants import OTHER, ALIVE, DEAD, YES, UNKNOWN
from edc_constants.constants import PARTICIPANT, NO
from edc_form_validators import FormValidator
from edc_form_validators.base_form_validator import REQUIRED_ERROR,\
    INVALID_ERROR

from ..constants import MISSED_VISIT, LOST_VISIT, UNSCHEDULED
from ..visit_sequence import VisitSequence, VisitSequenceError


class VisitFormValidator(FormValidator):

    visit_sequence_cls = VisitSequence
    participant_label = 'participant'

    def clean(self):
        appointment = self.cleaned_data.get('appointment')
        if not appointment:
            raise forms.ValidationError({
                'appointment': 'This field is required'},
                code=REQUIRED_ERROR)

        visit_sequence = self.visit_sequence_cls(appointment=appointment)

        try:
            visit_sequence.enforce_sequence()
        except VisitSequenceError as e:
            raise forms.ValidationError(e, code=INVALID_ERROR)

        self.validate_visit_code_sequence_and_reason()

        self.validate_presence()

        self.validate_survival_status_if_alive()

        self.validate_reason_and_info_source()

        self.validate_required_fields()

    def validate_visit_code_sequence_and_reason(self):
        appointment = self.cleaned_data.get('appointment')
        reason = self.cleaned_data.get('reason')
        if appointment:
            if (not appointment.visit_code_sequence
                    and reason == UNSCHEDULED):
                raise forms.ValidationError({
                    'reason': 'Invalid. This is not an unscheduled visit'},
                    code=INVALID_ERROR)
            if (appointment.visit_code_sequence
                    and reason != UNSCHEDULED):
                raise forms.ValidationError({
                    'reason': 'Invalid. This is an unscheduled visit'},
                    code=INVALID_ERROR)

    def validate_reason_and_info_source(self):
        cleaned_data = self.cleaned_data
        condition = cleaned_data.get('reason') != MISSED_VISIT
        self.required_if_true(
            condition,
            field_required='info_source',
            required_msg='Provide source of information.')

    def validate_survival_status_if_alive(self):
        cleaned_data = self.cleaned_data
        if cleaned_data.get('survival_status') in [ALIVE, DEAD]:
            if not cleaned_data.get('last_alive_date'):
                raise forms.ValidationError(
                    {'last_alive_date':
                     f'Provide date {self.participant_label} last known alive.'})

    def validate_presence(self):
        """Raise an exception if 'is_present' does not make sense relative to
         'survival status', 'reason' and 'info_source'."""
        cleaned_data = self.cleaned_data
        if cleaned_data.get('is_present') == YES:
            if cleaned_data.get('survival_status') in [UNKNOWN, DEAD]:
                raise forms.ValidationError(
                    {'survival_status':
                     'Survival status cannot be \'{survival_status}\' if '
                     '{participant} is present.'.format(
                         survival_status=cleaned_data.get(
                             'survival_status').lower(),
                         participant=self.participant_label)})

            if cleaned_data.get('reason') in [MISSED_VISIT, LOST_VISIT]:
                raise forms.ValidationError(
                    {'reason':
                     'You indicated that the reason for the visit report is '
                     '{reason} but also that the {participant} is present. '
                     'Please correct.'.format(
                         participant=self.participant_label,
                         reason=cleaned_data.get('reason'))})
        elif cleaned_data.get('is_present') == NO:
            if cleaned_data.get('info_source') == PARTICIPANT:
                raise forms.ValidationError(
                    {'info_source': 'Source of information cannot be from '
                     '{participant} if {participant} is not present.'.format(
                         participant=self.participant_label)})

    def validate_required_fields(self):

        self.required_if(
            MISSED_VISIT,
            field='reason',
            field_required='reason_missed')

        self.required_if(
            UNSCHEDULED,
            field='reason',
            field_required='reason_unscheduled')

        self.required_if(
            OTHER,
            field='info_source',
            field_required='info_source_other')

        self.required_if(
            OTHER,
            field='reason_unscheduled',
            field_required='reason_unscheduled_other')
