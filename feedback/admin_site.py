from django.contrib import admin

class CustomAdminSite(admin.AdminSite):
    site_header = "Rate.me Contol Panel"
    site_title = "Rate.me Admin"
    site_header = "Rate.me Contol Panel"
    index_title = "Admin Dashboard"
    
    def each_context(self, request):
        request.session.set_expiry(600)
        return super().each_context(request)
    
custom_admin_site = CustomAdminSite(name='custom_admin')
    