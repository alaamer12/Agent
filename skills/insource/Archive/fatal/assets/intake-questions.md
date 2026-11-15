# Intake: ask only what the artifacts cannot tell you

Before asking, run `scripts/crash_triage.py` and read the logs. Then ask at most these (one message, skip the answered):
1. When did you last SEE it running, and when did you notice it gone? (gives the death window)
2. What was the app doing / hidden / minimised / on battery / locked screen / asleep in that period?
3. Did anything on the machine run in that window (build, installer, update, scheduled task, logoff)?
4. Does it happen on a schedule (~N hours), after specific actions, or randomly?
5. Which build/version, and is it the installed copy or a portable/extracted copy?
6. Where are the app's logs and (if any) dumps? Are crash dumps enabled?
7. What has already been tried, and what evidence made people believe it was fixed?
