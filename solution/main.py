from solution.extract.extract import extract_data
from solution.data.compute_data import compute_data
import argparse
import logging

logging.basicConfig(
    level=logging.INFO,
    format="[%(asctime)s] %(levelname)s: %(message)s",
    datefmt="%H:%M",
)


def main():
    logging.info("Starting pipeline")
    parser = argparse.ArgumentParser()
    parser.add_argument("-audio", default="calls/call_01_northwind.txt")

    args = parser.parse_args()

    logging.info("Extracting audio file with LLM...")
    proposal_file = extract_data(args.audio)

    logging.info("Computing with internal data... ")
    compute_data(proposal_file)
    logging.info("Pipeline complete!")


if __name__ == "__main__":
    main()
