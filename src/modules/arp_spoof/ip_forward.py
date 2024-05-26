import platform
import winreg
import subprocess

class IPForward:
    def __init__(self):
        self.platform = platform.system()
        self.platform_methods = {
            "Linux": self.set_ip_forwarding_linux,
            "Windows": self.set_ip_forwarding_windows,
            "Darwin": self.set_ip_forwarding_darwin,
        }

    def set_ip_forwarding_linux(self, state: int):
        FILE_PATH = '/proc/sys/net/ipv4/ip_forward'
        with open(FILE_PATH, 'w') as file:
            file.write(f'{state}\n')

    def set_ip_forwarding_windows(self, state: int):
        REG_PATH = r"SYSTEM\CurrentControlSet\Services\Tcpip\Parameters"
        key = winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, REG_PATH, 0,
                             winreg.KEY_WRITE)
        winreg.SetValueEx(key, "IPEnableRouter", 0, winreg.REG_DWORD, state)
        winreg.CloseKey(key)

    def set_ip_forwarding_darwin(self, state: int):
        SYSCTL_COMMAND = ["sysctl", "-w", f"net.inet.ip.forwarding={state}"]
        try:
            subprocess.run(SYSCTL_COMMAND, check=True)
        except subprocess.CalledProcessError:
            raise Exception("Failed to set IP forwarding. Are you running this as root?")

    def set_ip_forwarding(self, state: int):
        try:
            self.platform_methods[self.platform](state)
        except KeyError:
            raise Exception("Unsupported platform")

    def enable(self):
        self.set_ip_forwarding(1)

    def disable(self):
        self.set_ip_forwarding(0)