"""Google Sheets integration will be added in the next implementation step.

Planned approach:
- Google Sheets API v4 with a service account.
- One row per job, keyed by company + external_job_id.
- Batch updates rather than one API request per job.
- Keep credentials outside source control.
"""
