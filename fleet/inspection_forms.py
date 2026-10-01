from django import forms
from .models import BusInspection

class InspectionForm(forms.ModelForm):
    # Field names for all Pass/Fail checks
    BOOLEAN_FIELDS = [
        'doc_registration', 'doc_route_permit', 'doc_insurance', 'doc_fitness', 'doc_tax_token',
        'mech_engine', 'mech_brake', 'mech_steering', 'mech_suspension', 'mech_electrical',
        'safe_fire_extinguisher', 'safe_first_aid', 'safe_emergency_exit', 'safe_hammer', 'safe_speed_governor',
        'body_tyres', 'body_windshield', 'body_damage',
        'int_seats', 'int_doors', 'int_overcrowding',
        'env_smoke', 'env_noise'
    ]

    class Meta:
        model = BusInspection
        fields = [
            'bus', 'location', 'next_inspection_date',
            'doc_registration', 'doc_route_permit', 'doc_insurance', 'doc_fitness', 'doc_tax_token',
            'mech_engine', 'mech_brake', 'mech_steering', 'mech_suspension', 'mech_electrical',
            'safe_fire_extinguisher', 'safe_first_aid', 'safe_emergency_exit', 'safe_hammer', 'safe_speed_governor',
            'body_tyres', 'body_windshield', 'body_damage',
            'int_seats', 'int_doors', 'int_overcrowding',
            'env_smoke', 'env_noise',
            'remarks', 'photo_evidence'
        ]
        widgets = {
            'bus': forms.Select(attrs={'class': 'form-select'}),
            'location': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter Inspection Location'}),
            'next_inspection_date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'remarks': forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'placeholder': 'Required if any field fails...'}),
            'photo_evidence': forms.FileInput(attrs={'class': 'form-control'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Convert all BooleanFields to TypedChoiceFields to handle Radio buttons properly
        choices = [(True, 'Pass'), (False, 'Fail')]
        for field in self.BOOLEAN_FIELDS:
            self.fields[field] = forms.TypedChoiceField(
                choices=choices,
                coerce=lambda x: x == 'True' if isinstance(x, str) else bool(x),
                widget=forms.RadioSelect,
                initial=True,
                label=self.fields[field].label
            )

    def clean(self):
        cleaned_data = super().clean()
        
        # Backend Validation: Remarks and Photo required if any field failed
        any_fail = any(cleaned_data.get(f) is False for f in self.BOOLEAN_FIELDS)
        
        if any_fail:
            if not cleaned_data.get('remarks'):
                self.add_error('remarks', 'Please provide remarks explaining the failure(s).')
            if not cleaned_data.get('photo_evidence'):
                self.add_error('photo_evidence', 'Please upload a photo as evidence for the failed items.')
        
        return cleaned_data
