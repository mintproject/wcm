from .auth import Auth


class UserOperation(Auth):

    def __init__(self, server, exportURL, userid, domain):
        super(UserOperation, self).__init__(server, userid)
        self.exportURL = exportURL
        self.domain = domain

    def get_request_url(self):
        return self.server + "/users/" + self.userid + "/" + self.domain + "/"

    def get_export_url(self):
        return self.exportURL + "/export/users/" + self.userid + "/" + self.domain + "/"
