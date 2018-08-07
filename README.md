# Call

Thread-based, JS-like asynchronous calls for Python. Works in both Python 2.7 and Python 3.5+.

## Install

You will be soon able to install through pypi.

```bash
git clone https://gitlab.com/solarliner/call.git
cd call
# Activate virtualenv if needed
python setup.py install
```

The library requires no other dependencies, and (will soon) support Python's `await` keyword.

## Use

Create a call:

```python
def cb(resolve, reject):
    result = factorial(100)
    resolve(result)
    
call = Call(cb)
```

Chain calls with the `then` keyword

```python
call = Call(cb).then(lambda val: print(val))
```

Catch errors:

```python
call = Call(cb)\
    .then(lambda val: raise Exception())\
    .catch(lambda err: print('Whoops'))
```

Compose calls:
```python
results = Call.all([Call(cb) for _ in range(10)])
```

Block thread until resolved (or raises on failure):
```python
result = call.wait()
```

Wait for call to either resolve or reject
```python
call.join()
result = call.data  # Not recommended
```