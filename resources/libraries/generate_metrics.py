#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import sys
from TestMetrics import TestMetrics

def main():
    """Generate metrics report from Robot Framework output.xml"""
    if len(sys.argv) < 2:
        print("Usage: python generate_metrics.py <output.xml> [report_dir]")
        sys.exit(1)
    
    output_xml = sys.argv[1]
    report_dir = sys.argv[2] if len(sys.argv) > 2 else 'metrics'
    
    try:
        metrics = TestMetrics()
        result = metrics.generate_metrics_report(output_xml, report_dir)
        print(result)
    except Exception as e:
        print(f"Error generating metrics report: {str(e)}")
        sys.exit(1)

if __name__ == '__main__':
    main() 