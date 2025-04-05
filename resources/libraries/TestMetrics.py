#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import json
from datetime import datetime
from xml.etree import ElementTree as ET
from robot.api import ExecutionResult


class TestMetrics:
    """Library for generating beautiful HTML reports from Robot Framework test results."""
    
    ROBOT_LIBRARY_SCOPE = 'GLOBAL'
    
    def __init__(self):
        self.current_dir = os.getcwd()
        self.metrics_template = os.path.join(os.path.dirname(__file__), 'templates', 'metrics_template.html')
        
    def _parse_output_xml(self, output_xml):
        """Parse the output.xml file and extract test execution data."""
        result = ExecutionResult(output_xml)
        result.configure()
        
        metrics = {
            'total_suites': len(list(result.suite.suites)),
            'total_tests': result.statistics.total.total,
            'passed_tests': result.statistics.total.passed,
            'failed_tests': result.statistics.total.failed,
            'skipped_tests': getattr(result.statistics.total, 'skipped', 0),
            'start_time': result.suite.starttime,
            'end_time': result.suite.endtime,
            'duration': result.suite.elapsedtime / 1000,  # Convert to seconds
            'suites': [],
            'keywords': {}
        }
        
        # Process suites
        for suite in result.suite.suites:
            suite_data = {
                'name': suite.name,
                'status': suite.status,
                'total': len(suite.tests),
                'passed': len([t for t in suite.tests if t.status == 'PASS']),
                'failed': len([t for t in suite.tests if t.status == 'FAIL']),
                'skipped': len([t for t in suite.tests if t.status == 'SKIP']),
                'duration': suite.elapsedtime / 1000,
                'tests': []
            }
            
            # Process tests in suite
            for test in suite.tests:
                test_data = {
                    'name': test.name,
                    'status': test.status,
                    'duration': test.elapsedtime / 1000,
                    'message': test.message,
                    'tags': list(test.tags)
                }
                suite_data['tests'].append(test_data)
                
                # Process keywords
                for kw in test.keywords:
                    if kw.name not in metrics['keywords']:
                        metrics['keywords'][kw.name] = {
                            'count': 0,
                            'failed': 0,
                            'durations': []
                        }
                    
                    metrics['keywords'][kw.name]['count'] += 1
                    if kw.status == 'FAIL':
                        metrics['keywords'][kw.name]['failed'] += 1
                    metrics['keywords'][kw.name]['durations'].append(kw.elapsedtime / 1000)
            
            metrics['suites'].append(suite_data)
        
        # Calculate keyword statistics
        for kw_name, kw_data in metrics['keywords'].items():
            durations = kw_data['durations']
            kw_data['min_duration'] = min(durations) if durations else 0
            kw_data['max_duration'] = max(durations) if durations else 0
            kw_data['avg_duration'] = sum(durations) / len(durations) if durations else 0
            del kw_data['durations']
        
        return metrics

    def generate_metrics_report(self, output_xml, report_dir='metrics'):
        """
        Generate a metrics report from Robot Framework output.xml
        
        Args:
            output_xml (str): Path to the output.xml file
            report_dir (str): Directory to save the generated report (default: metrics)
        """
        if not os.path.exists(output_xml):
            raise FileNotFoundError(f"Output file not found: {output_xml}")
        
        # Create report directory if it doesn't exist
        os.makedirs(report_dir, exist_ok=True)
        
        # Parse output.xml and get metrics
        metrics = self._parse_output_xml(output_xml)
        
        # Generate timestamp for the report
        timestamp = datetime.now().strftime("%Y%m%d-%H%M%S")
        
        # Save metrics data as JSON
        metrics_json = os.path.join(report_dir, f'metrics-{timestamp}.json')
        with open(metrics_json, 'w') as f:
            json.dump(metrics, f, indent=2)
        
        # Generate HTML report
        self._generate_html_report(metrics, report_dir, timestamp)
        
        return f"Report generated: {os.path.join(report_dir, f'metrics-{timestamp}.html')}"

    def _generate_html_report(self, metrics, report_dir, timestamp):
        """Generate HTML report from metrics data."""
        # Create templates directory if it doesn't exist
        templates_dir = os.path.dirname(self.metrics_template)
        os.makedirs(templates_dir, exist_ok=True)
        
        # Generate the HTML report
        report_file = os.path.join(report_dir, f'metrics-{timestamp}.html')
        
        # Read the template
        if not os.path.exists(self.metrics_template):
            self._create_default_template()
        
        with open(self.metrics_template, 'r') as f:
            template = f.read()
        
        # Replace placeholders with actual data
        html_content = template.replace('{{METRICS_DATA}}', json.dumps(metrics))
        
        # Write the report
        with open(report_file, 'w') as f:
            f.write(html_content)

    def _create_default_template(self):
        """Create the default HTML template if it doesn't exist."""
        template_dir = os.path.dirname(self.metrics_template)
        os.makedirs(template_dir, exist_ok=True)
        
        template_content = '''<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Robot Framework Test Metrics</title>
    <link href="https://cdnjs.cloudflare.com/ajax/libs/bootstrap/5.1.3/css/bootstrap.min.css" rel="stylesheet">
    <link href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0-beta3/css/all.min.css" rel="stylesheet">
    <link rel="stylesheet" href="https://cdn.datatables.net/1.11.5/css/jquery.dataTables.min.css">
    <link rel="stylesheet" href="https://cdn.datatables.net/buttons/2.1.0/css/buttons.dataTables.min.css">
    <script src="https://code.jquery.com/jquery-3.6.0.min.js"></script>
    <script src="https://cdn.jsdelivr.net/npm/apexcharts"></script>
    <script src="https://cdn.datatables.net/1.11.5/js/jquery.dataTables.min.js"></script>
    <!-- Add your custom CSS here -->
</head>
<body>
    <div id="metrics-data" style="display: none;">{{METRICS_DATA}}</div>
    
    <div class="container-fluid">
        <div class="row">
            <!-- Sidebar -->
            <nav class="col-md-2 d-none d-md-block bg-light sidebar">
                <div class="sidebar-sticky">
                    <ul class="nav flex-column">
                        <li class="nav-item">
                            <a class="nav-link active" href="#overview">
                                Overview
                            </a>
                        </li>
                        <li class="nav-item">
                            <a class="nav-link" href="#suites">
                                Test Suites
                            </a>
                        </li>
                        <li class="nav-item">
                            <a class="nav-link" href="#keywords">
                                Keywords
                            </a>
                        </li>
                    </ul>
                </div>
            </nav>

            <!-- Main content -->
            <main role="main" class="col-md-9 ml-sm-auto col-lg-10 px-4">
                <div id="overview" class="section">
                    <h2>Overview</h2>
                    <div class="row">
                        <div class="col-md-6">
                            <div id="testStatusChart"></div>
                        </div>
                        <div class="col-md-6">
                            <div id="suiteStatusChart"></div>
                        </div>
                    </div>
                </div>

                <div id="suites" class="section">
                    <h2>Test Suites</h2>
                    <table id="suitesTable" class="display">
                        <thead>
                            <tr>
                                <th>Suite Name</th>
                                <th>Status</th>
                                <th>Total</th>
                                <th>Passed</th>
                                <th>Failed</th>
                                <th>Skipped</th>
                                <th>Duration (s)</th>
                            </tr>
                        </thead>
                    </table>
                </div>

                <div id="keywords" class="section">
                    <h2>Keywords</h2>
                    <table id="keywordsTable" class="display">
                        <thead>
                            <tr>
                                <th>Keyword</th>
                                <th>Count</th>
                                <th>Failed</th>
                                <th>Min Duration (s)</th>
                                <th>Max Duration (s)</th>
                                <th>Avg Duration (s)</th>
                            </tr>
                        </thead>
                    </table>
                </div>
            </main>
        </div>
    </div>

    <script>
        // Load metrics data
        const metricsData = JSON.parse(document.getElementById('metrics-data').textContent);
        
        // Initialize DataTables
        $(document).ready(function() {
            $('#suitesTable').DataTable({
                data: metricsData.suites,
                columns: [
                    { data: 'name' },
                    { data: 'status' },
                    { data: 'total' },
                    { data: 'passed' },
                    { data: 'failed' },
                    { data: 'skipped' },
                    { data: 'duration' }
                ]
            });

            const keywordsData = Object.entries(metricsData.keywords).map(([name, data]) => ({
                name: name,
                ...data
            }));

            $('#keywordsTable').DataTable({
                data: keywordsData,
                columns: [
                    { data: 'name' },
                    { data: 'count' },
                    { data: 'failed' },
                    { data: 'min_duration' },
                    { data: 'max_duration' },
                    { data: 'avg_duration' }
                ]
            });
        });

        // Initialize charts
        const testStatusOptions = {
            series: [
                metricsData.passed_tests,
                metricsData.failed_tests,
                metricsData.skipped_tests
            ],
            chart: {
                type: 'donut',
                height: 350
            },
            labels: ['Passed', 'Failed', 'Skipped'],
            colors: ['#28a745', '#dc3545', '#ffc107']
        };

        new ApexCharts(document.querySelector("#testStatusChart"), testStatusOptions).render();

        // Add more charts and visualizations as needed
    </script>
</body>
</html>'''
        
        with open(self.metrics_template, 'w') as f:
            f.write(template_content)


if __name__ == '__main__':
    import argparse
    
    parser = argparse.ArgumentParser(description='Generate test metrics report')
    parser.add_argument('--input', required=True, help='Path to output.xml file')
    parser.add_argument('--output', default='metrics', help='Output directory for the report')
    
    args = parser.parse_args()
    
    metrics = TestMetrics()
    print(metrics.generate_metrics_report(args.input, args.output)) 