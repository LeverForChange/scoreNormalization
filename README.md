This open source Python program, overall, reads data using the Torque API, handles missing values and outliers, calculates statistics, normalizes scores using two techniques - Min-Max normalization and Z-score normalization, performs data pivoting, calculates overall scores, ranks applications, and saves the results in a new CSV file. 

See [DESIGN.md](DESIGN.md) for more information.

# Usage

Copy `config.py.tmpl` to `config.py` and update the variables

```
$ cp config.py.tmpl config.py
$ $EDITOR config.py
```

Install dependencies

```
$ pip install pandas numpy seaborn matplotlib
```

Run

```
$ python main.py
```
