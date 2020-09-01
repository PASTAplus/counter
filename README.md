# counter
Reports data package and entity read counts from the EDI data repository, and
more...

## How does *counter* work

*counter* analyzes download metrics for each data package in the EDI data
repository during the period of time selected using the "start" and "end"
date options. Specifically, *counter* determines what data entities were
available for download during this period and then "counts" the number of
times they were requested for download through the PASTA+ REST API. This
value is recorded in a SQLite database, along with the data entity resource
identifier (its unique identifier within PASTA+), the package identifier
of the associated data package, the common name of the data enitty as found
in metadata, and the creation date and time of the data entity.

Using the information obtained for each data entity (specifically, the data
package identifier), *counter* then collects the data package metadata to
obtain the title and DOI of the data package, and then calculates the total
downloads for all data entities in the data package. This information is also
recorded in a SQLite database.

*counter* has two options for obtaining the above information: first, and by
default, *counter* uses the PASTA+ REST API to collate and aggregate the
download metrics. Alternatively, *counter* can use direct connections
to PASTA+ databases to generate the same download metrics -- this alternate
approach is much faster, but does require access privileges to PASTA+ databases.

## How to install *counter*

The most direct and straightforward way to install *counter* is to clone the
*counter* github repository `git clone https://github.com/PASTAplus/counter.git`
and install the necessary Python3 dependencies found in `environment-min.yml`
or `requirements.txt`.

Development was performed in a `conda` virtual environment using the PyCharm IDE.
To replicate and run *counter* in this manner, you must first install `anaconda3`
from https://www.anaconda.com/products/individual, and then create a working `conda`
virtual environment using `conda env create --file environment-min.yml`. `conda`
will use the dependency specifications in the `environment-min.yml` file to install
the appropriate Python3 packages. Once installed in this manner, you may execute
*counter* using either `python counter.py <OPTIONS> SCOPE CREDENTIALS` or by
installing *counter* using `pip install .` and then running it directly from the
command line as `counter <OPTIONS> SCOPE CREDENTIALS`. See below for specific
options and required arguments.


## How to use *counter*
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
