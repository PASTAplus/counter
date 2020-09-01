# counter
Reports data package and entity read counts from the EDI data repository, and
more...

## How to use
```
Usage: counter [OPTIONS] SCOPE CREDENTIALS

  Perform analysis of data entity downloads for the given PASTA+ SCOPE from
  START_DATE to END_DATE.

      SCOPE: PASTA+ scope value
      CREDENTIALS: User credentials in the form 'DN:PW', where DN is the
          EDI LDAP distinguished name and PW is the corresponding password

Options:
  -s, --start TEXT  Start date from which to begin search in ISO 8601
                    format(default is 2013-01-01T00:00:00)

  -e, --end TEXT    End date from which to end search in ISO 8601 format
                    (default is today)

  -p, --path TEXT   Directory path for which to write SQLite database and CSVs
  -n, --newest      Report only on newest data package entities
  -d, --db          Use the PASTA+ database directly (must have authorization)
  -c, --csv         Write out CSV tables in addition to the SQLite database
  -q, --quiet       Silence standard output
  -h, --help        Show this message and exit

```
