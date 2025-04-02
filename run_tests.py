#!/usr/bin/env python3
"""
Test runner script for the Robot Framework UI Test Automation Framework.
Provides options for running web tests, desktop tests, or unit tests.
"""
import os
import sys
import argparse
import subprocess


def run_robot_tests(directory, report_dir='reports', include_tags=None, exclude_tags=None):
    """
    Run Robot Framework tests in the specified directory.
    
    Args:
        directory (str): Directory containing the test files
        report_dir (str): Directory to store reports
        include_tags (list): Tags to include
        exclude_tags (list): Tags to exclude
    
    Returns:
        int: Return code from the test execution
    """
    cmd = ['robot', '--outputdir', report_dir]
    
    if include_tags:
        cmd.extend(['--include', ' OR '.join(include_tags)])
    
    if exclude_tags:
        cmd.extend(['--exclude', ' OR '.join(exclude_tags)])
    
    cmd.append(directory)
    print(f"Running command: {' '.join(cmd)}")
    
    return subprocess.call(cmd)


def run_unit_tests(directory='tests/unit', coverage=False):
    """
    Run unit tests using pytest.
    
    Args:
        directory (str): Directory containing the test files
        coverage (bool): Whether to generate coverage reports
    
    Returns:
        int: Return code from the test execution
    """
    cmd = ['python', '-m', 'pytest', directory]
    
    if coverage:
        cmd.extend(['--cov=utils', '--cov=resources', '--cov-report', 'term', '--cov-report', 'html:reports/coverage'])
    
    print(f"Running command: {' '.join(cmd)}")
    
    return subprocess.call(cmd)


def main():
    """Parse arguments and run tests."""
    parser = argparse.ArgumentParser(description='Run tests for the UI Test Automation Framework')
    parser.add_argument('--type', choices=['web', 'desktop', 'unit', 'all'], default='all',
                        help='Type of tests to run (web, desktop, unit, or all)')
    parser.add_argument('--report-dir', default='reports', help='Directory to store reports')
    parser.add_argument('--include', nargs='+', help='Tags to include')
    parser.add_argument('--exclude', nargs='+', help='Tags to exclude')
    parser.add_argument('--coverage', action='store_true', help='Generate coverage reports for unit tests')
    
    args = parser.parse_args()
    
    # Create reports directory if it doesn't exist
    os.makedirs(args.report_dir, exist_ok=True)
    
    return_codes = []
    
    if args.type in ['web', 'all']:
        print("\n=== Running Web UI Tests ===")
        web_return_code = run_robot_tests('tests/web', args.report_dir, args.include, args.exclude)
        return_codes.append(web_return_code)
    
    if args.type in ['desktop', 'all']:
        print("\n=== Running Desktop UI Tests ===")
        desktop_return_code = run_robot_tests('tests/desktop', args.report_dir, args.include, args.exclude)
        return_codes.append(desktop_return_code)
    
    if args.type in ['unit', 'all']:
        print("\n=== Running Unit Tests ===")
        unit_return_code = run_unit_tests(coverage=args.coverage)
        return_codes.append(unit_return_code)
    
    # Return non-zero if any of the test runs failed
    return max(return_codes) if return_codes else 0


if __name__ == '__main__':
    sys.exit(main()) 