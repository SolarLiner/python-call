from __future__ import print_function

import json
import os
import time
import unittest

from call import Call


# noinspection PyMethodMayBeStatic
class TestCall(unittest.TestCase):
    def callback_succeeds(self, resolve, _):
        resolve('Data')

    def callback_rejects(self, _, reject):
        reject('Fail')

    def callback_resolves_delay(self, resolve, _):
        time.sleep(2)
        resolve('Data')

    def callback_rejects_delay(self, _, reject):
        time.sleep(2)
        reject('Fail')

    def test_callback(self):
        call = Call(self.callback_resolves_delay)
        result = call.wait()
        self.assertEqual(result, 'Data')

    def test_rejects(self):
        with self.assertRaises(Exception):
            result = Call(self.callback_rejects_delay).wait()
            self.fail('Call should fail')

    def test_sets_status(self):
        call = Call(self.callback_succeeds)
        call.join()
        self.assertEqual(call.status, Call.RESOLVED)

        call = Call(self.callback_rejects)
        call.join()
        self.assertEqual(call.status, Call.REJECTED)

    def test_chains(self):
        call = Call(self.callback_resolves_delay).then(lambda val: val + ' appended')
        result = call.wait()

        self.assertEqual(result, 'Data appended')

    def test_chains_fail(self):
        call = Call(self.callback_rejects_delay).catch(lambda err: err)
        res = call.wait()
        self.assertEqual(res, 'Fail')

    def test_immediate_resolve(self):
        call = Call.resolve('Data')
        value = call.wait()
        self.assertEqual(value, 'Data')

    def test_immediate_reject(self):
        call = Call.reject(Exception('Something went wrong!'))
        with self.assertRaises(Exception):
            call.wait()
            self.fail('Call should fail')

    def test_all_class(self):
        def cb(res, rej):
            with open(os.path.join(os.path.dirname(__file__), 'data.json')) as f:
                if not f.readable():
                    rej('File not readable')
                res(f.read())

        call = Call(cb) \
            .then(lambda data: json.loads(data)) \
            .then(lambda data: data['app-id']) \
            .catch(lambda err: err)
        call.then(print)
        try:
            value = call.wait()
        except Exception as e:
            self.fail('Call.wait shouldn\'t throw as it is being caught')

        self.assertNotEqual(value, 'org.sindresorhus.Caprine')
        self.assertTrue(isinstance(value, Exception))
