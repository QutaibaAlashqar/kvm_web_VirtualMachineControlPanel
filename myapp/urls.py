from django.urls import path
from . import views
from django.conf import settings
from django.conf.urls.static import static
from myapp import views
from django.contrib.auth import views as auth_views  
from .views import (
    vm_control, start_vm, stop_vm, pause_vm, resume_vm, force_off_vm,
    edit_vm_xml, update_vm_xml, create_disk_form, submit_create_disk, list_existing_disks,
    use_disk, delete_disk, use_image, delete_image
)

urlpatterns = [
    path('', views.vm_control, name='vm_control'),
    path('start-vm/', views.start_vm, name='start_vm'),
    path('stop-vm/', views.stop_vm, name='stop_vm'),
    path('pause-vm/', views.pause_vm, name='pause_vm'),
    path('resume-vm/', views.resume_vm, name='resume_vm'), 
    path('force-off-vm/', views.force_off_vm, name='force_off_vm'),
    path('edit-vm-xml/', views.edit_vm_xml, name='edit_xml'),
    path('update-vm-xml/', views.update_vm_xml, name='update_xml'),
    path('vms/<str:vm_name>/create-disk/', views.create_disk_form, name='create_disk_form'),
    path('vms/<str:vm_name>/submit-disk/', views.submit_create_disk, name='submit_create_disk'),
    path('accounts/login/', auth_views.LoginView.as_view(), name='login'),
    path('vms/<str:vm_name>/existing-disks/', views.list_existing_disks, name='list_existing_disks'),
    path('use_disk/<str:vm_name>/<str:disk>/', use_disk, name='use_disk'),
    path('delete_disk/<str:vm_name>/<str:disk>/', delete_disk, name='delete_disk'),
    path('use_image/<str:vm_name>/<str:image>/', use_image, name='use_image'),
    path('delete_image/<str:vm_name>/<str:image>/', delete_image, name='delete_image'),
]
