from typing import List, Tuple, Optional

from db import PostgresqlDB
from abc import ABC, abstractmethod
import sys


class ChoiceHandler(ABC):

    def __init__(self, db_table: str):
        self.db = PostgresqlDB()
        self.db_table = db_table

    @abstractmethod
    def retrieve_object_info(self, obj_id: int) -> None:
        pass

    @abstractmethod
    def retrieve_all_objects(self) -> None:
        pass

    @staticmethod
    def choose_object_from_list(data: List[Tuple]):
        objects_lst = [f"{x[0]}. {x[1][1]}" for x in enumerate(data, 1)]
        print("Выберите нужный объект из списка ниже:")
        for y in objects_lst:
            print(y)
        while True:
            chosen_number = input("Ваш выбор:\n")
            checker = HotkeysChecker()
            corr_input = checker.check_input(chosen_number)
            if corr_input or corr_input == 0:
                for y in enumerate(data, 1):
                    if y[0] == corr_input:
                        return int(y[1][0])
            elif corr_input == 'redirected':
                return
            print("Вы ввели неверный номер")

    def create_object(self) -> None:
        new_object = input("Введите название для нового объекта:\n")
        self.db.create_record(self.db_table, new_object)

    def choose_from_list(self) -> int:
        qry_array = self.db.get_all_records(self.db_table)
        id = self.choose_object_from_list(qry_array)
        return id


class ProjectHandler(ChoiceHandler):

    def retrieve_object_info(self, obj_id: int):
        project = self.db.get_single_record(self.db_table, obj_id)
        contracts = self.db.get_project_contracts(project[0][0])
        print(f"Информация о выбранном проекте:\nНазвание: {project[0][1]}\n"
              f"Дата создания: {project[0][2]}\nДобавленные договора:")
        for contract in contracts:
            print(f"    {contract[1]}: {contract[4]}")
        print()

    def retrieve_all_objects(self) -> None:
        projects = self.db.get_all_records(self.db_table)
        print('ВСЕ ПРОЕКТЫ\n')
        for project in projects:
            print(f"ID: {project[0]}, НАЗВАНИЕ: {project[1]}")

    def add_contract_to_project(self, id: int) -> None:
        available_contracts = self.db.get_contracts_by_status('active', project_id=id, exclude=True)
        contract_id = self.choose_object_from_list(available_contracts)
        self.db.add_contract_to_project(id, contract_id)

    def close_active_contract(self, id: int) -> None:
        contract = self.db.get_contracts_by_status('active', project_id=id)
        if contract:
            self.db.change_contract_status(contract[0][0], 'completed')
            print(f"Вы успешно изменили статус договора {contract[0][1]} на 'completed'")
        else:
            WorkFlowError("У данного проекта нет активных договоров").raise_error()

    def already_has_active(self, id: int) -> bool:
        ds = self.db.get_contracts_by_status("active", id)
        if ds:
            return True
        return False

    def any_active_contract_exists(self) -> bool:
        if self.db.get_contracts_by_status('active'):
            return True
        return False


class ContractHandler(ChoiceHandler):

    def retrieve_object_info(self, obj_id: int) -> None:
        project = self.db.get_single_record(self.db_table, obj_id)
        print(f"Информация о выбранном объекте:\nНазвание: {project[0][1]}\nДата создания: {project[0][2]}\n")

    def retrieve_all_objects(self) -> None:
        contracts = self.db.get_all_records(self.db_table)
        print('ВСЕ ДОГОВОРЫ\n')
        for contract in contracts:
            print(f"ID: {contract[0]}, НАЗВАНИЕ: {contract[1]}, ДАТА СОЗДАНИЯ: {contract[2]},"
                  f" ТЕКУЩИЙ СТАТУС: {contract[4]}")


    def activate_contract(self) -> None:
        draft_contracts = self.db.get_contracts_by_status('draft')
        contract_id = self.choose_object_from_list(draft_contracts)
        self.db.change_contract_status(contract_id, 'active')

    def close_contract(self) -> None:
        active_contracts = self.db.get_contracts_by_status('active')
        contract_id = self.choose_object_from_list(active_contracts)
        self.db.change_contract_status(contract_id, 'completed')


class HotkeysChecker:

    def __init__(self):
        self.project_handler = ProjectHandler("projects")
        self.contract_handler = ContractHandler("contracts")
        self.HOT_KEYS = {'E': self.quit,
                         'P': self.project_handler.retrieve_all_objects,
                         'C': self.contract_handler.retrieve_all_objects}

    def check_input(self, input_made: str) -> Optional[int]:
        entered_val = input_made.strip()
        corr_input = None
        if entered_val in self.HOT_KEYS:
            self.HOT_KEYS[entered_val]()
            WorkFlowError(" ").raise_error()
        else:
            try:
                corr_input = int(entered_val)
            except ValueError:
                return None
        return corr_input

    @staticmethod
    def quit() -> None:
        print('\nПриглашайте на стажировку!')
        sys.exit(0)

    def stop_input(self) -> None:
        while True:
            inp = input("Введите '+', чтобы продолжить...: ")
            if inp.strip() == '+':
                break


class WorkFlowError:
    def __init__(self, message: str):
        self.message = message

    def raise_error(self) -> None:
        print(self.message)
        while True:
            inp = input("Введите '+', чтобы продолжить...: ")
            if inp.strip() == '+':
                break
