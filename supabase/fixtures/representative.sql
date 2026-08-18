-- Fictional development fixtures. Never publish as real institution facts.
do $$ begin
insert into public.providers(id,provider_type,official_name,status) values
('20000000-0000-4000-8000-000000000001','group','Fixture Early Learning Group','active'),
('20000000-0000-4000-8000-000000000002','group','Fixture Schools Group','active');

with fixture(id,name,type_code,ownership_code,publication_status) as (values
('30000000-0000-4000-8000-000000000001'::uuid,'Fixture Independent Nursery','nursery','private','draft'),
('30000000-0000-4000-8000-000000000002'::uuid,'Fixture Multi-Branch Nursery','nursery','private','draft'),
('30000000-0000-4000-8000-000000000003'::uuid,'Fixture Independent School','school','private','draft'),
('30000000-0000-4000-8000-000000000004'::uuid,'Fixture Group School','school','private','draft'),
('30000000-0000-4000-8000-000000000005'::uuid,'Fixture Multi-Campus School','school','private','draft'),
('30000000-0000-4000-8000-000000000006'::uuid,'Fixture British School','school','international','draft'),
('30000000-0000-4000-8000-000000000007'::uuid,'Fixture American School','school','international','draft'),
('30000000-0000-4000-8000-000000000008'::uuid,'Fixture Multi-Level School','school','private','draft'),
('30000000-0000-4000-8000-000000000009'::uuid,'Fixture Public University','university','public','draft'),
('30000000-0000-4000-8000-000000000010'::uuid,'Fixture Private University','university','private','draft'),
('30000000-0000-4000-8000-000000000011'::uuid,'Fixture Technological University','technological_institution','public','draft'),
('30000000-0000-4000-8000-000000000012'::uuid,'Fixture Foreign University Branch','foreign_university_branch','international','draft'))
insert into public.institutions(id,official_name,institution_type_id,ownership_type_id,provider_id,publication_status)
select f.id,f.name,it.id,ot.id,case when f.id='30000000-0000-4000-8000-000000000002'::uuid then '20000000-0000-4000-8000-000000000001'::uuid when f.id='30000000-0000-4000-8000-000000000004'::uuid then '20000000-0000-4000-8000-000000000002'::uuid end,f.publication_status
from fixture f join public.institution_types it on it.code=f.type_code join public.ownership_types ot on ot.code=f.ownership_code;

insert into public.institution_localizations(institution_id,locale,name,slug)
select id,'en-EG',official_name,lower(replace(official_name,' ','-')) from public.institutions where id::text like '30000000-%';
insert into public.institution_localizations(institution_id,locale,name,slug)
select id,'ar-EG','مؤسسة تجريبية '||right(id::text,2),'مؤسسة-تجريبية-'||right(id::text,2) from public.institutions where id::text like '30000000-%';

with cairo as (select id from public.locations where official_code='EG-C'), giza as (select id from public.locations where official_code='EG-GZ')
insert into public.campuses(institution_id,location_id,name,is_main)
select i.id,cairo.id,'Main campus',true from public.institutions i cross join cairo where i.id::text like '30000000-%';
with giza as (select id from public.locations where official_code='EG-GZ')
insert into public.campuses(institution_id,location_id,name,is_main) values
('30000000-0000-4000-8000-000000000002',(select id from giza),'Second branch',false),
('30000000-0000-4000-8000-000000000005',(select id from giza),'Second campus',false);

insert into public.institution_curricula(institution_id,curriculum_id)
select '30000000-0000-4000-8000-000000000006',id from public.curricula where code='british';
insert into public.institution_curricula(institution_id,curriculum_id)
select '30000000-0000-4000-8000-000000000007',id from public.curricula where code='american';
insert into public.institution_education_levels(institution_id,education_level_id)
select '30000000-0000-4000-8000-000000000008',id from public.education_levels where code in ('primary','preparatory','secondary');
end $$;
