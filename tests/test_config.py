import unittest
import tempfile
import json
import os
from dictra_analyzr.config import Config

class TestConfig(unittest.TestCase):
    def setUp(self):
        self.temp_dir = tempfile.TemporaryDirectory()
        self.temp_json_path = os.path.join(self.temp_dir.name, "settings.json")

    def tearDown(self):
        self.temp_dir.cleanup()

    def test_from_json_valid_data(self):
        data = {
            "timeflags": ["first", "last"],
            "dirList": ["dir1", "dir2"],
            "tc_setting": {
                "database": ["TCFE9", "MOBFE4"],
                "acRefs": ["A"],
                "phsToSus": ["LIQUID"],
                "p3flag": True,
                "mobFlag": True
            },
            "plot_settings": {
                "legend": "Test Legend",
                "lineW": 3,
                "legF": 14,
                "xlims": [0.0, 1.0],
                "title": "Test Title",
                "ylab": "Y",
                "xlab": "X",
                "labF": 14,
                "tickS": 14,
                "bins": 10,
                "figsize": [12, 10],
                "locLegSing": "upper right",
                "ncolLegSing": 2,
                "boxLW": 1,
                "acSERleg": ["A", "B"],
                "MPlotlegs": ["M1", "M2"],
                "MPlotPhase": "FCC",
                "MPlotK": [["A", "B", "C"]],
                "xlimsGM": [0.0, 0.5]
            },
            "actions": {
                "read": True,
                "calc": True,
                "value_correction": False,
                "plot": True,
                "plotoverlaid": True,
                "plotMG": False,
                "delPNGs": True,
                "showPlot": True
            },
            "name_pairs": [["OldName", "NewName"]],
            "phase_changes": [["Phase1", "Phase2", 10.0]]
        }

        with open(self.temp_json_path, 'w') as f:
            json.dump(data, f)

        config = Config.from_json(self.temp_json_path)

        self.assertEqual(config.timeflags, ["first", "last"])
        self.assertEqual(config.dirList, ["dir1", "dir2"])

        self.assertEqual(config.tc_setting.database, ["TCFE9", "MOBFE4"])
        self.assertEqual(config.tc_setting.acRefs, ["A"])
        self.assertEqual(config.tc_setting.phsToSus, ["LIQUID"])
        self.assertEqual(config.tc_setting.p3flag, True)
        self.assertEqual(config.tc_setting.mobFlag, True)

        self.assertEqual(config.plot_settings.legend, "Test Legend")
        self.assertEqual(config.plot_settings.lineW, 3)
        self.assertEqual(config.plot_settings.legF, 14)
        self.assertEqual(config.plot_settings.xlims, [0.0, 1.0])
        self.assertEqual(config.plot_settings.title, "Test Title")
        self.assertEqual(config.plot_settings.ylab, "Y")
        self.assertEqual(config.plot_settings.xlab, "X")
        self.assertEqual(config.plot_settings.labF, 14)
        self.assertEqual(config.plot_settings.tickS, 14)
        self.assertEqual(config.plot_settings.bins, 10)
        self.assertEqual(config.plot_settings.figsize, [12, 10])
        self.assertEqual(config.plot_settings.locLegSing, "upper right")
        self.assertEqual(config.plot_settings.ncolLegSing, 2)
        self.assertEqual(config.plot_settings.boxLW, 1)
        self.assertEqual(config.plot_settings.acSERleg, ["A", "B"])
        self.assertEqual(config.plot_settings.MPlotlegs, ["M1", "M2"])
        self.assertEqual(config.plot_settings.MPlotPhase, "FCC")
        self.assertEqual(config.plot_settings.MPlotK, [("A", "B", "C")])
        self.assertEqual(config.plot_settings.xlimsGM, [0.0, 0.5])

        self.assertEqual(config.actions.read, True)
        self.assertEqual(config.actions.calc, True)
        self.assertEqual(config.actions.value_correction, False)
        self.assertEqual(config.actions.plot, True)
        self.assertEqual(config.actions.plotoverlaid, True)
        self.assertEqual(config.actions.plotMG, False)
        self.assertEqual(config.actions.delPNGs, True)
        self.assertEqual(config.actions.showPlot, True)

        self.assertEqual(config.name_pairs, [("OldName", "NewName")])
        self.assertEqual(config.phase_changes, [("Phase1", "Phase2", 10.0)])


    def test_from_json_defaults(self):
        data = {}

        with open(self.temp_json_path, 'w') as f:
            json.dump(data, f)

        config = Config.from_json(self.temp_json_path)

        self.assertEqual(config.timeflags, ["last"])
        self.assertEqual(config.dirList, [])

        self.assertEqual(config.tc_setting.database, ["TCFE9"])
        self.assertEqual(config.tc_setting.acRefs, [])
        self.assertEqual(config.tc_setting.phsToSus, [])
        self.assertEqual(config.tc_setting.p3flag, False)
        self.assertEqual(config.tc_setting.mobFlag, False)

        self.assertEqual(config.plot_settings.legend, "")
        self.assertEqual(config.plot_settings.lineW, 2)
        self.assertEqual(config.plot_settings.legF, 12)
        self.assertEqual(config.plot_settings.xlims, [])
        self.assertEqual(config.plot_settings.title, "")
        self.assertEqual(config.plot_settings.ylab, "")
        self.assertEqual(config.plot_settings.xlab, "")
        self.assertEqual(config.plot_settings.labF, 12)
        self.assertEqual(config.plot_settings.tickS, 12)
        self.assertEqual(config.plot_settings.bins, 5)
        self.assertEqual(config.plot_settings.figsize, [10, 8])
        self.assertEqual(config.plot_settings.locLegSing, "best")
        self.assertEqual(config.plot_settings.ncolLegSing, 1)
        self.assertEqual(config.plot_settings.boxLW, 2)
        self.assertEqual(config.plot_settings.acSERleg, [])
        self.assertEqual(config.plot_settings.MPlotlegs, [])
        self.assertEqual(config.plot_settings.MPlotPhase, "")
        self.assertEqual(config.plot_settings.MPlotK, [])
        self.assertEqual(config.plot_settings.xlimsGM, [])

        self.assertEqual(config.actions.read, False)
        self.assertEqual(config.actions.calc, False)
        self.assertEqual(config.actions.value_correction, False)
        self.assertEqual(config.actions.plot, False)
        self.assertEqual(config.actions.plotoverlaid, False)
        self.assertEqual(config.actions.plotMG, False)
        self.assertEqual(config.actions.delPNGs, False)
        self.assertEqual(config.actions.showPlot, False)

        self.assertEqual(config.name_pairs, [])
        self.assertEqual(config.phase_changes, [])

if __name__ == '__main__':
    unittest.main()
