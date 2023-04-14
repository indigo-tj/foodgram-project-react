# Generated by Django 3.2.18 on 2023-04-13 04:01

import core.enums
import core.validators
from django.conf import settings
import django.contrib.auth.models
from django.db import migrations, models
import django.db.models.deletion
import django.db.models.expressions
import django.utils.timezone


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('auth', '0012_alter_user_first_name_max_length'),
    ]

    operations = [
        migrations.CreateModel(
            name='MyUser',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('last_login', models.DateTimeField(blank=True, null=True, verbose_name='last login')),
                ('is_superuser', models.BooleanField(default=False, help_text='Designates that this user has all permissions without explicitly assigning them.', verbose_name='superuser status')),
                ('is_staff', models.BooleanField(default=False, help_text='Designates whether the user can log into this admin site.', verbose_name='staff status')),
                ('date_joined', models.DateTimeField(default=django.utils.timezone.now, verbose_name='date joined')),
                ('email', models.EmailField(help_text='Обязательно для заполнения. Максимум 256 букв.', max_length=256, unique=True, verbose_name='Адрес электронной почты')),
                ('username', models.CharField(help_text='Обязательно для заполнения. От 3 до 32 букв.', max_length=32, unique=True, validators=[core.validators.MinLenValidator(field='username', min_len=core.enums.Limits['MIN_LEN_USERNAME']), core.validators.OneOfTwoValidator(field='username')], verbose_name='Уникальный юзернейм')),
                ('first_name', models.CharField(help_text='Обязательно для заполнения. Максимум 32 букв.', max_length=32, validators=[core.validators.OneOfTwoValidator(field='Имя', first_regex='[^а-яёА-ЯЁ -]+', second_regex='[^a-zA-Z -]+')], verbose_name='Имя')),
                ('last_name', models.CharField(help_text='Обязательно для заполнения. Максимум 32 букв.', max_length=32, validators=[core.validators.OneOfTwoValidator(field='Фамилия', first_regex='[^а-яёА-ЯЁ -]+', second_regex='[^a-zA-Z -]+')], verbose_name='Фамилия')),
                ('password', models.CharField(help_text='Обязательно для заполнения. Максимум 32 букв.', max_length=128, verbose_name='Пароль')),
                ('is_active', models.BooleanField(default=True, verbose_name='Активирован')),
                ('groups', models.ManyToManyField(blank=True, help_text='The groups this user belongs to. A user will get all permissions granted to each of their groups.', related_name='user_set', related_query_name='user', to='auth.Group', verbose_name='groups')),
                ('user_permissions', models.ManyToManyField(blank=True, help_text='Specific permissions for this user.', related_name='user_set', related_query_name='user', to='auth.Permission', verbose_name='user permissions')),
            ],
            options={
                'verbose_name': 'Пользователь',
                'verbose_name_plural': 'Пользователи',
                'ordering': ('username',),
            },
            managers=[
                ('objects', django.contrib.auth.models.UserManager()),
            ],
        ),
        migrations.CreateModel(
            name='Subscriptions',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('date_added', models.DateTimeField(auto_now_add=True, verbose_name='Дата создания подписки')),
                ('author', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='subscribers', to=settings.AUTH_USER_MODEL, verbose_name='Автор рецепта')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='subscriptions', to=settings.AUTH_USER_MODEL, verbose_name='Подписчики')),
            ],
            options={
                'verbose_name': 'Подписка',
                'verbose_name_plural': 'Подписки',
            },
        ),
        migrations.AddConstraint(
            model_name='subscriptions',
            constraint=models.UniqueConstraint(fields=('author', 'user'), name='\nRepeat subscription\n'),
        ),
        migrations.AddConstraint(
            model_name='subscriptions',
            constraint=models.CheckConstraint(check=models.Q(('author', django.db.models.expressions.F('user')), _negated=True), name='\nNo self sibscription\n'),
        ),
        migrations.AddConstraint(
            model_name='myuser',
            constraint=models.CheckConstraint(check=models.Q(('username__length__gte', 3)), name='\nusername is too short\n'),
        ),
    ]
