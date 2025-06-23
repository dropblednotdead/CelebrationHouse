from django.contrib.auth import logout, login
from django.contrib.auth.decorators import login_required
from django.contrib.auth.views import LoginView
from django.shortcuts import render, redirect
from django.db import IntegrityError
from datetime import datetime, timedelta

from django.views.generic import CreateView

from celebration_project.forms import LocationSearchForm, BookingForm, AuthorizationUserForm, RegistrationUserForm
from celebration_project.models import Locations, Booking, Regions, Zones, BookingServices, Sales
from django.urls import reverse, reverse_lazy


def index(request):
    sales = Sales.objects.all()
    form = LocationSearchForm(request.POST or None)
    locations = None

    if request.method == 'POST' and form.is_valid():
        region = form.cleaned_data['region']
        people = form.cleaned_data['people']
        date = form.cleaned_data['date']

        # Находим все бронирования на указанную дату
        booked_zones = Booking.objects.filter(
            date=date,
            status='Подтверждено'
        ).values_list('zone_id', flat=True)

        # Фильтруем локации
        locations = Locations.objects.filter(
            region=region,
            zone__people__gte=people
        ).exclude(
            zone__id__in=booked_zones
        ).distinct()
        print(locations)

        # Сохраняем отфильтрованные локации в сессии
        request.session['search_results'] = [loc.id for loc in locations]
        request.session['search_params'] = {
            'region': region.id,
            'people': people,
            'date': date.strftime('%Y-%m-%d')
        }

        # Редирект на страницу с результатами поиска
        return redirect(reverse('search'))

    context = {
        "form": form,
        'sales': sales
    }
    return render(request, 'celebration_project/index.html', context)


def search(request):
    # Получаем ID локаций из сессии
    location_ids = request.session.get('search_results', [])
    print(location_ids)
    search_params = request.session.get('search_params', {})

    # Получаем полные объекты локаций
    locations = Locations.objects.filter(id__in=location_ids)

    # Получаем параметры поиска для отображения
    region = Regions.objects.get(id=search_params.get('region')) if search_params.get('region') else None

    context = {
        'locations': locations,
        'search_params': {
            'region': region,
            'people': search_params.get('people'),
            'date': search_params.get('date')
        }
    }

    return render(request, 'celebration_project/search.html', context)


def seat(request, *args):
    location_key = request.GET.get('location')
    selected_location = Locations.objects.get(pk=location_key)

    zones = Zones.objects.filter(location=selected_location)

    context = {
        'zones': zones,
    }

    return render(request, 'celebration_project/seat.html', context)


def booking(request, *args):
    zone = Zones.objects.get(pk=request.GET.get('zone'))
    search_params = request.session.get('search_params', {})

    region = Regions.objects.get(id=search_params.get('region')) if search_params.get('region') else None

    if request.method == 'POST':
        form = BookingForm(request.POST or None)
        if form.is_valid():
            booking_form = form.save(commit=False)
            booking_form.zone = zone
            booking_form.people = search_params.get('people')
            booking_form.date = search_params.get('date')
            booking_form.client = request.user if request.user else None
            try:
                booking_form.save()
            except IntegrityError:
                form.add_error(None, 'Зона уже забронирована на выбранную дату.')
                context = {
                    'zone': zone,
                    "form": form,
                    'search_params': {
                        'region': region,
                        'people': search_params.get('people'),
                        'date': search_params.get('date')
                    }
                }
                return render(request, 'celebration_project/booking.html', context)

            # Сохраняем услуги, если всё хорошо
            services = form.cleaned_data['booking_services']
            for service in services:
                BookingServices.objects.create(booking=booking_form, service=service)
            return redirect('index')
    else:
        form = BookingForm()

    context = {
        'zone': zone,
        "form": form,
        'search_params': {
            'region': region,
            'people': search_params.get('people'),
            'date': search_params.get('date')
        }
    }

    return render(request, 'celebration_project/booking.html', context)


class RegistrationUser(CreateView):
    form_class = RegistrationUserForm
    template_name = 'celebration_project/registration.html'
    success_url = 'celebration_project/authorization.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        return context

    def form_valid(self, form):
        user = form.save()
        login(self.request, user)
        return redirect('index')


class AuthorizationUser(LoginView):
    form_class = AuthorizationUserForm
    template_name = 'celebration_project/authorization.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        return context

    def get_success_url(self):
        return reverse_lazy('index')


def logout_user(request):
    logout(request)
    return redirect('index')


@login_required
def user_profile_view(request):
    bookings = Booking.objects.filter(client=request.user)

    booking_card = request.GET.get('booking', None)

    if booking_card:  # только если передан ID бронирования
        try:
            card = bookings.filter(pk=booking_card)
            card.delete()
            redirect('profile')
        except Booking.DoesNotExist:
            pass

    context = {
        'bookings': bookings,
    }
    return render(request, 'celebration_project/profile.html', context)


def booking_edit(request, *args):
    booking_list = Booking.objects.all()

    status = request.GET.get('status', None)
    booking_card = request.GET.get('booking', None)

    if booking_card:  # только если передан ID бронирования
        try:
            card = Booking.objects.get(pk=booking_card)
            if status is not None:
                if status == '1':
                    card.status = 'Подтверждено'
                else:
                    card.status = 'Отклонено'
                card.save()
            else:
                card.delete()
            redirect('admin')
        except Booking.DoesNotExist:
            pass  # или можно вывести сообщение, если нужно

    context = {
        'bookings': booking_list,
        'accept': 'Подтверждено',
        'no_accept': 'Отклонено'
    }

    return render(request, 'celebration_project/admin.html', context)