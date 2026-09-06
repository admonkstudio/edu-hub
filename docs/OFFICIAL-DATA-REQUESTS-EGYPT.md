# Official Egypt Education Data Requests

Status: acquisition support. These requests are designed to obtain the **raw source datasets before Edu Hub chooses its canonical schema**.

## Request principle

Do not ask the authority to map data into an Edu Hub-defined field list. Ask for the **complete current extract with all columns available in the source system**, plus a data dictionary when one exists.

Preferred delivery formats, in order:

1. CSV UTF-8
2. XLSX
3. JSON / API export
4. database dump or another machine-readable format

PDF is acceptable only as supporting documentation, not as the preferred row-level dataset.

Every delivery should retain the authority's native record identifier wherever possible.

---

## A. Ministry of Education / EMIS — Egyptian Schools Directory

### Dataset requested

Current row-level extract behind the official **Egyptian Schools Directory — دليل المدارس المصرية**, which the current `emis.gov.eg/main.js` links to at `https://search.emis.gov.eg/`.

Known official 2025/26 aggregate coverage target: **62,690 schools**.

### Request

Please provide the latest complete machine-readable extract of all schools represented in the Egyptian Schools Directory / Ministry Education Management Information System for academic year 2025/2026 or the latest available date.

Please include **all source columns currently available**, without reducing the export to a predefined external schema.

Where available, please also include:

- the native unique school ID/code;
- Arabic and English names if both exist;
- governorate;
- educational administration/directorate;
- address/location fields;
- school type/classification;
- education stages/levels;
- gender model;
- language/system/curriculum classifications;
- ownership/management classification;
- operating/status fields;
- telephone/contact details;
- latitude/longitude or map identifiers;
- any public website/profile URL;
- academic-year/effective-date fields;
- last-update timestamp;
- lookup/code tables required to interpret coded values.

The list above is illustrative only. **Please retain every other available source field in the export.**

### Also request

- data dictionary / field definitions;
- lookup tables for codes and enums;
- record count for the delivered extract;
- extraction date;
- academic year / effective period;
- whether closed/inactive schools are included;
- whether one row represents a school, campus, branch or another unit;
- any restrictions on republication of fields that are already shown through the public directory.

### Acceptance checks

The acquisition team should not mark MOE coverage complete until:

- a machine-readable row-level file is received;
- native IDs are preserved where available;
- delivered row count is reconciled with the authority's stated universe and scope;
- coded values have lookup definitions or are preserved exactly as delivered;
- no rows are silently removed merely because some fields are blank.

---

## B. Ministry of Social Solidarity — National Nursery Census

### Dataset requested

The row-level source database for the **2025 National Comprehensive Nursery Census**, whose published aggregate reports **48,225 nurseries across 27 directorates**.

### Request

Please provide the complete machine-readable row-level extract used to produce the 2025 national nursery census and/or the latest current nursery registry derived from it.

Please include **all source columns available in the census/database**, rather than mapping the data into a field list defined by Edu Hub.

Where available, please also include:

- native nursery ID/code;
- nursery name;
- licensing status and license identifiers;
- responsible directorate / administrative unit;
- governorate, city/district/area and address;
- latitude/longitude or map identifiers;
- nursery ownership/type/classification;
- licensed and actual capacity;
- enrollment / number of children;
- number of classes;
- staffing / employee counts;
- age groups accepted;
- operating status;
- working days/hours;
- fees and fee period where publicly distributable;
- contact details;
- service/program classifications;
- accessibility/special-needs fields where represented;
- inspection/quality/classification fields where represented;
- last verification/update date;
- fields intended for the planned public nursery digital map/platform;
- source lookup/code tables.

The list above is illustrative only. **Please retain every additional field present in the source database.**

### Also request

- data dictionary / field definitions;
- lookup tables;
- extraction date;
- record count;
- meaning of one record (nursery, branch, licensed unit, etc.);
- whether unlicensed/closed/suspended facilities are present;
- whether fields such as fees, capacity and licensing status may be republished from the future public map;
- geographic coordinates in the same format intended for the public map, when available.

### Acceptance checks

Do not mark the 48,225-nursery universe acquired merely because the aggregate PDF is available. Completion requires a row-level machine-readable extract or a public row-level map/API after its official launch.

---

## C. Delivery preservation

When either authority provides a file:

1. save the original file unchanged;
2. calculate a SHA-256 hash;
3. record source, sender/authority, received date and effective date;
4. preserve every original column name;
5. convert to JSONL/Parquet only as an additional derived artifact;
6. run a raw field census;
7. do **not** deduplicate or map into Edu Hub canonical tables yet.

Target raw structure:

```text
sources/<authority>/<dataset>/<retrieval-date>/
  original/<file-as-received>
  manifest.json
  records.jsonl
  field-inventory.csv
```

## D. What happens after both datasets are obtained

Only after the major official and secondary record universes are assembled do we move to:

1. source-by-source field inventory;
2. actual-value and null-coverage analysis;
3. duplicate-candidate analysis;
4. institution/campus identity rules;
5. user selection of important public fields;
6. canonical database contract;
7. Instatic field/projection contract;
8. import.

This keeps the database and website aligned with the **data that actually exists**, rather than designing around a small sample.
