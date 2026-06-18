# run_id Specification

Every agent action in the ecosystem emits a `run_id` in this exact format. Cross-agent traceability (and Bhishma R10) depend on it.

## Format

```
<agent>-<YYYYMMDD-HHMMSSZ>-<6char-hash>
```

## Components

- **agent** — the lowercase agent name. Must match a name listed in `bhishma.md` or in the agents directory. Examples: `sanjaya`, `hanuman`, `vyasa`.
- **YYYYMMDD-HHMMSSZ** — UTC timestamp in ISO 8601 basic format with the `Z` suffix indicating UTC. (Bhishma R19.) The dash between date and time is mandatory; no colons.
- **6char-hash** — first 6 hex characters of the SHA-256 of the run's input arguments concatenated with the timestamp. Lowercase. Provides uniqueness when two runs land in the same second.

## Examples

```
hanuman-20260510-143012Z-a3f9b1
sanjaya-20260510-090000Z-5e2c14
vyasa-20260510-180000Z-c91e08
sahadeva-20260510-100000Z-77ab4f
nakula-20260510-090000Z-d10c2e
arjuna-20260510-153044Z-bb8902
narada-20260510-120800Z-419e7d
vidura-20260510-110015Z-3f0a55
```

## Where it appears

- First line of every per-run log file: `# run_id: hanuman-20260510-143012Z-a3f9b1`
- Frontmatter of every artifact (proposal, journal entry, report): `run_id: ...`
- Heartbeat entries (`logs/heartbeat.json` written by Nakula): `run_id` field
- Citations in proposals (Bhishma R10): `example_run_ids: [..., ..., ...]`

## Validation

A run_id is valid if and only if:

1. It matches the regex `^[a-z]+-\d{8}-\d{6}Z-[0-9a-f]{6}$`
2. The agent name segment exists in the live agents directory
3. The timestamp is parseable as UTC and is not in the future (allow 60s clock skew)
4. The hash is the first 6 hex chars of `SHA-256(args || timestamp)`, where `args` is the canonical JSON of the run's input arguments

Sahadeva includes a run_id format-conformance check in its weekly audit (Section 5: Anomalies).

## Generating a run_id (reference implementation)

```bash
gen_run_id() {
  local agent="$1"
  local args_json="$2"
  local ts=$(date -u +"%Y%m%d-%H%M%SZ")
  local hash=$(printf "%s%s" "$args_json" "$ts" | sha256sum | head -c 6)
  echo "${agent}-${ts}-${hash}"
}
```

```python
import hashlib, json, datetime

def gen_run_id(agent: str, args: dict) -> str:
    ts = datetime.datetime.now(datetime.timezone.utc).strftime("%Y%m%d-%H%M%SZ")
    payload = json.dumps(args, sort_keys=True, separators=(",", ":")) + ts
    h = hashlib.sha256(payload.encode()).hexdigest()[:6]
    return f"{agent}-{ts}-{h}"
```
