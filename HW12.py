from collections import UserDict
from datetime import datetime
from types import GeneratorType
from itertools import islice
import pickle

FILENAME = "book.dat"


class Field:
    ''' Базовий клас для полів запису '''
    def __init__(self, value: str) -> None:
        self.__value = None
        self.value = value

    def __str__(self) -> str:
        return str(self.__value)

class Name(Field):
    ''' Клас для зберігання імені контакту. '''
    @property
    def value(self) -> str:
        return self.__value
    
    @value.setter
    def value(self, value) -> None:
        self.__value = value

class Phone(Field):
    ''' Клас для зберігання номера телефону. '''
    @property
    def value(self):
        return self.__value

    @value.setter
    def value(self, new_value: str):
        ''' Вбудована перевірка, має бути 10 цифр '''
        PHONE_LENGTH = 10
        if len(new_value) == PHONE_LENGTH and new_value.isdigit():
            self.__value = new_value
        else:
            raise ValueError

class Birthday(Field):
    ''' Клас для зберігання дня народження. '''
    @property
    def value(self):
        return self.__value

    @value.setter
    def value(self, new_date: str) -> str:
        '''
        Вбудована перевірка, має бути правильний формат дати YYYY-MM-DD
        '''
        # TODO: Перевіряємо декілька варіантів формату дати:
        self.__value = datetime.strptime(new_date, '%Y-%m-%d').date()


    def __str__(self):
        return datetime.strftime(self.__value, '%d %B')

class Record:
    '''
    Клас для зберігання інформації про контакт, включаючи ім'я та список телефонів. 
    Відповідає за логіку додавання/видалення/редагування полів та зберігання поля Name
    '''

    def __init__(self, name: str, birthday=None) -> None:
        self.name = Name(name)
        self.phones = []
        if birthday:
            self.birthday = Birthday(birthday)

    def __str__(self) -> str:
        if hasattr(self, 'birthday'):
            __days_to_bdy = f"{self.days_to_birthday} days to next birthday" if self.days_to_birthday else f'it is TODAY!'
            __last_part = f"Birthday: {self.birthday}\n{__days_to_bdy}"
        else:
            __last_part = ""
        message = (
                f"Name: {self.name.value}\n"
                f"Phones: {', '.join(p.value for p in self.phones)}\n"
                f"{__last_part}"
            )
        return message

    def add_phone(self, phone: str) -> None:
        ''' Додавання номеру телефону до контакту '''
        if phone not in list(map(lambda x: x.value, self.phones)):
            self.phones.append(Phone(phone))

    def remove_phone(self, removing: str) -> None:
        ''' Видалення телефону контакта '''
        for phone in self.phones:
            if phone.value == removing:
                self.phones.remove(phone)

    def edit_phone(self, old_phone: str, new_phone: str) -> None:
        ''' Редагування телефону контакта '''
        if old_phone not in (ph.value for ph in self.phones):
            raise ValueError
        # it works, but I do not like it
        for index, phone in enumerate(self.phones):
            if phone.value == old_phone:
                self.phones[index].value = new_phone

    def find_phone(self, search: str) -> Phone:
        # -> Phone, not str !!!
        ''' Пошук телефону контакта '''
        # does it work at all ?
        for phone in self.phones:
            if phone.value == search:
                return phone
        return None

    def add_birthday(self, birthday: str) -> None:
        ''' Додавання дня народження до контакту '''
        self.birthday = Birthday(birthday)

    @property
    def days_to_birthday(self) -> int:
        ''' Кількість днів до наступного дня народження '''
        today = datetime.now().date()
        this_year_birthday = self.birthday.value.replace(year=today.year)
        next_year_birthday = self.birthday.value.replace(year=today.year+1)
        difference = (this_year_birthday - today).days
        if difference <= 0:
            difference = (next_year_birthday - today).days
        return difference

class AddressBook(UserDict):
    ''' Клас для зберігання та управління записами. '''

    def add_record(self, record: Record) -> None:
        '''
        Додавання запису до self.data.
        '''
        self.data[record.name.value] = record

    def find(self, name: str) -> Record:
        '''
        Пошук записів за іменем.
        '''
        record = self.data.get(name)
        # return record if record else None
        if record:
            return record
        else:
            raise KeyError

    def delete(self, name: str) -> None:
        ''' Видалення записів за іменем. '''
        if name in self.data:
            self.data.pop(name)

    def iterator(self, n=2) -> GeneratorType:
        ''' generator '''
        for i in range(0, len(self), n):
            yield islice(self.data.values(), i, i+n)

    def save(self, filename="book.dat", format='bin'):
        ''' TODO: format selection and using different formats '''
        with open(filename, 'wb') as fh:
            pickle.dump(self.data, fh)

    def load(self, filename="book.dat", format='bin'):
        ''' TODO: format selection and using different formats '''
        # check if filename provided as non-default argument, else -> request, if empty -> set default
        try:
            with open(filename, 'rb') as fh: 
                self.data = pickle.load(fh)
        except FileNotFoundError:
            print("File not found, using new book.")