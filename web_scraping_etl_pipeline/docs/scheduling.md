# Scheduling notes

## Windows Task Scheduler (recommended for a first project)
1. Create a virtual environment and install requirements.
2. Find the full path to the virtual environment's Python executable.
3. Create a task with a daily trigger.
4. Program/script: full path to `.venv\Scripts\python.exe`
5. Add arguments: `-m src.pipeline --pages 2`
6. Start in: the project root folder.
7. Run once manually first; inspect `logs/pipeline.log` and `reports/`.

## macOS/Linux cron example
Run `crontab -e` and add a daily job, changing the project path:
```cron
0 8 * * * cd /path/to/web_scraping_etl_pipeline && /path/to/.venv/bin/python -m src.pipeline --pages 2
```

## Important
- Scheduled jobs need the right working directory and environment variables.
- Keep database credentials out of source control.
- Do not schedule aggressive scraping. Use small page counts and polite delays.
