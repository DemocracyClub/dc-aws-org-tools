import csv
import sys

from botocore.exceptions import ClientError
from utils import EachAccount


@EachAccount()
def list_lambdas(account, writer):
    regions = account.session.get_available_regions("lambda")

    arns_by_region = {}

    for region in regions:
        tag_client = account.session.client(
            "resourcegroupstaggingapi", region_name=region
        )
        paginator = tag_client.get_paginator("get_resources")
        try:
            for page in paginator.paginate(
                ResourceTypeFilters=["lambda:function"]
            ):
                for resource in page["ResourceTagMappingList"]:
                    arn = resource["ResourceARN"]
                    arns_by_region.setdefault(region, []).append(arn)
        except ClientError:
            # There are some regions that aren't active, so we can skip them
            continue

    for region, arns in arns_by_region.items():
        lambda_client = account.session.client("lambda", region_name=region)
        for arn in arns:
            try:
                resp = lambda_client.get_function(FunctionName=arn)
                config = resp["Configuration"]
                writer.writerow(
                    [
                        account.account_id,
                        region,
                        config["FunctionName"],
                        config.get(
                            "Runtime", "Unknown"
                        ),  # e.g., python3.12, nodejs18.x
                        config["FunctionArn"],
                    ]
                )
            except lambda_client.exceptions.ResourceNotFoundException:
                continue


def list_all_lambdas():
    writer = csv.writer(sys.stdout, delimiter="\t")
    writer.writerow(["AccountID", "Region", "FunctionName", "Runtime", "ARN"])
    list_lambdas(writer)


if __name__ == "__main__":
    list_all_lambdas()
