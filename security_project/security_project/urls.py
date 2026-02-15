from django.contrib import admin
from django.urls import path
from django.contrib.auth.views import LogoutView
from ip_tracking import views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', views.home_view, name='home'),
    path('login/', views.login_view, name='login'),
    path('dashboard/', views.dashboard_view, name='dashboard'),
    path('logout/', LogoutView.as_view(next_page='home'), name='logout'),
    path('rate-limited/', views.rate_limited_view, name='rate_limited'),
]