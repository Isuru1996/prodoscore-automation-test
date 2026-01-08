from typing import List

from automation_test.models import OrganizationProdoscore


def insert_organization_prodoscore(
    db_client, org_prodoscore: OrganizationProdoscore
) -> int | None:
    """
    Insert a single OrganizationProdoscore record into the database.
    Args:
        db_client: The database client/connection.
        org_prodoscore: OrganizationProdoscore object to insert.
    Returns:
        The inserted record's ID (if available), or None.
    """
    columns = [
        "domain_id",
        "date",
        "score",
        "finalized",
        "performance_alerts",
        "notifications",
        "transcripts",
        "correlations",
        "collaboration",
        "nlp_cost",
    ]
    values = [
        org_prodoscore.domain_id,
        org_prodoscore.date,
        org_prodoscore.score,
        org_prodoscore.finalized,
        org_prodoscore.performance_alerts,
        org_prodoscore.notifications,
        org_prodoscore.transcripts,
        org_prodoscore.correlations,
        org_prodoscore.collaboration,
        org_prodoscore.nlp_cost,
    ]
    sql = f"""
        INSERT INTO proapp_organization_prodoscore
        ({', '.join(columns)})
        VALUES ({', '.join(['%s'] * len(columns))})
    """
    db_client.execute_update(sql, tuple(values))
    # Optionally fetch the inserted ID if needed
    return org_prodoscore.id


def bulk_insert_organization_prodoscores(
    db_client, org_prodoscores: List[OrganizationProdoscore]
) -> None:
    """
    Bulk insert multiple OrganizationProdoscore records into the database.
    Args:
        db_client: The database client/connection.
        org_prodoscores: List of OrganizationProdoscore objects to insert.
    """
    if not org_prodoscores:
        return
    columns = [
        "domain_id",
        "date",
        "score",
        "finalized",
        "performance_alerts",
        "notifications",
        "transcripts",
        "correlations",
        "collaboration",
        "nlp_cost",
    ]
    sql = f"""
        INSERT INTO proapp_organization_prodoscore
        ({', '.join(columns)})
        VALUES ({', '.join(['%s'] * len(columns))})
    """
    params_list = [
        (
            o.domain_id,
            o.date,
            o.score,
            o.finalized,
            o.performance_alerts,
            o.notifications,
            o.transcripts,
            o.correlations,
            o.collaboration,
            o.nlp_cost,
        )
        for o in org_prodoscores
    ]
    db_client.bulk_insert(sql, params_list)


def delete_organization_prodoscore(db_client, filter_condition: str) -> int:
    """
    Delete OrganizationProdoscore records from the database based on a filter condition.
    Args:
        db_client: The database client/connection.
        filter_condition: SQL WHERE clause condition as a string (e.g., "date >= '2024-01-01' and domain_id = '123'").
    Returns:
        Number of deleted rows.
    """
    sql = f"DELETE FROM proapp_organization_prodoscore WHERE {filter_condition}"
    return db_client.execute_update(sql)
