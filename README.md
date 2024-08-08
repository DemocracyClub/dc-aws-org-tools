# AWS Organization Account Checker

This project contains Python utilities for iterating over AWS accounts in an AWS
Organization and performing various
checks.

## Installation

**Install the required packages:**

Requires Python 3.12

 ```bash
 pip install -r requirements.txt
 ```

## Authentication

You need to be authenticated to the `Root Root - DC` account before running the
scripts.

## Usage

### EachAccount

The `EachAccount` class can be used as an iterator or a decorator to yield a
session for each account in the
organization.

#### Usage as an Iterator

```python
from utils import EachAccount

for account in EachAccount():
    # Perform actions with account.session
    print(account.name)
```

#### Usage as a Decorator

```python
from utils import EachAccount


@EachAccount()
def my_function(account):
    # Perform actions with account.session
    print(account.name)


if __name__ == "__main__":
    my_function()
```

### Example: List S3 Buckets in Each Account

You can use `EachAccount` to perform various tasks in each account. Here is an
example script to list S3
buckets in each account:

Create a new file named `list_s3_buckets.py`:

```python
from utils import EachAccount


@EachAccount()
def list_s3_buckets(account):
    s3_client = account.session.client("s3")
    response = s3_client.list_buckets()
    buckets = [bucket['Name'] for bucket in response['Buckets']]
    print(f"Account: {account.name}, S3 Buckets: {buckets}")


if __name__ == "__main__":
    list_s3_buckets()
```

Run the script using the following command:

```bash
python list_s3_buckets.py
```
