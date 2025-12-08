from pathlib import Path
from .config import Config
from .data_loader import DataLoader
from .calculator import ThermodynamicCalculator
from .corrector import ResultCorrector
from .plotter import Plotter

class DictraPipeline:
    def __init__(self, config_path: str, base_path: str = None):
        self.config = Config.from_json(config_path)
        # If base_path provided, override; else assume config logic determines path context
        # In original code, main(path) sets the context. Config was loaded from that path.
        if base_path:
            self.base_path = Path(base_path)
        else:
            self.base_path = Path.cwd()

    def run(self):
        print(f"Starting pipeline in: {self.base_path}")

        # 1. Data Loading
        if self.config.actions.read:
            print("Step: Reading Data")
            loader = DataLoader(self.base_path)
            loader.process_directories(self.config)

        # 2. Calculation
        if self.config.actions.calc:
            print("Step: Thermodynamics Calculation")
            calculator = ThermodynamicCalculator(self.base_path)
            calculator.process_calculations(self.config)

        # 3. Correction
        if self.config.actions.value_correction:
            print("Step: Result Correction")
            corrector = ResultCorrector(self.base_path)
            corrector.process_corrections(self.config)

        # 4. Plotting
        if self.config.actions.plot or self.config.actions.plotoverlaid or self.config.actions.plotMG:
            print("Step: Plotting")
            plotter = Plotter(self.base_path)
            plotter.process_plots(self.config)

        print("Pipeline Completed.")
