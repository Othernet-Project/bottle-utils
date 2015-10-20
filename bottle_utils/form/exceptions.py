

class ValidationError(Exception):

    def __init__(self, message, params, is_form=False):
        self.message = message
        self.params = params
        self.is_form = is_form
        super(ValidationError, self).__init__(message)

    def __str__(self):
        """Calls renderer function"""
        return self.render()

    def __unicode__(self):
        """Calls renderer function"""
        return self.render()
