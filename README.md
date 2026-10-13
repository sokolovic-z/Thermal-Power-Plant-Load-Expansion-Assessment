# Load Expansion Study in DIgSILENT PowerFactory

**Automated Load Expansion Analysis Using Python**

## Overview

This project implements a Python-based workflow for conducting load expansion studies in **DIgSILENT PowerFactory**. The script automates the process of adding new loads to medium-voltage and low-voltage network buses, progressively increasing their active power, performing load flodw calculations, and identifying network operating limit violations.

The objective is to determine the maximum additional active load that can be connected at selected network nodes while respecting voltage limits and equipment loading constraints.

## Features

* **PowerFactory integration:** Automates network simulations using the PowerFactory Python API.
* **Project and study case activation:** Imports a PowerFactory project and activates a study case and operation scenario.
* **Network variation management:** Creates a network variation and expansion stage for the study.
* **Automatic load creation:** Adds new load elements to selected network buses.
* **Incremental load increase:** Progressively increases active power in configurable steps.
* **Load flow analysis:** Executes load flow calculations after each load increment.
* **Violation detection:** Checks bus voltages and the loading of lines, transformers, and series reactors.
* **Power factor assignment:** Estimates the load power factor using connected asynchronous motors, with a fallback value when no motors are identified.
* **Excel export:** Saves the detected operating limits and associated network violations to an Excel file.

## Methodology

The analysis follows an incremental load expansion approach:

1. Initialize the PowerFactory application and import the network project.
2. Activate the relevant study case and operation scenario.
3. Create a network variation and expansion stage.
4. Retrieve network elements required for the analysis.
5. Identify energized buses with nominal voltages up to 6 kV.
6. Exclude selected network elements from the study.
7. Create a new load at each selected bus.
8. Assign an initial active power and an assumed power factor.
9. Increase the load active power incrementally.
10. Execute a load flow calculation after each increment.
11. Check for voltage violations and equipment overloading.
12. Record the loading level at which a violation is detected.
13. Export the results to Excel.

### Technical criteria

| Parameter              | Description                                   |
| ---------------------- | --------------------------------------------- |
| Load model             | PowerFactory `ElmLod`                         |
| Load input mode        | Active power and power factor (`PC`)          |
| Initial active power   | 0 MW                                          |
| Active power increment | 0.1 MW                                        |
| Power factor           | Estimated from associated asynchronous motors |
| Voltage monitoring     | Bus voltage magnitude                         |
| Line monitoring        | Line loading                                  |
| Transformer monitoring | Calculated transformer loading                |
| Reactor monitoring     | Reactor loading                               |
| Results format         | Excel (`.xlsx`)                               |

The active power increment can be adjusted to obtain a finer or coarser estimate of the maximum load.

## Project Structure

```text
Load-Expansion-Study/
├── project/
│   └── thermal_power_plant.pfd
├── output/
│   └── results.xlsx
├── src/
│   └── load_expansion.py
├── requirements.txt
└── README.md
```

*The structure above is illustrative; adapt the filenames and directories to match the actual repository.*

## Requirements

* DIgSILENT PowerFactory 2024 SP2
* A compatible Python version supported by the installed PowerFactory release
* Access to the PowerFactory Python API
* Python packages:

  * `pandas`
  * `numpy`
  * `openpyxl`

The PowerFactory Python API is provided by the PowerFactory installation and is not installed through a standard `pip install powerfactory` command.

## Configuration

Before running the script, verify the following settings:

### 1. PowerFactory Python API path

Update `POWERFACTORY_PYTHON_PATH` to match your local installation:

```python
POWERFACTORY_PYTHON_PATH = Path(
    r"C:/Program Files/DIgSILENT/PowerFactory 2024 SP2/Python/3.12"
)
```

The Python interpreter and API version must be compatible with your PowerFactory installation.

### 2. Project file path

Set `PROJECT_FILEPATH` to the location of the PowerFactory project file:

```python
PROJECT_FILEPATH = (
    ROOT_PATH / "project" / "thermal_power_plant.pfd"
)
```

### 3. Load increment

The active power increment is configured as:

```python
deltaP = 0.1  # MW
```

Adjust this value according to the desired resolution of the study.

### 4. Network selection

The script filters energized terminals with nominal voltages up to 6 kV and excludes selected elements whose names contain `SKO`. Modify these conditions to match the network under investigation.

## Running the Study

1. Install the required Python packages:

   ```bash
   pip install pandas numpy openpyxl
   ```

2. Ensure that DIgSILENT PowerFactory is installed and its Python API is accessible.

3. Configure the PowerFactory API path and project file path.

4. Verify that the project contains the required study case, operation scenario, and network model.

5. Run the script using a compatible Python interpreter:

   ```bash
   python src/load_expansion.py
   ```

Execution may also require appropriate PowerFactory licensing, permissions, and a valid application session.

## Output

The script exports its results to:

```text
output/results.xlsx
```

The spreadsheet contains the following columns:

| Column             | Description                                            |
| ------------------ | ------------------------------------------------------ |
| `Bus`              | Bus associated with the added load                     |
| `Smax`             | Apparent power value calculated by the script          |
| `Pmax`             | Active power at the detected violation                 |
| `cosphi`           | Assumed load power factor                              |
| `Critical element` | Network element associated with the detected violation |
| `Value`            | Voltage or loading value recorded for that element     |

**Important:** The recorded power corresponds to the first simulated increment at which the script detects a violation. It should not automatically be interpreted as the exact maximum permissible load. A refined search and validation of the preceding feasible operating point may be required.

## Limitations and Further Development

Potential improvements include:

* Implementing a binary search or adaptive load increment to estimate the maximum permissible load more accurately.
* Adding explicit convergence checks and handling unsuccessful load flow calculations.
* Distinguishing voltage violations from equipment overloads in the output.
* Refining the association between asynchronous motors and the buses or substations being analyzed.
* Validating transformer loading calculations against the relevant PowerFactory attributes and transformer ratings.
* Recording the last feasible load and the first infeasible load separately.
* Adding configurable voltage limits, equipment loading limits, and load power factors.
* Improving cleanup and restoration of the original network state after the simulation.

## Technologies

* Python
* DIgSILENT PowerFactory
* PowerFactory Python API
* NumPy
* pandas
* Excel / openpyxl

## Author

**Živko Sokolović**

GitHub: [@sokolovic-z](https://github.com/sokolovic-z)

## License

Specify a license before redistributing this project. If the repository contains proprietary PowerFactory project files or other restricted network data, ensure that you have permission to publish them.
