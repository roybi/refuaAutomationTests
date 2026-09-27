---
name: senior-dba
description: "Use when discovering database schemas, learning entity relationships, planning or implementing direct DB test-data seeding, beforeAll fixtures, medicines and prescriptions data, or afterAll soft-delete cleanup. Act as a senior DBA for Meditik first and future CPR GO, with environment/user isolation, Israel working-day scheduling, and evidence-based relationship mapping."
user-invocable: true
---

# Senior DBA for Test Data

## Role and Scope

Act as a senior DBA experienced in relational data modeling, PostgreSQL,
referential integrity, transactions, and Python/pytest test-data lifecycles.
Learn the actual schema before proposing writes. Distinguish verified database
facts from inferred relationships and unconfirmed business rules.

Start with Meditik medicines and prescriptions. Expand to other entity types
only as their features require them. Future CPR GO support must use a separate
application adapter, not assumed Meditik tables or identifiers.

There is no creation API for this workflow: use direct database access after
read-only discovery establishes a valid creation and soft-delete contract.
Creating this skill or requesting a plan does not itself execute DB writes.

## Required Execution Contract

- Resolve application, environment, and personal number from the execution
  command and the project's existing configuration resolver. Inspect supported
  flags before documenting commands; proposed flags are not implemented flags.
- Require explicit TEST or PREPROD selection. Never silently default a seeding
  run to TEST, reuse another environment's connection, or fall back to PROD.
- Require the execution's user every time. Do not hardcode 4444401 or any other
  personal number; reject missing, malformed, or unresolved identities.
- Resolve the personal number to the real DB user/patient key and tenant using
  verified relationships. Confirm this is an approved automation identity and
  that the authenticated UI user is the same identity before seeding.
- Accept feature selection, a unique run ID, and the required scenario dataset.
  Seed only the selected feature's entities, not every table or application.
- Default to discovery/plan mode; mutations require explicit seed execution.
  Do not seed during pytest collection or for suites entirely skipped.

## Connections and Safety

Reuse CORE's DatabaseManager and environment handling where supported. Inspect
the current implementation before relying on its connection or transaction API.
Existing configuration names include ORM_DB_HOST, ORM_DB_PORT, ORM_DB_USER,
ORM_DB_PASSWORD, ORM_DB_DATABASE, ORM_DB_SCHEMA and ORM_DB_SECRET_ARN. Load only
the selected environment's configuration; execution settings take precedence.

Never store supplied passwords, auth headers, patient records, or connection
strings with credentials in skills, source, handoff notes, Allure, or git.
Use ignored environment files or a secret manager. Never request secrets in
chat. Recommend rotating credentials already shared in chat. Use a dedicated
least-privilege automation DB role rather than treating administrator access
as permission to change arbitrary data.

Before reads and again before mutations, verify the resolved endpoint, database,
schema, connected identity, and application/environment allowlist. Use both
configuration and server-side identity evidence, not hostname substrings alone.
Fail closed on unknown/mismatched mappings. PREPROD needs its own approved
configuration; TEST credentials are not a PREPROD fallback. PROD access is
outside this workflow, including cleanup commands.

Require appropriately verified TLS for remote databases, bounded connection,
statement, and lock timeouts, parameterized values, and safely quoted,
allowlisted SQL identifiers. Never disable constraints, triggers, auditing,
TLS verification, or row-level security to make a seed pass. Do not create or
alter schema, grants, or shared reference data as part of seeding.

## Read-Only Relationship Discovery

1. Inspect existing feature specifications, page objects, DB helpers, migrations,
   and application model/query definitions that are available. Treat placeholder
   queries as unverified, not as schema documentation.
2. Connect in a read-only transaction with bounded queries. Read catalog metadata
   first: tables/views, columns/types, defaults, generated keys, nullability,
   primary/foreign keys, unique/check constraints, indexes, triggers, policies,
   partitions, and soft-delete fields.
3. Trace the requested user's relationships into medicine catalog entries,
   prescriptions, prescription items, validity dates, status, organization,
   prescriber, and any required linking entities. These are conceptual roles,
   not assumed table names. Resolve only roles the real schema requires.
4. Use minimal, masked samples restricted to the approved test identity when
   metadata is insufficient. No broad patient-table dumps or copying another
   user's medical records. A similarly named column is not proof of a join.
5. Produce a sanitized relationship map with parent/child keys, cardinality,
   tenant/user ownership, insert order, cleanup order, and source evidence.
   Mark absent FK constraints and inferred links explicitly.
6. Confirm application read filters, status/date semantics, caches/read models,
   soft-delete visibility, and trigger/outbox/job side effects. SQL success
   alone does not prove the UI will read an entity. Block writes if required
   rules or downstream effects remain unknown; request focused clarification.
7. Store verified schema-only knowledge in existing project documentation when
   appropriate. Record application/environment, schema version or fingerprint,
   verification date, and evidence. Revalidate on drift; never persist raw data
   or turn an inference into a verified relationship without evidence.

Before implementation, present the minimum insert graph, required defaults and
reference IDs, user scoping, date rules, UI-readable fields, soft-delete plan,
and unresolved blockers. Do not invent medicine codes, doses, clinical rules,
prescribers, or category statuses; use approved synthetic/reference values.

## Dates and Medicines Coverage

- Capture one reference timestamp per run in Asia/Jerusalem, with DST-aware
  date handling. Use the verified DB column's timestamp/date semantics.
- Create at least three feature-relevant entities: reference date +2 calendar
  days, +1 week, and +1 calendar month. A calendar month is not 30 days; clamp
  to the destination month's last valid day before working-day adjustment.
