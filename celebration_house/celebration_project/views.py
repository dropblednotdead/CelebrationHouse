from django.shortcuts import render, redirect
from datetime import datetime, timedelta
from celebration_project.forms import LocationSearchForm
from celebration_project.models import Locations, Booking, Regions, Zones
from django.urls import reverse


def index(request):
    form = LocationSearchForm(request.POST or None)
    locations = None

    if request.method == 'POST' and form.is_valid():
        region = form.cleaned_data['region']
        people = form.cleaned_data['people']
        date = form.cleaned_data['date']

        # Находим все бронирования на указанную дату
        booked_zones = Booking.objects.filter(
            date__date=date,  # Проверяем только дату (игнорируем время)
            status='Подтверждено'
        ).values_list('zone_id', flat=True)

        # Фильтруем локации
        locations = Locations.objects.filter(
            region=region,
            zones__people__gte=people
        ).exclude(
            zones__id__in=booked_zones
        ).distinct()

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
    }
    return render(request, 'celebration_project/index.html', context)


def search(request):
    # Получаем ID локаций из сессии
    location_ids = request.session.get('search_results', [])
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




