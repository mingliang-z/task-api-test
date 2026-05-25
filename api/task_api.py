
import requests


from config.config import config


class BaseAPI:
    def __init__(self):
        self.base_url = config.BASE_URL
        self.session = requests.Session()


    def get(self,path,**kwargs):
        response = self.session.get(self.base_url +path ,timeout= config.TIMEOUT,**kwargs)
        return response

    def post(self,path,**kwargs):
        response = self.session.post(self.base_url +path ,timeout= config.TIMEOUT,**kwargs)
        return response

    def patch(self,path,**kwargs):
        response = self.session.patch(self.base_url +path ,timeout= config.TIMEOUT,**kwargs)
        return response



class UserAPI(BaseAPI):


    def create_user(self, username, role="member"):
        body = {
            "username" : username,
            "role" : role
        }
        return self.post("/users",json=body)


    def get_user_by_id(self,user_id):
        return self.get(f"/users/{user_id}")




class ProjectAPI(BaseAPI):
    def create_project(self, name, owner_id):
        body = {
            "name": name,
            "owner_id": owner_id
        }
        return self.post("/projects",json=body)

    def get_project_by_id(self,project_id):
        return self.get(f"/projects/{project_id}")

    def patch_project_archive(self,project_id,user_id):
        return self.patch(f"/projects/{project_id}/archive",params = {"user_id":user_id})





class TaskAPI(BaseAPI):
    def create_task(self,project_id,title,description,assignee_id,priority):
        body = {
              "project_id": project_id,
              "title": title,
              "description": description,
              "assignee_id": assignee_id,
              "priority": priority
        }
        return self.post("/tasks",json=body)

    def get_task_by_id(self,task_id):
        return self.get(f"/tasks/{task_id}")

    def get_tasks_list(self,project_id):
        return self.get(f"/projects/{project_id}/tasks")

    def patch_task_status(self,task_id,new_status):
        return self.patch(f"/tasks/{task_id}/status",json = {"new_status":new_status})

    def patch_task_assign(self,task_id,assignee_id):
        return self.patch(f"/tasks/{task_id}/assign",json = {"assignee_id":assignee_id})