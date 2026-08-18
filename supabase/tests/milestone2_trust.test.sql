begin;
select plan(24);

select has_table('public','change_sets','change sets exist');
select has_table('public','entity_revisions','entity revisions exist');
select has_table('public','sources','sources exist');
select has_table('public','source_snapshots','source snapshots exist');
select has_table('public','entity_assertions','field assertions exist');
select has_table('public','assertion_conflicts','assertion conflicts exist');
select has_table('public','research_tasks','research tasks exist');
select has_table('public','freshness_policies','freshness policies exist');
select has_table('public','field_freshness','field freshness exists');
select has_table('public','completeness_requirements','completeness requirements exist');
select function_privs_are('public','create_institution_command',array['jsonb','text'], 'authenticated', array['EXECUTE'],'only authenticated can execute create command');

insert into auth.users(instance_id,id,aud,role,email,encrypted_password,created_at,updated_at)
values('00000000-0000-0000-0000-000000000000','20000000-0000-4000-8000-000000000001','authenticated','authenticated','m2-test@example.test','',now(),now());
insert into public.staff_users(user_id,role,status) values('20000000-0000-4000-8000-000000000001','researcher','active');
set local role authenticated;
select set_config('request.jwt.claim.sub','20000000-0000-4000-8000-000000000001',true);
select set_config('request.jwt.claim.role','authenticated',true);

select lives_ok(
  format($f$select public.create_institution_command(%L::jsonb,'Initial sourced research record')$f$,
    jsonb_build_object(
      'core',jsonb_build_object('official_name','Atomic Test Institution','institution_type_id',(select id from public.institution_types order by code limit 1),'publication_status','draft','data_status','candidate'),
      'localizations',jsonb_build_array(
        jsonb_build_object('locale','en-EG','name','Atomic Test Institution','slug','atomic-test-institution'),
        jsonb_build_object('locale','ar-EG','name','مؤسسة اختبار ذرية','slug','مؤسسة-اختبار-ذرية')
      ),
      'campus',jsonb_build_object('name','Main campus','location_id',(select id from public.locations where location_type='governorate' order by official_code limit 1)),
      'relationships',jsonb_build_object('education_levels',jsonb_build_array(),'curricula',jsonb_build_array(),'languages',jsonb_build_array(),'certificates',jsonb_build_array())
    )::text),
  'transactional command creates the complete record'
);
select is((select count(*)::integer from public.change_sets),1,'canonical command writes one change set');
select ok((select count(*) from public.entity_revisions)>=2,'canonical command writes append-only revisions');

select throws_ok(
  format($f$select public.create_institution_command(%L::jsonb,'Forced rollback proof')$f$,
    jsonb_build_object(
      'core',jsonb_build_object('official_name','Must Roll Back','institution_type_id',(select id from public.institution_types order by code limit 1)),
      'localizations',jsonb_build_array(
        jsonb_build_object('locale','en-EG','name','Must Roll Back','slug','must-roll-back'),
        jsonb_build_object('locale','ar-EG','name','يجب التراجع','slug','مؤسسة-اختبار-ذرية')
      ),
      'campus',jsonb_build_object('name','Main campus','location_id',(select id from public.locations where location_type='governorate' order by official_code limit 1)),
      'relationships',jsonb_build_object('education_levels',jsonb_build_array(),'curricula',jsonb_build_array(),'languages',jsonb_build_array(),'certificates',jsonb_build_array())
    )::text),
  '23505',null,'a late localization failure aborts the command'
);
select is((select count(*)::integer from public.institutions),1,'forced failure rolls back the institution and change set');

select throws_ok(
  $$insert into public.institutions(official_name,institution_type_id) values('Direct write must fail',(select id from public.institution_types order by code limit 1))$$,
  '42501',null,'authenticated staff cannot bypass the audited canonical command'
);

insert into public.sources(source_type,publisher,title,url,language,authority_level,created_by)
values
('institution_website','Atomic Test','Website','https://atomic.example.test','en',2,'20000000-0000-4000-8000-000000000001'),
('institution_social','Atomic Test','Official post','https://social.example.test/atomic','en',4,'20000000-0000-4000-8000-000000000001');
insert into public.entity_assertions(entity_type,entity_id,field_key,value_jsonb,source_id,observed_at,created_by)
select 'institution',i.id,'official_website_url','"https://one.example.test"'::jsonb,s.id,now(),'20000000-0000-4000-8000-000000000001' from public.institutions i cross join lateral(select id from public.sources order by authority_level limit 1)s limit 1;
insert into public.entity_assertions(entity_type,entity_id,field_key,value_jsonb,source_id,observed_at,created_by)
select 'institution',i.id,'official_website_url','"https://two.example.test"'::jsonb,s.id,now(),'20000000-0000-4000-8000-000000000001' from public.institutions i cross join lateral(select id from public.sources order by authority_level desc limit 1)s limit 1;
select is((select count(*)::integer from public.assertion_conflicts where status='open'),1,'different active field assertions create one conflict');
select is((select count(*)::integer from public.entity_assertions where assertion_status='conflicting'),2,'both conflicting assertions are preserved');

select throws_ok(
  format($f$select public.resolve_assertion_conflict_command(%L,%L,'Researcher must not review')$f$,
    (select id from public.assertion_conflicts where status='open' limit 1),
    (select id from public.entity_assertions order by created_at limit 1)),
  '42501',null,'researcher cannot perform reviewer decisions'
);

reset role;
update public.staff_users set role='reviewer' where user_id='20000000-0000-4000-8000-000000000001';
set local role authenticated;
select lives_ok(
  format($f$select public.resolve_assertion_conflict_command(%L,%L,'Official website reviewed against both sources')$f$,
    (select id from public.assertion_conflicts where status='open' limit 1),
    (select id from public.entity_assertions order by created_at limit 1)),
  'reviewer resolves a conflict through the command'
);
select is((select count(*)::integer from public.assertion_conflicts where status='resolved'),1,'conflict resolution is retained');
select results_eq($$select assertion_status,count(*)::bigint from public.entity_assertions group by assertion_status order by assertion_status$$,$$select * from (values('accepted'::text,1::bigint),('rejected'::text,1::bigint)) expected(assertion_status,count)$$,'resolution preserves accepted and rejected assertions');
select is((select status from public.field_freshness where field_key='official_website_url'),'fresh','accepted conflict resolution refreshes the field');

rollback;
