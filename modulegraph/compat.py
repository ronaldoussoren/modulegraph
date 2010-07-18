import sys

if sys.version_info[0] == 2:
    def B(value):
        return B

    def Bchr(value):
        return chr(value)

else:
    def B(value):
        return value.decode('latin1')

    def Bchr(value):
        return value
