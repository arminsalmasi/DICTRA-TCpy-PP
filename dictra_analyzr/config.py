import json
from dataclasses import dataclass, field
from pathlib import Path
from typing import List, Tuple, Dict, Any, Optional

@dataclass
class TCSetting:
    database: List[str]
    acRefs: List[str]
    phsToSus: List[str]
    p3flag: bool
    mobFlag: bool = False

@dataclass
class PlotSettings:
    legend: str
    lineW: int
    legF: int
    xlims: List[float]
    title: str
    ylab: str
    xlab: str
    labF: int
    tickS: int
    bins: int
    figsize: List[int]
    locLegSing: str = "best"
    ncolLegSing: int = 1
    boxLW: int = 2
    acSERleg: List[str] = field(default_factory=list)
    # GMX Plotter settings
    MPlotlegs: List[str] = field(default_factory=list)
    MPlotPhase: str = ""
    MPlotK: List[Tuple[str, str, str]] = field(default_factory=list)
    xlimsGM: List[float] = field(default_factory=list)


@dataclass
class Actions:
    read: bool
    calc: bool
    value_correction: bool
    plot: bool
    plotoverlaid: bool
    plotMG: bool
    delPNGs: bool
    showPlot: bool

@dataclass
class Config:
    timeflags: List[Any] # Can be 'first', 'last', or int/float
    dirList: List[str]
    actions: Actions
    tc_setting: TCSetting
    plot_settings: PlotSettings
    name_pairs: List[Tuple[str, str]] = field(default_factory=list)
    phase_changes: List[Tuple[str, str, float]] = field(default_factory=list)

    @classmethod
    def from_json(cls, json_path: str):
        with open(json_path, 'r') as f:
            data = json.load(f)

        # Parse nested structures
        tc_data = data.get('tc_setting', {})
        # Handle cases where database might be a string or list in legacy
        if isinstance(tc_data.get('database'), str):
             tc_data['database'] = [tc_data['database']]

        tc_setting = TCSetting(
            database=tc_data.get('database', ['TCFE9']),
            acRefs=tc_data.get('acRefs', []),
            phsToSus=tc_data.get('phsToSus', []),
            p3flag=tc_data.get('p3flag', False),
            mobFlag=tc_data.get('mobFlag', False)
        )

        plt_data = data.get('plot_settings', {})
        plot_settings = PlotSettings(
            legend=plt_data.get('legend', ''),
            lineW=plt_data.get('lineW', 2),
            legF=plt_data.get('legF', 12),
            xlims=plt_data.get('xlims', []),
            title=plt_data.get('title', ''),
            ylab=plt_data.get('ylab', ''),
            xlab=plt_data.get('xlab', ''),
            labF=plt_data.get('labF', 12),
            tickS=plt_data.get('tickS', 12),
            bins=plt_data.get('bins', 5),
            figsize=plt_data.get('figsize', [10, 8]),
            locLegSing=plt_data.get('locLegSing', 'best'),
            ncolLegSing=plt_data.get('ncolLegSing', 1),
            boxLW=plt_data.get('boxLW', 2),
            acSERleg=plt_data.get('acSERleg', []),
            MPlotlegs=plt_data.get('MPlotlegs', []),
            MPlotPhase=plt_data.get('MPlotPhase', ''),
            MPlotK=[tuple(k) for k in plt_data.get('MPlotK', [])],
            xlimsGM=plt_data.get('xlimsGM', [])
        )

        actions_data = data.get('actions', {})
        actions = Actions(
            read=actions_data.get('read', False),
            calc=actions_data.get('calc', False),
            value_correction=actions_data.get('value_correction', False),
            plot=actions_data.get('plot', False),
            plotoverlaid=actions_data.get('plotoverlaid', False),
            plotMG=actions_data.get('plotMG', False),
            delPNGs=actions_data.get('delPNGs', False),
            showPlot=actions_data.get('showPlot', False)
        )

        # Handle list of lists for name_pairs if necessary, ensure tuples
        name_pairs = [tuple(p) for p in data.get('name_pairs', [])]
        phase_changes = [tuple(p) for p in data.get('phase_changes', [])]

        return cls(
            timeflags=data.get('timeflags', ['last']),
            dirList=data.get('dirList', []),
            actions=actions,
            tc_setting=tc_setting,
            plot_settings=plot_settings,
            name_pairs=name_pairs,
            phase_changes=phase_changes
        )
