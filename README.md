# migrate_dsdf

Script to migrate outside hours from one dreaming.com account to another.
Usefull if you have been logging dreaming french hours to a separate dreaming spanish account before dreaming french launched.

Usage:

# Spanish to French (default)
python migrate_progress.py --source-token TOKEN1 --target-token TOKEN2

# French to Spanish
python migrate_progress.py --source-token TOKEN1 --target-token TOKEN2 --source-language fr --target-language es

# Spanish to Spanish (same language, different accounts)
python migrate_progress.py --source-token TOKEN1 --target-token TOKEN2 --source-language es --target-language es

# French to French (same language, different accounts)
python migrate_progress.py --source-token TOKEN1 --target-token TOKEN2 --source-language fr --target-language fr

# Execute migration (add --execute flag)
python migrate_progress.py --source-token TOKEN1 --target-token TOKEN2 --source-language es --target-language fr --execute