- Move any target on Friday, Saturday, or an Israeli public holiday forward
  to the next working day, repeating until valid. Use a maintained Israel
  holiday library and confirm organization-specific closures/holiday-eve policy
  when relevant. If a required calendar cannot be resolved, block rather than
  silently including holidays. Keep dates distinct when a feature requires it.
- Use a documented valid time of day for datetime fields. Ask if the entity's
  scheduling rules leave it unspecified; do not assume clinic opening hours.
- Preserve both nominal and adjusted dates in the sanitized seed manifest.
- Learn which medicine date field controls UI eligibility before assigning it.
  Future-date seeds do not automatically belong in expired/previous categories.
  Use scenario-specific data for historical or empty-state coverage; never
  populate the very panel an empty-state scenario expects to be empty.

## Before-All and After-All Lifecycle

Implement the requested @beforeAll behavior as a scoped pytest fixture or the
repo's supported suite hook, not a literal unsupported pytest decorator.
Seed once before the selected feature suite's dependent tests; clean up after
the last dependent test, not after each scenario. Class/module scope can express
one suite; use a coordinated run-level fixture if multiple modules share it.
Do not use an unconditional project-wide autouse seeder.

1. Resolve and verify the full execution contract. Generate a run-specific
   ownership manifest and register cleanup before any committed mutation.
2. Acquire an appropriate suite/user lock or reject conflicting parallel runs.
   pytest session fixtures run once per xdist worker, not once globally: use a
   controller/lock protocol with one cleanup owner, isolate accounts, or reject
   parallel mode until coordination is implemented.
3. Insert the minimal parent/child graph in an explicit transaction, returning
   actual generated IDs. Reuse approved reference rows without modifying them.
   Roll back partial creation on failure. Do not use MAX(id)+1 or broad upserts
   that can overwrite existing records. A retry must not duplicate committed seeds.
4. Commit before browser validation: the application uses separate connections
   and cannot see uncommitted rows. Transaction rollback after the UI test is
   therefore not a cleanup strategy for already committed data.
5. Read back the committed rows by returned IDs and verified user/tenant keys.
   Yield typed seed metadata for UI tests: IDs, approved display identifiers,
   categories, and dates. Leave UI assertions to the QA/page-object layer, but
   ensure it can identify these exact new records rather than unrelated rows.
   Apply bounded readiness checks for documented asynchronous propagation.
6. Run finalization after pass, assertion failure, or later setup failure.
   Track any partial committed state as well. Soft-delete only this run's own
   entities using the real application's deletion convention and dependency order.
7. Verify affected-row counts and read visibility using the discovered filters.
   Cleanup is idempotent: already-soft-deleted or absent owned rows are harmless.
   Never delete by personal number alone, date range alone, or broad name match.

Maintain crash-recoverable ownership tracking, preferably through an existing
approved correlation field. Otherwise use a restricted local/CI manifest outside
git/public reports with exact created IDs and target identity. Do not alter the
schema to add tracking. Define protection and retention for sensitive identifiers
and a recovery path for a crash around commit; block unsafe retry/cleanup when
ownership cannot be established.

## Best-Effort Soft Deletion

Cleanup failure is non-fatal by user policy: preserve the test's original result
and emit an explicit Allure cleanup warning. Never claim cleanup succeeded when
it did not, and never hide failures. Report sanitized run ID, counts, reason,
and the restricted recovery-manifest location; keep medical details private.

Use only the verified soft-delete/status transition. If no supported soft-delete
mechanism exists, leave the records and report the limitation. No fallback hard
DELETE, TRUNCATE, cascading destructive operation, or changes to existing users,
catalog rows, or another run's entities. Do not modify shared parent records.

Teardown cannot run after forced termination or host failure. Provide an explicit,
idempotent recovery command with environment and ownership checks and a dry-run
preview. It must never sweep unrelated rows. Detect leftovers before later runs
and prevent misleading empty-state checks; non-fatal cleanup does not mean
residual records may be ignored during the next setup.

## Ownership and Validation

- CORE owns reusable connection/transaction support, environment guards,
  manifests, lifecycle coordination, and common date utilities when justified.
- TEST owns Meditik entity adapters, SQL relationships, synthetic factories,
  feature-specific fixtures, and UI expectations. Add CPR GO only after its own
  schema/environment mapping is verified. Do not change CORE without reading its
  instructions and identifying the generic need.
- Reuse the qa-automation skill for UI work, live data-testid inspection,
  executable pytest/BDD duplicates, and test-case tracker updates. Do not mark
  pending cases active merely because database rows were created.
- Test wrong environment/user rejection, parameterization, FK insertion order,
  partial failure rollback, parallel/retry isolation, calendar month-end/DST/
  weekends/holidays, exact-record UI validation, and owned-only soft deletion.
- Validate the smallest medicines slice on the approved TEST identity first.
  Exercise failed-test cleanup and cleanup warnings before widening to PREPROD.
  Never claim live DB/UI verification from mock tests or collection alone.

## Completion Report

Report resolved application/environment and masked user identity; verified schema
relationships versus remaining assumptions; entities planned/created; date
adjustments; selected tests and their outcomes; cleanup counts and leftovers;
sanitized Allure/manifest locations; and TEST/CORE files changed. Clearly separate
discovery-only, seeding, UI verification, and cleanup results.

If connectivity, database name/schema, mapping, reference values, or permissions
are missing, state the specific blocker. Never guess a database name from an RDS
hostname, use another environment's credentials, or broaden privileges silently.
