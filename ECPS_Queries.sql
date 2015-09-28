SELECT
  DISTINCT wpd.empl_bdge_num as person_id,
  shift.utc_date as shift_start_date,
  shift.mins as shift_duration
FROM emcas_engr_s360.global_scheduler_shift shift
  JOIN emcas_engr_s360.w_person_d wpd on shift.person_id = wpd.pers_11i_id
WHERE
  (shift.utc_date, shift.utc_date + cast(shift.mins/60-1 || 'hours' AS INTERVAL))
  OVERLAPS
  (now()::TIMESTAMP, now()::TIMESTAMP)
LIMIT 10;

SELECT
  DISTINCT person.empl_bdge_num as person_id,
  person.pers_first_nm as first_name,
  person.pers_last_nm as last_name
FROM
  emcas_engr_s360.w_person_d as person
WHERE
  emc_emp_type LIKE 'Employee' and
  person.empl_bdge_num is not NULL
LIMIT 1000;

SELECT
  DISTINCT sr.srvc_req_num as sr_num,
  wpd.empl_bdge_num as sr_owner_person_id,
  rsr.pers_first_nm as first_name,
  rsr.pers_last_nm as last_name,
  sr.srvc_req_prob_text as problem_description,
  sr.srvc_req_crte_dt as srvc_req_crte_dt
FROM
  emcas_engr_s360.w_service_request_d as sr,
  emcas_engr_s360.w_resource_role_ref as rsr,
  emcas_engr_s360.w_person_d as wpd
WHERE
  sr.srvc_req_ownr_rsrc_id = rsr.rsrc_id and
  wpd.empl_bdge_num != 'NA' and
  rsr.pers_11i_id = wpd.pers_11i_id and
  sr.srvc_req_crte_dt > now()::TIMESTAMP - cast(365 || 'days' as INTERVAL)
ORDER BY
  sr_owner_person_id,
  srvc_req_crte_dt DESC
LIMIT 1000;


SELECT
  DISTINCT sr.srvc_req_num as sr_num,
  wpd.empl_bdge_num as sr_owner_person_id,
  rsr.pers_first_nm as first_name,
  rsr.pers_last_nm as last_name,
  sr.srvc_req_prob_text as problem_description,
  sr.srvc_req_crte_dt as srvc_req_crte_dt,
  wpd.empl_11i_num,
  rsr.rsrc_id
FROM
  emcas_engr_s360.w_service_request_d as sr,
  emcas_engr_s360.w_resource_role_ref as rsr,
  emcas_engr_s360.w_person_d as wpd
WHERE
  sr.srvc_req_ownr_rsrc_id = rsr.rsrc_id and
  rsr.empl_bdge_num != 'NA' and
  rsr.pers_11i_id = wpd.pers_11i_id and
  sr.srvc_req_crte_dt > now()::TIMESTAMP - cast(365 || 'days' as INTERVAL)
ORDER BY
  srvc_req_crte_dt DESC
LIMIT 100;


