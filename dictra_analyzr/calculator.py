import os
import sys
from .serialization import save_data, load_data
import copy
from collections import defaultdict
import numpy as np
from pathlib import Path
from .config import Config
from .safe_io import load_data, save_data

logger = logging.getLogger(__name__)

try:
    from tc_python import TCPython
except ImportError:
    # Mock for environments without tc_python
    class TCPython:
        def __enter__(self): return self
        def __exit__(self, exc_type, exc_val, exc_tb): pass
        def set_cache_folder(self, folder): return self
        def select_database_and_elements(self, db, els): return self
        def select_thermodynamic_and_kinetic_databases_with_elements(self, db1, db2, els): return self
        def deselect_phase(self, ph): return self
        def get_system(self): return self
        def with_single_equilibrium_calculation(self): return self
        def run_poly_command(self, cmd): pass
        def remove_all_conditions(self): pass
        def set_condition(self, cond, val): pass
        def calculate(self): return self
        def get_stable_phases(self): return []
        def get_value_of(self, val): return 0.0
        def set_phase_to_suspended(self, ph): pass

class ThermodynamicCalculator:
    def __init__(self, base_path: Path):
        self.base_path = base_path

    def process_calculations(self, config: Config):
        for dir_name in config.dirList:
            dir_path = self.base_path / dir_name
            for timeflag in config.timeflags:
                input_file = dir_path / f'rawdata_{timeflag}.json'
                output_file = dir_path / f'uncorrected_results_{timeflag}.json'

                if not input_file.exists():
                    print(f"Skipping calculation for {input_file}: File not found.")
                    continue

                print(f">>>>>> TCpy calculator in {dir_path} for {timeflag} tstp")
                tS_VLUs = load_data(input_file)

                # Inject settings
                tS_VLUs['tc_setting'] = config.tc_setting

                # Perform calculation
                tS_tc_VLUs = self.tccalc(tS_VLUs)

                save_data(tS_tc_VLUs, output_file)
                print(f"Saved uncorrected results to {output_file}")

    def tccalc(self, dict_input):
        """Calculate single equilibrium pt by pt with input condition."""
        # Deep copy to avoid mutating input
        d = copy.deepcopy(dict_input)

        try:
            mfs = d['tS_DICT_mfs']
            database = d['tc_setting'].database # List expected
            n_pts = len(d['tS_pts'])
            phsToSus = d['tc_setting'].phsToSus
            acsRef = d['tc_setting'].acRefs
            T = d['T']
            elnames = d['elnames']
            pth = d['path']
            poly3Flag = d['tc_setting'].p3flag
            McalcFlag = d['tc_setting'].mobFlag
        except KeyError as e:
            print(f"Error in TC input data: Missing key {e}")
            return d

        print('Calculing thermodynamics...')

        with TCPython() as start:
            poly = self._setup_system(start, database, elnames, poly3Flag, McalcFlag, pth)

            if phsToSus:
                for phase in phsToSus:
                    poly.set_phase_to_suspended(phase)

            poly.set_condition("T", float(T))

            # Result containers
            tc_phnames = {}
            tc_npms = {}
            tc_vpvs = {}
            tc_phXs = {}
            tc_acRefs = defaultdict(list)
            tc_acSER = defaultdict(list)
            tc_mus = defaultdict(list)
            tc_ws = defaultdict(list)

            tc_M = {}
            tc_G = {}

            # Iterate points
            for pt in range(n_pts):
                # Set conditions (skipping last element as balance)
                for nel, el in enumerate(elnames[:-1]):
                    poly.set_condition(f"X({el})", float(mfs[pt, nel]))

                try:
                    pntEq = poly.calculate()
                    stablePhs = pntEq.get_stable_phases()
                    tc_phnames[pt] = stablePhs

                    if 'C' in elnames:
                        for reference in acsRef:
                            val = pntEq.get_value_of(f'ac(C, {reference})')
                            tc_acRefs[f'ac(C, {reference})'].append(val)

                    for el in elnames:
                        tc_acSER[el].append(pntEq.get_value_of(f'ac({el})'))
                        tc_mus[el].append(pntEq.get_value_of(f'mu({el})'))
                        tc_ws[el].append(pntEq.get_value_of(f'w({el})'))

                    for ph in stablePhs:
                        tc_npms[f'{pt}, {ph}'] = pntEq.get_value_of(f'npm({ph})')
                        tc_vpvs[f'{pt}, {ph}'] = pntEq.get_value_of(f'vpv({ph})')

                        # Phase composition
                        temp1 = []
                        for el2 in elnames:
                            temp1.append(pntEq.get_value_of(f'X({ph}, {el2})'))
                        tc_phXs[f'{pt}, {ph}'] = np.array(temp1)

                        # Mobility / Gibbs
                        if McalcFlag:
                            temp2, temp3 = [], []
                            for el2 in elnames:
                                m_val = pntEq.get_value_of(f'M({ph}, {el2})')
                                x_val = pntEq.get_value_of(f'X({ph}, {el2})')
                                temp2.append(m_val)
                                temp3.append(m_val * x_val) # Approximation? Original code: M * X
                            tc_M[f'{pt}, {ph}'] = np.array(temp2)
                            tc_G[f'{pt}, {ph}'] = np.array(temp3)

                except Exception as e:
                    # Log error but continue
                    logger.warning(f"Calculation failed at point {pt}: {e}")

        # Post-loop organization
        if McalcFlag:
            d['tS_TC_M'] = tc_M
            d['tS_TC_G'] = tc_G

        d['tS_TC_phnames'] = tc_phnames
        d['tS_TC_npms'] = tc_npms
        d['tS_TC_vpvs'] = tc_vpvs
        d['tS_TC_phXs'] = tc_phXs
        d['tS_TC_acRef'] = dict(tc_acRefs)
        d['tS_TC_acSER'] = dict(tc_acSER)
        d['tS_TC_mus'] = dict(tc_mus)
        d['tS_TC_ws'] = dict(tc_ws)

        self._trim_results(d, elnames, n_pts, tc_phnames, tc_npms, tc_vpvs, tc_phXs, tc_M if McalcFlag else None, tc_G if McalcFlag else None, McalcFlag)

        return d

    def _setup_system(self, start, database, elnames, poly3Flag, McalcFlag, pth):
        if poly3Flag and os.path.isfile(f'{pth}/p.POLY3'):
            print('************ Reading poly3 file, calculating')
            poly = start.select_database_and_elements(database[0], elnames).get_system().with_single_equilibrium_calculation()
            poly.run_poly_command(f'read {pth}/p.POLY3')
            poly.remove_all_conditions()
            poly.set_condition('N', 1)
            poly.set_condition('P', 1e5)
        else:
            if McalcFlag:
                # Need thermodynamic and kinetic databases
                td_db = database[0]
                kin_db = database[1] if len(database) > 1 else database[0] # Fallback

                if ("Fe" not in elnames) and ("MOBFE" in kin_db.upper()):
                     poly = start.set_cache_folder("./_cache2").select_thermodynamic_and_kinetic_databases_with_elements(td_db, kin_db, elnames).deselect_phase("CEMENTITE").get_system().with_single_equilibrium_calculation()
                else:
                     poly = start.set_cache_folder("./_cache2").select_thermodynamic_and_kinetic_databases_with_elements(td_db, kin_db, elnames).get_system().with_single_equilibrium_calculation()
            else:
                td_db = database[0]
                poly = start.set_cache_folder("./_cache2").select_database_and_elements(td_db, elnames).get_system().with_single_equilibrium_calculation()
        return poly

    def _trim_results(self, d, elnames, n_pts, tc_phnames, tc_npms, tc_vpvs, tc_phXs, tc_M, tc_G, McalcFlag):
        # Flatten structure for plotting
        tc_NEAT_mfs = {}
        for nel, el in enumerate(elnames):
            tc_NEAT_mfs[el] = d['tS_DICT_mfs'][:, nel]

        # Collect all unique phases encountered
        tc_NEAT_phnames = []
        for i in range(n_pts):
            if i in tc_phnames:
                for ph in tc_phnames[i]:
                    if ph not in tc_NEAT_phnames:
                        tc_NEAT_phnames.append(ph)

        tc_NEAT_npms = {}
        tc_NEAT_vpvs = {}
        tc_NEAT_phXs = {}
        tc_NEAT_G = {}
        tc_NEAT_M = {}

        for ph in tc_NEAT_phnames:
            tc_NEAT_npms[ph] = np.zeros(n_pts)
            tc_NEAT_vpvs[ph] = np.zeros(n_pts)
            tc_NEAT_phXs[ph] = np.zeros((n_pts, len(elnames)))
            if McalcFlag:
                tc_NEAT_G[ph] = np.zeros((n_pts, len(elnames)))
                tc_NEAT_M[ph] = np.zeros((n_pts, len(elnames)))

        for nph, ph in enumerate(tc_NEAT_phnames):
            for pt in range(n_pts):
                key = f'{pt}, {ph}'
                if key in tc_npms:
                    tc_NEAT_npms[ph][pt] = tc_npms[key]
                    tc_NEAT_vpvs[ph][pt] = tc_vpvs[key]
                    tc_NEAT_phXs[ph][pt, :] = tc_phXs[key]

                    if McalcFlag:
                        tc_NEAT_G[ph][pt, :] = tc_G[key]
                        tc_NEAT_M[ph][pt, :] = tc_M[key]

        d['tS_TC_NEAT_phnames'] = tc_NEAT_phnames
        d['tS_TC_NEAT_npms'] = tc_NEAT_npms
        d['tS_TC_NEAT_vpvs'] = tc_NEAT_vpvs
        d['tS_TC_NEAT_phXs'] = tc_NEAT_phXs
        d['tS_TC_NEAT_mfs'] = tc_NEAT_mfs
        if McalcFlag:
            d['tS_TC_NEAT_G'] = tc_NEAT_G
            d['tS_TC_NEAT_M'] = tc_NEAT_M
