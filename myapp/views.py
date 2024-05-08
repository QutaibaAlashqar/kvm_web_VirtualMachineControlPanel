from django.shortcuts import render
import libvirt
from django.shortcuts import redirect
from django.urls import reverse
from django.http import HttpResponse
import logging
import subprocess
import os
import uuid
from django.http import JsonResponse
from myapp import views
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.decorators import login_required
import xml.etree.ElementTree as ET
from django.views.decorators.http import require_http_methods
from django.views.decorators.http import require_http_methods, require_POST
from .libvirt_helpers import get_libvirt_connection
from django.views.decorators.http import require_POST

logger = logging.getLogger(__name__)


##########
##########   # INFO
##########


def get_vm_info():
    conn = libvirt.open('qemu:///system')
    if conn is None:
        print("Failed to open connection to qemu:///system")
        return []

    domains = conn.listAllDomains()
    vm_info = []
    for domain in domains:
        vm_name = domain.name()
        info = domain.info() 
        state_map = {
            0: 'No State',
            1: 'Running',
            2: 'Blocked',
            3: 'Paused',
            4: 'Shutting Down',
            5: 'Shutoff',
            6: 'Crashed',
            7: 'Suspended'
        }
        vm_state = state_map.get(info[0], 'Unknown')
        
        vm_info.append({
            'name': vm_name,
            'state': state,
            'id': info[0],  
        })

    conn.close()  
    return vm_info


def get_vm_info():
    try:
        # Open connection to libvirt
        conn = libvirt.open('qemu:///system')
        if conn is None:
            return []

        # Get list of domains (virtual machines)
        domains = conn.listAllDomains()
        vm_info = []
        for domain in domains:
            try:
                # Retrieve detailed information about the domain
                info = domain.info()
                state = "Running" if domain.isActive() else "Stopped"
                
                vm_info.append({
                    'name': domain.name(),
                    'id': info[0],
                    'uuid': domain.UUIDString(),
                    'os_type': domain.OSType(),
                    'state': state,  
                    'cpu_count': domain.maxVcpus(),  
                    'cpu_time': domain.info()[4],  
                    'max_memory': domain.maxMemory(),
                    'used_memory': domain.memoryStats()['actual'],
                    'persistent': 'Yes' if domain.isPersistent() else 'No',
                    'autostart': 'Enabled' if domain.autostart() else 'Disabled',
                    'managed_save': 'Yes' if domain.hasManagedSaveImage() else 'No',
                })
            except libvirt.libvirtError as e:
                vm_info.append({
                    'name': domain.name(),
                    'state': 'Stopped'  
                })

        return vm_info
    except libvirt.libvirtError as e:
        print(f"Failed to connect to libvirt: {e}")
        return []


##########
##########   # showing the machines
##########


def vm_control(request):
    success_message = request.GET.get('success')
    error_message = request.GET.get('error')
    vm_info = get_vm_info()

    # Logging each VM's name and state for debugging purposes
    for vm in vm_info:
        print(f"{vm['name']} - State: {vm['state']}")

    context = {'vm_info': vm_info}
    if success_message:
        context['message'] = success_message
    if error_message:
        context['error'] = error_message
    return render(request, 'myapp/index.html', context)


##########
##########   # Start
##########


def start_vm(request):
    if request.method == 'POST':
        vm_name = request.POST.get('vm_name')
        print("Start VM request received for:", vm_name)  # Add this line for debugging
        success, message = start_virtual_machine(vm_name)
        if success:
            return render(request, 'myapp/index.html', {'vm_info': get_vm_info(), 'message': message})
        else:
            return render(request, 'myapp/index.html', {'vm_info': get_vm_info(), 'error': message})
    else:
        return render(request, 'myapp/index.html', {'error': 'Method not allowed'})


