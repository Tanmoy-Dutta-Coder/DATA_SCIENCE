# Data Science Learning Repository

A practical collection of exercises and study notes from a data-science learning batch. The repository brings together Python fundamentals, object-oriented programming, NumPy, Pandas, basic data visualization, and introductory HTML, CSS, and JavaScript practice.

The examples are intentionally small and exploratory. They are designed to be read, run, modified, and used as stepping stones toward larger data-analysis projects.

## Learning Tracks

| Track | What it covers | Start here |
| --- | --- | --- |
| Python | Strings, lists, dictionaries, functions, user input, random values, and small console programs | [`PYTHON/test.py`](PYTHON/test.py), [`PYTHON/don.py`](PYTHON/don.py) |
| Object-oriented Python | Classes, inheritance, composition, polymorphism, operator overloading, and method overriding | [`PYTHON/oop_13_Aug.py`](PYTHON/oop_13_Aug.py), [`PYTHON/poly_3.py`](PYTHON/poly_3.py) |
| NumPy | Arrays, dimensions, dtypes, casting, random distributions, concatenation, stacking, and splitting | [`NUMPY/code1.py`](NUMPY/code1.py), [`NUMPY/Array_manipulation/Stack1.py`](NUMPY/Array_manipulation/Stack1.py) |
| Pandas and visualization | DataFrames, indexing, missing values, CSV/JSON/Excel input, date handling, resampling, rolling calculations, and plots | [`PANDAS/p2.ipynb`](PANDAS/p2.ipynb), [`PANDAS/data visualization.ipynb`](PANDAS/data%20visualization.ipynb) |
| Web fundamentals | CSS selectors, specificity, typography, colors, layouts, navigation, and JavaScript operators and conditionals | [`WEBDEEV/CSS_PRACTICE/grid_pr.html`](WEBDEEV/CSS_PRACTICE/grid_pr.html), [`WEBDEEV/JS/Js_if_else.js`](WEBDEEV/JS/Js_if_else.js) |

## Repository Layout

```text
DATA_SCIENCE/
├── NUMPY/
│   ├── code1.py                 Basic array creation
│   ├── code_2.py                Dtype conversion and memory size
│   ├── code_3.py                Array dimensions
│   ├── RANDOM/unifrom.py        Random distributions and seeding
│   └── Array_manipulation/      Concatenation, stacking, splitting
├── PANDAS/
│   ├── p2.ipynb                 DataFrame operations and file loading
│   ├── practice.ipynb           DataFrame editing and missing values
│   ├── Resampling.ipynb         Datetime indexes, resampling, and windows
│   ├── data visualization.ipynb Plot examples with Matplotlib
│   ├── d.py, datav.py            Small Pandas scripts
│   └── Qestion_practice/        CSV, Excel, JSON, and analysis exercises
├── PYTHON/
│   ├── q100.py                  Large bank of Python/OOP practice questions
│   ├── poly_*.py                Polymorphism and operator-overloading examples
│   └── *.py                     Fundamentals, inheritance, and console exercises
├── WEBDEEV/
│   ├── CSS_PRACTICE/            Standalone CSS/HTML experiments
│   ├── JS/                      JavaScript fundamentals
│   └── pr/                      Two static page layout exercises
├── LICENSE                      MIT License
└── README.md                    This guide
```

## Getting Started

### Requirements

- Python 3.10 or newer
- NumPy
- Pandas
- Matplotlib
- Jupyter Notebook or JupyterLab for `.ipynb` files
- A modern browser for the HTML exercises
- Node.js is optional and useful for running the JavaScript files from a terminal

The repository does not currently include a dependency manifest. Create a virtual environment and install the data-science dependencies with:

```bash
python -m venv .venv
```

Windows PowerShell:

```powershell
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
python -m pip install numpy pandas matplotlib jupyter openpyxl
```

macOS/Linux:

```bash
source .venv/bin/activate
python -m pip install --upgrade pip
python -m pip install numpy pandas matplotlib jupyter openpyxl
```

