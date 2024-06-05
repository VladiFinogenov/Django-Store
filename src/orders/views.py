from django.shortcuts import render
from django.views.generic import FormView
from .forms import UserDataForm, PasswordForm


class Step1UserData(FormView):
    template_name = 'orders/step1-user-data.html'
    form_class = UserDataForm
    success_url = 'orders:delivery'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        if not self.request.user.is_authenticated:
            context['password_form'] = PasswordForm()
        context['current_step'] = 'step1'
        return context

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        if self.request.user.is_authenticated:
            kwargs['initial'] = {
                'first_name': self.request.user.first_name,
                'phone': self.request.user.phone,
                'email': self.request.user.email,
            }
        return kwargs

    def form_valid(self, form):
        form.save()
        return super().form_valid(form)


class Step2SelectDelivery(FormView):
    template_name = 'orders/step2-select-delivery.html'
    success_url = 'orders:payment'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['current_step'] = 'step2'
        return context


class Step3SelectPayment(FormView):
    template_name = 'orders/step3-select-payment.html'
    success_url = 'orders:delivery'


class Step4OrderConfirmation(FormView):
    pass
    #
    # class Stage1UserData(LoginRequiredMixin, FormView):
    #     template_name = 'stage1_user_data.html'
    #     form_class = Stage1UserDataForm
    #     success_url = '/next-step/'
    #

    #
    #     def get_context_data(self, **kwargs):
    #         context = super().get_context_data(**kwargs)
    #         if not self.request.user.is_authenticated:
    #             context['password_form'] = PasswordForm()
    #         return context
    #
    #     def form_valid(self, form):
    #         # save the form data
    #         form.save()
    #         return super().form_valid(form)
    #
    # И
    # соответствующие
    # формы:
    #
    # from django import forms
    # from django.contrib.auth.models import User
    #
    # class Stage1UserDataForm(forms.ModelForm):
    #     class Meta:
    #         model = User
    #         fields = ['first_name', 'last_name', 'email']
    #
    #     phone = forms.CharField(max_length=20)
    #
    #     def save(self, commit=True):
    #         user = super().save(commit=False)
    #         user.profile.phone = self.cleaned_data['phone']
    #         if commit:
    #             user.save()
    #             user.profile.save()
    #         return user

