# MOE/EMIS Local Acquisition Handoff

## Why this exists

Edu Hub's hosted acquisition environments can reach `emis.gov.eg` but repeatedly time out against the current public Egyptian Schools Directory at `search.emis.gov.eg`.

The directory is still publicly referenced in 2026 and is the official route for searching Egyptian schools. We therefore treat this as a network-reachability problem, not as permission to replace the official registry with a secondary directory.

## Gate 1 — Capture and analyze the current live contract from Egypt

From a Windows/macOS/Linux machine on an Egypt-reachable network:

```bash
git clone https://github.com/admonkstudio/edu-hub.git
cd edu-hub
git checkout edu-data-1-national-registry
python -m venv .venv
```

Windows PowerShell:

```powershell
.\.venv\Scripts\Activate.ps1
pip install -r tools/data-acquisition/requirements.txt
python tools/data-acquisition/run_emis_local_capture.py
```

macOS/Linux:

```bash
source .venv/bin/activate
pip install -r tools/data-acquisition/requirements.txt
python tools/data-acquisition/run_emis_local_capture.py
```

The one-command handoff performs only two safe operations:

1. capture the public page/form contract;
2. analyze the saved evidence offline to determine whether pilot-adapter design is unblocked.

It does **not** enumerate schools or submit search forms.

Expected output folder:

```text
artifacts/emis-local-capture/
  capture-report.json
  enumerator-contract.json
  *.html
```

The capture currently probes:

- `https://search.emis.gov.eg/`
- `https://search.emis.gov.eg/sch_data.aspx`
- `https://search.emis.gov.eg/search_schpriv.aspx`

The capture records:

- status/final URLs and timing;
- SHA-256 of each captured page;
- form method/action;
- field names/IDs and associated labels where exposed;
- public select option values/text;
- ASP.NET state-field **names** without copying hidden state values into the JSON manifest;
- postback/autopostback behavior;
- referenced scripts;
- candidate public endpoints/links;
- a safety manifest confirming no authentication, access-control bypass or bulk enumeration occurred.

The raw public HTML remains the evidence copy used to understand live form state. `enumerator-contract.json` ranks candidate search forms and infers likely filter roles such as governorate/administration/stage only as adapter-design hints. Inference is never treated as source data.

### Manual two-step form

If needed, the two steps can still be run separately:

```bash
python tools/data-acquisition/emis_local_capture.py
python tools/data-acquisition/registry/analyze_emis_capture.py
```

## Do not bulk scrape at this stage

The first successful Egypt-local run is still a **contract capture**. Even when `enumerator-contract.json` reports `adapter_design_unblocked=true`, that only authorizes implementation of a bounded pilot adapter. It does not authorize national enumeration.

This avoids repeating the previous mistake of coding assumptions around historical endpoints and then treating partial results as a national registry.

## Gate 2 — Build/test the bounded enumerator

After a successful capture and analysis, the next adapter must:

1. preserve ASP.NET form state correctly;
2. preserve source-declared postback dependencies between filters;
3. enumerate only public geographic/classification filters rather than guessing school names;
4. retain every stable native school identifier exposed by the source;
5. follow public result pagination;
6. preserve source-shaped payloads before normalization;
7. rate-limit conservatively and respect server errors/retry-after responses;
8. checkpoint by governorate/administration so a failure cannot invalidate the entire national run;
9. write failed filter combinations explicitly for targeted repair;
10. never use authentication or bypass controls;
11. validate a small governorate/administration pilot before scaling;
12. never present the job as complete until coverage is reconciled against the official 62,690-school 2025/26 universe and the source's actual scope.

The pilot must write a machine-readable report with requested combinations, successful combinations, failed combinations, source IDs, duplicate IDs, pagination evidence and zero canonical/public mutations.

## Gate 3 — National acquisition

Once the tested enumerator passes a small governorate pilot:

```text
MOE public directory
  -> governorate shards
  -> administration/filter shards
  -> owned raw JSONL/SQLite/Postgres archive
  -> field inventory
  -> source-ID coverage audit
  -> staging/matching
```

The national run should occur on a stable Egypt-reachable worker rather than GitHub-hosted runners if the directory continues to block or time out from overseas infrastructure.

## Alternative / preferred official route

The repository also contains a formal MOE/EMIS data request. A current machine-readable export from the Ministry is preferable to crawling when the Ministry can provide it, because it can retain native identifiers, code tables and fields not exposed in the public directory.

These are parallel paths: running the public capture does not replace the official export request.

## Evidence preservation

Every successful capture/run should store:

- retrieval timestamp;
- source URL;
- source record/native ID;
- raw HTML/response or source-shaped payload as appropriate;
- SHA-256 hash;
- acquisition run ID;
- errors/failed shards;
- source field inventory.

No EMIS record is published directly. It flows through `edu_raw -> edu_staging -> edu_core -> public projection`.
