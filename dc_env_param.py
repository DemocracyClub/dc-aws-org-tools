from botocore.exceptions import ClientError

from utils import EachAccount

param_name = "DC_ENVIRONMENT"


@EachAccount()
def check_dc_env_param_set(account):
    ssm_client = account.session.client("ssm")
    try:
        has_dc_env_set = ssm_client.get_parameter(Name=param_name)["Parameter"]["Value"]
    except ClientError as e:
        if e.response['Error']['Code'] == 'ParameterNotFound':
            has_dc_env_set = False
        else:
            raise

    print("\t".join([str(has_dc_env_set), account.name]))


@EachAccount()
def set_dc_env_values(account):
    ssm_client = account.session.client("ssm")
    try:
        has_dc_env_set = ssm_client.get_parameter(Name=param_name)["Parameter"]["Value"]
    except ClientError as e:
        if e.response['Error']['Code'] == 'ParameterNotFound':
            has_dc_env_set = False
        else:
            raise

    if not has_dc_env_set:
        env = None
        if account.name.startswith("Production -"):
            env = "production"
        if account.name.startswith("Staging -"):
            env = "staging"
        if account.name.startswith("Dev -"):
            env = "development"
        if env:
            ssm_client.put_parameter(Name=param_name, Value=env, Type="String")


if __name__ == "__main__":
    # Uncomment to check
    # check_dc_env_param_set()
    # Uncomment to set
    # set_dc_env_values()

    print("Look at the file ane uncomment depending on what you're doing")
