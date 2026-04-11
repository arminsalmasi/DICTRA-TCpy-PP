import pickle
import copy
import sys
import numpy as np
from pathlib import Path
from .config import Config

class ResultCorrector:
    def __init__(self, base_path: Path):
        self.base_path = base_path

    def process_corrections(self, config: Config):
        for dir_name in config.dirList:
            dir_path = self.base_path / dir_name
            for tflag in config.timeflags:
                input_file = dir_path / f'uncorrected_results_{tflag}.pickle'
                output_file = dir_path / f'results_{tflag}.pickle'

                if not input_file.exists():
                     print(f"Skipping correction for {input_file}: File not found.")
                     continue

                print(f">>>>>>> correcting tstp {tflag} in {dir_path}")
                with open(input_file, 'rb') as f:
                    dict_in = pickle.load(f)

                # Inject config
                dict_in['name_pairs'] = config.name_pairs
                dict_in['phase_changes'] = config.phase_changes

                # Processing pipeline
                dict1 = self.correct_phase_indices(dict_in)
                dict2 = self.add_compSets(dict1)
                dict3 = self.phnameChange(dict2)
                dict_out = self.add_compSets_DICT(dict3)

                with open(output_file, 'wb') as f:
                    pickle.dump(dict_out, f)
                print(f"Saved corrected results to {output_file}")

    def correct_phase_indices(self, dict_input):
        """Handle miscibility gaps by splitting phases based on composition cutoffs."""
        d = copy.deepcopy(dict_input)
        try:
            n_pts = len(d['tS_pts'])
            tS_TC_NEAT_npms = d['tS_TC_NEAT_npms']
            tS_TC_NEAT_phXs = d['tS_TC_NEAT_phXs']
            elnames = d['elnames']
            nelements = len(elnames)
            tS_TC_NEAT_phnames = d['tS_TC_NEAT_phnames']
            phase_changes = d['phase_changes']
        except KeyError as e:
            print(f"Input error, correcting phase indices failed: {e}")
            return d

        print('Correcting indices...')
        CQT_tS_TC_NEAT_phXs = copy.deepcopy(tS_TC_NEAT_phXs)
        CQT_tS_TC_NEAT_npms = copy.deepcopy(tS_TC_NEAT_npms)

        for change in phase_changes:
            phase_to_change, search_element, cutoff = change
            # Find relevant phases
            phases_to_process = [ph for ph in tS_TC_NEAT_phnames if phase_to_change in ph]

            for phase in phases_to_process:
                # Iterate points
                for pt in range(n_pts):
                    phXs = tS_TC_NEAT_phXs[phase][pt, :]
                    if np.any(phXs > 0):
                        # Sort by fraction to find major elements
                        # The logic in original code seems to try to find if 'search_element' is dominant
                        sorted_indices = np.flip(np.argsort(phXs))
                        sorted_elnames = elnames[sorted_indices]

                        try:
                            search_idx = np.where(sorted_elnames == search_element)[0][0]
                        except IndexError:
                            continue # Search element not present?

                        # Original logic reconstruction:
                        # cutoff > 0 and < 1: check if search_element fraction > cutoff
                        # cutoff == 1: check if search_element is the largest constituent (index 0)

                        condition_met = False
                        if 0 < cutoff < 1:
                             # Wait, original code checks sorted_phXs[sorted_searchElidx] > cutoff
                             # sorted_phXs matches sorted_elnames.
                             # So if search_element is at index `search_idx` in `sorted_elnames`,
                             # its value is `phXs[original_index_of_search_element]`.
                             # The original code:
                             # sorted_phXs = ...
                             # sorted_searchElidx = np.where( sorted_elnames ==  search_element )[0][0]
                             # if sorted_phXs[sorted_searchElidx] > cutoff: ...

                             # Let's trust the logic: is the concentration of search_element > cutoff?
                             current_conc = phXs[np.where(elnames == search_element)[0][0]]
                             if current_conc > cutoff:
                                 condition_met = True

                        elif cutoff == 1:
                            if search_idx == 0: # It is the largest constituent
                                if phXs[np.where(elnames == search_element)[0][0]] > 0:
                                    condition_met = True

                        if condition_met:
                             # Generate new phase name e.g. "BCC_A2-W" if top 2 elements are W and something else?
                             # Original code uses top 2 elements for name generation if cutoff < 1, top 1 if cutoff == 1
                             if 0 < cutoff < 1:
                                 st = phase_to_change + '-' + "".join(sorted_elnames[:2])
                             else:
                                 st = phase_to_change + '-' + "".join(sorted_elnames[:1])

                             # Add to new arrays
                             if st not in CQT_tS_TC_NEAT_npms:
                                 CQT_tS_TC_NEAT_phXs[st] = np.zeros((n_pts, nelements))
                                 CQT_tS_TC_NEAT_npms[st] = np.zeros(n_pts)

                             CQT_tS_TC_NEAT_phXs[st][pt] = phXs
                             CQT_tS_TC_NEAT_npms[st][pt] = CQT_tS_TC_NEAT_npms[phase][pt]

                             # Zero out old phase
                             CQT_tS_TC_NEAT_phXs[phase][pt] = np.zeros(nelements)
                             CQT_tS_TC_NEAT_npms[phase][pt] = 0

        d['CQT_tS_TC_NEAT_phXs'] = CQT_tS_TC_NEAT_phXs
        d['CQT_tS_TC_NEAT_npms'] = CQT_tS_TC_NEAT_npms

        # Clean up empty phases
        keys_to_remove = [k for k, v in d['CQT_tS_TC_NEAT_npms'].items() if np.all(v < 1e-4)]
        for k in keys_to_remove:
            d['CQT_tS_TC_NEAT_npms'].pop(k, None)

        keys_to_remove = [k for k, v in d['CQT_tS_TC_NEAT_phXs'].items() if np.all(v.ravel() == 0)]
        for k in keys_to_remove:
            d['CQT_tS_TC_NEAT_phXs'].pop(k, None)

        return d

    def add_compSets(self, dict_in):
        """Sum up split phases (miscibility gaps) e.g. Phase#1 + Phase#2."""
        d = copy.deepcopy(dict_in)
        npms_dict = copy.deepcopy(d['CQT_tS_TC_NEAT_npms'])
        keys = list(npms_dict.keys())

        # Merge numbered duplicates (e.g. BCC#1, BCC#2 -> BCC#1)
        phs_without_Csets = set()
        for key in keys:
            if '#1' in key:
                phs_without_Csets.add(key.split('#')[0])

        for ph in phs_without_Csets:
             base_key = ph + '#1'
             if base_key not in npms_dict: continue

             for i in range(2, 10):
                 variant_key = f"{ph}#{i}"
                 if variant_key in npms_dict:
                     npms_dict[base_key] += npms_dict[variant_key]
                     npms_dict.pop(variant_key)

        # Merge same names if any left (Original code logic seems to check for sorted(key) equality?)
        # "if sorted(keys[i]) == sorted(keys[j])": This implies checking for permutations of names?
        # Unlikely to be useful unless names are compositions.
        # But let's keep it to preserve behavior.
        keys = list(npms_dict.keys())
        for i in range(len(keys)):
            for j in range(i + 1, len(keys)):
                key1, key2 = keys[i], keys[j]
                if key1 in npms_dict and key2 in npms_dict: # check existence as we pop
                    if sorted(key1) == sorted(key2): # This is risky if names are just anagrams
                        if key1 != key2:
                            npms_dict[key1] += npms_dict[key2]
                            npms_dict.pop(key2)

        d['sum_CQT_tS_TC_NEAT_npms'] = npms_dict
        return d

    def phnameChange(self, dict_in):
        """Rename phases based on mapping."""
        d = copy.deepcopy(dict_in)
        name_pairs = d['name_pairs']

        # Use sum_CQT_tS_TC_NEAT_npms if available, otherwise fallback to CQT_tS_TC_NEAT_npms
        source_key = 'sum_CQT_tS_TC_NEAT_npms' if 'sum_CQT_tS_TC_NEAT_npms' in d else 'CQT_tS_TC_NEAT_npms'
        npms_dict = copy.deepcopy(d[source_key])

        for name_from, name_to in name_pairs:
            if name_from in npms_dict:
                if name_to in npms_dict:
                    npms_dict[name_to] += npms_dict[name_from]
                else:
                    npms_dict[name_to] = npms_dict[name_from]
                del npms_dict[name_from]

        d['nameChanged_CQT_tS_TC_NEAT_npms'] = npms_dict
        return d

    def add_compSets_DICT(self, dict_in):
        """Sum up DICTRA phases (raw input phases)."""
        d = copy.deepcopy(dict_in)
        npms = np.array(d['tS_DICT_npms'])
        phnames = d['tS_DICT_phnames']

        npms_dict = {}
        phnames_without_Csets = []

        for ph in phnames:
            clean_name = ph.split('#')[0] if '#' in ph else ph
            if clean_name not in phnames_without_Csets:
                phnames_without_Csets.append(clean_name)
                npms_dict[clean_name] = np.zeros(npms.shape[0])

        for ph1 in phnames_without_Csets:
            for nph, ph2 in enumerate(phnames):
                if ph1 in ph2:
                    npms_dict[ph1] += npms[:, nph]

        d['sum_tS_DICT_npms'] = npms_dict
        return d
