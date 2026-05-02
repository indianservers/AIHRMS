from app.models.platform import IntegrationEvent


def test_integration_events_have_retry_worker_composite_index():
    indexes = {index.name: tuple(index.columns.keys()) for index in IntegrationEvent.__table__.indexes}

    assert indexes["idx_integration_event_type_status_retry"] == (
        "event_type",
        "status",
        "next_retry_at",
    )
