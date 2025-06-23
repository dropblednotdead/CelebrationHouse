from django.db import models
from django.contrib.auth.models import User


class UnsignedIntegerField(models.IntegerField):
    def db_type(self, connection):
        if connection.vendor == 'mysql':
            return 'integer UNSIGNED'
        return super().db_type(connection)


class Booking(models.Model):
    id = models.BigAutoField(primary_key=True)
    client = models.ForeignKey(
        User,
        models.DO_NOTHING,
        blank=True,
        null=True,
        verbose_name='Клиент'
    )
    last_name = models.CharField(
        max_length=50,
        verbose_name='Фамилия',
        blank=True,
        null=True
    )
    first_name = models.CharField(
        max_length=50,
        verbose_name='Имя',
        blank=True,
        null=True
    )
    patronymic = models.CharField(max_length=100, null=True, blank=True, verbose_name='Отчество')
    phone_num = models.CharField(
        max_length=20,
        verbose_name='Номер телефона',
        blank=True,
        null=True,
    )
    zone = models.ForeignKey(
        'Zones',
        models.DO_NOTHING,
        verbose_name='Зона'
    )
    total_price = models.DecimalField(
        max_digits=7,
        decimal_places=2,
        verbose_name='Итоговая цена',
    )
    comment = models.TextField(verbose_name='Комментарий')
    date = models.DateField(
        verbose_name='Дата',
        blank=True,
        null=True
    )

    people = UnsignedIntegerField(
        verbose_name='Кол-во человек',
        blank=True,
        null=True
    )
    status = models.CharField(
        choices=[('Подтверждено', 'Подтверждено'),
                 ('Отклонено', 'Отклонено'),
                 ('Ожидание', 'Ожидание')],
        max_length=50,
        verbose_name='Статус',
        default='Ожидание'
    )
    booking_services = models.ManyToManyField(
        'Services',
        blank=True,
        related_name='booking_services',
        through='BookingServices'
    )

    class Meta:
        managed = True
        db_table = 'booking'
        verbose_name = 'Бронирование'
        verbose_name_plural = 'Бронирования'
        ordering = ['id', '-total_price']
        constraints = [
            models.UniqueConstraint(fields=['zone', 'date'], name='unique_booking_per_zone_per_date')
        ]

    def __str__(self):
        return f'{self.first_name} {self.last_name} {self.date}'


class Services(models.Model):
    PRICE_TYPES = [
        ('per_person', 'Р/чел'),
        ('per_day', 'Р/сутки'),
        ('per_hour', 'Р/час'),
        ('taxi', 'Такси (50р + 10р/км)'),
    ]

    id = models.BigAutoField(primary_key=True)
    name = models.CharField(max_length=255, verbose_name='Название')
    description = models.TextField(
        verbose_name='Описание',
        blank=True,
        null=True
    )
    cost = models.DecimalField(
        max_digits=7,
        decimal_places=2,
        verbose_name='Стоимость'
    )
    price_type = models.CharField(
        max_length=20,
        choices=PRICE_TYPES,
        default='per_day',
        verbose_name='Тип расчета'
    )

    class Meta:
        managed = True
        db_table = 'services'
        verbose_name = 'Услуга'
        verbose_name_plural = 'Услуги'
        ordering = ['-cost', 'id']

    def __str__(self):
        return f'{self.name}'


class BookingServices(models.Model):
    id = models.BigAutoField(primary_key=True)
    booking = models.ForeignKey(
        'Booking',
        on_delete=models.CASCADE,
        verbose_name='Аренда',
        related_name='booking_serv'
    )
    service = models.ForeignKey(
        'Services',
        models.DO_NOTHING,
        verbose_name='Услуга'
    )

    class Meta:
        managed = True
        db_table = 'booking_services'
        verbose_name = 'Услуга в бронировании'
        verbose_name_plural = 'Услуги в бронировании'
        ordering = ['id']

    def __str__(self):
        return f'{self.booking} {self.service}'


