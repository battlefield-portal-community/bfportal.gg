# Generalizing "likes" to any page type

## Context

When the project began, "liking" was hard-bound to `ExperiencePage`. The like
relationship is currently stored **three times** across separate, manually-synced
join tables:

- `Profile.liked` — M2M → `core.ExperiencePage` (`core/models/users.py:41`)
- `ExperiencePage.liked_by` — M2M → `core.Profile` (`core/models/experience.py:157`)
- `SnippetPage.liked_by` — M2M → `core.Profile` (`bf6/models/scripts_page/snippets.py:68`)

`Profile.add_liked_page` / `remove_liked_page` (`users.py:70-84`) exist only to keep
the two experience tables in sync. The bf6 `SnippetPage` copied the `liked_by` field
but nothing else was generalized: the view, template filter, profile "liked" page,
and `Profile.liked` are all still hardcoded to `ExperiencePage`, so snippet likes
can't actually be created or displayed through the normal flow.

Now that more likeable page types are being added (snippets, and more to come), we
want a single, type-agnostic way to like **any** page.

Key enabling fact: everything likeable is a Wagtail `Page` subclass
(`ExperiencePage`, `SnippetPage` both inherit `CustomBasePage` → `Page`), and Wagtail
page IDs are globally unique across page types. The like endpoint already only needs
a page id.

## Agreed approach

Replace the per-type M2M tables with **one central `Like` model** keyed by a direct
FK to `wagtailcore.Page`:

```
Like:
  profile  FK → core.Profile        related_name="likes"
  page     FK → wagtailcore.Page     related_name="likes"
  created  DateTimeField(auto_now_add=True)
  Meta: unique_together = (profile, page)
```

Rationale (vs. the two approaches considered):
- A field-per-model on `Profile` or a column-per-type `Likes` table both require a
  schema change + migration for every new likeable type. The FK-to-Page table makes
  **any current or future page type likeable with zero schema change**.
- Gives DB-level referential integrity and cascade-on-delete (the manual-sync
  helpers give neither).
- Both directions become trivial: `page.likes.count()` for the count;
  `Page.objects.filter(likes__profile=p).specific()` for "everything a user liked"
  across all types in one query; `page.specific` resolves the concrete type for
  rendering.

Decision: likeables are **Pages only** (no ContentType/GenericForeignKey needed).

Decision on existing data: **backfill the new table, but keep the old M2M fields in
place** as a rollback safety net for now (dropping them is a later change). To keep
those old fields a *valid* rollback target, writes should **dual-write** during the
transition — update the new `Like` row and the old M2M(s) in one place.

### Shape of the changes

- **New model + migration** in `core` (alongside `Profile`): the `Like` model above,
  plus a **data migration** that backfills one `Like` row per existing entry in
  `ExperiencePage.liked_by` and `SnippetPage.liked_by` (dedupe against
  `unique_together`). Note `tasks.py` already has a `--populate_liked_by` backfill
  command as precedent for this kind of one-off sync.

- **Centralize like/unlike + dual-write.** Rework `Profile.add_liked_page` /
  `remove_liked_page` (`core/models/users.py:70-84`) — or add a small
  `toggle_like(page)` helper — to operate on a generic `Page` and write both the new
  `Like` row and the legacy M2M field(s) so old fields stay consistent for rollback.

- **Generalize the view.** `handle_like_request` (`core/views.py:326-340`, routed at
  `bfportal/urls.py:74-78` as `api/like/<id>/`) should fetch the page generically
  (`Page.objects.get(id=page_id)`, no `.specific` needed to create a `Like`) instead
  of `ExperiencePage.objects.get(...)`, then toggle via the helper and return the new
  `page.likes.count()`. The JS caller in `bf6/templates/bf6/base.html`
  (`add_to_liked`) already just posts the id and reads back a count — no change
  needed there.

- **Shared `like_count`.** Both `ExperiencePage.like_count` (`experience.py:240-243`)
  and `SnippetPage.like_count` (`snippets.py:139-141`) become `self.likes.count()`.
  Factor into a tiny mixin the likeable models use (keeps it consistent for future
  types).

- **`is_liked_by_user` filter** (`core/templatetags/template_filters.py:77-81`):
  switch from `post in request.user.profile.liked.all()` to an existence check on the
  new table (`Like.objects.filter(profile=..., page=post).exists()`), so it works for
  any page type. Optional follow-up: prefetch the set of liked page ids once per
  request instead of one check per card.

- **Profile "liked" listing.** The `/liked/` route and profile template currently
  read `profile.liked.all()` (`users.py:185-196`,
  `core/templates/core/profile_page.html:91-103`) — both experience-only. Repoint at
  `Page.objects.filter(likes__profile=user.profile).specific()` so liked snippets (and
  future types) show up. Also revisit `earned_likes` (`users.py:149`,
  aggregates `Count("liked_by")` over experiences) if snippet likes should count.

- **API/serializers.** `ExperiencePage` exposes `liked_by` (`core/api/experience.py:45`,
  `core/serializers/experiences.py`). During the transition these keep working off the
  old field (dual-written). Add the equivalent to the snippet API when its serializer
  is built; longer term these can derive from `page.likes`.

### Files touched (representative)

- `core/models/users.py` — `Like` model, `Profile` helpers, profile `/liked/` route,
  `earned_likes`.
- `core/migrations/` — new schema migration + data-migration backfill.
- `core/views.py` — generalize `handle_like_request`.
- `core/models/experience.py`, `bf6/models/scripts_page/snippets.py` — `like_count`
  via shared mixin.
- `core/templatetags/template_filters.py` — `is_liked_by_user`.
- `core/templates/core/profile_page.html` (+ related listing templates) — liked list.
- Old M2M fields (`Profile.liked`, `*.liked_by`) are **kept** for now.

## Verification

1. `python manage.py makemigrations core` produces the `Like` model + confirm the
   hand-written data migration; `migrate` runs clean on a copy of the DB.
2. After migrate, spot-check counts: number of `Like` rows == total rows across
   `ExperiencePage.liked_by` + `SnippetPage.liked_by` (minus any dupes).
3. Run the app; on an **experience** page and a **snippet** page: click the heart —
   count increments, icon fills, refresh persists; click again — decrements/unfills.
   Confirm both the new `Like` row and the legacy `liked_by` are written (dual-write).
4. Visit a profile's `/liked/` page — liked snippets *and* experiences both appear.
5. `is_liked_by_user` shows filled hearts on listing cards for both types when logged
   in as a user who liked them.
6. Re-run the mock commands (`core .../mock.py`, `bf6 .../mock_snippets.py`) if they
   should now populate the `Like` table too.
