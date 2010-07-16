###############  langlet importer definition ##################

from langlet_config import parent_langlet
from langscape.base.loader import BaseClass


class LangletImporter(BaseClass("Importer", parent_langlet)):
    '''
    Defines langlet specific import hooks.
    '''

