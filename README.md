This open source Python program, overall, reads data using the Torque API, handles missing values and outliers, calculates statistics, normalizes scores using two techniques - Min-Max normalization and Z-score normalization, performs data pivoting, calculates overall scores, ranks applications, and saves the results back up to Torque. 

See [DESIGN.md](DESIGN.md) for more information.

# Usage

Copy `config.py.tmpl` to `config.py` and update the variables

```
$ cp config.py.tmpl config.py
$ $EDITOR config.py
```

## Install dependencies

```
$ pip install pandas numpy seaborn matplotlib torqueclient
```

## Run

```
$ python main.py [--csv]
```

The `--csv` option is to output the result to a csv file rather than uploading to torque.

## Install as a local library

```
$ pip3 install -e .
```
