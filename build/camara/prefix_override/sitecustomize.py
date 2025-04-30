import sys
if sys.prefix == '/usr':
    sys.real_prefix = sys.prefix
    sys.prefix = sys.exec_prefix = '/home/darhf/Manchester/camara/lectura_camara/camara/install/camara'
