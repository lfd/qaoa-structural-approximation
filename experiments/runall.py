import alma.experiment
from pathlib import Path


def main():
    SCRIPT_DIR = Path(__file__).parent

    for experiment_file in SCRIPT_DIR.glob("*.experiment"):
        print(f"Running {experiment_file.stem}")

        dispatcher = alma.experiment.load(experiment_file)
        dispatcher.start()
        dispatcher.join()


if __name__ == "__main__":
    main()
