from django.contrib import messages
from django.forms import ValidationError
from django.db import IntegrityError
from django.shortcuts import (get_object_or_404, redirect, render,
                              render_to_response)
from django.views.generic import (CreateView, DeleteView, DetailView,
                                  ListView, UpdateView)

from cyder.base.utils import tablefy


def home(request):
    return render_to_response('base/index.html', {
        'read_only': getattr(request, 'read_only', False),
    })


class BaseListView(ListView):
    """
    Inherit ListView to specify our pagination.
    """
    template_name = 'list.html'
    extra_context = None
    paginate_by = 30

    def get_context_data(self, **kwargs):
        context = super(ListView, self).get_context_data(**kwargs)
        context['Model'] = self.model
        context['model_name'] = self.model._meta.db_table
        context['object_table'] = tablefy(context['page_obj'])
        context['form_title'] = "{0} Details".format(
            self.form_class.Meta.model.__name__
        )

        # Extra_context takes precedence over original values in context.
        try:
            context = dict(context.items() + self.extra_context.items())
        except AttributeError:
            pass

        return context


class BaseDetailView(DetailView):
    template_name = 'detail.html'
    extra_context = None

    def get_context_data(self, **kwargs):
        context = super(DetailView, self).get_context_data(**kwargs)
        context['form_title'] = "{0} Details".format(
            self.form_class.Meta.model.__name__
        )

        # Extra_context takes precedence over original values in context.
        try:
            context = dict(context.items() + self.extra_context.items())
        except AttributeError:
            pass

        return context


class BaseCreateView(CreateView):
    template_name = "form.html"
    extra_context = None

    def post(self, request, *args, **kwargs):
        try:
            obj = super(BaseCreateView, self).post(request, *args, **kwargs)

        # Redirect back to form if errors.
        except (IntegrityError, ValidationError), e:
            messages.error(request, str(e))
            request.method = 'GET'
            return super(BaseCreateView, self).get(request, *args, **kwargs)

        return obj

    def get(self, request, *args, **kwargs):
        return super(BaseCreateView, self).get(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super(CreateView, self).get_context_data(**kwargs)
        context['form_title'] = "Create {0}".format(
            self.form_class.Meta.model.__name__
        )

        # extra_context takes precedence over original values in context.
        try:
            context = dict(context.items() + self.extra_context.items())
        except AttributeError:
            pass

        return context


class BaseUpdateView(UpdateView):
    template_name = "form.html"
    extra_context = None

    def __init__(self, *args, **kwargs):
        super(UpdateView, self).__init__(*args, **kwargs)

    def get_form(self, form_class):
        form = super(BaseUpdateView, self).get_form(form_class)
        return form

    def post(self, request, *args, **kwargs):
        try:
            obj = super(BaseUpdateView, self).post(request, *args, **kwargs)

        except ValidationError, e:
            messages.error(request, str(e))
            request.method = 'GET'
            return super(BaseUpdateView, self).get(request, *args, **kwargs)

        return obj

    def get(self, request, *args, **kwargs):
        return super(BaseUpdateView, self).get(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super(UpdateView, self).get_context_data(**kwargs)
        context['form_title'] = "Update {0}".format(
            self.form_class.Meta.model.__name__
        )

        # Extra_context takes precedence over original values in context.
        try:
            context = dict(context.items() + self.extra_context.items())
        except AttributeError:
            pass

        return context


class BaseDeleteView(DeleteView):
    template_name = 'confirm_delete.html'
    extra_content = None
    success_url = '/'

    def get_object(self, queryset=None):
        obj = super(BaseDeleteView, self).get_object()
        return obj

    def delete(self, request, *args, **kwargs):
        # Get the object to delete.
        obj = get_object_or_404(self.form_class.Meta.model,
                                pk=kwargs.get('pk', 0))

        try:
            view = super(BaseDeleteView, self).delete(request, *args, **kwargs)
        except ValidationError, e:
            messages.error(request, "Error: {0}".format(' '.join(e.messages)))
            return redirect(obj)

        messages.success(request, "Deletion Successful")
        return view

    def get_context_data(self, **kwargs):
        context = super(DeleteView, self).get_context_data(**kwargs)
        context['form_title'] = "Update {0}".format(
            self.form_class.Meta.model.__name__
        )

        # Extra_context takes precedence over original values in context.
        try:
            context = dict(context.items() + self.extra_context.items())
        except AttributeError:
            pass

        return context


class Base(DetailView):
    def get(self, request, *args, **kwargs):
        return render(request, "base.html")
