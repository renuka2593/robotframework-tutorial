#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import argparse
import os
import sys
import json
import logging
from pathlib import Path
from typing import Union # Add this import
from robot.api import ExecutionResult # Import ExecutionResult

# Add the library directory to sys.path to find TestMetrics
script_dir = Path(__file__).parent.parent # Go up one level from libraries/
library_dir = script_dir / 'libraries'
sys.path.insert(0, str(library_dir))

try:
    from TestMetrics import TestMetrics # Import the refactored visitor class
except ImportError as e:
    print(f"Error importing TestMetrics: {e}", file=sys.stderr)
    print(f"Please ensure TestMetrics.py is in the directory: {library_dir}", file=sys.stderr)
    sys.exit(1)

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Define template path relative to this script
_TEMPLATE_PATH = library_dir / 'templates' / 'report_template.html'

def find_output_files(input_path: Path) -> list[Path]:
    """Finds output.xml files based on the input path."""
    if input_path.is_file() and input_path.name == 'output.xml':
        logger.info(f"Processing single input file: {input_path}")
        return [input_path]
    elif input_path.is_dir():
        logger.info(f"Searching for output.xml files recursively in: {input_path}")
        output_files = list(input_path.rglob('output.xml'))
        logger.info(f"Found {len(output_files)} output.xml file(s).")
        return output_files
    else:
        logger.warning(f"Input path is neither a directory nor an output.xml file: {input_path}")
        return []

def merge_results(output_files: list[Path]) -> Union[ExecutionResult, None]:
    """Merges multiple output.xml files into a single ExecutionResult object."""
    if not output_files:
        logger.warning("merge_results called with empty file list.")
        return None
    
    # Log the exact files being processed/merged
    logger.debug(f"Files to process/merge: {[str(f) for f in output_files]}")

    if len(output_files) == 1:
        logger.info("Processing single result file.")
        try:
            result = ExecutionResult(output_files[0])
            logger.debug(f"Loaded single result. Type: {type(result)}")
            return result
        except Exception as e:
            logger.error(f"Error reading single result file {output_files[0]}: {e}", exc_info=True)
            return None
    else:
        logger.info(f"Attempting to merge {len(output_files)} result files...")
        try:
            # In RF 7.0+, ExecutionResult constructor handles merging
            result = ExecutionResult(*output_files) 
            logger.info("Result files merged successfully using ExecutionResult.")
            logger.debug(f"Merged result type: {type(result)}")
            # ExecutionResult already handles wrapping, return it directly
            return result
        except Exception as e:
            logger.error(f"Error merging result files using ExecutionResult: {e}", exc_info=True)
            return None

def generate_html_report(metrics_data: dict, report_html_path: Path):
    """Generates the HTML report from metrics data using the template."""
    logger.debug(f"Generating HTML report to: {report_html_path}")
    template_path = _TEMPLATE_PATH
    logger.debug(f"Using template path: {template_path}")

    # Read Template
    try:
        with open(template_path, 'r', encoding='utf-8') as f:
            template_content = f.read()
        logger.debug(f"Read template file ({len(template_content)} bytes).")
    except FileNotFoundError:
        logger.error(f"CRITICAL ERROR: HTML template file not found at {template_path}! Cannot generate HTML.")
        raise # Re-raise to stop the process
    except Exception as e:
        logger.error(f"CRITICAL ERROR: Failed to read template file {template_path}: {e}", exc_info=True)
        raise

    # Prepare JSON Data
    try:
        metrics_json_string = json.dumps(metrics_data, default=str, separators=(',', ':'))
    except Exception as json_e:
        logger.error(f"ERROR: Failed to serialize metrics data to JSON string: {json_e}", exc_info=True)
        error_data = {'error': f"Failed to serialize metrics data: {json_e}"}
        metrics_json_string = json.dumps(error_data)

    # Replace Placeholder
    placeholder = '{{METRICS_DATA}}'
    if placeholder not in template_content:
        logger.error(f"CRITICAL ERROR: Placeholder '{placeholder}' not found in template file {template_path}. Report will be incomplete.")
        html_content = template_content # Proceed without replacement, JS will likely fail
    else:
        html_content = template_content.replace(placeholder, metrics_json_string)
        logger.debug(f"Placeholder '{placeholder}' replaced.")

    # Write Report
    try:
        with open(report_html_path, 'w', encoding='utf-8') as f:
            f.write(html_content)
        logger.debug(f"Successfully wrote HTML report ({len(html_content)} bytes) to {report_html_path}")
    except Exception as e:
        logger.error(f"CRITICAL ERROR: Failed to write final HTML report file {report_html_path}: {e}", exc_info=True)
        raise

