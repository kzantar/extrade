#-*- coding:utf-8 -*-
from django.contrib import admin
from django.contrib.auth import get_user_model
from users.models import ProfileRole, ProfileBalance
from django.contrib.auth.admin import UserAdmin
from users.forms import UserAdminForm

Profile = get_user_model()

class ProfileBalanceAdmin(admin.ModelAdmin):
    list_display=('value', 'valuta', 'profile', 'action', 'bank', 'accept', 'cancel')
    list_editable = ('accept', 'cancel')
    list_filter = ('action', 'accept', 'cancel', 'confirm')

class ProfileRoleAdminInline(admin.TabularInline):
    model = ProfileRole
    extra = 1
    classes = ('grp-collapse grp-closed',)
    inline_classes = ('grp-collapse grp-closed',)
class ProfileBalanceAdminInline(admin.TabularInline):
    model = ProfileBalance
    extra = 1
    classes = ('grp-collapse grp-closed',)
    inline_classes = ('grp-collapse grp-closed',)

class ProfileAdmin(UserAdmin):
    form = UserAdminForm
    fieldsets = (
        (None, {'fields': ('email', 'password', 'username')}),
        (('Permissions'), {'fields': ('is_active', 'is_staff', 'is_superuser',
                                       'groups', 'user_permissions')}),
        (('Important dates'), {'fields': ('last_login', 'date_joined')}),
    )
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('email', 'password1', 'password2'),
        }),
    )
    list_display = ('email', 'username', 'date_joined')
    list_filter = ('is_staff', 'is_superuser', 'is_active', 'groups')
    date_hierarchy = 'date_joined'
    search_fields = ('email', )
    ordering = ('email',)
    inlines = [ProfileRoleAdminInline, ProfileBalanceAdminInline]

    #def has_add_permission(self, request):
    #    return False

admin.site.register(Profile, ProfileAdmin)
admin.site.register(ProfileBalance, ProfileBalanceAdmin)