def start_virtual_machine(vm_name):
    conn = libvirt.open('qemu:///system')
    if conn is None:
        return False, 'Failed to open connection to qemu:///system'
    
    domain = conn.lookupByName(vm_name)
    if domain is None:
        return False, f'Virtual machine {vm_name} not found'

    # Check if the VM is already running
    if domain.isActive():
        return False, f'Virtual machine {vm_name} is already running'
    
    # Attempt to start the VM
    if domain.create() == 0:
        return True, f'Successfully started virtual machine {vm_name}'
    else:
        return False, f'Failed to start virtual machine {vm_name}'


##########
##########   # Stop
##########


def stop_vm(request):
    if request.method == 'POST':
        vm_name = request.POST.get('vm_name')
        success, message = stop_virtual_machine(vm_name)
        if success:
            return render(request, 'myapp/index.html', {'vm_info': get_vm_info(), 'message': message})
        else:
            return render(request, 'myapp/index.html', {'vm_info': get_vm_info(), 'error': message})
    else:
        return render(request, 'myapp/index.html', {'error': 'Method not allowed'})


def stop_virtual_machine(vm_name):
    conn = libvirt.open('qemu:///system')
    if conn is None:
        return False, 'Failed to open connection to qemu:///system'
    
    domain = conn.lookupByName(vm_name)
    if domain is None:
        return False, f'Virtual machine {vm_name} not found'

    # Check if the VM is not running before trying to stop it
    if not domain.isActive():
        return False, f'Virtual machine {vm_name} is not running, cannot be stopped'
    
    # Attempt to gracefully shut down the VM
    if domain.shutdown() == 0:
        return True, f'Successfully shut down virtual machine {vm_name}'
    else:
        return False, f'Failed to shut down virtual machine {vm_name}'


##########
##########   # Stop
##########


def pause_vm(request):
    if request.method == 'POST':
        vm_name = request.POST.get('vm_name')
        success, message = pause_virtual_machine(vm_name)
        if success:
            return redirect(reverse('vm_control') + "?success=" + message)
        else:
            return redirect(reverse('vm_control') + "?error=" + message)
    else:
        return redirect(reverse('vm_control') + "?error=Method not allowed")


def pause_virtual_machine(vm_name):
    conn = libvirt.open('qemu:///system')
    if conn is None:
        return False, "Failed to open connection to qemu:///system"

    domain = conn.lookupByName(vm_name)
    if domain is None:
        print("VM not found")
        return False, f"Virtual machine {vm_name} not found"

    if domain.isActive():
        result = domain.suspend()
        if result == 0:
            print("Successfully paused virtual machine")
            print(f"State after pausing: {domain.info()[0]}")  # This should reflect the paused state
            return True, "Successfully paused virtual machine"
        else:
            print("Failed to pause virtual machine")
            return False, "Failed to pause virtual machine"
    else:
        print("Virtual machine is not running")
        return False, "Virtual machine is not running"

   
##########
##########   # Resume
##########


def resume_vm(request):
    if request.method == 'POST':
        vm_name = request.POST.get('vm_name')
        print("Resume VM request received for:", vm_name)  # Add this line for debugging
        success, message = resume_virtual_machine(vm_name)
        if success:
            return render(request, 'myapp/index.html', {'vm_info': get_vm_info(), 'message': message})
        else:
            return render(request, 'myapp/index.html', {'vm_info': get_vm_info(), 'error': message})
    else:
        return render(request, 'myapp/index.html', {'error': 'Method not allowed'})


def resume_virtual_machine(vm_name):
    conn = libvirt.open('qemu:///system')
    if conn is None:
        return False, "Failed to open connection to qemu:///system"

    try:
        domain = conn.lookupByName(vm_name)
        if domain is None:
            return False, f"Virtual machine {vm_name} not found"

        state, _ = domain.state()
        if state == libvirt.VIR_DOMAIN_PAUSED:
            if domain.resume() == 0:
                return True, "Successfully resumed virtual machine"
            else:
                return False, "Failed to resume virtual machine"
        elif state == libvirt.VIR_DOMAIN_RUNNING:
            return False, "Virtual machine is already running"
        else:
            return False, f"Cannot resume virtual machine. Current state: {state}"
    except libvirt.libvirtError as e:
        return False, f"Error: {e}"


