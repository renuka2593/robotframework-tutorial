#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import sys
import json
from datetime import datetime
from robot.api import ExecutionResult
from TestMetrics import TestMetrics
import argparse

def main():
    """
    Generate test metrics report from Robot Framework output.xml files.
    Usage: python generate_metrics.py <results_dir> <output_dir>
    """
    if len(sys.argv) != 3:
        print("Usage: python generate_metrics.py <results_dir> <output_dir>")
        sys.exit(1)

    results_dir = sys.argv[1]
    output_dir = sys.argv[2]

    # Create output directory if it doesn't exist
    os.makedirs(output_dir, exist_ok=True)

    # Find all output.xml files in the results directory
    output_files = []
    for root, _, files in os.walk(results_dir):
        for file in files:
            if file == 'output.xml':
                output_files.append(os.path.join(root, file))

    if not output_files:
        print(f"No output.xml files found in {results_dir}")
        sys.exit(1)

    # Process each output.xml file
    for output_xml in output_files:
        try:
            # Create metrics collector
            metrics = TestMetrics()
            
            # Parse the output.xml file
            result = ExecutionResult(output_xml)
            result.visit(metrics)

            # Generate timestamp for filenames
            timestamp = datetime.now().strftime("%Y%m%d-%H%M%S")
            
            # Save metrics data as JSON
            metrics_json = os.path.join(output_dir, f'metrics-{timestamp}.json')
            with open(metrics_json, 'w') as f:
                json.dump(metrics.metrics, f, indent=2, default=str)
            
            # Generate HTML report
            metrics.generate_metrics_report(output_xml, output_dir)
            
            print(f"Generated metrics report for {output_xml}")
            print(f"JSON data saved to: {metrics_json}")
            print(f"HTML report saved to: {os.path.join(output_dir, 'index.html')}")

        except Exception as e:
            print(f"Error processing {output_xml}: {str(e)}")
            continue

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Generate test metrics report')
    parser.add_argument('input', help='Path to output.xml file')
    parser.add_argument('output', help='Output directory for the report')
    
    args = parser.parse_args()
    
    try:
        metrics = TestMetrics()
        report_file = metrics.generate_metrics_report(args.input, args.output)
        print(f"Successfully generated metrics report: {report_file}")
    except Exception as e:
        print(f"Error generating metrics report: {str(e)}")
        exit(1) 