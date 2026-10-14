# Load Expansion Assessment of a Thermal Power Plant Auxiliary Electrical System Using DIgSILENT PowerFactory and Python

## Overview

This project implements a Python-based workflow for conducting load expansion studies in **DIgSILENT PowerFactory**. The script automates the process of adding new loads to medium-voltage and low-voltage network buses, progressively increasing their active power, performing load flow calculations, and identifying network operating limit violations.

The objective is to determine the maximum additional active load that can be connected at selected network nodes while respecting voltage limits and equipment loading constraints.


## Methodology

The analysis follows an incremental load expansion approach:

1. Initialize the PowerFactory application and import project.
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
| Voltage monitoring     | Bus voltage magnitude in p.u.                 |
| Line monitoring        | Line loading (current)                        |
| Transformer monitoring | Transformer loading (apparent power)          |
| Reactor monitoring     | Reactor loading (current)                     |
| Results format         | Excel (`.xlsx`)                               |

The active power increment can be adjusted to obtain a finer or coarser estimate of the maximum load.

## Project Structure

```text
Thermal-Power-Plant-Load-Expansion-Assessment/
├── doc/
│   ├── workflow.png
│   └── sld.pdf
├── src/
│   └── load_expansion.py
├── .gitignore
├── requirements.txt
└── README.md
```

## Requirements

* DIgSILENT PowerFactory 2024 or later
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

 1. Clone the repository and navigate to the project directory:

```bash
git clone https://github.com/sokolovic-z/Thermal-Power-Plant-Load-Expansion-Assessment.git 
cd Thermal-Power-Plant-Load-Expansion-Assessment
```

2. Install the required Python packages:

   ```bash
   pip install -r requirements.txt
   ```

3. Ensure that DIgSILENT PowerFactory is installed and its Python API is accessible.

4. Configure the PowerFactory API path and project file path.

5. Verify that the project contains the required study case, operation scenario, and network model.

6. Run the script using a compatible Python interpreter:

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


## Author

**Živko Sokolović**

GitHub: [@sokolovic-z](https://github.com/sokolovic-z)


