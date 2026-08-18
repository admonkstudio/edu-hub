alter table public.staff_users add column display_name text;

-- Canonical facts and reviewed workflow state must only change through audited
-- commands. RLS still governs reads, while the private security-definer
-- functions below perform authorization again at execution time.
revoke insert,update,delete on table
  public.institutions,
  public.institution_localizations,
  public.campuses,
  public.institution_education_levels,
  public.institution_curricula,
  public.institution_languages,
  public.institution_certificates
from authenticated;
revoke update,delete on table public.entity_assertions,public.assertion_conflicts,public.research_tasks,public.field_freshness from authenticated;

create function private.review_assertion(p_assertion_id uuid,p_decision text,p_reason text)
returns void language plpgsql security definer set search_path='' as $$
declare v_actor uuid:=(select auth.uid()); v_old public.entity_assertions; v_change uuid; v_interval integer; begin
  if not private.has_staff_role(array['super_admin','admin','reviewer']) then raise exception 'reviewer role required' using errcode='42501'; end if;
  if p_decision not in ('accepted','rejected','superseded') then raise exception 'invalid review decision' using errcode='22023'; end if;
  if length(trim(coalesce(p_reason,'')))<3 then raise exception 'review reason required' using errcode='22023'; end if;
  select * into v_old from public.entity_assertions where id=p_assertion_id for update;
  if not found then raise exception 'assertion not found' using errcode='P0002'; end if;
  if v_old.assertion_status='conflicting' then raise exception 'resolve the conflict instead' using errcode='23514'; end if;
  insert into public.change_sets(actor_id,reason,source_id) values(v_actor,p_reason,v_old.source_id) returning id into v_change;
  update public.entity_assertions set assertion_status=p_decision,reviewed_by=v_actor,reviewed_at=now(),review_reason=p_reason where id=p_assertion_id;
  perform private.write_revision(v_change,'assertion',p_assertion_id,'transition','assertion_status',to_jsonb(v_old.assertion_status),to_jsonb(p_decision));
  if p_decision='accepted' then
    select review_interval_days into v_interval from public.freshness_policies where entity_type=v_old.entity_type and field_key=v_old.field_key and status='active';
    insert into public.field_freshness(entity_type,entity_id,field_key,last_verified_at,next_review_at,status,assertion_id)
    values(v_old.entity_type,v_old.entity_id,v_old.field_key,now(),case when v_interval is null then null else now()+make_interval(days=>v_interval) end,case when v_interval is null then 'unknown' else 'fresh' end,p_assertion_id)
    on conflict(entity_type,entity_id,field_key) do update set last_verified_at=excluded.last_verified_at,next_review_at=excluded.next_review_at,status=excluded.status,assertion_id=excluded.assertion_id,updated_at=now();
  end if;
end $$;
revoke all on function private.review_assertion(uuid,text,text) from public;
grant execute on function private.review_assertion(uuid,text,text) to authenticated;

create function private.resolve_assertion_conflict(p_conflict_id uuid,p_accepted_assertion_id uuid,p_reason text)
returns void language plpgsql security definer set search_path='' as $$
declare v_actor uuid:=(select auth.uid()); v_conflict public.assertion_conflicts; v_assertion public.entity_assertions; v_change uuid; v_interval integer; begin
  if not private.has_staff_role(array['super_admin','admin','reviewer']) then raise exception 'reviewer role required' using errcode='42501'; end if;
  if length(trim(coalesce(p_reason,'')))<3 then raise exception 'resolution reason required' using errcode='22023'; end if;
  select * into v_conflict from public.assertion_conflicts where id=p_conflict_id and status='open' for update;
  if not found then raise exception 'open conflict not found' using errcode='P0002'; end if;
  select a.* into v_assertion from public.entity_assertions a join public.assertion_conflict_members m on m.assertion_id=a.id where m.conflict_id=p_conflict_id and a.id=p_accepted_assertion_id;
  if not found then raise exception 'accepted assertion is not a conflict member' using errcode='23514'; end if;
  insert into public.change_sets(actor_id,reason,source_id) values(v_actor,p_reason,v_assertion.source_id) returning id into v_change;
  update public.entity_assertions a set assertion_status=case when a.id=p_accepted_assertion_id then 'accepted' else 'rejected' end,reviewed_by=v_actor,reviewed_at=now(),review_reason=p_reason from public.assertion_conflict_members m where m.conflict_id=p_conflict_id and m.assertion_id=a.id;
  update public.assertion_conflicts set status='resolved',resolution_reason=p_reason,resolved_by=v_actor,resolved_at=now() where id=p_conflict_id;
  select review_interval_days into v_interval from public.freshness_policies where entity_type=v_assertion.entity_type and field_key=v_assertion.field_key and status='active';
  insert into public.field_freshness(entity_type,entity_id,field_key,last_verified_at,next_review_at,status,assertion_id)
  values(v_assertion.entity_type,v_assertion.entity_id,v_assertion.field_key,now(),case when v_interval is null then null else now()+make_interval(days=>v_interval) end,case when v_interval is null then 'unknown' else 'fresh' end,p_accepted_assertion_id)
  on conflict(entity_type,entity_id,field_key) do update set last_verified_at=excluded.last_verified_at,next_review_at=excluded.next_review_at,status=excluded.status,assertion_id=excluded.assertion_id,updated_at=now();
  perform private.write_revision(v_change,'assertion',p_accepted_assertion_id,'transition','conflict_resolution',null,jsonb_build_object('conflict_id',p_conflict_id,'decision','accepted'));
