#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""Script to generate test execution metrics."""

from robot.api import ExecutionResult
import json
import os
from datetime import datetime

def generate_metrics(output_xml, output_dir="metrics"):
    """Generate metrics report from Robot Framework output.xml."""
    result = ExecutionResult(output_xml)
    result.configure(stat_config={'suite_stat_level': 2,
                                'tag_stat_combine': 'tagANDanother'})

    # Ensure output directory exists
    os.makedirs(output_dir, exist_ok=True)

    # Collect metrics
    metrics = {
        'generated_at': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
        'total_tests': result.statistics.total.total,
        'passed_tests': result.statistics.total.passed,
        'failed_tests': result.statistics.total.failed,
        'skipped_tests': result.statistics.total.skipped,
        'total_time': result.suite.elapsedtime / 1000,  # Convert to seconds
        'suites': [],
        'tags': []
    }

    # Suite metrics
    for suite in result.suite.suites:
        suite_metrics = {
            'name': suite.name,
            'total': len(suite.tests),
            'passed': len([t for t in suite.tests if t.status == 'PASS']),
            'failed': len([t for t in suite.tests if t.status == 'FAIL']),
            'skipped': len([t for t in suite.tests if t.status == 'SKIP']),
            'time': suite.elapsedtime / 1000
        }
        metrics['suites'].append(suite_metrics)

    # Tag metrics
    for tag in result.statistics.tags:
        tag_metrics = {
            'name': tag.longname,
            'total': tag.total,
            'passed': tag.passed,
            'failed': tag.failed,
            'skipped': getattr(tag, 'skipped', 0),
            'time': getattr(tag, 'elapsed', 0) / 1000
        }
        metrics['tags'].append(tag_metrics)

    # Save metrics to JSON file
    metrics_file = os.path.join(output_dir, 'metrics.json')
    with open(metrics_file, 'w') as f:
        json.dump(metrics, f, indent=2)

    # Generate HTML report
    html_report = generate_html_report(metrics)
    html_file = os.path.join(output_dir, 'metrics.html')
    with open(html_file, 'w') as f:
        f.write(html_report)

    return metrics

def generate_html_report(metrics):
    """Generate an HTML report from the metrics data."""
    html = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <title>Robot Framework Test Metrics</title>
        <style>
            body {{ font-family: Arial, sans-serif; margin: 20px; }}
            .container {{ max-width: 1200px; margin: 0 auto; }}
            .card {{ background: #fff; border-radius: 8px; padding: 20px; margin: 20px 0; box-shadow: 0 2px 4px rgba(0,0,0,0.1); }}
            .metric {{ display: inline-block; margin: 10px; padding: 15px; text-align: center; min-width: 150px; }}
            .metric h3 {{ margin: 0; color: #333; }}
            .metric p {{ font-size: 24px; margin: 10px 0; }}
            .pass {{ color: #28a745; }}
            .fail {{ color: #dc3545; }}
            .skip {{ color: #ffc107; }}
            table {{ width: 100%; border-collapse: collapse; margin: 20px 0; }}
            th, td {{ padding: 12px; text-align: left; border-bottom: 1px solid #ddd; }}
            th {{ background-color: #f8f9fa; }}
        </style>
    </head>
    <body>
        <div class="container">
            <h1>Robot Framework Test Metrics</h1>
            <p>Generated at: {metrics['generated_at']}</p>
            
            <div class="card">
                <h2>Overall Statistics</h2>
                <div class="metric">
                    <h3>Total Tests</h3>
                    <p>{metrics['total_tests']}</p>
                </div>
                <div class="metric">
                    <h3>Passed</h3>
                    <p class="pass">{metrics['passed_tests']}</p>
                </div>
                <div class="metric">
                    <h3>Failed</h3>
                    <p class="fail">{metrics['failed_tests']}</p>
                </div>
                <div class="metric">
                    <h3>Skipped</h3>
                    <p class="skip">{metrics['skipped_tests']}</p>
                </div>
                <div class="metric">
                    <h3>Total Time</h3>
                    <p>{metrics['total_time']:.2f}s</p>
                </div>
            </div>

            <div class="card">
                <h2>Suite Statistics</h2>
                <table>
                    <tr>
                        <th>Suite Name</th>
                        <th>Total</th>
                        <th>Passed</th>
                        <th>Failed</th>
                        <th>Skipped</th>
                        <th>Time (s)</th>
                    </tr>
                    {''.join(f"""
                    <tr>
                        <td>{suite['name']}</td>
                        <td>{suite['total']}</td>
                        <td class="pass">{suite['passed']}</td>
                        <td class="fail">{suite['failed']}</td>
                        <td class="skip">{suite['skipped']}</td>
                        <td>{suite['time']:.2f}</td>
                    </tr>
                    """ for suite in metrics['suites'])}
                </table>
            </div>

            <div class="card">
                <h2>Tag Statistics</h2>
                <table>
                    <tr>
                        <th>Tag Name</th>
                        <th>Total</th>
                        <th>Passed</th>
                        <th>Failed</th>
                        <th>Skipped</th>
                        <th>Time (s)</th>
                    </tr>
                    {''.join(f"""
                    <tr>
                        <td>{tag['name']}</td>
                        <td>{tag['total']}</td>
                        <td class="pass">{tag['passed']}</td>
                        <td class="fail">{tag['failed']}</td>
                        <td class="skip">{tag['skipped']}</td>
                        <td>{tag['time']:.2f}</td>
                    </tr>
                    """ for tag in metrics['tags'])}
                </table>
            </div>
        </div>
    </body>
    </html>
    """
    return html

if __name__ == '__main__':
    import sys
    if len(sys.argv) < 2:
        print("Usage: python3 generate_metrics.py <output.xml> [output_dir]")
        sys.exit(1)
    
    output_xml = sys.argv[1]
    output_dir = sys.argv[2] if len(sys.argv) > 2 else "metrics"
    generate_metrics(output_xml, output_dir) 