def main():
    parser = argparse.ArgumentParser(description='Generate merged test metrics report from Robot Framework output.xml files.')
    parser.add_argument('input_path', type=Path,
                        help='Path to a single output.xml file or a directory containing output.xml files (searched recursively)')
    parser.add_argument('output_dir', type=Path, 
                        help='Directory to save metrics.json and index.html')
    parser.add_argument('-v', '--verbose', action='store_true', help='Enable debug logging')
    
    args = parser.parse_args()

    log_level = logging.DEBUG if args.verbose else logging.INFO
    logging.getLogger().setLevel(log_level)
    logger.info(f"Log level set to: {logging.getLevelName(log_level)}")

    logger.info(f"Input path: {args.input_path}")
    logger.info(f"Output directory: {args.output_dir}")

    # --- Find and Merge Output Files ---
    output_files = find_output_files(args.input_path)
    if not output_files:
        logger.error("No output.xml files found at the specified path. Exiting.")
        sys.exit(1)
    
    result = merge_results(output_files)
    if not result:
        logger.error("Failed to load or merge result files. Exiting.")
        sys.exit(1)
    logger.info(f"Successfully loaded/merged results. Result object type: {type(result)}")

    # --- Process Results with Visitor ---
    logger.info("Initializing TestMetrics visitor...")
    metrics_processor = TestMetrics()
    try:
        logger.info("Attempting to visit the result object...")
        result.visit(metrics_processor) # Visit the merged or single result object
        logger.info("Visiting complete.")
        metrics_data = metrics_processor.get_metrics() # Retrieve collected data
        logger.info("Metrics data retrieved from visitor.")
        # Log some basic retrieved data
        logger.debug(f"Retrieved metrics keys: {list(metrics_data.keys())}")
        logger.debug(f"Retrieved total tests: {metrics_data.get('total_tests', 'N/A')}")
    except Exception as visit_e:
        logger.error(f"CRITICAL ERROR during result visiting: {visit_e}", exc_info=True)
        sys.exit(1)
        
    if not metrics_data or not metrics_data.get('suites'):
         logger.error("CRITICAL ERROR: Metrics data is empty after processing. Check visitor logic and input XML.")
         sys.exit(1)

    # --- Prepare Output Directory and Paths ---
    try:
        args.output_dir.mkdir(parents=True, exist_ok=True)
        logger.debug(f"Ensured output directory exists: {args.output_dir}")
    except OSError as e_mkdir:
         logger.error(f"CRITICAL ERROR: Failed to create output directory {args.output_dir}: {e_mkdir}", exc_info=True)
         sys.exit(1)

    metrics_json_path = args.output_dir / 'metrics.json'
    report_html_path = args.output_dir / 'index.html'

    # --- Generate Reports --- 
    logger.info(f"Generating JSON report to: {metrics_json_path}")
    try:
        with open(metrics_json_path, 'w', encoding='utf-8') as f:
            json.dump(metrics_data, f, indent=2)
        logger.info("Successfully saved JSON report.")
    except Exception as e:
         logger.error(f"ERROR: Failed to save metrics JSON: {e}", exc_info=True)
         # Optionally exit here or allow HTML generation to proceed

    logger.info(f"Generating HTML report to: {report_html_path}")
    try:
        generate_html_report(metrics_data, report_html_path)
        logger.info("Successfully generated HTML report.")
    except Exception as e:
        logger.error(f"Failed during HTML report generation step: {e}", exc_info=True)
        sys.exit(1)

    # --- Final Summary --- 
    logger.info(f"------------------------------------------")
    logger.info(f"  Metrics Report Generation Complete")
    logger.info(f"------------------------------------------")
    logger.info(f"  Input Source(s): {args.input_path} (Found {len(output_files)} file(s))")
    logger.info(f"  JSON Data:       {metrics_json_path}")
    logger.info(f"  HTML Report:     {report_html_path}")
    logger.info(f"  Total Tests:     {metrics_data.get('total_tests', 'N/A')}")
    try:
        overall_status = metrics_data.get('suites', [{}])[0].get('status', 'N/A') # Status of root suite
    except IndexError:
        overall_status = "N/A (No root suite found)"
    logger.info(f"  Overall Status:  {overall_status}")
    logger.info(f"------------------------------------------")
    sys.exit(0)

if __name__ == '__main__':
    main() 