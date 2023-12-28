from django import forms

class StarRatingWidget(forms.NumberInput):
    template_name = 'star.html'

    def get_context(self, name, value, attrs):
        context = super().get_context(name, value, attrs)
        context['widget']['value'] = value  # Set the value dynamically
        context['widget']['name'] = name  # Pass the field name to the template
        return context

class StarRatingSelect(StarRatingWidget, forms.Select):
    pass
