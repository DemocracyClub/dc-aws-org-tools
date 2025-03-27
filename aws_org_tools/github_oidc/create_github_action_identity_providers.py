import json
import sys
from pathlib import Path
from urllib.parse import urlparse

from github_action_config import (
    GITHUB_ACTIONS_PERMISSIONS,
)

# Add the parent directory to the path
root_dir = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(root_dir))

from aws_org_tools.utils import EachAccount  # noqa: E402


@EachAccount()
def configure_github_oicd_provider(account):
    iam_client = account.session.client("iam")
    account_name = account.name
    account_id = account.account_id
    account_details = f"'{account_name}' ({account_id})"
    print(
        f"\n{'=' * len(account_details)}\n{account_details}\n{'=' * len(account_details)}"
    )
    repos = GITHUB_ACTIONS_PERMISSIONS.get(account_name, None)
    github_oidc_url = "https://token.actions.githubusercontent.com"

    if repos is None:
        print(
            f"No entry for '{account_name}' found in GITHUB_ACTIONS_PERMISSIONS"
        )
        return

    if len(repos) == 0:
        print(
            f"No repos found in GITHUB_ACTIONS_PERMISSIONS entry for '{account_name}'."
        )
        return

    print(
        f"Doing get or create of Github OIDC Provider '{account_name}' ({account_id})"
    )
    github_oidc_provider_arn = get_github_oidc_provider(
        iam_client, account_id, github_oidc_url
    )
    if github_oidc_provider_arn:
        print(f"    Found GitHub OIDC provider: {github_oidc_provider_arn}")
    else:
        github_oidc_provider_arn = create_github_oidc_provider(
            iam_client, account_name, account_id, github_oidc_url
        )

    print(
        f"Setting up role for {len(repos)} repo{'s' if len(repos) == 1 else ''}"
    )
    for repo in repos:
        role_name = make_role(
            iam_client,
            github_oidc_provider_arn,
            repo.github_org,
            repo.repo_name,
        )

        attach_role_policy(iam_client, role_name)


def create_github_oidc_provider(
    iam_client, account_name, account_id, github_oidc_url, client_ids=None
):
    if client_ids is None:
        client_ids = ["sts.amazonaws.com"]
    try:
        response = iam_client.create_open_id_connect_provider(
            Url=github_oidc_url,
            ClientIDList=client_ids,
            Tags=[
                {"Key": "created-by", "Value": "dc-aws-org-tools"},
                {"Key": "name", "Value": "github-oidc-provider"},
            ],
        )
        print(
            f"    Created OpenID Connect provider in '{account_name}' ({account_id}): {response['OpenIDConnectProviderArn']}"
        )
        return response["OpenIDConnectProviderArn"]
    except Exception as e:
        raise Exception(
            f"Error creating GitHub OIDC provider in '{account_name}' ({account_id})."
        ) from e


def get_github_oidc_provider(iam_client, account_id, github_oidc_url):
    oidc_provider_arn = make_oidc_provider_arn(account_id, url=github_oidc_url)
    try:
        iam_client.get_open_id_connect_provider(
            OpenIDConnectProviderArn=oidc_provider_arn,
        )
        return oidc_provider_arn
    except iam_client.exceptions.NoSuchEntityException:
        return None
    except Exception as e:
        raise Exception(
            f"Error getting GitHub OIDC provider with arn: {oidc_provider_arn}."
        ) from e


def make_oidc_provider_arn(account_id, url):
    "arn:aws:iam::1234567890:oidc-provider/token.actions.githubusercontent.com"
    parsed_url = urlparse(url)
    return f"arn:aws:iam::{account_id}:oidc-provider/{parsed_url.netloc}"


def make_role(iam_client, github_oidc_provider_arn, github_org, github_repo):
    print(f"Doing get or create of role for {github_org}/{github_repo}")
    role_name = f"github-actions-role-for-{github_repo.replace(' ', '-')}"

    try:
        response = iam_client.create_role(
            RoleName=role_name,
            AssumeRolePolicyDocument=make_assume_role_policy_document(
                github_oidc_provider_arn, github_org, github_repo
            ),
            Description=f"Role for GitHub Actions deployment of {github_org}/{github_repo}",
        )
        print(f"    Created role: {role_name}")
        print(f"        {response['Role']['Arn']}")
        return role_name
    except iam_client.exceptions.EntityAlreadyExistsException:
        print(f"    Role {role_name} already exists.")
        response = iam_client.get_role(RoleName=role_name)
        print(f"        {response['Role']['Arn']}")
        return role_name
    except Exception as e:
        raise (f"Error making role for {github_org}/{github_repo}.") from e


def make_assume_role_policy_document(github_oidc_arn, github_org, github_repo):
    policy = {
        "Version": "2012-10-17",
        "Statement": [
            {
                "Effect": "Allow",
                "Principal": {
                    "Federated": github_oidc_arn,
                },
                "Action": "sts:AssumeRoleWithWebIdentity",
                "Condition": {
                    "StringLike": {
                        "token.actions.githubusercontent.com:sub": f"repo:{github_org}/{github_repo}:*"
                    },
                    "StringEquals": {
                        "token.actions.githubusercontent.com:aud": "sts.amazonaws.com"
                    },
                },
            }
        ],
    }
    return json.dumps(policy)


def attach_role_policy(iam_client, role_name):
    policy_name = "CDK_Deployer_Policy"
    try:
        iam_client.put_role_policy(
            RoleName=role_name,
            PolicyName=policy_name,
            PolicyDocument=json.dumps(
                {
                    "Version": "2012-10-17",
                    "Statement": [
                        {
                            "Effect": "Allow",
                            "Action": ["sts:AssumeRole"],
                            "Resource": ["arn:aws:iam::*:role/cdk-*"],
                        }
                    ],
                }
            ),
        )
        print(f"    put {policy_name} on role {role_name}")
    except Exception as e:
        raise Exception(
            f"Error putting policy {policy_name} on role {role_name}"
        ) from e


if __name__ == "__main__":
    configure_github_oicd_provider()
