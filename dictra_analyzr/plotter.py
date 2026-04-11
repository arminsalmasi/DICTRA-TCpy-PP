import pickle
import glob
from . import safe_io
import numpy as np
import matplotlib.pyplot as plt
import pandas as pd
from pathlib import Path
from typing import Dict, Any, List, Optional
from .config import Config, PlotSettings
from .secure_io import secure_load

class Plotter:
    def __init__(self, base_path: Path):
        self.base_path = base_path

    def process_plots(self, config: Config):
        for dir_name in config.dirList:
            dir_path = self.base_path / dir_name
            if not dir_path.exists(): continue

            # Clean old files
            if config.actions.delPNGs:
                self.del_pngs_pdf(dir_path)

            if config.actions.plot:
                self.single_plotter(dir_path, config)

            if config.actions.plotoverlaid:
                self.ol_plotter(dir_path, config)

        if config.actions.plotMG and config.tc_setting.mobFlag:
             self.all_GMX_plotter(self.base_path, config)

        if config.actions.showPlot:
            plt.show()
        else:
            plt.close('all')

    def single_plotter(self, path: Path, config: Config):
        for tflag in config.timeflags:
            filename = f'results_{tflag}.json'
            input_file = path / filename
            if not input_file.exists(): continue

            print(f'>>>>>> plotting tstp {tflag} from {path}')
            data = secure_load(input_file)

            settings = config.plot_settings
            # Use data-derived xlims if not provided
            xlims = settings.xlims if settings.xlims else self.get_xlims(data)
            ylims = [0, 1] # Fixed for now as per original code

            # Define plot tasks
            # Each task: (key_in_data, Y-label, legend_key)
            tasks_arrays = [
                ('tS_DICT_ufs', r'$U \: fraction$', 'elnames'),
                ('tS_DICT_mfs', r'$Mole \: Fraction$' ,'elnames')
            ]

            for key, ylab, leg_key in tasks_arrays:
                self.plot_generic(
                    x=data['tS_pts'],
                    y=data[key],
                    legend=data[leg_key],
                    title=str(path),
                    filename=path / f"{key}_{int(data['nearestTime'])}",
                    ylab=ylab,
                    xlims=xlims,
                    settings=settings
                )

            tasks_dicts = [
                ('tS_TC_ws', r'$Mass \:Fraction$'),
                ('nameChanged_CQT_tS_TC_NEAT_npms', r'$Phase \: Fraction$')
            ]

            for key, ylab in tasks_dicts:
                self.plot_dict_generic(
                    x=data['tS_pts'],
                    y_dict=data[key],
                    title=str(path),
                    filename=path / f"{key}_{int(data['nearestTime'])}",
                    ylab=ylab,
                    xlims=xlims,
                    settings=settings
                )

            # Log plots
            if 'tS_TC_acSER' in data:
                self.plot_ylog_dict(
                    x=data['tS_pts'],
                    y_dict=data['tS_TC_acSER'],
                    legend=settings.acSERleg,
                    title=str(path),
                    filename=path / f"tS_TC_acSER_{int(data['nearestTime'])}",
                    ylab=r"$Log_{10}(Activity) \: (SER)$",
                    xlims=xlims,
                    settings=settings
                )

    def ol_plotter(self, path: Path, config: Config):
        settings = config.plot_settings
        tflags = config.timeflags

        datalist = []
        print(f'>>>>> overlaid plots in {path}')
        for tflag in tflags:
            fpath = path / f'results_{tflag}.json'
            if fpath.exists():
                datalist.append(secure_load(fpath))

        if not datalist: return

        if not settings.xlims:
            # Union of limits? Original code takes min of mins and max of maxs?
            # Original: [min(tmpxlims[0]),max(tmpxlims[1])] where tmpxlims is calculated per dataset
            all_xlims = [self.get_xlims(d) for d in datalist]
            xlims = [min(x[0] for x in all_xlims), max(x[1] for x in all_xlims)]
        else:
            xlims = settings.xlims

        # Overlaid Arrays
        tasks_arrays = [
            ('tS_DICT_ufs', r'$U \: fraction$', 'elnames'),
            ('tS_DICT_mfs', r'$Mole \: Fraction$' ,'elnames')
        ]

        t_str = f"{tflags[0]}_{tflags[-1]}" if len(tflags) > 1 else str(tflags[0])

        for key, ylab, leg_key in tasks_arrays:
            self.overlaid_list_plotter(
                datalist=datalist,
                keys=[ 'tS_pts', key, leg_key],
                filename=path / f"{key}_{t_str}",
                ylab=ylab,
                xlims=xlims,
                settings=settings,
                title=str(path)
            )

        # Overlaid Dicts
        tasks_dicts = [
            ('tS_TC_ws', r'$Mass \: Fraction$'),
            ('nameChanged_CQT_tS_TC_NEAT_npms', r'$Phase \: Fraction$')
        ]

        for key, ylab in tasks_dicts:
             self.overlaid_dict_plotter(
                datalist=datalist,
                keys=['tS_pts', key],
                filename=path / f"{key}_{t_str}",
                ylab=ylab,
                xlims=xlims,
                settings=settings,
                title=str(path)
             )

        # Overlaid Logs
        if 'tS_TC_acSER' in datalist[0]:
             self.overlaid_dict_ylog_plotter(
                datalist=datalist,
                keys=['tS_pts', 'tS_TC_acSER'],
                filename=path / f"tS_TC_acSER_{t_str}",
                ylab=r"$log_{10}(Activity)\: [SER]$",
                xlims=xlims,
                settings=settings,
                title=str(path),
                path=path
             )

    def all_GMX_plotter(self, path: Path, config: Config):
        settings = config.plot_settings
        target_els = settings.MPlotlegs
        phase = settings.MPlotPhase
        ks = settings.MPlotK

        # We need data from all directories for the "last" timestep usually, as per original code
        # Original: iterates dirs, opens results_last.json

        # Prepare data structure: List of dicts? Or map of dir -> data?
        # Original code plots overlay of different conditions (directories).

        # Let's iterate Ks (G or M)
        for k_key, k_ylab, k_el_key in ks:
            fig, ax = plt.subplots(1, 1, figsize=settings.figsize)

            full_legend = []
            # Color/Marker cycle
            markers = ["X", "P", "s", "p", "H", "h", "o", "v"]
            colors = ['red', 'green', 'blue', 'k', 'magenta', 'cyan', 'orange', 'purple']

            for i, dir_name in enumerate(config.dirList):
                dir_path = path / dir_name
                # Original code used 'results_last.json' hardcoded
                fpath = dir_path / 'results_last.json'
                if not fpath.exists(): continue

                data = secure_load(fpath)

                # Filter elements
                leglist_idx = [nel for nel, el in enumerate(data['elnames']) if el in target_els]
                current_legend_els = data['elnames'][leglist_idx]

                # Extract Data
                # data[k_key] is a dict like {'BCC': array(shape=(n_pts, n_els))}
                if phase not in data[k_key]: continue

                y_data_full = data[k_key][phase] # (n_pts, n_els)
                x_pts = data['tS_pts']

                # Plot specific elements
                marker = markers[i % len(markers)]
                color = colors[i % len(colors)]

                for j, el_idx in enumerate(leglist_idx):
                    y_el = y_data_full[:, el_idx]

                    # Remove undefined logs (zeros)
                    mask = y_el != 0
                    if not np.any(mask): continue

                    x_plot = x_pts[mask]
                    y_plot = np.log10(y_el[mask])

                    ax.plot(x_plot, y_plot, linewidth=settings.lineW,
                            color=color, marker=marker, markersize=10, fillstyle='none')

                # Create label for this directory
                temp_c = data.get("T", 273) - 273
                full_legend.extend([f"{el} {temp_c}C" for el in current_legend_els])

            ax.legend(full_legend, fontsize=settings.legF)
            self._decorate_ax(ax, phase, k_ylab, settings.xlab, settings.xlimsGM, settings)

            filename = path / f"{k_key}_ol"
            self._save_fig(filename, settings.xlimsGM)
            plt.close(fig)

    # --- Plotting Primitives ---

    def plot_generic(self, x, y, legend, title, filename, ylab, xlims, settings: PlotSettings):
        fig, ax = plt.subplots(1, 1, figsize=settings.figsize)
        ax.plot(x, y, linewidth=settings.lineW)
        ax.legend(legend, fontsize=settings.legF)
        self._decorate_ax(ax, title, ylab, settings.xlab, xlims, settings)
        self._save_fig(filename, xlims)
        plt.close(fig)

    def plot_dict(self, x, y_dict, title, filename, ylab, xlims, settings: PlotSettings):
        self.plot_dict_generic(x, y_dict, title, filename, ylab, xlims, settings)

    def plot_dict_generic(self, x, y_dict, title, filename, ylab, xlims, settings: PlotSettings):
        fig, ax = plt.subplots(1, 1, figsize=settings.figsize)
        legend_keys = list(y_dict.keys())
        for key in legend_keys:
            ax.plot(x, y_dict[key], linewidth=settings.lineW)

        ax.legend(legend_keys, fontsize=settings.legF, loc=settings.locLegSing, ncol=settings.ncolLegSing)
        self._decorate_ax(ax, title, ylab, settings.xlab, xlims, settings)
        self._save_fig(filename, xlims)
        plt.close(fig)

    def plot_ylog_dict(self, x, y_dict, legend, title, filename, ylab, xlims, settings: PlotSettings):
        fig, ax = plt.subplots(1, 1, figsize=settings.figsize)
        keys = legend if legend else list(y_dict.keys())
        for key in keys:
            if key in y_dict:
                ax.plot(x, np.log10(y_dict[key]), linewidth=settings.lineW)

        ax.legend(keys, fontsize=settings.legF)
        self._decorate_ax(ax, title, ylab, settings.xlab, xlims, settings)
        self._save_fig(filename, xlims)
        plt.close(fig)

    def overlaid_list_plotter(self, datalist, keys, filename, ylab, xlims, settings: PlotSettings, title):
        fig, ax = plt.subplots(1, 1, figsize=settings.figsize)
        lstyle = [':', '-'] * (len(datalist) // 2 + 1)

        full_legend = []
        for t, data in enumerate(datalist):
            x = data[keys[0]]
            y = data[keys[1]]
            legs = data[keys[2]]
            ax.plot(x, y, lstyle[t], linewidth=settings.lineW)
            full_legend.extend(legs) # This logic accumulates legend, might duplicate if multiple lines per step

        # Original code logic for legend was: np.append(settings['legend'], settings['legend'])?
        # That seems like it duplicates labels.
        # We will just try to show what's plotted.

        ax.legend(full_legend, fontsize=settings.legF)
        self._decorate_ax(ax, title, ylab, settings.xlab, xlims, settings)
        self._save_fig(filename, xlims)
        plt.close(fig)

    def overlaid_dict_plotter(self, datalist, keys, filename, ylab, xlims, settings: PlotSettings, title):
        fig, ax = plt.subplots(1, 1, figsize=settings.figsize)
        lstyle = [':', '-'] * (len(datalist) // 2 + 1)

        full_legend = []
        for t, data in enumerate(datalist):
            x = data[keys[0]]
            y_dict = data[keys[1]]
            current_keys = list(y_dict.keys())
            for k in current_keys:
                ax.plot(x, y_dict[k], lstyle[t], linewidth=settings.lineW)
            full_legend.extend(current_keys)

        ax.legend(full_legend, fontsize=settings.legF, loc=settings.locLegSing, ncol=settings.ncolLegSing)
        self._decorate_ax(ax, title, ylab, settings.xlab, xlims, settings)
        self._save_fig(filename, xlims)
        plt.close(fig)

    def overlaid_dict_ylog_plotter(self, datalist, keys, filename, ylab, xlims, settings: PlotSettings, title, path):
         fig, ax = plt.subplots(1, 1, figsize=settings.figsize)
         lstyle = [':', '-'] * (len(datalist) // 2 + 1)

         full_legend = []
         for t, data in enumerate(datalist):
            x = data[keys[0]]
            y_dict = data[keys[1]]
            current_keys = list(y_dict.keys())

            for k in current_keys:
                log_y = np.log10(y_dict[k])
                ax.plot(x, log_y, lstyle[t], linewidth=settings.lineW)

                # Export to CSV (feature from original code)
                try:
                    df = pd.DataFrame({'x': x, f'{k}_log': log_y})
                    time_label = 'first' if t == 0 else 'last' # Simplification
                    csv_name = path / f'log10_AC_{time_label}_SER.csv'
                    df.to_csv(csv_name, index=False)
                except Exception:
                    pass

            full_legend.extend(current_keys)

         ax.legend(full_legend, fontsize=settings.legF)
         self._decorate_ax(ax, title, ylab, settings.xlab, xlims, settings)
         self._save_fig(filename, xlims)
         plt.close(fig)

    # --- Helpers ---

    def _decorate_ax(self, ax, title, ylab, xlab, xlims, settings):
        ax.set_title(title)
        ax.set_ylabel(ylab, fontsize=settings.labF)
        ax.set_xlabel(xlab, fontsize=settings.labF)
        ax.set_xlim(xlims)
        ax.tick_params(axis="both", labelsize=settings.tickS)
        if settings.bins:
            try:
                ax.locator_params(axis='y', nbins=settings.bins)
                ax.locator_params(axis='x', nbins=settings.bins)
            except: pass
        for x in ax.spines.values():
            x.set_linewidth(settings.boxLW)

    def _save_fig(self, filename, xlims):
        suffix = f"_{xlims[0]}_{xlims[1]}"
        try:
            plt.savefig(f"{filename}{suffix}.png", dpi=400, bbox_inches='tight')
            # plt.savefig(f"{filename}{suffix}.pdf", dpi=1000, bbox_inches='tight') # PDF often slow
        except Exception as e:
            print(f"Error saving figure {filename}: {e}")

    def get_xlims(self, data):
        pts = data.get('tS_pts')
        if pts is not None and len(pts) > 0:
            return [pts[0], pts[-1]]
        return [0, 100]

    def del_pngs_pdf(self, path: Path):
        for ext in ['*.png', '*.pdf']:
            for f in path.glob(ext):
                try:
                    f.unlink()
                except OSError:
                    pass
