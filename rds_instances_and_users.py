import csv
import sys

from utils import EachAccount, once_per_run

HOSTNAMES = set()


@EachAccount()
def list_all_rds_instances(account):
    rds_client = account.session.client("rds")

    out = csv.DictWriter(
        sys.stdout,
        fieldnames=[
            "account",
            "db_name",
            "instance_class",
            "engine",
            "engine_version",
            "hostname",
        ],
    )
    rows = []
    for instance in rds_client.describe_db_instances()["DBInstances"]:
        HOSTNAMES.add(instance["Endpoint"]["Address"])
        rows.append(
            {
                "account": account.name,
                "db_name": instance["DBInstanceIdentifier"],
                "instance_class": instance["DBInstanceClass"],
                "engine": instance["Engine"],
                "engine_version": instance["EngineVersion"],
                "hostname": instance["Endpoint"]["Address"],
            }
        )

    if rows:
        if once_per_run("rds_header"):
            out.writeheader()
        out.writerows(rows)

@EachAccount()
def accounts_using_each_rds_in_ssm(account):

    out = csv.DictWriter(
        sys.stdout,
        fieldnames=[
            "account",
            "param_name",
            "param_value",
        ],
    )

    rows = []
    ssm_client = account.session.client("ssm")
    paginator = ssm_client.get_paginator("describe_parameters")
    for page in paginator.paginate():
        for param in page["Parameters"]:
            param_name = param["Name"]

            response = ssm_client.get_parameter(Name=param_name, WithDecryption=True)
            param_value = response["Parameter"]["Value"]

            # Check if the parameter name contains any of the search strings
            if param_value in HOSTNAMES:
                rows.append(
                    {
                        "account": account.name,
                        "param_name": param_name,
                        "param_value": param_value,
                    }
                )
    if rows:
        if once_per_run("ssm_header"):
            out.writeheader()
        out.writerows(rows)


if __name__ == "__main__":
    list_all_rds_instances()
    print()
    print()
    print("----------------------------------")
    print()
    print()
    accounts_using_each_rds_in_ssm()
