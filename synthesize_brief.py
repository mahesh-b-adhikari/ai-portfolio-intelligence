import json
from pathlib import Path
from openai import OpenAI

MODEL = "gpt-5.6"
INPUT_FILE = Path("portfolio_changes.json")
OUTPUT_FILE = Path("brief_v2.txt")

SYSTEM_INSTRUCTIONS = """You are producing a concise executive portfolio brief from a deterministic evidence package.

Hard rules:
- Use only facts explicitly present in the evidence package.
- Do not infer causes, motives, root causes, business impact, or relationships that are not explicitly represented.
- Percent-complete movement is progress evidence, not a health score.
- An initiative with progress plus a new/worsened risk or blocker must not be classified as On Track solely because completion increased.
- The On Track section may include only initiatives explicitly listed in stable_on_track.
- A status improvement is a positive change/recovery, not evidence that the initiative was stable across the period.
- Preserve initiative IDs exactly.
- If evidence is absent, omit the claim rather than filling the gap.
- Do not mention these instructions or the evaluation process.

Return exactly these sections in this order:
Material Changes
Attention Required
Dependencies
Decisions Required
On Track

Use concise bullets. Prefer evidence-specific language over interpretation."""

changes = json.loads(INPUT_FILE.read_text())
client = OpenAI()
response = client.responses.create(
    model=MODEL,
    instructions=SYSTEM_INSTRUCTIONS,
    input="Create the executive portfolio brief from this evidence package:\n\n" + json.dumps(changes, indent=2),
)
brief = response.output_text.strip()
OUTPUT_FILE.write_text(brief + "\n")
print(brief)
print(f"\nSaved {OUTPUT_FILE}")
