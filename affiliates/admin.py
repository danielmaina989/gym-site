from django.contrib import admin
from .models import Affiliate, Referral

# Register your models here.
class RefferralInline(admin.TabularInline):
    model = Referral
    extra = 0  # Don't show extra empty forms


@admin.register(Affiliate)
class AffiliateAdmin(admin.ModelAdmin):
    list_display = ("user", "status", "total_earnings", "created_at")
    list_filter = ("status",)
    actions = ["approve_affiliates", "reject_affiliates"]

    def approve_affiliates(self, request, queryset):
        queryset.update(status="Approved")
        self.message_user(request, "Selected affiliates approved.")

    def reject_affiliates(self, request, queryset):
        queryset.update(status="Rejected")
        self.message_user(request, "Selected applications rejected.")

admin.site.register(Referral)