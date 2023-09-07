from typing import Callable, Dict

from choice_handlers import ProjectHandler, ContractHandler, HotkeysChecker, WorkFlowError
import functools


def add_header(method):
    @functools.wraps(method)
    def wrapper(*args, **kwargs):
        print("*" * 71)
        print("*" * 10 + " ВЫХОД: 'E' / ВСЕ ПРОЕКТЫ: 'P' / ВСЕ ДОГОВОРЫ: 'C' " + "*" * 10)
        print(" " * 20 + "*" * 31)
        print(" " * 30 + f"{method.__doc__}")
        result = method(*args, **kwargs)
        return result
    return wrapper


class MainMenu:

    def __init__(self):
        self.project_handler = ProjectHandler("projects")
        self.contract_handler = ContractHandler("contracts")
        self.hk_checker = HotkeysChecker()

    @staticmethod
    def _build_menu(menu: Dict) -> None:
        for x,y in menu.items():
            print(f"{x}. {y}")

    @add_header
    def main_menu(self) -> None:
        """ГЛАВНОЕ МЕНЮ"""
        menu = {1: "Проект", 2: "Договор", 3: "Завершить работу с программой"}
        self._build_menu(menu)
        choice = input("Ваш выбор: ")
        checked_input = self.hk_checker.check_input(choice)
        if checked_input and checked_input in menu.keys():
            if checked_input == 1:
                self.project_menu()
            elif checked_input == 2:
                self.contract_menu()
            elif checked_input == 3:
                self.hk_checker.quit()
        else:
            print("Вы ввели неверный запрос")
            self.main_menu()

    @add_header
    def project_menu(self) -> None:
        """МЕНЮ ПРОЕКТОВ"""
        menu = {1: "Создать новый проект", 2: "Выбрать проект"}
        self._build_menu(menu)
        choice = input("Ваш выбор: ")
        checked_input = self.hk_checker.check_input(choice)
        if checked_input and checked_input in menu.keys():
            if checked_input == 1:
                if self.project_handler.any_active_contract_exists():
                    self.project_handler.create_object()
                    print("Новый проект успешно создан")
                else:
                    WorkFlowError("Для начала Вы должны создать хотя бы один договор со статусом 'active'")\
                        .raise_error()
            elif checked_input == 2:
                project_id = self.project_handler.choose_from_list()
                self.single_project_menu(project_id)
        else:
            print("Вы ввели неверный запрос")
            self.project_menu()

    @add_header
    def single_project_menu(self, id: int) -> None:
        """ПРОСМОТР ПРОЕКТА"""
        self.project_handler.retrieve_object_info(id)
        menu = {1: "Добавить договор в проект", 2: "Завершить активный договор"}
        self._build_menu(menu)
        choice = input("Ваш выбор: ")
        checked_input = self.hk_checker.check_input(choice)
        if checked_input and checked_input in menu.keys():
            if checked_input == 1:
                if self.project_handler.already_has_active(id):
                    WorkFlowError("У проекта уже имеется один активный договор").raise_error()
                else:
                    self.project_handler.add_contract_to_project(id)
                    print("Договор успешно добавлен в проект")
            elif checked_input == 2:
                self.project_handler.close_active_contract(id)
                print("Договор успешно звершен")
        else:
            print("Вы ввели неверный запрос")
            self.single_project_menu(id)

    @add_header
    def contract_menu(self) -> None:
        """МЕНЮ ДОГОВОРОВ"""
        menu = {1: "Создать новый договор", 2: "Подтвердить договор", 3:"Завершить договор"}
        self._build_menu(menu)
        choice = input("Ваш выбор: ")
        checked_input = self.hk_checker.check_input(choice)
        if checked_input and checked_input in menu.keys():
            if checked_input == 1:
                self.contract_handler.create_object()
                print("Договор успешно создан")
            elif checked_input == 2:
                self.contract_handler.activate_contract()
                print("Договор успешно подписан")
            elif checked_input == 3:
                self.contract_handler.close_contract()
                print("Договор успешно завершен")
        else:
            print("Вы ввели неверный запрос")
            self.contract_menu()
