#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import json
import platform
import psutil
from datetime import datetime
from xml.etree import ElementTree as ET
from robot.api import ExecutionResult


class TestMetrics:
    """Library for generating beautiful HTML reports from Robot Framework test results."""
    
    ROBOT_LIBRARY_SCOPE = 'GLOBAL'
    
    def __init__(self):
        self.current_dir = os.getcwd()
        self.metrics_template = os.path.join(os.path.dirname(__file__), 'templates', 'metrics_template.html')
        
    def _get_system_info(self):
        """Get system information."""
        return {
            'os': platform.system(),
            'os_version': platform.version(),
            'python_version': platform.python_version(),
            'machine': platform.machine(),
            'processor': platform.processor(),
            'cpu_count': psutil.cpu_count(),
            'memory_total': psutil.virtual_memory().total,
            'memory_available': psutil.virtual_memory().available,
            'timestamp': datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }
        
    def _parse_output_xml(self, output_xml):
        """Parse the output.xml file and extract test execution data."""
        result = ExecutionResult(output_xml)
        result.configure()
        
        metrics = {
            'system_info': self._get_system_info(),
            'total_suites': len(list(result.suite.suites)),
            'total_tests': result.statistics.total.total,
            'passed_tests': result.statistics.total.passed,
            'failed_tests': result.statistics.total.failed,
            'skipped_tests': getattr(result.statistics.total, 'skipped', 0),
            'start_time': result.suite.starttime,
            'end_time': result.suite.endtime,
            'duration': result.suite.elapsedtime / 1000,  # Convert to seconds
            'suites': [],
            'keywords': {},
            'tags': {},
            'critical_failures': [],
            'test_timeline': []
        }
        
        # Process suites
        for suite in result.suite.suites:
            suite_data = {
                'id': suite.id,
                'name': suite.name,
                'status': suite.status,
                'total': len(suite.tests),
                'passed': len([t for t in suite.tests if t.status == 'PASS']),
                'failed': len([t for t in suite.tests if t.status == 'FAIL']),
                'skipped': len([t for t in suite.tests if t.status == 'SKIP']),
                'duration': suite.elapsedtime / 1000,
                'setup_status': suite.setup.status if suite.setup else 'N/A',
                'teardown_status': suite.teardown.status if suite.teardown else 'N/A',
                'tests': [],
                'critical_failures': []
            }
            
            # Process tests in suite
            for test in suite.tests:
                test_data = {
                    'id': test.id,
                    'name': test.name,
                    'status': test.status,
                    'duration': test.elapsedtime / 1000,
                    'message': test.message,
                    'tags': list(test.tags),
                    'setup_status': test.setup.status if test.setup else 'N/A',
                    'teardown_status': test.teardown.status if test.teardown else 'N/A',
                    'critical': 'critical' in test.tags
                }
                
                # Add to timeline
                metrics['test_timeline'].append({
                    'name': test.name,
                    'suite': suite.name,
                    'start_time': test.starttime,
                    'end_time': test.endtime,
                    'duration': test.elapsedtime / 1000,
                    'status': test.status
                })
                
                # Process tags
                for tag in test.tags:
                    if tag not in metrics['tags']:
                        metrics['tags'][tag] = {
                            'total': 0,
                            'passed': 0,
                            'failed': 0,
                            'skipped': 0
                        }
                    metrics['tags'][tag]['total'] += 1
                    metrics['tags'][tag][test.status.lower()] += 1
                
                # Track critical failures
                if test.status == 'FAIL' and test_data['critical']:
                    failure_data = {
                        'test_name': test.name,
                        'suite_name': suite.name,
                        'message': test.message,
                        'timestamp': test.starttime
                    }
                    metrics['critical_failures'].append(failure_data)
                    suite_data['critical_failures'].append(failure_data)
                
                suite_data['tests'].append(test_data)
                
                # Process keywords
                for kw in test.keywords:
                    if kw.name not in metrics['keywords']:
                        metrics['keywords'][kw.name] = {
                            'count': 0,
                            'failed': 0,
                            'passed': 0,
                            'durations': [],
                            'suites_used': set(),
                            'tests_used': set()
                        }
                    
                    metrics['keywords'][kw.name]['count'] += 1
                    if kw.status == 'FAIL':
                        metrics['keywords'][kw.name]['failed'] += 1
                    else:
                        metrics['keywords'][kw.name]['passed'] += 1
                    metrics['keywords'][kw.name]['durations'].append(kw.elapsedtime / 1000)
                    metrics['keywords'][kw.name]['suites_used'].add(suite.name)
                    metrics['keywords'][kw.name]['tests_used'].add(test.name)
            
            metrics['suites'].append(suite_data)
        
        # Calculate keyword statistics
        for kw_name, kw_data in metrics['keywords'].items():
            durations = kw_data['durations']
            kw_data['min_duration'] = min(durations) if durations else 0
            kw_data['max_duration'] = max(durations) if durations else 0
            kw_data['avg_duration'] = sum(durations) / len(durations) if durations else 0
            kw_data['success_rate'] = (kw_data['passed'] / kw_data['count']) * 100 if kw_data['count'] > 0 else 0
            kw_data['suites_used'] = list(kw_data['suites_used'])
            kw_data['tests_used'] = list(kw_data['tests_used'])
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
    <script src="https://cdn.datatables.net/buttons/2.1.0/js/dataTables.buttons.min.js"></script>
    <script src="https://cdnjs.cloudflare.com/ajax/libs/jszip/3.1.3/jszip.min.js"></script>
    <script src="https://cdn.datatables.net/buttons/2.1.0/js/buttons.html5.min.js"></script>
    <style>
        .dashboard-card {
            border-radius: 10px;
            box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
            margin-bottom: 20px;
            padding: 20px;
        }
        .status-badge {
            padding: 5px 10px;
            border-radius: 15px;
            font-weight: bold;
        }
        .status-pass { background-color: #d4edda; color: #155724; }
        .status-fail { background-color: #f8d7da; color: #721c24; }
        .status-skip { background-color: #fff3cd; color: #856404; }
        .metric-value {
            font-size: 24px;
            font-weight: bold;
            margin: 10px 0;
        }
        .timeline-container {
            margin: 20px 0;
            padding: 20px;
            background: #f8f9fa;
            border-radius: 10px;
        }
    </style>
</head>
<body>
    <div id="metrics-data" style="display: none;">{{METRICS_DATA}}</div>
    
    <div class="container-fluid">
        <div class="row">
            <!-- Sidebar -->
            <nav class="col-md-2 d-none d-md-block bg-light sidebar py-3">
                <div class="sidebar-sticky">
                    <h5 class="sidebar-heading">Navigation</h5>
                    <ul class="nav flex-column">
                        <li class="nav-item">
                            <a class="nav-link active" href="#overview">
                                <i class="fas fa-home"></i> Overview
                            </a>
                        </li>
                        <li class="nav-item">
                            <a class="nav-link" href="#system-info">
                                <i class="fas fa-info-circle"></i> System Info
                            </a>
                        </li>
                        <li class="nav-item">
                            <a class="nav-link" href="#suites">
                                <i class="fas fa-folder"></i> Test Suites
                            </a>
                        </li>
                        <li class="nav-item">
                            <a class="nav-link" href="#keywords">
                                <i class="fas fa-code"></i> Keywords
                            </a>
                        </li>
                        <li class="nav-item">
                            <a class="nav-link" href="#tags">
                                <i class="fas fa-tags"></i> Tags
                            </a>
                        </li>
                        <li class="nav-item">
                            <a class="nav-link" href="#timeline">
                                <i class="fas fa-clock"></i> Timeline
                            </a>
                        </li>
                        <li class="nav-item">
                            <a class="nav-link" href="#failures">
                                <i class="fas fa-exclamation-triangle"></i> Critical Failures
                            </a>
                        </li>
                    </ul>
                </div>
            </nav>

            <!-- Main content -->
            <main role="main" class="col-md-10 ml-sm-auto px-4">
                <div id="overview" class="section mt-4">
                    <h2><i class="fas fa-home"></i> Overview</h2>
                    <div class="row">
                        <div class="col-md-3">
                            <div class="dashboard-card bg-light">
                                <h5>Total Tests</h5>
                                <div class="metric-value" id="totalTests"></div>
                                <div class="progress">
                                    <div class="progress-bar bg-success" id="passRate"></div>
                                </div>
                            </div>
                        </div>
                        <div class="col-md-3">
                            <div class="dashboard-card bg-light">
                                <h5>Total Duration</h5>
                                <div class="metric-value" id="totalDuration"></div>
                                <small>Hours:Minutes:Seconds</small>
                            </div>
                        </div>
                        <div class="col-md-6">
                            <div class="dashboard-card bg-light">
                                <div id="testStatusChart"></div>
                            </div>
                        </div>
                    </div>
                </div>

                <div id="system-info" class="section mt-4">
                    <h2><i class="fas fa-info-circle"></i> System Information</h2>
                    <div class="dashboard-card bg-light">
                        <div id="systemInfo"></div>
                    </div>
                </div>

                <div id="suites" class="section mt-4">
                    <h2><i class="fas fa-folder"></i> Test Suites</h2>
                    <div class="dashboard-card bg-light">
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
                                    <th>Setup</th>
                                    <th>Teardown</th>
                                </tr>
                            </thead>
                        </table>
                    </div>
                </div>

                <div id="keywords" class="section mt-4">
                    <h2><i class="fas fa-code"></i> Keywords</h2>
                    <div class="row">
                        <div class="col-md-8">
                            <div class="dashboard-card bg-light">
                                <table id="keywordsTable" class="display">
                                    <thead>
                                        <tr>
                                            <th>Keyword</th>
                                            <th>Count</th>
                                            <th>Success Rate</th>
                                            <th>Min Duration (s)</th>
                                            <th>Max Duration (s)</th>
                                            <th>Avg Duration (s)</th>
                                        </tr>
                                    </thead>
                                </table>
                            </div>
                        </div>
                        <div class="col-md-4">
                            <div class="dashboard-card bg-light">
                                <div id="keywordUsageChart"></div>
                            </div>
                        </div>
                    </div>
                </div>

                <div id="tags" class="section mt-4">
                    <h2><i class="fas fa-tags"></i> Tags</h2>
                    <div class="dashboard-card bg-light">
                        <div id="tagStatusChart"></div>
                    </div>
                </div>

                <div id="timeline" class="section mt-4">
                    <h2><i class="fas fa-clock"></i> Test Timeline</h2>
                    <div class="dashboard-card bg-light">
                        <div id="timelineChart"></div>
                    </div>
                </div>

                <div id="failures" class="section mt-4">
                    <h2><i class="fas fa-exclamation-triangle"></i> Critical Failures</h2>
                    <div class="dashboard-card bg-light">
                        <table id="failuresTable" class="display">
                            <thead>
                                <tr>
                                    <th>Test Name</th>
                                    <th>Suite</th>
                                    <th>Message</th>
                                    <th>Timestamp</th>
                                </tr>
                            </thead>
                        </table>
                    </div>
                </div>
            </main>
        </div>
    </div>

    <script>
        // Load metrics data
        const metricsData = JSON.parse(document.getElementById('metrics-data').textContent);
        
        // Format duration
        function formatDuration(seconds) {
            const hours = Math.floor(seconds / 3600);
            const minutes = Math.floor((seconds % 3600) / 60);
            const secs = Math.floor(seconds % 60);
            return `${hours.toString().padStart(2, '0')}:${minutes.toString().padStart(2, '0')}:${secs.toString().padStart(2, '0')}`;
        }

        // Update overview metrics
        document.getElementById('totalTests').textContent = metricsData.total_tests;
        document.getElementById('totalDuration').textContent = formatDuration(metricsData.duration);
        
        const passRate = (metricsData.passed_tests / metricsData.total_tests * 100).toFixed(1);
        document.getElementById('passRate').style.width = passRate + '%';
        document.getElementById('passRate').textContent = passRate + '%';

        // System Info
        const sysInfo = metricsData.system_info;
        document.getElementById('systemInfo').innerHTML = `
            <div class="row">
                <div class="col-md-4">
                    <p><strong>OS:</strong> ${sysInfo.os} ${sysInfo.os_version}</p>
                    <p><strong>Python:</strong> ${sysInfo.python_version}</p>
                </div>
                <div class="col-md-4">
                    <p><strong>Machine:</strong> ${sysInfo.machine}</p>
                    <p><strong>Processor:</strong> ${sysInfo.processor}</p>
                </div>
                <div class="col-md-4">
                    <p><strong>CPU Count:</strong> ${sysInfo.cpu_count}</p>
                    <p><strong>Memory:</strong> ${Math.round(sysInfo.memory_total / (1024 * 1024 * 1024))} GB</p>
                </div>
            </div>
            <p><strong>Timestamp:</strong> ${sysInfo.timestamp}</p>
        `;
        
        // Initialize DataTables
        $(document).ready(function() {
            $('#suitesTable').DataTable({
                data: metricsData.suites,
                columns: [
                    { data: 'name' },
                    { 
                        data: 'status',
                        render: function(data) {
                            const statusClass = data === 'PASS' ? 'status-pass' : 
                                              data === 'FAIL' ? 'status-fail' : 'status-skip';
                            return `<span class="status-badge ${statusClass}">${data}</span>`;
                        }
                    },
                    { data: 'total' },
                    { data: 'passed' },
                    { data: 'failed' },
                    { data: 'skipped' },
                    { 
                        data: 'duration',
                        render: function(data) {
                            return data.toFixed(2);
                        }
                    },
                    { data: 'setup_status' },
                    { data: 'teardown_status' }
                ],
                dom: 'Bfrtip',
                buttons: ['csv', 'excel']
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
                    { 
                        data: 'success_rate',
                        render: function(data) {
                            return data.toFixed(1) + '%';
                        }
                    },
                    { 
                        data: 'min_duration',
                        render: function(data) {
                            return data.toFixed(3);
                        }
                    },
                    { 
                        data: 'max_duration',
                        render: function(data) {
                            return data.toFixed(3);
                        }
                    },
                    { 
                        data: 'avg_duration',
                        render: function(data) {
                            return data.toFixed(3);
                        }
                    }
                ],
                dom: 'Bfrtip',
                buttons: ['csv', 'excel']
            });

            $('#failuresTable').DataTable({
                data: metricsData.critical_failures,
                columns: [
                    { data: 'test_name' },
                    { data: 'suite_name' },
                    { data: 'message' },
                    { data: 'timestamp' }
                ],
                dom: 'Bfrtip',
                buttons: ['csv', 'excel']
            });
        });

        // Test Status Chart
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
            title: {
                text: 'Test Execution Status'
            },
            labels: ['Passed', 'Failed', 'Skipped'],
            colors: ['#28a745', '#dc3545', '#ffc107'],
            plotOptions: {
                pie: {
                    donut: {
                        labels: {
                            show: true,
                            total: {
                                show: true,
                                label: 'Total Tests'
                            }
                        }
                    }
                }
            }
        };

        new ApexCharts(document.querySelector("#testStatusChart"), testStatusOptions).render();

        // Tag Status Chart
        const tagData = Object.entries(metricsData.tags).map(([tag, data]) => ({
            tag,
            ...data
        }));

        const tagStatusOptions = {
            series: [{
                name: 'Passed',
                data: tagData.map(t => t.passed)
            }, {
                name: 'Failed',
                data: tagData.map(t => t.failed)
            }, {
                name: 'Skipped',
                data: tagData.map(t => t.skipped)
            }],
            chart: {
                type: 'bar',
                height: 350,
                stacked: true
            },
            title: {
                text: 'Test Status by Tag'
            },
            xaxis: {
                categories: tagData.map(t => t.tag)
            },
            colors: ['#28a745', '#dc3545', '#ffc107'],
            plotOptions: {
                bar: {
                    horizontal: false
                }
            },
            legend: {
                position: 'top'
            }
        };

        new ApexCharts(document.querySelector("#tagStatusChart"), tagStatusOptions).render();

        // Timeline Chart
        const timelineOptions = {
            series: [{
                data: metricsData.test_timeline.map(test => ({
                    x: test.name,
                    y: [
                        new Date(test.start_time).getTime(),
                        new Date(test.end_time).getTime()
                    ],
                    fillColor: test.status === 'PASS' ? '#28a745' : 
                              test.status === 'FAIL' ? '#dc3545' : '#ffc107'
                }))
            }],
            chart: {
                height: 350,
                type: 'rangeBar'
            },
            title: {
                text: 'Test Execution Timeline'
            },
            plotOptions: {
                bar: {
                    horizontal: true
                }
            },
            xaxis: {
                type: 'datetime'
            }
        };

        new ApexCharts(document.querySelector("#timelineChart"), timelineOptions).render();

        // Keyword Usage Chart
        const topKeywords = keywordsData
            .sort((a, b) => b.count - a.count)
            .slice(0, 10);

        const keywordUsageOptions = {
            series: [{
                name: 'Usage Count',
                data: topKeywords.map(kw => kw.count)
            }],
            chart: {
                type: 'bar',
                height: 350
            },
            title: {
                text: 'Top 10 Most Used Keywords'
            },
            xaxis: {
                categories: topKeywords.map(kw => kw.name),
                labels: {
                    rotate: -45
                }
            },
            plotOptions: {
                bar: {
                    borderRadius: 4,
                    horizontal: false,
                    columnWidth: '70%'
                }
            }
        };

        new ApexCharts(document.querySelector("#keywordUsageChart"), keywordUsageOptions).render();
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