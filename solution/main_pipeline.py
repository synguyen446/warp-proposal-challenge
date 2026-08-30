from solution.extract.extract import extract_data
from solution.data.compute_data import compute_data
from solution.AI.ai_eval import llm_evaluate
from solution.no_ai_pipeline import run_pipeline_no_ai
import argparse
import logging
import os

logging.basicConfig(
    level=logging.INFO,
    format="[%(asctime)s] %(levelname)s: %(message)s",
    datefmt="%H:%M",
)


def main():
    logging.info("Starting pipeline")
    parser = argparse.ArgumentParser()
    parser.add_argument("-audio", default="calls/call_01_northwind.txt")
    parser.add_argument("--no-ai", default=False, action="store_true")

    args = parser.parse_args()

    logging.info("STEP 1: Extracting audio file with LLM.")

    if args.no_ai:
        proposal_file = run_pipeline_no_ai(args.audio)
    else:
        proposal_file = extract_data(args.audio)

    logging.info("STEP 2: Computing with internal data. ")
    computer_proposal_file = compute_data(proposal_file)
    
    if not args.no_ai:
        logging.info("STEP 3: Intepreting with AI...")
        llm_evaluate(computer_proposal_file)

    logging.info("Pipeline complete!")
    logging.info(f"Output Path: {os.getcwd()}/out/")


if __name__ == "__main__":
    main()
