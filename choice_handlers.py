from db import PostgresqlDB
from abc import ABC, abstractmethod


class ChoiceHandler(ABC):

    def __init__(self, db_table):
        self.db = PostgresqlDB()
        self.db_table = db_table

    @abstractmethod
    def retrieve_object_info(self, obj_id):
        pass

    @staticmethod
    def choose_object_from_list(data):
        objects_lst = [f"{x[0]}. {x[1][1]}" for x in enumerate(data)]
        print("Выберите нужный объект из списка ниже:\n")
        for y in objects_lst:
            print(y)
        while True:
            chosen_number = input("Ваш выбор:\n")
            for y in enumerate(data):
                if int(y[0]) == int(chosen_number):
                    return int(y[1][0])
            print("Вы ввели неверный номер")

    def create_object(self):
        new_object = input("Введите название для нового объекта:\n")
        self.db.create_record(self.db_table, new_object)

    def choose_from_list(self):
        qry_array = self.db.get_all_records(self.db_table)
        id = self.choose_object_from_list(qry_array)
        return id


class ProjectHandler(ChoiceHandler):

    def retrieve_object_info(self, obj_id):
        project = self.db.get_single_record(self.db_table, obj_id)
        contracts = self.db.get_project_contracts(project[0][0])
        print(f"Информация о выбранном проекте:\nНазвание: {project[0][1]}\nДата создания: {project[0][2]}\nДобавленные договора:\n")
        for contract in contracts:
            print(f"    {contract[1]}: {contract[4]}")

    def add_contract_to_project(self, id):
        available_contracts = self.db.get_contracts_by_status('active', project_id=id, exclude=True)
        contract_id = self.choose_object_from_list(available_contracts)
        self.db.add_contract_to_project(id, contract_id)

    def close_active_contract(self, id):
        contract = self.db.get_contracts_by_status('active', project_id=id)
        if contract:
            self.db.change_contract_status(contract[0][0], 'completed')
            print(f"Вы успешно изменили статус договора {contract[0][1]} на 'completed'")
        else:
            print("У данного проекта нет активных договоров")

    def any_active_contract_exists(self):
        return self.db.get_contracts_by_status('active')


class ContractHandler(ChoiceHandler):

    def retrieve_object_info(self, obj_id):
        project = self.db.get_single_record(self.db_table, obj_id)
        print(f"Информация о выбранном объекте:\nНазвание: {project[0][1]}\nДата создания: {project[0][2]}\n")

    def activate_contract(self):
        draft_contracts = self.db.get_contracts_by_status('draft')
        contract_id = self.choose_object_from_list(draft_contracts)
        self.db.change_contract_status(contract_id, 'active')

    def close_contract(self):
        active_contracts = self.db.get_contracts_by_status('active')
        contract_id = self.choose_object_from_list(active_contracts)
        self.db.change_contract_status(contract_id, 'completed')
