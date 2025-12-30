from ..models import Domain


def create_domain(db_client, domain_id):
    """
    Fetch a domain record from the database and return as a Domain model.
    """
    sql = "SELECT * FROM proapp_domain WHERE id = %s"
    result = db_client.fetch_one(sql, (domain_id,))
    if not result:
        raise ValueError(f"Domain with id {domain_id} not found")
    return Domain(
        id=result["id"],
        title=result["title"],
        origin=result["origin"],
        show_details=result["show_details"],
        workingdays=result["workingdays"],
        timezone=result["timezone"],
        workshift_enable=result["workshift_enable"],
        daystart=result["daystart"],
        dayend=result["dayend"],
        gap_time=result["gap_time"],
        active_time=result["active_time"],
        gap_time_start=result["gap_time_start"],
        gap_time_end=result["gap_time_end"],
        ipscanner_enabled=result["ipscanner_enabled"],
        ipscanner_method=result["ipscanner_method"],
        crx_modules=result["crx_modules"],
        collab_enabled=result["collab_enabled"],
        collab_modules=result["collab_modules"],
        workplace_prod=result["workplace_prod"],
    )


def update_domain_defaults(db_client, domain_id):
    """
    Update the domain with default values in the database for the given domain ID.
    """
    row_to_update = {
        "daystart": "00:00",
        "dayend": "23:59",
        "show_details": 1,
        "workingdays": "[0, 1, 2, 3, 4, 5, 6]",
        "timezone": "America/Los_Angeles",
        "workshift_enable": 0,
        "crx_modules": None,
        "collab_enabled": 0,
        "collab_modules": 0,
        "gap_time": 0,
        "active_time": 0,
        "ipscanner_enabled": 0,
        "workplace_prod": 0,
    }
    set_clause = ", ".join(f"{k} = %s" for k in row_to_update)
    values = list(row_to_update.values())
    sql = f"UPDATE proapp_domain SET {set_clause} WHERE id = %s"
    db_client.execute_update(sql, tuple(values + [domain_id]))
