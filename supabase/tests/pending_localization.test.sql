begin;
select plan(20);

insert into auth.users(instance_id,id,aud,role,email,encrypted_password,created_at,updated_at)
values('00000000-0000-0000-0000-000000000000','20000000-0000-4000-8000-000000000002','authenticated','authenticated','localization-test@example.test','',now(),now());
insert into public.staff_users(user_id,role,status)
values('20000000-0000-4000-8000-000000000002','researcher','active');
set local role authenticated;
select set_config('request.jwt.claim.sub','20000000-0000-4000-8000-000000000002',true);
select set_config('request.jwt.claim.role','authenticated',true);

select lives_ok(
  format($f$select public.create_institution_command(%L::jsonb,'English-only candidate')$f$,
    jsonb_build_object(
      'core',jsonb_build_object('official_name','English Candidate','institution_type_id',(select id from public.institution_types order by code limit 1),'publication_status','draft','data_status','candidate'),
      'localizations',jsonb_build_array(jsonb_build_object('locale','en-EG','name','English Candidate','slug','english-candidate')),
      'campus',jsonb_build_object('name','Main campus','location_id',(select id from public.locations where location_type='governorate' order by official_code limit 1)),
      'relationships',jsonb_build_object('education_levels',jsonb_build_array(),'curricula',jsonb_build_array(),'languages',jsonb_build_array(),'certificates',jsonb_build_array())
    )::text),
  'draft candidate with English only succeeds'
);
select is((select count(*)::integer from public.institution_localizations where name='English Candidate'),1,'no placeholder localization is generated');
select ok((select public.institution_readiness(id)->'reasons' from public.institutions where official_name='English Candidate') ? 'missing_required_localization: ar-EG','missing Arabic explicitly blocks readiness');
select is((select public.institution_readiness(id)->>'public_ready' from public.institutions where official_name='English Candidate'),'false','missing Arabic prevents public readiness');

select lives_ok(
  format($f$select public.create_institution_command(%L::jsonb,'Arabic-only candidate')$f$,
    jsonb_build_object(
      'core',jsonb_build_object('official_name','Arabic Candidate','institution_type_id',(select id from public.institution_types order by code limit 1),'publication_status','draft','data_status','candidate'),
      'localizations',jsonb_build_array(jsonb_build_object('locale','ar-EG','name','مؤسسة عربية','slug','مؤسسة-عربية')),
      'campus',jsonb_build_object('name','Main campus','location_id',(select id from public.locations where location_type='governorate' order by official_code limit 1)),
      'relationships',jsonb_build_object('education_levels',jsonb_build_array(),'curricula',jsonb_build_array(),'languages',jsonb_build_array(),'certificates',jsonb_build_array())
    )::text),
  'draft candidate with Arabic only succeeds'
);
select ok((select public.institution_readiness(id)->'reasons' from public.institutions where official_name='Arabic Candidate') ? 'missing_required_localization: en-EG','missing English explicitly blocks readiness');

select throws_ok(
  format($f$select public.create_institution_command(%L::jsonb,'No localization')$f$,
    jsonb_build_object(
      'core',jsonb_build_object('official_name','No Localization','institution_type_id',(select id from public.institution_types order by code limit 1)),
      'localizations',jsonb_build_array(),
      'relationships',jsonb_build_object('education_levels',jsonb_build_array(),'curricula',jsonb_build_array(),'languages',jsonb_build_array(),'certificates',jsonb_build_array())
    )::text),
  '22023','at least one complete localization is required','zero localizations fail'
);
select is((select count(*)::integer from public.institutions where official_name='No Localization'),0,'failed command rolls back the institution');
select is((select count(*)::integer from public.change_sets),2,'zero-localization failure leaves no change-set residue');
select is((select count(*)::integer from public.entity_revisions),6,'zero-localization failure leaves no revision residue');

