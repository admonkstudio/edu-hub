# MOE/EMIS Local Acquisition Handoff

## Why this exists

Edu Hub's hosted acquisition environments can reach `emis.gov.eg` but repeatedly time out against the current public Egyptian Schools Directory at `search.emis.gov.eg`.

The directory is still publicly referenced in 2026 and is the official route for searching Egyptian schools. We therefore treat this as a network-reachability problem, not as permission to replace the official registry with a secondary directory.

## Gate 1 — Capture the current live contract from Egypt

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
python tools/data-acquisition/emis_local_capture.py
```

macOS/Linux:

```bash
source .venv/bin/activate
pip install -r tools/data-acquisition/requirements.txt
python tools/data-acquisition/emis_local_capture.py
```

Expected output folder:

```text
artifacts/emis-local-capture/
  capture-report.json
  *.html
```

The capture currently probes:

- `https://search.emis.gov.eg/`
- `https://search.emis.gov.eg/sch_data.aspx`
- `https://search.emis.gov.eg/search_schpriv.aspx`

The output records status/final URLs, timing, hashes, form methods/actions, input/select names, option lists, ASP.NET hidden-field names, referenced scripts and candidate endpoints.

## Do not bulk scrape at this stage

The first successful Egypt-local run is a **contract capture**. We review the returned current form structure and build the enumerator against what the server actually exposes now.

This avoids repeating the previous mistake of coding assumptions around historical endpoints and then treating partial results as a national registry.

## Gate 2 — Build/test the enumerator

After a successful capture, the next adapter must:

1. preserve ASP.NET form state correctly;
2. enumerate public geographic/classification filters rather than guessing school names;
3. retain every stable native school identifier exposed by the source;
4. follow public result pagination;
5. preserve source-shaped payloads before normalization;
6. rate-limit conservatively and respect server errors/retry-after responses;
7. checkpoint by governorate/administration so a failure cannot invalidate the entire national run;
8. write failed filter combinations explicitly for targeted repair;
9. never use authentication or bypass controls;
10. never present the job as complete until coverage is reconciled against the official 62,690-school 2025/26 universe and source scope.

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