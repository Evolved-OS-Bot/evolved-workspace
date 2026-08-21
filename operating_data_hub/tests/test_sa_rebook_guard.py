from operating_data_hub.sa_rebook_guard import classify_rebook_guard


def test_customer_branch_has_live_precedence():
    assert (
        classify_rebook_guard(
            ["strength assessment showed", " Member "],
            contact_type=" Customer ",
        )
        == "existing_customer_stop"
    )


def test_completed_assessment_branch_stops_non_member():
    assert (
        classify_rebook_guard(["STRENGTH   ASSESSMENT SHOWED"])
        == "assessment_completed_stop"
    )


def test_contact_without_exclusion_is_eligible():
    assert (
        classify_rebook_guard(["member", "organic"], contact_type="lead")
        == "eligible_for_rebooking"
    )
