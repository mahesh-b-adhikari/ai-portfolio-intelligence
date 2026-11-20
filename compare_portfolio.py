
import json
from datetime import datetime

status_rank = {
    "green": 1,
    "amber": 2,
    "red": 3
}

def calculate_percent_complete(initiative):
    completed_weight = 0

    for deliverable in initiative["deliverables"]:
        if deliverable["status"] == "complete":
            completed_weight += deliverable["weight"]

    return completed_weight

with open("portfolio_week_1.json", "r") as file:
    week_1 = json.load(file)

with open("portfolio_week_2.json", "r") as file:
    week_2 = json.load(file)

print(week_1["portfolio_name"])
print(
    "Comparison:",
    week_1["reporting_date"],
    "->",
    week_2["reporting_date"]
)


for initiative in week_1["initiatives"]:
    print(initiative["initiative_id"], initiative["name"])

status_deteriorations = []
print("\nSTATUS DETERIORATIONS")

for week_1_initiative in week_1["initiatives"]:
    initiative_id = week_1_initiative["initiative_id"]

    for week_2_initiative in week_2["initiatives"]:
        if week_2_initiative["initiative_id"] == initiative_id:

            old_status = week_1_initiative["status"]
            new_status = week_2_initiative["status"]

            if status_rank[new_status] > status_rank[old_status]:
                status_deteriorations.append(
                  {
                      "initiative_id": initiative_id,
                      "old_status": old_status,
                      "new_status": new_status
                  }
              )

print(status_deteriorations)

status_improvements = []
print("\nSTATUS IMPROVEMENTS")

for week_1_initiative in week_1["initiatives"]:
    initiative_id = week_1_initiative["initiative_id"]

    for week_2_initiative in week_2["initiatives"]:
        if week_2_initiative["initiative_id"] == initiative_id:

            old_status = week_1_initiative["status"]
            new_status = week_2_initiative["status"]

            if status_rank[new_status] < status_rank[old_status]:
              status_improvements.append(
                 {
                     "initiative_id": initiative_id,
                     "old_status": old_status,
                     "new_status": new_status
                 }
             )
print(status_improvements)

milestone_date_changes = []

print("\nMILESTONE DATE CHANGES")

for week_1_initiative in week_1["initiatives"]:
    initiative_id = week_1_initiative["initiative_id"]

    for week_2_initiative in week_2["initiatives"]:
        if week_2_initiative["initiative_id"] == initiative_id:

            old_date = datetime.strptime(
                week_1_initiative["milestone_date"],
                "%Y-%m-%d"
            )

            new_date = datetime.strptime(
                week_2_initiative["milestone_date"],
                "%Y-%m-%d"
            )

            if old_date != new_date:
                difference = (new_date - old_date).days

                   
                milestone_date_changes.append(
                       {
                           "initiative_id": initiative_id,
                           "old_date": week_1_initiative["milestone_date"],
                           "new_date": week_2_initiative["milestone_date"],
                           "change_days": difference
                       }
                   )               

print(milestone_date_changes)

completion_changes = []

print("\nCOMPLETION CHANGES")

for week_1_initiative in week_1["initiatives"]:
    initiative_id = week_1_initiative["initiative_id"]

    for week_2_initiative in week_2["initiatives"]:
        if week_2_initiative["initiative_id"] == initiative_id:

            old_complete = calculate_percent_complete(week_1_initiative)
            new_complete = calculate_percent_complete(week_2_initiative)

            if old_complete != new_complete:
                difference = new_complete - old_complete

                completion_changes.append(
                    {
                        "initiative_id": initiative_id,
                        "old_complete": old_complete,
                        "new_complete": new_complete,
                        "change": difference
                    }
                )

print(completion_changes)

new_risks_found = []

print("\nNEW RISKS")

for week_1_initiative in week_1["initiatives"]:
    initiative_id = week_1_initiative["initiative_id"]

    for week_2_initiative in week_2["initiatives"]:
        if week_2_initiative["initiative_id"] == initiative_id:

            old_risks = week_1_initiative["risks"]
            new_risks = week_2_initiative["risks"]

            for risk in new_risks:

                risk_existed_before = False

                for old_risk in old_risks:
                    if old_risk["id"] == risk["id"]:
                        risk_existed_before = True

                if risk_existed_before == False:
                    new_risks_found.append(
                        {
                            "initiative_id": initiative_id,
                            "risk_id": risk["id"],
                            "severity": risk["severity"],
                            "description": risk["description"]
                        }
                    )