`openpyxl` is included because the Pandas question set loads [`stores.xlsx`](PANDAS/Qestion_practice/stores.xlsx).

## How to Use the Repository

### Run a Python example

Run examples from the repository root so that relative paths behave as expected:

```bash
python NUMPY/code1.py
python NUMPY/Array_manipulation/Stack1.py
python PYTHON/oop_13_Aug.py
```

Many Python files are interactive or execute their demonstration code immediately, so read the file before running it. Input-driven examples may wait for values in the terminal.

### Open the notebooks

```bash
jupyter notebook
```

Then open one of the notebooks under `PANDAS/`. A useful progression is:

1. [`PANDAS/p2.ipynb`](PANDAS/p2.ipynb) for DataFrame creation, indexing, columns, and file input.
2. [`PANDAS/practice.ipynb`](PANDAS/practice.ipynb) for editing and cleaning DataFrames.
3. [`PANDAS/Resampling.ipynb`](PANDAS/Resampling.ipynb) for datetime indexes, resampling, rolling means, and expanding means.
4. [`PANDAS/data visualization.ipynb`](PANDAS/data%20visualization.ipynb) for Matplotlib plots including bar, line, pie, histogram, box, and hexbin charts.
5. [`PANDAS/Qestion_practice/question.ipynb`](PANDAS/Qestion_practice/question.ipynb) for a small multi-file data-loading exercise.

The question notebook works with:

- [`sales_raw.csv`](PANDAS/Qestion_practice/sales_raw.csv): sales transactions with mixed date formats and missing values.
- [`stores.xlsx`](PANDAS/Qestion_practice/stores.xlsx): store reference data.
- [`returns.json`](PANDAS/Qestion_practice/returns.json): transaction return dates and reasons.

### View the web exercises

Open the HTML files directly in a browser. The static page exercises can be opened from [`WEBDEEV/pr/index.html`](WEBDEEV/pr/index.html) and [`WEBDEEV/pr/index1.html`](WEBDEEV/pr/index1.html). Their stylesheets and local image asset are stored beside them.

The web examples use external Google Fonts, Unsplash images, Font Awesome, and a YouTube embed in some pages, so those pages need an internet connection for the complete visual experience.

To run the JavaScript examples with Node.js:

```bash
node WEBDEEV/JS/Js_if_else.js
node WEBDEEV/JS/for_js_data_ver.js
```

## Suggested Study Path

1. Build confidence with the small Python scripts in `PYTHON/`.
2. Practice array shape and manipulation concepts in `NUMPY/`.
3. Move to DataFrames and file input in `PANDAS/`.
4. Apply cleaning and date operations to the files in `PANDAS/Qestion_practice/`.
5. Use the visualization notebook to communicate patterns in tabular data.
6. Continue with the OOP examples and the question bank in [`PYTHON/q100.py`](PYTHON/q100.py).
7. Explore the web fundamentals in `WEBDEEV/` as a separate frontend practice track.

## Current Notes

This is a practice repository, not a packaged application. Some files are intentionally incomplete, commented out, or written to demonstrate an error. In particular:

- [`PYTHON/menu.py`](PYTHON/menu.py) and [`PYTHON/q100.py`](PYTHON/q100.py) currently contain incomplete blocks and are not syntax-clean entry points.
- [`PYTHON/multi_level.py`](PYTHON/multi_level.py) contains an import path that depends on a package named `foldet`, which is not present in this repository.
- Several NumPy and Pandas examples demonstrate invalid or version-sensitive operations and may need correction while being studied.
- Notebook outputs capture the state of earlier runs and may not match the current installed library versions. Re-run cells from the top when experimenting.
- Filenames retain their original learning-batch spelling, including names such as `Qestion_practice`, `unifrom.py`, `concatinate.py`, and `ploy_2.py`.

Treat errors as part of the learning workflow: isolate the failing cell or statement, inspect the library error, and update the example with a small reproducible fix.

## License

Released under the [MIT License](LICENSE). See [`LICENSE`](LICENSE) for the complete text.