##########
##########   # Force off
##########


def force_off_vm(request):
    if request.method == 'POST':
        vm_name = request.POST.get('vm_name')
        if vm_name is None:
            return render(request, 'myapp/index.html', {'error': 'VM name not provided'})

        print("ForceOFF VM request received for:", vm_name)  # Add this line for debugging
        success, message = force_off_virtual_machine(vm_name)
        if success:
            return render(request, 'myapp/index.html', {'vm_info': get_vm_info(), 'message': message})
        else:
            return render(request, 'myapp/index.html', {'vm_info': get_vm_info(), 'error': message})
    else:
        return render(request, 'myapp/index.html', {'error': 'Method not allowed'})


def force_off_virtual_machine(vm_name):
    conn = libvirt.open('qemu:///system')
    if conn is None:
        return False, 'Failed to open connection to qemu:///system'

    domain = conn.lookupByName(vm_name)
    if domain is None:
        return False, f'Virtual machine {vm_name} not found'

    if domain.isActive():
        if domain.destroy() == 0:
            return True, f'Successfully forcefully shut down virtual machine {vm_name}'
        else:
            return False, f'Failed to forcefully shut down virtual machine {vm_name}'
    else:
        return False, f'Virtual machine {vm_name} is not active'


##########
##########   # EDIT XML
##########


# Display the XML edit form
def edit_vm_xml(request):
    if request.method == 'GET':
        vm_name = request.GET.get('vm_name')
        try:
            conn = libvirt.open('qemu:///system')
            if conn is None:
                raise Exception("Failed to open connection to qemu:///system")

            domain = conn.lookupByName(vm_name)
            if domain is None:
                raise Exception(f"Virtual machine {vm_name} not found")

            # Get the current XML
            xml_description = domain.XMLDesc()

            conn.close()
            return render(request, 'myapp/edit_xml.html', {'vm_name': vm_name, 'xml_description': xml_description})
        except libvirt.libvirtError as e:
            return redirect(reverse('vm_control') + f"?error=Error: {str(e)}")


# Update the VM XML configuration
def update_vm_xml(request):
    if request.method == 'POST':
        vm_name = request.POST.get('vm_name')
        updated_xml = request.POST.get('xml_description')
        try:
            conn = libvirt.open('qemu:///system')
            if conn is None:
                return HttpResponse('Failed to open connection to qemu:///system', status=500)

            domain = conn.lookupByName(vm_name)
            if domain.isPersistent():
                domain.undefine()  # Note: Only if necessary and safe

            # Define the new XML
            result = conn.defineXML(updated_xml)
            if not result:
                raise Exception("Failed to define new XML")
            
            conn.close()
            return redirect(f'/edit-vm-xml/?vm_name={vm_name}&saved=True')
        except libvirt.libvirtError as e:
            return HttpResponse(f'Error updating virtual machine: {str(e)}', status=500)


##########
##########   # New Disk, 1. Create Disk
##########


def create_disk_form(request, vm_name):
    # Renders a form where users can input the disk size
    return render(request, 'myapp/create_disk_form.html', {'vm_name': vm_name})


@csrf_exempt
def submit_create_disk(request, vm_name):
    if request.method == 'POST':
        size_gb = request.POST.get('size_gb')
        # unique_id = uuid.uuid4()  # Generate a unique identifier
        disk_id = get_next_disk_id(vm_name)
        image_path = os.path.join('/var/lib/libvirt/images', f"{vm_name}_disk_no_{disk_id}.qcow2")

        try:
            subprocess.run(['sudo', 'qemu-img', 'create', '-f', 'qcow2', image_path, f'{size_gb}G'], check=True)
            success_message = 'Disk created successfully'
            return render(request, 'myapp/create_disk_form.html', {'vm_name': vm_name, 'success_message': success_message})
        except subprocess.CalledProcessError as e:
            error_message = f"Failed to create disk: {e}"
            return render(request, 'myapp/create_disk_form.html', {'vm_name': vm_name, 'error_message': error_message})
    else:
        error_message = 'Invalid request'
        return render(request, 'myapp/create_disk_form.html', {'vm_name': vm_name, 'error_message': error_message})


