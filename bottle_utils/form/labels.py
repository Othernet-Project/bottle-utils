from bottle_utils.common import unicode


class Label(object):

    def __init__(self, text, for_element):
        self.text = text
        self.for_element = for_element

    def __str__(self):
        """Calls renderer function"""
        return unicode(self.text)

    def __unicode__(self):
        """Calls renderer function"""
        return self.__str__()

    def __mod__(self, other):
        """ Provides string interpolation using % operator """
        return self.__str__() % other

    def format(self, *args, **kw):
        """ Provides string interpolation with .format() method """
        return self.__str__().format(*args, **kw)
