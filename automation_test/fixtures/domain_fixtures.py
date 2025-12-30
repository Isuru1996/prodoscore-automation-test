import pytest

from ..db.domain_utils import create_domain, update_domain_defaults


@pytest.fixture(scope="function", autouse=True, name="domain")
def domain_config(db_client, config, logger):
    """
    Sets up a domain with default values in the database for the given domain ID.
    Runs once per test function, before and after each test.
    """
    domain_id = config.get("domain.id")
    logger.info(f"Setting up domain defaults for domain ID: {domain_id}")
    update_domain_defaults(db_client, domain_id)
    domain = create_domain(db_client, domain_id)
    yield domain
    # Teardown: reset domain to defaults again
    logger.info(f"Tearing down domain defaults for domain ID: {domain_id}")
    update_domain_defaults(db_client, domain_id)
