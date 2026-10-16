"""
This script automates the assessment of maximum additional load
that can be connected to selected buses in a thermal power plant's
auxiliary electrical system using DIgSILENT PowerFactory.
------------------------------------------------
The workflow includes:
- Importing a project file
- Activating a study case and operation scenario
- Creating a network variation and expansion stage
- Creating and connecting new loads to each MV/LV bus in the network
- Incrementally increasing load
- Running load flow calculations
- Checking for voltage violations and overloading
- Exporting results to Excel

Author: Živko Sokolović 
GitHub: @sokolovic-z
Date: October 2026
"""

# === Import Packages ===
import sys
from pathlib import Path

# Update this path to your PowerFactory installation directory
POWERFACTORY_PYTHON_PATH = Path(
    r"C:/Program Files/DIgSILENT/PowerFactory 2024 SP2/Python/3.12"
) 
sys.path.append(str(POWERFACTORY_PYTHON_PATH))

import powerfactory as pf

import pandas as pd
import numpy as np

import warnings
warnings.filterwarnings('ignore')


# === Paths ==== 
SCRIPT_FILEPATH = Path(__file__).resolve()
ROOT_PATH = SCRIPT_FILEPATH.parent.parent
PROJECT_FILEPATH = ROOT_PATH / 'project' / 'thermal_power_plant.pfd'

OUTPUT_PATH = ROOT_PATH / 'output'
OUTPUT_PATH.mkdir(exist_ok=True)

# === Functions ===
def check_violations(
        buses: list[pf.DataObject]=[],
        lines: list[pf.DataObject]=[],
        transformers: list[pf.DataObject]=[],
        reactors: list[pf.DataObject]=[]
) -> dict[str, float]:
    """
    Check voltage violations and overloading for given network elements.  
    Returns a dictionary of critical elements with violation values.
    """
    celements = {} # critical elements
    
    # Voltage violations
    for bus in buses:
        voltage = bus.GetAttribute('m:u')
        if voltage < bus.vmin or voltage > bus.vmax: # acceptable voltage range (vmin, vmax)
            celements[bus.loc_name] = voltage
    # Line overloading
    for line in lines:
        loading = line.GetAttribute('c:loading')
        if loading > 100:
            celements[line.loc_name] = loading
    # Transformer overloading
    for tr in transformers:
        loading = 100 * tr.GetAttribute('m:S:bushv') / tr.GetAttribute('t:strn')
        if loading > 100:
            celements[tr.loc_name] = loading
    # Series reactor overloading
    for reactor in reactors:
        loading = reactor.GetAttribute('c:loading')
        if loading > 100:
            celements[reactor.loc_name] = loading

    return celements

def add_loads(app, grid, nodes, display=False):
    """
    Create and connect new loads to each node in nodes.
    Optionally display them in the single-line diagram
    """
    loads = []
    for node in nodes:
        # create a new load element
        new_load = grid.CreateObject('ElmLod', f'{node.loc_name} Load')
        # connect new load to a terminal
        new_cub = node.CreateObject('StaCubic', 'new_cub') # cubicle
        new_cub.obj_id = new_load
        # append to list of loads
        loads.append(new_load)
    
    # Display new elements in existing diagram (optional)
    if display:
        graphic = app.GetDesktop()
        graphic.Unfreeze()
        comlayout = app.GetFromStudyCase('ComSgllayout') # diagram layout tool
        comlayout.iAction = 1
        comlayout.insertionMode = 1
        comlayout.Execute()
    
    return loads

