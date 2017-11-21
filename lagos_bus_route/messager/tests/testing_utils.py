class Response(object):
    def __init__(self, status_code, first_name=None):
        self.status_code = status_code
        self.first_name = first_name

    def json(self):
        return {'first_name': self.first_name}
