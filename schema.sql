create table if not exists public.posts (
 id text primary key,
 created_at timestamptz,
 text text not null,
 url text not null,
 prefecture text,
 carrier text,
 benefit text,
 amount bigint,
 model text,
 collected_at timestamptz
);
create index if not exists posts_created_at_idx on public.posts (created_at desc);
alter table public.posts enable row level security;
-- No anonymous table policy: reads/writes use server-side service-role only.
