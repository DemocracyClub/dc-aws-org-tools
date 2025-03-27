import functools
from dataclasses import dataclass
from typing import Any

import boto3


@dataclass
class AWSAccount:
    name: str
    session: boto3.Session


class EachAccount:
    """Iterator or decorator to yield a session for each account in the organization."""

    def __init__(self):
        self.org_client = boto3.client("organizations")

    def list_accounts_raw(self):
        """List all accounts in the organisation in JSON format."""
        accounts = []
        paginator = self.org_client.get_paginator("list_accounts")
        for page in paginator.paginate():
            accounts.extend(page["Accounts"])
        return accounts

    def assume_role(self, account_id):
        """Assume role in the target account."""
        sts_client = boto3.client("sts")
        role_arn = f"arn:aws:iam::{account_id}:role/OrganizationAccountAccessRole"
        response = sts_client.assume_role(
            RoleArn=role_arn, RoleSessionName="OrgAccountSession"
        )
        credentials = response["Credentials"]
        return boto3.Session(
            aws_access_key_id=credentials["AccessKeyId"],
            aws_secret_access_key=credentials["SecretAccessKey"],
            aws_session_token=credentials["SessionToken"],
            region_name="eu-west-2",
        )

    def __iter__(self) -> AWSAccount:
        raw_accounts = self.list_accounts_raw()
        for raw_account in raw_accounts:
            if raw_account["Name"] == "Root Root - DC":
                continue
            if raw_account["Status"] == "ACTIVE":
                session = self.assume_role(raw_account["Id"])
                yield AWSAccount(name=raw_account["Name"], session=session)

    def __call__(self, func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            for session in self:
                func(session, *args, **kwargs)

        return wrapper


PER_RUN_VALUES = set()


def once_per_run(value: Any) -> bool:
    """
    Because @EachAccount ends up calling the function once per AWS account,
    it can be hard to print a single value once per run, e.g the header row of a CSV.

    This util stores values in a set. If it's seen the value before, then it returns False,
    else True and it will store the fact it's seen the value.

    Use by:

    ```
    if once_per_run("foo"):
        // Do a thing once

    ```
    """
    if value in PER_RUN_VALUES:
        return False
    PER_RUN_VALUES.add(value)
    return True
