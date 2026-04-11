import os
import numpy as np
from .secure_io import secure_save
from pathlib import Path
from typing import Dict, Any, List, Tuple, Union
import copy
from .config import Config
from .safe_io import save_data

class DataLoader:
    def __init__(self, base_path: Union[str, Path]):
        self.base_path = Path(base_path)

    def process_directories(self, config: Config):
        """Iterates through directories specified in config and processes data."""
        results = {}
        for dir_name in config.dirList:
            dir_path = self.base_path / dir_name
            if not dir_path.exists():
                print(f"Warning: Directory {dir_path} does not exist. Skipping.")
                continue

            print(f">>>>>>> Reading DICTRA data from path: {dir_path}")
            rData = self.get_values_from_textfiles(dir_path)

            for timeflag in config.timeflags:
                tS, nearestTime = self.get_timestamp(rData['times'], timeflag)
                tS_VLUs = self.get_tS_VLUs(rData, tS, nearestTime)

                output_file = dir_path / f'rawdata_{timeflag}.json'
                secure_save(tS_VLUs, output_file)
                print(f"Saved raw data to {output_file}")

    def get_values_from_textfiles(self, path: Path) -> Dict[str, Any]:
        """Reads all values from a given path."""
        data = {}
        data['path'] = str(path)

        try:
            data['all_mfs'] = np.loadtxt(path / 'MOLE_FRACTIONS.TXT', dtype=float)
            data['elnames'] = np.loadtxt(path / 'EL_NAMES.TXT', dtype=str)
            data['all_pts'] = np.loadtxt(path / 'VOLUME_MIDPOINTS.TXT', dtype=float)
            data['times'] = np.loadtxt(path / 'TIME.TXT', dtype=float)
            data['n_pts'] = np.loadtxt(path / 'VOLUMES_PER_REGION.TXT', dtype=float)
            data['DICT_all_npms'] = np.loadtxt(path / 'PHASE_FRACTIONS.TXT', dtype=float)
            data['DICT_all_mus'] = np.loadtxt(path / 'CHEMICAL_POTENTIALS.TXT', dtype=float)
            data['T'] = np.loadtxt(path / 'T.DAT', dtype=int)
        except Exception as e:
            print(f"Error reading text files in {path}: {e}")
            raise

        phnames = []
        try:
            with open(path / 'PH_NAMES.TXT', 'r') as f:
                for line in f:
                    phnames.append(line.strip())
            data['DICT_phnames'] = np.array(phnames)
        except FileNotFoundError:
            print(f"Warning: PH_NAMES.TXT not found in {path}")
            data['DICT_phnames'] = np.array([])

        # Identify interstitials and substitutionals
        data['interstitials'], data['substitutionals'] = self._categorize_elements(data['elnames'])

        return data

    def _categorize_elements(self, elnames: np.ndarray) -> Tuple[List[Any], List[Any]]:
        interstitial_list = ['N', 'C', 'H', 'O', 'VA']
        int_idx = []
        sub_idx = list(range(len(elnames)))

        found_interstitials = []
        for el in interstitial_list:
            if el in elnames:
                idx = np.where(elnames == el)[0][0]
                int_idx.append(idx)
                found_interstitials.append(el)

        # Remove interstitial indices from substitutional list
        # We need to sort int_idx descending to pop correctly if we were popping by index from a list,
        # but here sub_idx contains indices, so we just remove the values.
        for idx in int_idx:
            if idx in sub_idx:
                sub_idx.remove(idx)

        interstitials = [np.array(found_interstitials), int_idx]
        substitutionals = [elnames[sub_idx], sub_idx]

        return interstitials, substitutionals

    def get_timestamp(self, times: np.ndarray, timeflag: Any) -> Tuple[int, float]:
        """Finds the timestep index and value based on the flag."""
        if timeflag == "first":
            tS = 1
            nearestTime = times[1] if len(times) > 1 else times[0]
        elif timeflag == "last":
            tS = len(times) - 1
            nearestTime = times[-1]
        elif isinstance(timeflag, (int, float)) and 0 < timeflag < times[-1]:
             idx, nearestTime = self._find_nearest(times, timeflag)
             tS = idx # Assuming timeflag passed as a value refers to a time, but logic in original code is mixed.
             # In original code: tS=timeflag. If it's an index or time?
             # Original: if (type(timeflag) == int or type(timeflag) == float) and timeflag>0 and timeflag <times[-1]:
             #           tS=timeflag
             #           _, nearestTime=find_nearest(times, tS)
             # This suggests 'timeflag' is interpreted as TIME here.
             # BUT wait, finding nearest of 'tS' in 'times'.
             # Let's assume user provides a time value.
        else:
             # Fallback or manual input (removed manual input for automation)
             print(f"Warning: Invalid timeflag {timeflag}. Defaulting to last.")
             tS = len(times) - 1
             nearestTime = times[-1]

        # print(f'timeflag:{timeflag}, timestep:{tS}, nearest time:{nearestTime}')
        return tS, nearestTime

    def _find_nearest(self, array: np.ndarray, value: float) -> Tuple[int, float]:
        array = np.asarray(array)
        idx = (np.abs(array - value)).argmin()
        return idx, array[idx]

    def calculate_u_fractions(self, mf: np.ndarray, sub_idx: List[int], elnames: np.ndarray) -> np.ndarray:
        # Avoid division by zero
        sub_sum = np.sum(mf[:, sub_idx], axis=1)
        sub_sum[sub_sum == 0] = 1.0 # Protect against div by zero

        uf = []
        for nel, el in enumerate(elnames):
            uf.append(mf[:, nel] / sub_sum[:])
        return np.array(uf)

    def get_tS_VLUs(self, dict_input: Dict[str, Any], tS: int, nearestTime: float) -> Dict[str, Any]:
        """Extracts values for a specific timestep."""
        d = copy.deepcopy(dict_input)

        # Safety check for tS index
        if tS == 0: tS = 1
        if tS >= len(d['n_pts']): tS = len(d['n_pts'])

        d['tS'] = tS
        d['nearestTime'] = nearestTime

        n_pts = d['n_pts']
        start_idx = int(np.sum(n_pts[:tS-1]))
        end_idx = int(np.sum(n_pts[:tS]))

        # Volume midpoints
        d['tS_pts'] = d['all_pts'][start_idx:end_idx] * 1e6

        # Phase fractions
        phnames = d['DICT_phnames']
        idx1_ph = start_idx * len(phnames)
        idx2_ph = end_idx * len(phnames)
        d['tS_DICT_npms'] = d['DICT_all_npms'][idx1_ph:idx2_ph].reshape((-1, len(phnames)))

        if len(phnames) > 0 and 'ZZDICT_GHOST' in phnames[-1]:
             d['tS_DICT_phnames'] = copy.deepcopy(phnames[:-1])
             # Reshape/Slice might need adjustment if ghost is removed from data too?
             # Original code just slices phnames but doesn't seem to slice data columns.
             # We will keep consistency with original code for now.
        else:
             d['tS_DICT_phnames'] = copy.deepcopy(phnames)

        # Mole fractions and Potentials
        elnames = d['elnames']
        idx1_el = start_idx * len(elnames)
        idx2_el = end_idx * len(elnames)

        d['tS_DICT_mfs'] = d['all_mfs'][idx1_el:idx2_el].reshape((-1, len(elnames)))
        d['tS_DICT_mus'] = d['DICT_all_mus'][idx1_el:idx2_el].reshape((-1, len(elnames)))

        # U-fractions
        d['tS_DICT_ufs'] = self.calculate_u_fractions(d['tS_DICT_mfs'], d['substitutionals'][1], elnames).T

        # Clean up huge arrays
        for key in ['all_mfs', 'all_pts', 'times', 'n_pts', 'DICT_all_npms', 'DICT_phnames', 'DICT_all_mus']:
            d.pop(key, None)

        return d
