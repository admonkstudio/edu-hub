-- Read-only V7 verification. Every boolean column must return true.

with checks as (
  select
    (select count(*) from edu_raw.sources) = 13 as source_count_ok,
    (select count(*) from edu_raw.raw_records) = 24916 as raw_record_count_ok,
    (select count(*) from edu_raw.record_ownership) = 24916 as ownership_count_ok,
    (select count(*) from edu_raw.media_assets) = 2101 as media_asset_count_ok,
    (select count(*) from edu_raw.media_files) = 453 as media_file_count_ok,
    not exists (
      select 1 from edu_raw.raw_records
      group by source_id, raw_hash having count(*) > 1
    ) as source_hash_unique_ok,
    not exists (
      select 1 from edu_raw.media_assets a
      left join edu_raw.media_files f on f.file_sha256 = a.file_sha256
      where a.file_sha256 is not null and f.file_sha256 is null
    ) as media_references_ok,
    not exists (
      select 1 from edu_raw.media_assets
      where public_use_allowed and rights_status = 'unknown'
    ) as media_rights_gate_ok,
    exists (
      select 1 from edu_raw.import_batches
      where archive_version = 7
        and archive_sha256 = 'fb4e6c332bdf1c0c9505ee78ad2d720d6d96d67241431a6a21ffc79ef8f6408a'
        and status = 'verified'
    ) as import_batch_verified_ok
)
select * from checks;

select source_id, count(*) as record_count
from edu_raw.raw_records
group by source_id
order by source_id;

select archive_version, archive_sha256, status, imported_records,
       imported_media_assets, started_at, finished_at
from edu_raw.import_batches
order by started_at desc;