# Placeholder function to get the next disk ID
def get_next_disk_id(vm_name):
    try:
        with open(f'/tmp/{vm_name}_disk_id.txt', 'r') as file:
            last_id = int(file.read().strip())
    except FileNotFoundError:
        last_id = 0

    next_id = (last_id % 1000) + 1  # Cycles from 1 to 100

    with open(f'/tmp/{vm_name}_disk_id.txt', 'w') as file:
        file.write(str(next_id))

    return next_id


##########
##########   # New Disk, 2. Add exist Disk or Image.
##########


def get_libvirt_connection():
    try:
        conn = libvirt.open('qemu:///system')
        if conn is None:
            raise Exception("Failed to open connection to qemu:///system")
        return conn
    except libvirt.libvirtError as error:
        raise Exception(f"Failed to connect to libvirt: {str(e)}")


def list_existing_disks(request, vm_name):
    image_dir = '/var/lib/libvirt/images'
    disks = [f for f in os.listdir(image_dir) if f.startswith(f"{vm_name}_disk")]
    images = [f for f in os.listdir(image_dir) if f.startswith(f"{vm_name}_image")]
    return render(request, 'myapp/existing_disks.html', {'vm_name': vm_name, 'disks': disks, 'images': images})


def use_disk(request, vm_name, disk):
    if request.method == 'POST':
        try:
            conn = get_libvirt_connection()
            domain = conn.lookupByName(vm_name)
            if not domain.isActive():
                return HttpResponse("Operation failed: Domain is not running.", status=400)

            # Retrieve the existing disk targets to avoid conflicts
            xml_desc = domain.XMLDesc()
            used_targets = set()
            xml = ET.fromstring(xml_desc)
            for disk_elem in xml.findall('.//devices/disk/target'):
                used_targets.add(disk_elem.get('dev'))

            # Find the next available target
            for i in range(97, 123):  # ASCII values for 'a' to 'z'
                candidate = f'vd{chr(i)}'
                if candidate not in used_targets:
                    target_dev = candidate
                    break
            else:
                return HttpResponse("Failed to find available target device.", status=500)

            disk_xml = f"""
            <disk type='file' device='disk'>
                <driver name='qemu' type='qcow2'/>
                <source file='/var/lib/libvirt/images/{disk}'/>
                <target dev='{target_dev}' bus='virtio'/>
            </disk>
            """
            domain.attachDeviceFlags(disk_xml, libvirt.VIR_DOMAIN_AFFECT_CONFIG)
            return HttpResponse(f"Disk {disk} is now being used with VM {vm_name} on target {target_dev}.")
        except libvirt.libvirtError as e:
            return HttpResponse(f"Failed to attach disk: {str(e)}", status=500)



def delete_disk(request, vm_name, disk):
    if request.method == 'POST':
        disk_path = f"/var/lib/libvirt/images/{disk}"
        try:
            subprocess.run(['sudo', 'rm', disk_path], check=True)
            return HttpResponse(f"Disk {disk} deleted successfully.")
        except subprocess.CalledProcessError as e:
            return HttpResponse(f"Error deleting disk: {str(e)}", status=500)



def use_image(request, vm_name, image):
    if request.method == 'POST':
        # Implement logic to "use" the image
        return HttpResponse("Image is now in use. FAKEEEEE")


def delete_image(request, vm_name, image):
    if request.method == 'POST':
        try:
            image_path = f"/var/lib/libvirt/images/{image}"
            if os.path.exists(image_path):
                os.remove(image_path)
                return HttpResponse(f"Image {image} deleted successfully.")
            else:
                return HttpResponse("Image file not found.", status=404)
        except Exception as e:
            return HttpResponse(f"Error deleting image: {str(e)}", status=500)


##########
##########   # Add Network
##########