import cloudpickle


def serialize_task(function, *args, **kwargs):
    """Serialize a function and its arguments."""
    return cloudpickle.dumps({
        "function": function,
        "args": args,
        "kwargs": kwargs,
    })


def deserialize_task(data):
    """Deserialize task data."""
    task = cloudpickle.loads(data)

    return (
        task["function"],
        task["args"],
        task["kwargs"],
    )


def execute_task(data):
    """Deserialize and execute a serialized task."""
    function, args, kwargs = deserialize_task(data)

    return function(*args, **kwargs)


def serialize_result(result):
    """Serialize the execution result."""
    return cloudpickle.dumps(result)


def deserialize_result(data):
    """Deserialize the execution result."""
    return cloudpickle.loads(data)


# Test functions
def add(a, b):
    return a + b


def multiply(a, b):
    return a * b


if __name__ == "__main__":
    # Create task
    task = serialize_task(add, 10, 20)

    print("Task serialized")

    # Execute task
    result = execute_task(task)

    print("Execution Result:", result)

    # Serialize result
    result_data = serialize_result(result)

    print("Result serialized")

    # Deserialize result
    final_result = deserialize_result(result_data)

    print("Final Result:", final_result)