import libvirt


def get_libvirt_connection():
    try:
        connection = libvirt.open('qemu:///system')
        if connection is None:
            raise Exception("Failed to open connection to qemu:///system")
        return connection
    except libvirt.libvirtError as e:
        raise Exception(f"Failed to connect to libvirt: {str(e)}")