print(new_risks_found)

changed_risks = []

print("\nCHANGED RISKS")

for week_1_initiative in week_1["initiatives"]:
    initiative_id = week_1_initiative["initiative_id"]

    for week_2_initiative in week_2["initiatives"]:
        if week_2_initiative["initiative_id"] == initiative_id:

            old_risks = week_1_initiative["risks"]
            new_risks = week_2_initiative["risks"]

            for new_risk in new_risks:

                for old_risk in old_risks:

                    if old_risk["id"] == new_risk["id"]:

                        if old_risk["severity"] != new_risk["severity"]:
                            changed_risks.append(
                                {
                                    "initiative_id": initiative_id,
                                    "risk_id": new_risk["id"],
                                    "old_severity": old_risk["severity"],
                                    "new_severity": new_risk["severity"],
                                    "description": new_risk["description"]
                                }
                            )

print(changed_risks)

resolved_risks = []

print("\nRESOLVED RISKS")

for week_1_initiative in week_1["initiatives"]:
    initiative_id = week_1_initiative["initiative_id"]

    for week_2_initiative in week_2["initiatives"]:
        if week_2_initiative["initiative_id"] == initiative_id:

            old_risks = week_1_initiative["risks"]
            new_risks = week_2_initiative["risks"]

            for old_risk in old_risks:

                risk_still_exists = False

                for new_risk in new_risks:
                    if new_risk["id"] == old_risk["id"]:
                        risk_still_exists = True

                if risk_still_exists == False:
                    resolved_risks.append(
                        {
                            "initiative_id": initiative_id,
                            "risk_id": old_risk["id"],
                            "severity": old_risk["severity"],
                            "description": old_risk["description"]
                        }
                    )

print(resolved_risks)

new_blockers_found = []

print("\nNEW BLOCKERS")

for week_1_initiative in week_1["initiatives"]:
    initiative_id = week_1_initiative["initiative_id"]

    for week_2_initiative in week_2["initiatives"]:
        if week_2_initiative["initiative_id"] == initiative_id:

            old_blockers = week_1_initiative["blockers"]
            new_blockers = week_2_initiative["blockers"]

            for blocker in new_blockers:

                blocker_existed_before = False

                for old_blocker in old_blockers:
                    if old_blocker["id"] == blocker["id"]:
                        blocker_existed_before = True

                if blocker_existed_before == False:
                    new_blockers_found.append(
                        {
                            "initiative_id": initiative_id,
                            "blocker_id": blocker["id"],
                            "severity": blocker["severity"],
                            "description": blocker["description"]
                        }
                    )

print(new_blockers_found)

new_decisions_found = []

print("\nNEW DECISIONS")

for week_1_initiative in week_1["initiatives"]:
    initiative_id = week_1_initiative["initiative_id"]

    for week_2_initiative in week_2["initiatives"]:
        if week_2_initiative["initiative_id"] == initiative_id:

            old_decisions = week_1_initiative["decisions_needed"]
            new_decisions = week_2_initiative["decisions_needed"]

            for decision in new_decisions:
                decision_text = decision.get("description", decision.get("decision"))
                decision_key = decision.get("id", decision_text)
                old_keys = [d.get("id", d.get("description", d.get("decision"))) for d in old_decisions]

                if decision_key not in old_keys:
                    new_decisions_found.append(
                        {
                            "initiative_id": initiative_id,
                            "decision_id": decision.get("id"),
                            "description": decision_text,
                            "due_date": decision.get("due_date", decision.get("needed_by")),
                            "status": decision.get("status"),
                            "impact_if_delayed": decision.get("impact_if_delayed")
                        }
                    )

print(new_decisions_found)

dependencies_found = []

print("\nDEPENDENCIES")

for initiative in week_2["initiatives"]:

    initiative_id = initiative["initiative_id"]
    dependencies = initiative["dependencies"]

    for dependency in dependencies:
        dependencies_found.append(
            {
                "initiative_id": initiative_id,
                "depends_on": dependency["initiative_id"]
            }
        )

