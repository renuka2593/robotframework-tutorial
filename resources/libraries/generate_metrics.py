#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import sys
import glob
from TestMetrics import TestMetrics

def find_output_files(results_dir):
    """Find all output.xml files in the results directory and its subdirectories."""
    pattern = os.path.join(results_dir, '**', 'output.xml')
    return glob.glob(pattern, recursive=True)

def main():
    """Generate metrics report from Robot Framework output.xml files"""
    if len(sys.argv) < 2:
        print("Usage: python generate_metrics.py <results_dir> [report_dir]")
        sys.exit(1)
    
    results_dir = sys.argv[1]
    report_dir = sys.argv[2] if len(sys.argv) > 2 else 'metrics'
    
    try:
        metrics = TestMetrics()
        output_files = find_output_files(results_dir)
        
        if not output_files:
            print(f"No output.xml files found in {results_dir}")
            sys.exit(1)
        
        print(f"Found {len(output_files)} output.xml files")
        for output_xml in output_files:
            print(f"Processing: {output_xml}")
            result = metrics.generate_metrics_report(output_xml, report_dir)
            print(result)
            
    except Exception as e:
        print(f"Error generating metrics report: {str(e)}")
        sys.exit(1)

if __name__ == '__main__':
    main() 