class InvalidUsage(Exception):
    status_code = 400

    def __init__(self, message, status_code=None, payload=None, error_type=None):
        Exception.__init__(self)
        self.message = message
        if status_code is not None:
            self.status_code = status_code
        self.payload = payload
        self.error_type = error_type

    def to_dict(self):
        rv = dict(self.payload or ())
        rv['status_code'] = self.status_code
        rv['message'] = self.message
        return rv

    def get_error_type(self):
        return self.error_type
