# Entry file for Kamailio configuration.
# Kamailio will call the mod_init function which should return
# a new object with the configuration inside

from utils import ksr_print
from Kamailio import Kamailio

def mod_init():
    ksr_print('From python mod init')
    return Kamailio()