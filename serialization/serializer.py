import cloudpickle


def serialize_task(function, *args, **kwargs) -> bytes:
    """Serialize a function and its arguments into bytes."""
    return cloudpickle.dumps({
        "function": function,
        "args": args,
        "kwargs": kwargs,
    })


def deserialize_task(data: bytes):
    """Deserialize task bytes into function and arguments."""
    task = cloudpickle.loads(data)

    return (
        task["function"],
        task["args"],
        task["kwargs"],
    )


def execute_task(data: bytes):
    """Deserialize and execute a task."""
    function, args, kwargs = deserialize_task(data)

    return function(*args, **kwargs)


def serialize_result(result) -> bytes:
    """Serialize an execution result into bytes."""
    return cloudpickle.dumps(result)


def deserialize_result(data: bytes):
    """Deserialize result bytes back into a Python object."""
    return cloudpickle.loads(data)


# -------------------------
# Local tests
# -------------------------

def add(a, b):
    return a + b


def multiply(a, b):
    return a * b


if __name__ == "__main__":
    # Addition
    task = serialize_task(add, 10, 20)
    result = execute_task(task)

    result_data = serialize_result(result)
    final_result = deserialize_result(result_data)

    print("Addition:", final_result)

    # Multiplication
    task = serialize_task(multiply, 5, 6)
    result = execute_task(task)

    result_data = serialize_result(result)
    final_result = deserialize_result(result_data)

    print("Multiplication:", final_result)