print(dependencies_found)

dependency_deteriorations = []

print("\nDEPENDENCY DETERIORATIONS")

for initiative in week_2["initiatives"]:

    initiative_id = initiative["initiative_id"]

    for dependency in initiative["dependencies"]:

        dependency_id = dependency["initiative_id"]

        for week_1_dependency in week_1["initiatives"]:

            if week_1_dependency["initiative_id"] == dependency_id:

                for week_2_dependency in week_2["initiatives"]:

                    if week_2_dependency["initiative_id"] == dependency_id:

                        old_status = week_1_dependency["status"]
                        new_status = week_2_dependency["status"]

                        if status_rank[new_status] > status_rank[old_status]:
                            dependency_deteriorations.append(
                                {
                                    "initiative_id": initiative_id,
                                    "depends_on": dependency_id,
                                    "old_status": old_status,
                                    "new_status": new_status
                                }
                            )

print(dependency_deteriorations)

dependency_improvements = []

print("\nDEPENDENCY IMPROVEMENTS")

for initiative in week_2["initiatives"]:

    initiative_id = initiative["initiative_id"]

    for dependency in initiative["dependencies"]:

        dependency_id = dependency["initiative_id"]

        for week_1_dependency in week_1["initiatives"]:

            if week_1_dependency["initiative_id"] == dependency_id:

                for week_2_dependency in week_2["initiatives"]:

                    if week_2_dependency["initiative_id"] == dependency_id:

                        old_status = week_1_dependency["status"]
                        new_status = week_2_dependency["status"]

                        if status_rank[new_status] < status_rank[old_status]:
                            dependency_improvements.append(
                                {
                                    "initiative_id": initiative_id,
                                    "depends_on": dependency_id,
                                    "old_status": old_status,
                                    "new_status": new_status
                                }
                            )

print(dependency_improvements)

# Identify initiatives that remained green with no adverse change.
week_1_by_id = {i["initiative_id"]: i for i in week_1["initiatives"]}
week_2_by_id = {i["initiative_id"]: i for i in week_2["initiatives"]}

adverse_ids = set()
for collection in [status_deteriorations, milestone_date_changes, new_risks_found, changed_risks, new_blockers_found, new_decisions_found, dependency_deteriorations]:
    for item in collection:
        # milestone changes only disqualify slips, not accelerations
        if collection is milestone_date_changes and item.get("change_days", 0) <= 0:
            continue
        # changed risks only disqualify worsening severity
        if collection is changed_risks and status_rank.get(item.get("new_severity"), 0) <= status_rank.get(item.get("old_severity"), 0):
            continue
        adverse_ids.add(item["initiative_id"])

stable_on_track = []
for initiative_id, current in week_2_by_id.items():
    previous = week_1_by_id[initiative_id]
    if previous["status"] == "green" and current["status"] == "green" and initiative_id not in adverse_ids:
        stable_on_track.append({
            "initiative_id": initiative_id,
            "initiative_name": current["name"],
            "status": current["status"]
        })

print("\nSTABLE ON TRACK")
for item in stable_on_track:
    print(item["initiative_id"], "-", item["initiative_name"], "-", item["status"])

portfolio_changes = {
    "portfolio_name": week_1["portfolio_name"],

    "comparison": {
        "from": week_1["reporting_date"],
        "to": week_2["reporting_date"]
    },

    "status_deteriorations": status_deteriorations,
    "status_improvements": status_improvements,
    "milestone_date_changes": milestone_date_changes,
    "completion_changes": completion_changes,

    "new_risks": new_risks_found,
    "changed_risks": changed_risks,
    "resolved_risks": resolved_risks,

    "new_blockers": new_blockers_found,
    "new_decisions": new_decisions_found,

    "dependencies": dependencies_found,
    "dependency_deteriorations": dependency_deteriorations,
    "dependency_improvements": dependency_improvements,
    "stable_on_track": stable_on_track,
}

print("\nPORTFOLIO CHANGES")
print(json.dumps(portfolio_changes, indent=2))

with open("portfolio_changes.json", "w") as file:
    json.dump(portfolio_changes, file, indent=2)