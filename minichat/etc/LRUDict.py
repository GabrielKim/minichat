#-*- coding: utf-8 -*-

from collections import deque

class LRUDictforNumCheck(object):
    def __init__(self, capacity: int) -> None:
        super().__init__()

        self.__dict = {}
        self.__deque = deque([])
        self.__capacity = capacity;

    def delete(self, key: str) -> None:
        if key in self.__dict.keys() \
            and key in self.__deque:
            del self.__dict[key]
            self.__deque.remove(key)

    def front(self) -> dict:
        if len(self.__dict) > 0:
            _key = self.__deque[0]
            _value = self.__dict[_key]
            return {_key:_value}
        return {}

    def pop(self) -> dict:
        # delete and return to left
        _cached_dict = self.front()
        if len(_cached_dict) != 0:
            for _key in self.__deque:
                if _key in _cached_dict:
                    self.delete(_key)
                    break
        return _cached_dict

    def push(self, key: str, value: int) -> None:
        if len(self.__dict) < self.__capacity:
            self.__dict[key] = value
            self.__deque.append(key)

    def goBack(self, key: str) -> None:
        if key in self.__dict.keys() \
            and key in self.__deque:
            self.__deque.remove(key)
            self.__deque.append(key)

    def updateValue(self, key: str, value: int) -> None:
        self.__dict[key] = value