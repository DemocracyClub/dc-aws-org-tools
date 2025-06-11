from dataclasses import dataclass


@dataclass
class GithubActionsConfig:
    repo_name: str
    github_org: str = "DemocracyClub"
    policy_file: str = None


dc_data_baker_config = GithubActionsConfig(
    repo_name="dc-data-baker",
    policy_file="dc-data-baker.json",
)

dc_logging_config = GithubActionsConfig(
    repo_name="dc_logging", policy_file="dc_logging.json"
)


GITHUB_ACTIONS_PERMISSIONS = {
    "Staging - API - EC": [],
    "Production - API - EC": [],
    "Dev - API - EC": [],
    "Production - Aggregator API - DC": [dc_data_baker_config],
    "Dev - Aggregator API - DC": [dc_data_baker_config],
    "Staging - Aggregator API - DC": [dc_data_baker_config],
    "Production - ElectionLeaflets - DC": [],
    "Staging - ElectionLeaflets - DC": [],
    "Production - Every Election - DC": [],
    "Dev - Every Election - DC": [],
    "Staging - Every Election - DC": [],
    "Dev - Monitoring - DC": [dc_logging_config],
    "Production - Monitoring - DC": [dc_logging_config],
    "Dev - Postcode Lookup - EC": [],
    "Staging - Postcode Lookup - EC": [],
    "Production - Postcode Lookup - EC": [],
    "Staging - Where Do I Vote - DC": [],
    "Dev - Where Do I Vote - DC": [],
    "Production - Where Do I Vote - DC": [],
    "Staging - Who Can I Vote For - DC": [],
    "Production - Who Can I Vote For - DC": [],
    "Dev - Who Can I Vote For - DC": [],
}
