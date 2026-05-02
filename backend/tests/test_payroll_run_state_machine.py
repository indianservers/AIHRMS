import pytest

from app.crud import crud_payroll
from app.models.payroll import PayrollRun


def test_payroll_run_status_machine_allows_only_forward_path():
    run = PayrollRun(status="draft")

    for status in [
        "inputs_pending",
        "calculated",
        "approved",
        "locked",
        "paid",
    ]:
        crud_payroll.transition_payroll_run_status(run, status)
        assert run.status == status


def test_payroll_run_status_machine_rejects_skipped_transition():
    run = PayrollRun(status="calculated")

    with pytest.raises(ValueError, match="calculated -> locked"):
        crud_payroll.transition_payroll_run_status(run, "locked")


def test_payroll_run_status_machine_normalizes_legacy_values():
    run = PayrollRun(status="Completed")

    crud_payroll.coerce_payroll_run_status(run)
    assert run.status == "calculated"

    crud_payroll.transition_payroll_run_status(run, "Approved")
    assert run.status == "approved"
