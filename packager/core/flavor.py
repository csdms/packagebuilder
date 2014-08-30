from subprocess import call

def debian_check():
    ''' 
    Returns True if this is a Debian-based Linux system.
    '''
    return (call(["test", "-f", "/etc/debian_version"]) == 0)