def main(app):   
    # Activate study case and operation scenario
    project = app.GetActiveProject()
    study_case = app.GetProjectFolder('study').GetContents()[0]
    oscen = app.GetProjectFolder('scen').GetContents()[0]
    study_case.Activate()
    oscen.Activate()
    print(f'[*] Project: {project.loc_name}')
    print(f'[*] Study case: {study_case.loc_name}')
    print(f'[*] Operation scenario: {oscen.loc_name}')

    # Create network variation, expansion stage, and start recording
    scheme = app.GetProjectFolder('scheme')
    netvar = scheme.CreateObject('IntScheme', 'Load Expansion')
    expstage = netvar.CreateObject('IntSstage', 'Expansion Stage')
    netvar.Activate()
    expstage.Activate(1)
    print(f'[*] Network variation: {netvar.loc_name}')
   
    # Get all required network elements
    grid = app.GetCalcRelevantObjects('Grid.ElmNet')[0]
    nodes = app.GetCalcRelevantObjects('*.ElmTerm')
    lines = app.GetCalcRelevantObjects('*.ElmLne')
    asm = app.GetCalcRelevantObjects('*.ElmAsm')
    transformers = app.GetCalcRelevantObjects('*.ElmTr2')
    series_reactors = app.GetCalcRelevantObjects('*.ElmSind')

    # Filter energized MV/LV nodes
    nodes = [n for n in nodes if n.uknom <= 6. and n.IsEnergized()]
    
    # Exclude problematic substation "SKO" due to line overloading and voltage violations
    nodes = [n for n in nodes if "SKO" not in n.loc_name]
    lines = [l for l in lines if "SKO" not in l.loc_name]

    # Add loads to buses
    loads = add_loads(app, grid, nodes)
    
    # Load flow object
    ldf = app.GetFromStudyCase('ComLdf')
 
    # Results DataFrame
    res_df = pd.DataFrame(columns=['Bus', 'Smax', 'Pmax', 'cosphi', 'Critical element', 'Value'])

    # Increment active power of loads until violation is detected
    for load in loads:
        print(f'[*] {load.loc_name} ...')
        
        # Extract terminal info
        cub = load.bus1 # returns cubicle object 
        bus = cub.cterm # returns bus object

        # Set active power P and power factor cosφ
        load.mode_inp = 'PC' # set input mode: (P, cosφ)
        load.SetAttribute('plini', 0)  # initial active power to 0
        # compute power factor cosφ equal to average power factor of the all ASM connected to the same substation/bus
        cosphi = np.mean(
            [am.GetAttribute('t:cosn') for am in asm 
            if bus.loc_name in am.bus1.cterm.loc_name]
        )
        # fallback: set cosφ = 1 if no ASM are found 
        if np.isnan(cosphi): cosphi = 1
        load.SetAttribute('coslini', cosphi)
        
        deltaP = 0.1  # increment step [MW]
        while True:
            # increase active power by deltaP
            p = load.plini + deltaP 
            load.SetAttribute('plini', p)
            
            # Run load flow calculation
            ldf.Execute() 

            # Check violations
            celements = check_violations(nodes, lines, transformers, series_reactors)
            if len(celements) > 0:
                for elem, value in celements.items():
                    print(f"[+] Violation detected -> Element: {elem}, Value: {value:.2f}")
                    res_df.loc[len(res_df)] = [bus.loc_name, p/cosphi, p, cosphi, elem, value]
                # Reset load
                load.SetAttribute('plini', 0)  
                load.SetAttribute('coslini', 1)  
                
                break

            # Reset calculation results
            app.ResetCalculation()

    # Export results
    res_df.sort_values(by='Bus', inplace=True)
    res_df = res_df.round(3)
    res_df.to_excel(OUTPUT_PATH / 'results.xlsx', index=False, engine='openpyxl')

    # Clean up network variation
    netvar.Deactivate()
    netvar.Delete()
    

# === Entry Point ===
if __name__ == "__main__":
    print('[*] Initializing PF application...')
    app = pf.GetApplicationExt()
    if app is None:
        print("[-] PowerFactory application not found. Please ensure PowerFactory is installed and the path is correct.")
        sys.exit(1)

    # Import project file
    print(f'[*] Importing {PROJECT_FILEPATH.name} ...')
    user_folder = app.GetCurrentUser()
    importObj = user_folder.CreateObject('CompfdImport', 'PFD Import')
    importObj.SetAttribute('g_file', str(PROJECT_FILEPATH))
    importObj.SetAttribute('g_target', user_folder)
    importObj.activatePrj = True # activate project 
    importObj.Execute()
    importObj.Delete()

    # Run main workflow
    main(app)

    # Print final msg and terminate script
    print('[+] Load expansion study completed successfully.')
    print(f'[+] Results exported to: {OUTPUT_PATH / "results.xlsx"}')
    sys.exit(0)
