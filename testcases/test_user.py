import pytest
import allure


from api.task_api import UserAPI
from data.data_loader import load_test_data

@allure.feature('用户模块')
class TestCreateUser:
    def setup_class(self):
        self.api = UserAPI()


    test_data = load_test_data('test_data.json')
    success_cases = test_data['create_user_success']
    fail_cases = test_data['create_user_fail']

    @allure.story('正向案例')
    @allure.title('创建用户 - {user[username]}')
    @pytest.mark.parametrize('user',success_cases)
    def test_create_user_success(self, user):
        with allure.step('创建用户'):
            response = self.api.create_user(
                username = user['username'],
                role = user['role']
            )
        with allure.step('检查结果'):
            assert response.status_code == 201,\
                f'期望状态码为201，实际为{response.status_code}'
            data = response.json()
            assert data['username'] == user['username'], \
                f'期望用户名为{user["username"]}，实际为{data["username"]}'
            assert data['role'] == user['role'], \
                f'期望角色为{user["role"]}，实际为{data["role"]}'

    @allure.story('反向案例')
    @allure.title('创建用户 - {user[username]}')
    @pytest.mark.parametrize('user', fail_cases)
    def test_create_user_fail(self, user):
        with allure.step('创建用户'):
            response = self.api.create_user(
                username = user['username'],
                role = user['role']
            )
        with allure.step('检查结果'):
            assert response.status_code == 422,\
                f'期望状态码为422，实际为{response.status_code}'

    @allure.story("反向用例")
    @allure.title("查询不存在的用户")
    def test_get_user_not_found(self):
        with allure.step('查询不存在订单'):
            response = self.api.get_user_by_id(999999)
        with allure.step('检查结果'):
            assert response.status_code == 404,\
                f'期望状态码为404，实际为{response.status_code}'