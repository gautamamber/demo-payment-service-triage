"""S02 fixture: seeds a large volume of rows server-side (Postgres generates
them via generate_series — no per-row round trip, so 2M rows takes seconds,
not minutes). Idempotent: skips if the table is already at/above the target."""

import sys

from sqlalchemy import text

from app.db import engine

N = int(sys.argv[1]) if len(sys.argv) > 1 else 2_000_000

with engine.begin() as conn:
    existing = conn.execute(text("SELECT count(*) FROM payments")).scalar()
    if existing >= N:
        print(f"payments already has {existing} rows (>= {N}), skipping seed")
        sys.exit(0)

    to_add = N - existing
    conn.execute(
        text(
            "INSERT INTO payments (id, customer_id, amount, status, created_at) "
            "SELECT gen_random_uuid()::text, "
            # Many distinct customer_ids (~10 rows each on average) so a
            # single lookup is genuinely selective — with 3 buckets across 2M
            # rows, Postgres's planner picks a sequential scan regardless of
            # any index (a third of the table matching isn't selective enough
            # to prefer an index seek), which defeats the point of this
            # scenario. High cardinality is what makes the missing index
            # actually matter.
            "       'cust-' || floor(random() * 200000)::int, "
            "       round((random()*500)::numeric, 2), "
            "       'completed', "
            "       now() - (random() * interval '30 days') "
            "FROM generate_series(1, :n)"
        ),
        {"n": to_add},
    )

print(f"seeded {to_add} rows (total now ~{N})")
