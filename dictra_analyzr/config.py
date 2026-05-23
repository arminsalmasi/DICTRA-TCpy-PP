import json
from dataclasses import dataclass, field
from typing import List, Tuple, Dict, Any, Optional

@dataclass
class TCSetting:
    database: List[str]
    acRefs: List[str]
    phsToSus: List[str]
    p3flag: bool
    mobFlag: bool = False

    @classmethod
    def from_dict(cls, data: dict):
        if isinstance(data.get('database'), str):
             data['database'] = [data['database']]
        return cls(
            database=data.get('database', ['TCFE9']),
            acRefs=data.get('acRefs', []),
            phsToSus=data.get('phsToSus', []),
            p3flag=data.get('p3flag', False),
            mobFlag=data.get('mobFlag', False)
        )

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

    @classmethod
    def from_dict(cls, data: dict):
        return cls(
            legend=data.get('legend', ''),
            lineW=data.get('lineW', 2),
            legF=data.get('legF', 12),
            xlims=data.get('xlims', []),
            title=data.get('title', ''),
            ylab=data.get('ylab', ''),
            xlab=data.get('xlab', ''),
            labF=data.get('labF', 12),
            tickS=data.get('tickS', 12),
            bins=data.get('bins', 5),
            figsize=data.get('figsize', [10, 8]),
            locLegSing=data.get('locLegSing', 'best'),
            ncolLegSing=data.get('ncolLegSing', 1),
            boxLW=data.get('boxLW', 2),
            acSERleg=data.get('acSERleg', []),
            MPlotlegs=data.get('MPlotlegs', []),
            MPlotPhase=data.get('MPlotPhase', ''),
            MPlotK=[tuple(k) for k in data.get('MPlotK', [])],
            xlimsGM=data.get('xlimsGM', [])
        )


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

    @classmethod
    def from_dict(cls, data: dict):
        return cls(
            read=data.get('read', False),
            calc=data.get('calc', False),
            value_correction=data.get('value_correction', False),
            plot=data.get('plot', False),
            plotoverlaid=data.get('plotoverlaid', False),
            plotMG=data.get('plotMG', False),
            delPNGs=data.get('delPNGs', False),
            showPlot=data.get('showPlot', False)
        )

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
    def from_dict(cls, data: dict):
        tc_setting = TCSetting.from_dict(data.get('tc_setting', {}))
        plot_settings = PlotSettings.from_dict(data.get('plot_settings', {}))
        actions = Actions.from_dict(data.get('actions', {}))

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

    @classmethod
    def from_json(cls, json_path: str):
        with open(json_path, 'r') as f:
            data = json.load(f)
        return cls.from_dict(data)
