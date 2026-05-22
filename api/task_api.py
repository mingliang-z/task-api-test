from asyncio import timeout
from http.client import responses

import requests


from config.config import config


class BaseAPI:
    def __init__(self):
        self.base_url = config.BASE_URL
        self.session = requests.Session()


    def get(self,path,**kwargs):
        response = self.get(self.base_url +path ,timeout= config.TIMEOUT,**kwargs)
        return response

    def post(self,path,**kwargs):
        response = self.post(self.base_url +path ,timeout= config.TIMEOUT,**kwargs)
        return response

    def put(self,path,**kwargs):
        response = self.put(self.base_url +path ,timeout= config.TIMEOUT,**kwargs)
        return response

    def delete(self,path,**kwargs):
        response = self.delete(self.base_url +path ,timeout= config.TIMEOUT,**kwargs)
        return response

    def patch(self,path,**kwargs):
        response = self.patch(self.base_url +path ,timeout= config.TIMEOUT,**kwargs)
        return response



class UserAPI(BaseAPI):


    def create_user(self, username, role="member"):
        body = {
            "username" : "张三",
            "role" : "admin"
        }
        return self.api.post("/users",json=body)


    def get_user_by_id(self,user_id):
        return self.api.get(f"/users/{user_id}")




class ProjectAPI(BaseAPI):
    pass




class TaskAPI(BaseAPI):
    pass