select throws_ok(
  format($f$select public.create_institution_command(%L::jsonb,'Partial localization')$f$,
    jsonb_build_object(
      'core',jsonb_build_object('official_name','Partial Localization','institution_type_id',(select id from public.institution_types order by code limit 1)),
      'localizations',jsonb_build_array(jsonb_build_object('locale','en-EG','name','Partial Localization','slug','')),
      'relationships',jsonb_build_object('education_levels',jsonb_build_array(),'curricula',jsonb_build_array(),'languages',jsonb_build_array(),'certificates',jsonb_build_array())
    )::text),
  '22023','each localization requires a supported locale, name, and slug','partial localization fails without creating a placeholder'
);
select is((select count(*)::integer from public.institutions where official_name='Partial Localization'),0,'partial localization failure leaves no institution residue');
select is((select count(*)::integer from public.entity_revisions),6,'partial localization failure leaves no revision residue');

select throws_ok(
  format($f$select public.create_institution_command(%L::jsonb,'Premature publication')$f$,
    jsonb_build_object(
      'core',jsonb_build_object('official_name','Premature Publication','institution_type_id',(select id from public.institution_types order by code limit 1),'publication_status','public_noindex'),
      'localizations',jsonb_build_array(jsonb_build_object('locale','en-EG','name','Premature Publication','slug','premature-publication')),
      'relationships',jsonb_build_object('education_levels',jsonb_build_array(),'curricula',jsonb_build_array(),'languages',jsonb_build_array(),'certificates',jsonb_build_array())
    )::text),
  '22023','both launch localizations are required for publication','missing launch locale prevents publication'
);
select throws_ok(
  format($f$select public.create_institution_command(%L::jsonb,'Premature index readiness')$f$,
    jsonb_build_object(
      'core',jsonb_build_object('official_name','Premature Index Readiness','institution_type_id',(select id from public.institution_types order by code limit 1),'publication_status','index_ready'),
      'localizations',jsonb_build_array(jsonb_build_object('locale','en-EG','name','Premature Index Readiness','slug','premature-index-readiness')),
      'relationships',jsonb_build_object('education_levels',jsonb_build_array(),'curricula',jsonb_build_array(),'languages',jsonb_build_array(),'certificates',jsonb_build_array())
    )::text),
  '22023','both launch localizations are required for publication','missing launch locale prevents index-ready persistence'
);

select lives_ok(
  format($f$select public.update_institution_command(%L,%L::jsonb,'Add established Arabic localization')$f$,
    (select id from public.institutions where official_name='English Candidate'),
    jsonb_build_object(
      'core',jsonb_build_object('official_name','English Candidate','institution_type_id',(select id from public.institution_types order by code limit 1),'publication_status','draft','data_status','candidate'),
      'localizations',jsonb_build_array(jsonb_build_object('locale','ar-EG','name','مؤسسة إنجليزية','slug','مؤسسة-إنجليزية')),
      'campus',jsonb_build_object('id',(select id from public.campuses where institution_id=(select id from public.institutions where official_name='English Candidate')),'name','Main campus','location_id',(select id from public.locations where location_type='governorate' order by official_code limit 1)),
      'relationships',jsonb_build_object('education_levels',jsonb_build_array(),'curricula',jsonb_build_array(),'languages',jsonb_build_array(),'certificates',jsonb_build_array())
    )::text),
  'Arabic localization can be added later'
);
select ok(not ((select public.institution_readiness(id)->'reasons' from public.institutions where official_name='English Candidate') ? 'missing_required_localization: ar-EG'),'adding Arabic clears the localization blocker');
select is((select count(*)::integer from public.change_sets),3,'successful candidate commands retain one audit change set each');
select is((select count(*)::integer from public.entity_revisions),9,'successful candidate commands retain append-only audit revisions');
select is((select count(*)::integer from public.entity_revisions r join public.change_sets c on c.id=r.change_set_id where r.entity_type='institution_localization' and r.field_key='ar-EG' and c.reason='Add established Arabic localization'),1,'adding Arabic records its localization revision in the expected change set');

select * from finish();
rollback;
