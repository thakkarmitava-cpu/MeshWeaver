# MeshWeaver

MeshWeaver is a distributed task execution system for executing
Python functions remotely.

## Week 1: Serialization & Remote Execution

### Features

- Function serialization using cloudpickle
- Function argument serialization
- Socket-based task transfer
- Task deserialization on receiver
- Remote function execution
- Result serialization
- Result transfer back to client
- Addition and multiplication testing

## Execution Flow

Client
  ↓
Serialize function + arguments
  ↓
Socket
  ↓
Server
  ↓
Deserialize task
  ↓
Execute function
  ↓
Serialize result
  ↓
Socket
  ↓
Client receives result

## Tested Examples

Addition:

10 + 20 = 30

Multiplication:

10 × 20 = 200

## Run

```bash
python -m integration.remote_test