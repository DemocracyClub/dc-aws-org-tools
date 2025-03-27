from dataclasses import dataclass


@dataclass
class GithubActionsConfig:
    repo_name: str
    github_org: str = "DemocracyClub"


dc_data_baker_config = GithubActionsConfig(
    repo_name="dc-data-baker",
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
