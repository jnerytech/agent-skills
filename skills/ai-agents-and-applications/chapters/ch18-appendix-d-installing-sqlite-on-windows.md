# Appendix D: Installing SQLite on Windows

## Core Idea
SQLite needs no installer on Windows — unzip the tools package into a folder and add that folder to the system Path, then verify with `sqlite3`.

## Code Examples
```text
1. Download the latest zipped tools package from www.sqlite.org/download.html
   (e.g., sqlite-tools-win-x64-3460100.zip).
2. Unzip it to a folder, e.g., C:\sqlite
   -> files land in C:\sqlite\sqlite-tools-win-x64-3460100
3. Add that folder to the Path:
   Control Panel > "edit system environment variables" > Environment Variables
   > System Variables > Path > Edit > add C:\sqlite\sqlite-tools-win-x64-3460100
4. Open a new command shell and run:
   sqlite3
   -> should enter the SQLite prompt
```
- **What it demonstrates**: the minimal download-unzip-Path-verify sequence needed to get a working `sqlite3` CLI on Windows.

## Key Takeaways
1. No installer is required — unzipping plus a Path entry is sufficient.
2. Open a *new* command shell after editing Path, since existing shells won't pick up the change.
3. This setup is a prerequisite for the SQL-database examples used in chapters 10 and 12.

## Connects To
- **Ch 10**: query generation, routing, and retrieval postprocessing (structured SQL query generation)