end $$;
revoke all on function private.resolve_assertion_conflict(uuid,uuid,text) from public;
grant execute on function private.resolve_assertion_conflict(uuid,uuid,text) to authenticated;

create function private.transition_research_task(p_task_id uuid,p_status text,p_assigned_to uuid,p_outcome text)
returns void language plpgsql security definer set search_path='' as $$
declare v_actor uuid:=(select auth.uid()); v_old public.research_tasks; v_change uuid; begin
  if not private.is_internal_user() then raise exception 'staff role required' using errcode='42501'; end if;
  if p_status not in ('open','assigned','in_progress','in_review','completed','cancelled') then raise exception 'invalid task status' using errcode='22023'; end if;
  select * into v_old from public.research_tasks where id=p_task_id for update;
  if not found then raise exception 'task not found' using errcode='P0002'; end if;
  if p_assigned_to is distinct from v_old.assigned_to and not private.has_staff_role(array['super_admin','admin','reviewer']) then raise exception 'assignment role required' using errcode='42501'; end if;
  if v_old.assigned_to is not null and v_old.assigned_to<>v_actor and not private.has_staff_role(array['super_admin','admin','reviewer']) then raise exception 'task belongs to another staff member' using errcode='42501'; end if;
  insert into public.change_sets(actor_id,reason) values(v_actor,'Research task transition') returning id into v_change;
  update public.research_tasks set status=p_status,assigned_to=p_assigned_to,outcome=nullif(trim(coalesce(p_outcome,'')),''),completed_by=case when p_status='completed' then v_actor else null end,completed_at=case when p_status='completed' then now() else null end where id=p_task_id;
  perform private.write_revision(v_change,'research_task',p_task_id,'transition','status',to_jsonb(v_old.status),to_jsonb(p_status));
end $$;
revoke all on function private.transition_research_task(uuid,text,uuid,text) from public;
grant execute on function private.transition_research_task(uuid,text,uuid,text) to authenticated;

create function public.review_assertion_command(assertion_id uuid,decision text,reason text) returns void language sql security invoker set search_path='' as $$select private.review_assertion(assertion_id,decision,reason)$$;
create function public.resolve_assertion_conflict_command(conflict_id uuid,accepted_assertion_id uuid,reason text) returns void language sql security invoker set search_path='' as $$select private.resolve_assertion_conflict(conflict_id,accepted_assertion_id,reason)$$;
create function public.transition_research_task_command(task_id uuid,status text,assigned_to uuid,outcome text default null) returns void language sql security invoker set search_path='' as $$select private.transition_research_task(task_id,status,assigned_to,outcome)$$;
revoke all on function public.review_assertion_command(uuid,text,text),public.resolve_assertion_conflict_command(uuid,uuid,text),public.transition_research_task_command(uuid,text,uuid,text) from public,anon;
grant execute on function public.review_assertion_command(uuid,text,text),public.resolve_assertion_conflict_command(uuid,uuid,text),public.transition_research_task_command(uuid,text,uuid,text) to authenticated;
