TODO: Remove this after migrations are done!

WIP

## 1. Shut down the server

## 2. Backup the droplet and database

## 3. Run migrations

    python manage.py migrate

## 4. Remove duplicated corrections

The PerfectRow and CorrectedRow had some duplicated rows, total ~4000 entries.

    python manage.py remove_duplicate_corrections

## 5. Remove duplicated post replies

There were 5 duplicate post replies.

    python manage.py remove_duplicate_postreply

## 6. Run script to migrate data

    python manage.py migrate_data

This script will:

- migrate PerfectRow, CorrectedRow -> PostCorrection
- migrate OverallFeedback -> PostUserCorrection
- migrate PostReply -> Comment

## ?. Cleanup

- Remove deprecated code (Marked with `remove`)
- Remove management commands: `migrate_data`, `remove_duplicate_corrections`, `remove_duplicate_postreply`
- Remove this `MIRATION_GUIDE`
- Look over any TODO

##

---- DEV LOG / WIN

- PostList perf incr 895.30ms -> 527.95ms
