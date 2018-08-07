from threading import Thread
from typing import Callable, Any, TypeVar, Optional
from typing import Iterable

__all__ = ['Call']

T = TypeVar('T')
TT = TypeVar('TT')
E = TypeVar('E')

Thenable = Callable[[T], TT]
Resolvable = Callable[[T], None]
Rejectable = Callable[[E], None]
Callback = Callable[[Callable, Callable], Any]


class Call:
    """Asynchronously run code, letting further code subscribe to resolved values or failed exceptions."""
    PENDING = 'PENDING'
    RESOLVED = 'RESOLVED'
    REJECTED = 'REJECTED'

    def __init__(self, callback):
        # type: (Callback) -> Call
        """Initialize a new asynchronous Call.
        The callback must have signature (resolve, reject), which are two callback functions of their own; the first one
        is to be called with the resulting value, while the second one is to be called with an error.
        It is vividly recommended that the value in reject be an Exception.

        :param callback: Callback function. Must have (resolve, reject) functions."""
        self.status = self.PENDING
        self.data = None    # type: T
        self.error = None   # type: E
        self.t = Thread(target=callback, args=(self._on_resolve, self._on_rejected))
        self.t.start()

    def then(self, callback):
        # type: (Thenable) -> Call
        """Chain callback, called with the resolved value of the previous Call.

        :param callback: Callback function to be called with the resolved value of the current Call."""
        def cb(resolve, reject):
            # type: (Callable, Callable) -> None
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

    def catch(self, callback):
        # type: (Thenable) -> Call
        """Chain callback, called if a failure occured somewhere in the chain before this.

        :param callback: Callback function, called on error further up the chain."""
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
        # type: () -> T
        """Wait until call has resolved a value to return, or rejected to raise the exception."""
        self.t.join()
        if self.status == self.RESOLVED:
            return self.data
        else:
            if isinstance(self.error, Exception):
                raise self.error
            else:
                raise Exception(self.error)

    def join(self):
        # type: () -> None
        """Wait until the value has been resolved or rejected, but does not return the value nor raise."""
        self.t.join()

    @classmethod
    def resolve(cls, value=None):
        # type: (Optional[T]) -> Call
        """Create a Call that immediately resolves with the value

        :param value: Value to be resolved to"""
        return Call(lambda res, rej: res(value))

    @classmethod
    def reject(cls, error):
        # type: (E) -> Call
        """Create a Call that immediately rejects with the error

        :param error: Error to be passed. If not an exception, will be turned into one."""
        if not isinstance(error, Exception):
            error = Exception(error)
        return Call(lambda res, rej: rej(error))

    @classmethod
    def all(cls, calls):
        # type: (Iterable[Call]) -> Call
        """Resolve a list of calls' resolved values, or fail with the first exception

        :param calls: List of calls to resolve, in the same order than the Calls list"""

        def func():
            values = []
            try:
                for call in calls:
                    values.append(call.wait())
            except Exception:
                raise
            return values

        return Call.from_function(func)

    @classmethod
    def from_function(cls, func, *args, **kwargs):
        # type: (Callable[[Any], T], *Any, **Any) -> Call
        """Create a Call from a synchronous function. The function will then be called asynchronously, its return
        value used as the resolved value, and any exception raised as a reject error value.

        :param func: Synchronous function to be called
        :param args: Positional arguments to be passed to the function func
        :param kwargs: Dictionary arguments to be passed to the function func"""
        def cb(resolve, reject):
            # type: (Callable, Callable) -> None
            try:
                resolve(func(*args, **kwargs))
            except Exception as e:
                reject(e)
        return Call(cb)

    def _on_resolve(self, data):
        # type: (T) -> None
        """DO NOT USE. IS INTERNAL"""
        self.data = data
        self.error = None
        self.status = self.RESOLVED

    def _on_rejected(self, error):
        # type: (E) -> None
        """DO NOT USE. IS INTERNAL"""
        self.error = error
        self.data = None
        self.status = self.REJECTED
