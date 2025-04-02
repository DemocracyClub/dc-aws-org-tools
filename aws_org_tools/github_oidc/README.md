# Github OpenID Connect

When we need to authenticate to AWS from github actions, we use the AWS provided [configure-aws-credentials](https://github.com/aws-actions/configure-aws-credentials) action.

This is able to make use of OpenID Connect (OIDC).

For each AWS account we need to:
* Configure IAM to trust Github
* Create a role with the necessary permissions to do whatever we need in CI. 

In practical terms when setting up aws auth from github actions in a new repository these are the steps to take:
* Create a new `GithubActionsConfig` in `aws_org_tools/github_oidc/github_action_config.py`
  * If you want to do anything more than `cdk deploy` (i.e. use boto3/aws cli) in your actions, you will need to add specific permissions in a policy document which you can add to the `aws_org_tools/github_oidc/policies/` directory.
* Add the new `GithubActionsConfig` to the repos `GITHUB_ACTIONS_PERMISSIONS` dictionary in the same module.
* Locally authenticate to the root org account
* run `uv run aws_org_tools/github_oidc/create_github_action_identity_providers.py`
* Look at the output, and grab the arn for the relevant role.
* Go to the github repository where you're setting up github actions.
  * create an environment that corresponds to the aws account you want to auth to.
  * Add this arn to the secrets in that environment.
  * Use `${{ secrets.AWS_ROLE_ARN }}` in your action to refer to the secret. 