class Zones(models.Model):
    id = models.BigAutoField(primary_key=True)
    name = models.CharField(max_length=50, verbose_name='Название')
    image = models.ImageField(
        upload_to='zones/',
        null=True,
        blank=True,
        verbose_name='Изображение'
    )
    plan = models.ImageField(
        upload_to='zones/plan',
        null=True,
        blank=True,
        verbose_name='План'
    )
    price = models.DecimalField(
        max_digits=7,
        decimal_places=2,
        verbose_name='Цена',
    )
    people = UnsignedIntegerField(verbose_name='Кол-во человек')
    location = models.ForeignKey(
        'Locations',
        models.DO_NOTHING,
        verbose_name='Локация',
        related_name='zone'
    )
    description = models.TextField(
        blank=True,
        null=True,
        verbose_name='Описание'
    )
    start_time = models.TimeField(
        blank=True,
        null=True,
        verbose_name='Начальное время'
    )
    end_time = models.TimeField(
        blank=True,
        null=True,
        verbose_name='Конечное время'
    )

    class Meta:
        managed = True
        db_table = 'zones'
        verbose_name = 'Зона'
        verbose_name_plural = 'Зоны'
        ordering = ['id', '-price']

    def __str__(self):
        return f'{self.name}'


class Locations(models.Model):
    id = models.BigAutoField(primary_key=True)
    city = models.CharField(
        max_length=100,
        verbose_name='Город',
        blank=True,
        null=True,
    )
    street = models.CharField(max_length=100, verbose_name='Улица')
    building = models.IntegerField(verbose_name='Дом')
    name = models.CharField(
        max_length=100,
        verbose_name='Название',
        blank=True,
        null=True,
    )
    index = models.CharField(
        max_length=1,
        blank=True,
        null=True,
        verbose_name='Индекс')
    max_people = UnsignedIntegerField(verbose_name='Максимальное кол-во человек')
    region = models.ForeignKey(
        'Regions',
        models.DO_NOTHING,
        verbose_name='Регион',
        related_name='location'
    )
    photo = models.ImageField(
        upload_to='locations/',
        null=True,
        blank=True,
        verbose_name='Фото'
    )

    class Meta:
        managed = True
        db_table = 'locations'
        verbose_name = 'Локация'
        verbose_name_plural = 'Локации'
        ordering = ['id']

    def __str__(self):
        return (f"{self.name}, {self.region}, г. {self.city}, ул. {self.street}, "
                f"д. {self.building}{self.index if self.index is not None else ''}")


class Regions(models.Model):
    id = models.BigAutoField(primary_key=True)
    type = models.ForeignKey(
        'RegionTypes',
        models.DO_NOTHING,
        verbose_name='Тип',
        blank=True,
        null=True
    )
    name = models.CharField(max_length=50, verbose_name='Название')

    class Meta:
        managed = True
        db_table = 'regions'
        verbose_name = 'Регион'
        verbose_name_plural = 'Регионы'
        ordering = ['id']

    def __str__(self):
        if self.type.name == 'Республика':
            return f'{self.type} {self.name}'
        else:
            return f'{self.name} {self.type}'


class RegionTypes(models.Model):
    id = models.BigAutoField(primary_key=True)
    name = models.CharField(max_length=50, verbose_name='Тип')

    class Meta:
        managed = True
        db_table = 'region_types'
        verbose_name = 'Тип региона'
        verbose_name_plural = 'Типы регионов'
        ordering = ['id']

    def __str__(self):
        return f'{self.name}'


class Sales(models.Model):
    id = models.BigAutoField(primary_key=True)
    image = models.ImageField(
        upload_to='sales/',
        null=True,
        blank=True,
        verbose_name='Изображение'
    )
    name = models.CharField(max_length=255, verbose_name='Название')
    description = models.TextField(verbose_name='Описание')

    class Meta:
        managed = True
        db_table = 'sales'
        verbose_name = 'Акция'
        verbose_name_plural = 'Акции'
        ordering = ['id']

    def __str__(self):
        return f'{self.name}'
