from enum import Enum

class PortScanType(Enum):
    SYN = '-sS'
    TCP = '-sT'
    UDP = '-sU'

    def __str__(self):
        return self.name