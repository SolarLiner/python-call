from threading import Thread
from typing import Callable, Any, TypeVar

__all__ = ['Call']

T = TypeVar('T')
TT = TypeVar('TT')
E = TypeVar('E')

Thenable = Callable[[T], TT]
Resolvable = Callable[[T], None]
Rejectable = Callable[[E], None]
Callback = Callable[[Callable, Callable], Any]


class Call:
    PENDING = 'PENDING'
    RESOLVED = 'RESOLVED'
    REJECTED = 'REJECTED'

    def __init__(self, callback: Callback):
        self.status = self.PENDING
        self.chain = []
        self.t = Thread(target=callback, args=(self._on_resolve, self._on_rejected))
        self.t.start()

    def then(self, callback: Thenable):
        def cb(resolve: Callable, reject: Callable):
            self.t.join()
            if self.status == self.REJECTED:
                reject(self.error)
            else:
                try:
                    result = callback(self.data)
                    resolve(result)
                except Exception as e:
                    reject(e)

        return Call(cb)

    def catch(self, callback: Thenable):
        def cb(resolve, reject):
            self.t.join()
            if self.status == self.REJECTED:
                try:
                    result = callback(self.error)
                    resolve(result)
                except Exception as e:
                    reject(e)

        return Call(cb)

    def wait(self):
        self.t.join()
        if self.status == self.RESOLVED:
            return self.data
        else:
            if isinstance(self.error, Exception):
                raise self.error
            else:
                raise Exception(self.error)

    def join(self):
        self.t.join()

    @classmethod
    def resolve(cls, value: T):
        return Call(lambda res, rej: res(value))

    @classmethod
    def reject(cls, error: E):
        return Call(lambda res, rej: rej(error))

    def _on_resolve(self, data: T):
        self.data = data
        self.error = None
        self.status = self.RESOLVED

    def _on_rejected(self, error: E):
        self.error = error
        self.data = None
        self.status = self.REJECTED
