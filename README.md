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
*counter* github repository, create a Python virtual environment and activate,
install the necessary Python dependencies found in `environment-min.yml`
or `requirements.txt`, and then copy the file `config.py.template` to
`config.py`:

1. `git clone https://github.com/PASTAplus/counter.git`
1. `cd counter`
1. `conda env create --file environment-min.yml` or `pip install
    -r requirements.txt` (if using conda, a virtual environment will
    be created at this step; if using another Python distribution, create
    and activate a virtual environment per the distribution prior to doing `pip
    install`)
1. `cp ./src/counter/config.py.template ./src/counter/config.py`

If everything is installed correctly, you should be able to run
```
python counter.py --help
```
and see the *counter* help information.

Development was performed in a `conda` virtual environment using the PyCharm IDE.
To replicate and run *counter* in this manner, you must first install `anaconda3`
from https://www.anaconda.com/products/individual, and then create a working `conda`
virtual environment using `conda env create --file environment-min.yml`. `conda`
will use the dependency specifications in the `environment-min.yml` file to install
the appropriate Python3 packages. Once installed in this manner, you may execute
*counter* by first activating the *counter* virtual environment (`conda activate
counter`), and then using either `python counter.py <OPTIONS> SCOPE CREDENTIALS` or
by installing *counter* using `pip install .` and then running it directly from the
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

Running *counter* only requires the **SCOPE** of the data package of interest
and the **CREDENTIALS** for your EDI LDAP account, and of course, the *start*
and *end* dates of the time period you would like to analyze:

```
counter -s "2019-01-01T00:00:00" -e "2020-01-01T00:00:00" knb-lter-sev "<DISTINGUISHED_NAME>:<PASSWORD>"
```
Analysis times depend on the number of data entities found within the time
period and how busy PASTA+ is when running *counter*. In general, you can
expect *counter* to take between 10-30 seconds per entity. And since *counter*
utilizes a considerable number of PASTA+ REST API calls to perform the analysis,
its execution will result in PASTA+ becoming quite busy, naturally. With this
in mind, please be considerate of other users when running *counter* -- thanks!

## *counter* output

Data collected by *counter* is motivated by the needs of information managers
who need to report download statistics to colleagues and funding agencies. Two
sets of data are collected: 1) download metrics at the data entity level and 2)
basic metadata at the data package level, including an aggregated sum of all
data entity counts within the data package (see table schemas below).

### table *entities*:

1. **rid** (resource identifier) - string, primary key
1. **pid** (package identifier) - string
1. **date_created** (date of entity creation in PASTA+) - datetime
1. **count** (download count) - integer
1. **name** (entity common name) - string

### table *packages*:

1. **pid** (package identifier) - string, primary key
1. **doi** (package digital object identifier) - string
1. **title** (package title) - string
1. **count** (aggregated download count) - integer

### Thoughts on schema design

The two tables provide a means for users to generate any number of reports, including a simple summary
report by using only the *packages* table. One key aspect of the *entities* table is the `date_created`
value: one can better understand count values by placing the data entity into a timeline perspective,
especially if counts seem unusually low. For example, if your end date is 2020-01-01T00:00:00, and the date_created
of a data entity is 2019-12-15T14:03:12, then a low download count may be reasonable since the data entity was only 
avaiable 16 days for download. If, however, the date_created was 2013-12-15T4:03:12, I would be suspicious of
the low count.