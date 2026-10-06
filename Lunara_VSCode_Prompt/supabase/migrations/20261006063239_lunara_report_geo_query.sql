-- SECURITY INVOKER preserves the caller's privileges and existing RLS.
-- The GiST index reports_location_gix from the initial migration supports ST_DWithin.
create or replace function public.lunara_nearby_reports(
  p_lat double precision,
  p_lng double precision,
  p_radius_m integer,
  p_limit integer,
  p_public_only boolean
)
returns setof public.citizen_reports
language sql
stable
security invoker
set search_path = pg_catalog, extensions, gis, public
as $$
  select r.*
  from public.citizen_reports as r
  where p_lat between -90 and 90
    and p_lng between -180 and 180
    and p_radius_m between 50 and 5000
    and st_dwithin(
      r.location,
      st_setsrid(st_makepoint(p_lng, p_lat), 4326)::geography,
      p_radius_m
    )
    and (not p_public_only or r.status in ('verified', 'resolved'))
  order by st_distance(r.location, st_setsrid(st_makepoint(p_lng, p_lat), 4326)::geography)
  limit least(greatest(coalesce(p_limit, 500), 1), 500);
$$;

-- Functions normally grant EXECUTE to PUBLIC by default. Do not expose
-- pending reports or the privileged geospatial query to browser roles.
revoke all on function public.lunara_nearby_reports(double precision,double precision,integer,integer,boolean)
  from public, anon, authenticated;
grant execute on function public.lunara_nearby_reports(double precision,double precision,integer,integer,boolean)
  to service_role;
