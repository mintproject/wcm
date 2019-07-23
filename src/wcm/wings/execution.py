import os

import requests
from math import ceil
import json
from .auth import Auth
from .userop import UserOperation


class Execution(UserOperation):

    def __init__(self, server, exportURL, userid, domain):
        super(Execution, self).__init__(server, exportURL, userid, domain)
        self.limit = 100000

    def check_request(self, resp):
        try:
            resp.raise_for_status()
        except requests.exceptions.HTTPError as err:
            print(err)
        except requests.exceptions.RequestException as err:
            print(err)
        return resp

    def list_executions_by_page(self, page, pattern=None, status=None):
        start = self.limit*page
        params = {"start": start, "limit": self.limit}
        if pattern:
            params['pattern'] = pattern
        if status:
            params['status'] = status

        resp = self.session.get(self.get_request_url() + 'executions/getRunListSimple', params=params)
        return self.check_request(resp)

    def get_run_details(self, execution_id):
        postdata = {'run_id': execution_id}
        resp = self.session.post(self.get_request_url() + 'executions/getRunDetails', data=postdata)
        return self.check_request(resp)

    def delete_run(self, execution_id):
        json_data = json.dumps({"id": execution_id})
        postdata = {'json': json_data}
        headers = {
            'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8'
        }
        resp = self.session.post(self.get_request_url() + 'executions/deleteRun', data=postdata, headers=headers)
        return self.check_request(resp)

    def publish(self, execution_id):
        postdata = {'run_id': execution_id}
        resp = self.session.post(self.get_request_url() + 'executions/publishRun', data=postdata)
        return self.check_request(resp)
