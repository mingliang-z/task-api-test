import pytest
from api.task_api import UserAPI,ProjectAPI



@pytest.fixture(scope="class")
def test_user():

    """创建一个测试用户，整个测试类共享"""

    api = UserAPI()
    resp = api.create_user("测试用户","admin")
    return resp.json()