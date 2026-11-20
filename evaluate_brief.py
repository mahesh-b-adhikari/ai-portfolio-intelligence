import re


def evaluate_brief(brief, evidence, portfolio):
    """Check selected claims in an AI brief against source evidence."""

    findings = []

    valid_initiatives = {
        item["initiative_id"]
        for item in portfolio["initiatives"]
    }

    valid_risks = {
        item["risk_id"]
        for category in ("new_risks", "changed_risks", "resolved_risks")
        for item in evidence.get(category, [])
    }

    valid_blockers = {
        item["blocker_id"]
        for item in evidence.get("new_blockers", [])
    }

    # Check initiative identifiers
    for initiative_id in sorted(
        set(re.findall(r"\bPAY-\d+\b", brief))
    ):
        if initiative_id not in valid_initiatives:
            findings.append(f"Unknown initiative: {initiative_id}")

    # Check risk and blocker identifiers
    for identifier in sorted(
        set(re.findall(r"\b(?:R|B)-\d{2}-\d{2}\b", brief))
    ):
        if identifier not in valid_risks | valid_blockers:
            findings.append(f"Unsupported risk/blocker: {identifier}")

    # Check milestone delays when explicitly reported
    for change in evidence.get("milestone_date_changes", []):
        initiative_id = change["initiative_id"]

        lines = [
            line for line in brief.splitlines()
            if initiative_id in line
            and "milestone" in line.lower()
        ]

        for line in lines:
            match = re.search(r"(\d+)\s+days?", line)

            if match and int(match.group(1)) != change["change_days"]:
                findings.append(
                    f"{initiative_id}: reported delay "
                    f"{match.group(1)} days; "
                    f"expected {change['change_days']} days"
                )

    return {
        "passed": len(findings) == 0,
        "findings": findings,
    }