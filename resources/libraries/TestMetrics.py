#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import json
import platform
import psutil
from datetime import datetime, timezone
from robot.api import ExecutionResult, ResultVisitor
import time
import shutil
import traceback

# --- Determine Absolute Path for Template ---
# Get the directory where this script (TestMetrics.py) resides
_SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
# Construct the absolute path to the default template
_DEFAULT_TEMPLATE_PATH = os.path.join(_SCRIPT_DIR, 'templates', 'metrics_template.html')


class TestMetrics(ResultVisitor):
    """
    Generates comprehensive test metrics from Robot Framework output.xml using ResultVisitor.
    Includes system info, test stats, keyword usage, timeline, and tag analysis.
    """
    
    ROBOT_LIBRARY_SCOPE = 'GLOBAL'
    
    def __init__(self, metrics_template=_DEFAULT_TEMPLATE_PATH):
        # Ensure we use an absolute path for the template
        self.metrics_template_path = os.path.abspath(metrics_template)
        print(f"[DEBUG] Initialized TestMetrics. Template path set to: {self.metrics_template_path}")
        self.start_time = time.time()
        # Reset metrics structure for each new run
        self.metrics = {}
        self._suite_stack = []
        self._current_test_metrics = None
        self._keyword_stack = []

    def _get_system_info(self):
        """Gather system information."""
        uname = platform.uname()
        mem = psutil.virtual_memory()
        disk = psutil.disk_usage('/')
        
        # Get relevant environment variables
        env_vars = {
            var: os.environ.get(var, '') for var in [
                'PYTHONPATH', 'ROBOT_OPTIONS', 'BROWSER', 'HEADLESS', 
                'TEST_ENV', 'ROBOT_SYSLOG_FILE', 'ROBOT_LISTENER'
            ]
        }

        return {
            'os': uname.system,
            'os_release': uname.release,
            'os_version': uname.version,
            'architecture': uname.machine,
            'node': uname.node,
            'processor': uname.processor,
            'python_version': platform.python_version(),
            'python_implementation': platform.python_implementation(),
            'cpu_count': psutil.cpu_count(logical=True),
            'memory': {'total': mem.total, 'used': mem.used, 'free': mem.free, 'percent': mem.percent},
            'disk': {'total': disk.total, 'used': disk.used, 'free': disk.free, 'percent': disk.percent},
            'timestamp': datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S %Z"),
            'timezone': time.tzname[0] if time.tzname else 'Unknown',
            'env_vars': env_vars
        }

    # -- Visitor Methods --
    
    def start_suite(self, suite):
        suite_metrics = {
            'name': suite.name,
            'status': '',
            'total': 0,
            'passed': 0,
            'failed': 0,
            'skipped': 0,
            'duration': 0.0,
            'setup_status': suite.setup.status if suite.setup else 'NOT RUN',
            'teardown_status': suite.teardown.status if suite.teardown else 'NOT RUN',
            'keywords': {},
            'tests': [],
            'suites': []
        }
        if not self._suite_stack:
            self.metrics = {
                'total_tests': 0,
                'passed_tests': 0,
                'failed_tests': 0,
                'skipped_tests': 0,
                'duration': 0.0,
                'suites': [suite_metrics],
                'tags': {},
                'test_timeline': [],
                'critical_failures': [],
                'system_info': self._get_system_info(),
                'all_keywords': {}
            }
            self._suite_stack.append(self.metrics['suites'][0])
        else:
            parent_suite_metrics = self._suite_stack[-1]
            parent_suite_metrics['suites'].append(suite_metrics)
            self._suite_stack.append(suite_metrics)

    def end_suite(self, suite):
        if not self._suite_stack: return
        current_suite_metrics = self._suite_stack.pop()
        current_suite_metrics['status'] = suite.status
        current_suite_metrics['duration'] = suite.elapsedtime / 1000.0
        total = len(current_suite_metrics['tests']) + sum(s['total'] for s in current_suite_metrics['suites'])
        passed = sum(1 for t in current_suite_metrics['tests'] if t['status'] == 'PASS') + sum(s['passed'] for s in current_suite_metrics['suites'])
        failed = sum(1 for t in current_suite_metrics['tests'] if t['status'] == 'FAIL') + sum(s['failed'] for s in current_suite_metrics['suites'])
        skipped = sum(1 for t in current_suite_metrics['tests'] if t['status'] == 'SKIP') + sum(s['skipped'] for s in current_suite_metrics['suites'])
        current_suite_metrics['total'] = total
        current_suite_metrics['passed'] = passed
        current_suite_metrics['failed'] = failed
        current_suite_metrics['skipped'] = skipped
        if not self._suite_stack:
            self.metrics['total_tests'] = total
            self.metrics['passed_tests'] = passed
            self.metrics['failed_tests'] = failed
            self.metrics['skipped_tests'] = skipped
        self._calculate_keyword_stats(current_suite_metrics['keywords'])

    def start_test(self, test):
        if not self._suite_stack: return
        self._current_test_metrics = {
            'name': test.name,
            'status': '',
            'tags': list(test.tags),
            'duration': 0.0,
            'message': test.message or '',
            'start_time': str(test.starttime),
            'end_time': str(test.endtime),
            'steps': []
        }
        self._keyword_stack = []

    def end_test(self, test):
        if not self._current_test_metrics or not self._suite_stack: return
        self._current_test_metrics['status'] = test.status
        self._current_test_metrics['duration'] = test.elapsedtime / 1000.0
        self._current_test_metrics['message'] = test.message or ''
        parent_suite_metrics = self._suite_stack[-1]
        parent_suite_metrics['tests'].append(self._current_test_metrics)
        status = test.status
        for tag in list(test.tags):
            tag_stats = self.metrics['tags'].setdefault(tag, {'passed': 0, 'failed': 0, 'skipped': 0})
            if status == 'PASS': tag_stats['passed'] += 1
            elif status == 'FAIL': tag_stats['failed'] += 1
            else: tag_stats['skipped'] += 1
        self.metrics['test_timeline'].append({
            'name': test.name,
            'suite': parent_suite_metrics['name'],
            'status': status,
            'start_time': str(test.starttime),
            'end_time': str(test.endtime),
            'duration': test.elapsedtime / 1000.0
        })
        if status == 'FAIL' and test.critical == 'yes':
             self.metrics['critical_failures'].append({
                  'test_name': test.name,
                  'suite_name': parent_suite_metrics['name'],
                  'message': test.message or '',
                  'timestamp': str(test.endtime)
             })
        self._current_test_metrics = None
        self._keyword_stack = []

    def start_keyword(self, keyword):
         if not self._current_test_metrics: return
         keyword_metrics = {
                'name': keyword.name or f"[{keyword.type}]",
                'type': keyword.type,
                'status': '',
                'duration': 0.0,
                'messages': [],
                'arguments': list(keyword.args),
                'assign': list(keyword.assign)
            }
         if not self._keyword_stack:
             self._current_test_metrics['steps'].append(keyword_metrics)
         else:
             parent_keyword_metrics = self._keyword_stack[-1]
             parent_keyword_metrics.setdefault('children', []).append(keyword_metrics)
         self._keyword_stack.append(keyword_metrics)

    def end_keyword(self, keyword):
         if not self._keyword_stack: return
         current_keyword_metrics = self._keyword_stack.pop()
         current_keyword_metrics['status'] = keyword.status
         current_keyword_metrics['duration'] = keyword.elapsedtime / 1000.0
         self._aggregate_keyword_stats(keyword.name, keyword.elapsedtime / 1000.0, keyword.status)

    def visit_message(self, msg):
        if self._keyword_stack:
            self._keyword_stack[-1]['messages'].append({
                'level': msg.level,
                'timestamp': str(msg.timestamp),
                'text': msg.message
            })

    def _aggregate_keyword_stats(self, name, duration_secs, status):
         if not name: return
         is_pass = status == 'PASS'
         stats_global = self.metrics['all_keywords'].setdefault(name, 
             {'count': 0, 'passed': 0, 'failed': 0, 'min_duration': float('inf'), 'max_duration': 0.0, 'total_duration': 0.0})
         stats_global['count'] += 1
         stats_global['total_duration'] += duration_secs
         stats_global['min_duration'] = min(stats_global['min_duration'], duration_secs)
         stats_global['max_duration'] = max(stats_global['max_duration'], duration_secs)
         if is_pass: stats_global['passed'] += 1
         else: stats_global['failed'] += 1
         if self._suite_stack:
             current_suite_metrics = self._suite_stack[-1]
             stats_suite = current_suite_metrics['keywords'].setdefault(name,
                 {'count': 0, 'passed': 0, 'failed': 0, 'min_duration': float('inf'), 'max_duration': 0.0, 'total_duration': 0.0})
             stats_suite['count'] += 1
             stats_suite['total_duration'] += duration_secs
             stats_suite['min_duration'] = min(stats_suite['min_duration'], duration_secs)
             stats_suite['max_duration'] = max(stats_suite['max_duration'], duration_secs)
             if is_pass: stats_suite['passed'] += 1
             else: stats_suite['failed'] += 1
             
    def _calculate_keyword_stats(self, keyword_dict):
        for name, stats in keyword_dict.items():
            stats['success_rate'] = (stats['passed'] / stats['count'] * 100) if stats['count'] > 0 else 0
            stats['avg_duration'] = (stats['total_duration'] / stats['count']) if stats['count'] > 0 else 0
            if stats['min_duration'] == float('inf'): stats['min_duration'] = 0.0

    # --- Report Generation --- 

    def generate_metrics_report(self, output_xml, report_dir='metrics'):
        """
        Generate a metrics report from Robot Framework output.xml
        """
        if not os.path.exists(output_xml):
            raise FileNotFoundError(f"Output file not found: {output_xml}")
        
        report_dir = os.path.abspath(report_dir) # Use absolute path for output dir
        os.makedirs(report_dir, exist_ok=True)
        print(f"[DEBUG] Report directory: {report_dir}")
        
        # Reset internal state before parsing (important!)
        self.__init__(self.metrics_template_path)

        # Parse output.xml
        print(f"[DEBUG] Parsing XML: {output_xml}")
        try:
            result = ExecutionResult(output_xml)
            result.visit(self)
        except Exception as parse_e:
             print(f"CRITICAL ERROR: Failed to parse {output_xml}: {parse_e}")
             traceback.print_exc()
             return None # Cannot continue if parsing fails
        print("[DEBUG] XML Parsing complete.")
        
        # Finalize overall duration and keyword stats
        self.metrics['duration'] = time.time() - self.start_time
        self._calculate_keyword_stats(self.metrics['all_keywords'])

        metrics_data = self.metrics 
        
        # Save metrics data as JSON
        metrics_json_path = os.path.join(report_dir, 'metrics.json')
        print(f"[DEBUG] Saving JSON to: {metrics_json_path}")
        try:
            with open(metrics_json_path, 'w') as f:
                json.dump(metrics_data, f, indent=2, default=str)
        except Exception as e:
             print(f"Error saving metrics JSON: {e}") 
             traceback.print_exc()
        
        # Generate HTML report
        report_html_path = os.path.join(report_dir, 'index.html')
        print(f"[DEBUG] Generating HTML report to: {report_html_path}")
        try:
            self._generate_html_report(metrics_data, report_html_path)
            print(f"\n------------------------------------------")
            print(f"Metrics Report Generation Summary")
            print(f"------------------------------------------")
            print(f"Input XML:      {output_xml}")
            print(f"JSON Data:      {metrics_json_path}")
            print(f"HTML Report:    {report_html_path}")
            print(f"Total Tests:    {self.metrics.get('total_tests', 'N/A')}")
            print(f"Overall Status: {self.metrics['suites'][0]['status'] if self.metrics.get('suites') else 'N/A'}")
            print(f"------------------------------------------")
            return report_html_path
        except Exception as e:
             print(f"CRITICAL ERROR generating HTML report: {e}")
             traceback.print_exc()
             return None # Indicate failure

    def _generate_html_report(self, metrics, report_html_path):
        """Generate HTML report from metrics data into the specified file path."""
        template_path = self.metrics_template_path
        print(f"[DEBUG] Using template path: {template_path}")
        
        # Ensure the template exists or create it
        if not os.path.exists(template_path):
            print(f"Template not found at {template_path}. Forcing creation of default template.")
            self._create_default_template() # Force create if missing
            if not os.path.exists(template_path):
                 # This should not happen if _create_default_template worked
                 raise FileNotFoundError(f"CRITICAL: Failed to create template file at {template_path} after attempting creation.")
        
        # Read the template content
        print(f"[DEBUG] Reading template file: {template_path}")
        try:
            with open(template_path, 'r') as f:
                template_content = f.read()
            print(f"[DEBUG] Successfully read template file ({len(template_content)} bytes).")
        except Exception as e:
            print(f"CRITICAL ERROR: Failed to read template file {template_path}: {e}")
            traceback.print_exc()
            raise # Cannot proceed without template content

        # Verify template content (basic check)
        if 'suitesAccordion' not in template_content:
             print("*** WARNING ***: Template content read from {template_path} does not contain expected marker 'suitesAccordion'. It might be outdated.")
             print("*** WARNING ***: Attempting to recreate the template forcefully.")
             try:
                 self._create_default_template() # Force overwrite
                 with open(template_path, 'r') as f_new:
                     template_content = f_new.read()
                 print("[DEBUG] Re-read template after recreation ({len(template_content)} bytes).")
                 if 'suitesAccordion' not in template_content:
                      print("*** CRITICAL ERROR ***: Template still incorrect after recreation. Check file permissions or content of _create_default_template.")
                      # Decide whether to raise an error or proceed with potentially wrong template
                      # raise ValueError("Template content remains invalid after forced recreation.")
             except Exception as e_recr:
                 print(f"CRITICAL ERROR: Failed during forced template recreation: {e_recr}")
                 traceback.print_exc()
                 raise # Stop if recreation fails

        # Replace placeholder
        print("[DEBUG] Preparing metrics JSON string for HTML replacement.")
        try:
             metrics_json_string = json.dumps(metrics, default=str)
        except Exception as json_e:
             print(f"Error converting metrics to JSON string: {json_e}")
             metrics_json_string = "{\"error\": \"Failed to serialize metrics data\"}" # Indicate error in HTML
             
        print(f"[DEBUG] Replacing placeholder in HTML content ({len(template_content)} bytes template, {len(metrics_json_string)} bytes JSON).")
        html_content = template_content.replace('{{METRICS_DATA}}', metrics_json_string)
        
        # Write the final report
        print(f"[DEBUG] Writing final HTML report to: {report_html_path}")
        try:
            with open(report_html_path, 'w') as f:
                f.write(html_content)
            print(f"[DEBUG] Successfully wrote HTML report ({len(html_content)} bytes).")
        except Exception as e:
            print(f"CRITICAL ERROR: Failed to write HTML report file {report_html_path}: {e}")
            traceback.print_exc()
            raise

    def _create_default_template(self):
        """Create/Overwrite the default HTML template with the modern design."""
        template_path = self.metrics_template_path
        template_dir = os.path.dirname(template_path)
        print(f"[DEBUG] Ensuring template directory exists: {template_dir}")
        os.makedirs(template_dir, exist_ok=True)
        
        # Explicitly delete if exists to ensure overwrite
        if os.path.exists(template_path):
             print(f"[DEBUG] Attempting to remove existing template file: {template_path}")
             try:
                 os.remove(template_path)
                 print(f"[DEBUG] Removed existing template file successfully.")
             except OSError as e:
                 # Log warning but proceed, maybe write will succeed anyway
                 print(f"*** WARNING ***: Could not remove existing template file {template_path}: {e}. Attempting overwrite.")

        # The full fancy HTML template content (ensure this is correct)
        # (Content is the same as previous version - omitted for brevity, assume it's correct)
        template_content = '''<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Test Execution Report</title>
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.2/dist/css/bootstrap.min.css" rel="stylesheet">
    <link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/bootstrap-icons@1.10.5/font/bootstrap-icons.css">
    <script src="https://cdn.jsdelivr.net/npm/apexcharts"></script>
    <style>
        :root {
            --bs-primary-rgb: 66, 133, 244; /* Google Blue */
            --bs-success-rgb: 52, 168, 83;  /* Google Green */
            --bs-danger-rgb: 234, 67, 53;   /* Google Red */
            --bs-warning-rgb: 251, 188, 5;  /* Google Yellow */
            --bs-info-rgb: 66, 133, 244; 
            --bs-body-bg: #f8f9fa;
            --bs-card-bg: #ffffff;
            --bs-card-border-color: #dee2e6;
            --bs-accordion-bg: var(--bs-card-bg);
            --bs-accordion-border-color: var(--bs-card-border-color);
            --bs-accordion-button-active-bg: rgba(var(--bs-primary-rgb), 0.1);
            --bs-accordion-button-active-color: var(--bs-primary);
        }
        body {
            font-family: 'Roboto', -apple-system, BlinkMacSystemFont, 'Segoe UI', 'Helvetica Neue', Arial, sans-serif;
            background-color: var(--bs-body-bg);
        }
        .navbar {
            box-shadow: 0 2px 4px rgba(0,0,0,.1);
        }
        .metric-card {
            border: none;
            border-radius: 0.5rem;
            box-shadow: 0 1px 3px rgba(0,0,0,.1);
            transition: transform 0.2s ease, box-shadow 0.2s ease;
        }
        .metric-card:hover {
            transform: translateY(-2px);
            box-shadow: 0 4px 10px rgba(0,0,0,.15);
        }
        .metric-value {
            font-size: 2rem;
            font-weight: 500;
            color: var(--bs-primary);
        }
        .pass-rate .progress-bar { background-color: var(--bs-success); }
        .fail-rate .progress-bar { background-color: var(--bs-danger); }
        
        .status-badge {
            font-size: 0.75rem;
            font-weight: 500;
            padding: 0.3em 0.6em;
            border-radius: 0.25rem;
            text-transform: uppercase;
            vertical-align: middle;
        }
        .bg-status-pass { background-color: rgba(var(--bs-success-rgb), 0.1); color: var(--bs-success); border: 1px solid rgba(var(--bs-success-rgb), 0.3); }
        .bg-status-fail { background-color: rgba(var(--bs-danger-rgb), 0.1); color: var(--bs-danger); border: 1px solid rgba(var(--bs-danger-rgb), 0.3);}
        .bg-status-skip { background-color: rgba(var(--bs-warning-rgb), 0.1); color: var(--bs-warning); border: 1px solid rgba(var(--bs-warning-rgb), 0.3);}
        .bg-status-notrun { background-color: #e9ecef; color: #6c757d; border: 1px solid #ced4da;}

        .accordion-button { font-weight: 500; }
        .accordion-button:not(.collapsed) { box-shadow: none; }
        
        .suite-summary-item { margin-right: 15px; font-size: 0.9rem; }
        .suite-summary-item .icon { margin-right: 5px; }
        .suite-summary-item .bi-check-circle-fill { color: var(--bs-success); }
        .suite-summary-item .bi-x-circle-fill { color: var(--bs-danger); }
        .suite-summary-item .bi-slash-circle-fill { color: var(--bs-warning); }
        .suite-summary-item .bi-hourglass-split { color: var(--bs-primary); }

        .steps-table th { font-weight: 500; background-color: #f1f3f4; font-size: 0.9rem; }
        .steps-table td { font-size: 0.85rem; vertical-align: top; }
        .step-name { font-weight: 500; }
        .step-args { color: #6c757d; font-size: 0.8rem; word-break: break-all; }
        .step-msgs { margin-top: 5px; padding-left: 15px; border-left: 2px solid #e9ecef; font-size: 0.8rem; }
        .step-msg { margin-bottom: 3px; }
        .step-msg-text { color: #495057; }
        .step-msg-ts { color: #adb5bd; font-size: 0.75rem; margin-right: 5px;}
        .step-msg-level-INFO { /* Default */ }
        .step-msg-level-DEBUG { color: #6c757d; }
        .step-msg-level-TRACE { color: #adb5bd; }
        .step-msg-level-WARN { color: var(--bs-warning); }
        .step-msg-level-ERROR { color: var(--bs-danger); font-weight: 500; }
        
        .hidden-steps { display: none; }
        .toggle-steps-btn { cursor: pointer; }
        
        .chart-container {
             background-color: var(--bs-card-bg);
             padding: 1rem;
             border-radius: 0.5rem;
             box-shadow: 0 1px 3px rgba(0,0,0,.1);
        }
        
        /* Fix accordion button icon rotation */
        .accordion-button::after { 
             transition: transform .2s ease-in-out;
             filter: brightness(0.5); /* Make icon darker */
        }
        .accordion-button:not(.collapsed)::after {
             transform: rotate(-180deg);
        }
        
        .tests-table th { font-weight: 500; }

    </style>
</head>
<body>
    <nav class="navbar navbar-expand-lg navbar-light bg-white mb-4">
        <div class="container-fluid">
            <a class="navbar-brand" href="#">
                 <i class="bi bi-robot me-2 text-primary"></i> Test Execution Report
            </a>
             <span class="navbar-text ms-auto">
                 Generated: <span id="generationTime"></span>
             </span>
        </div>
    </nav>

    <div class="container-fluid">
        <!-- Overview Section -->
        <section id="overview" class="mb-4">
            <h4 class="mb-3">Execution Overview</h4>
            <div class="row">
                <div class="col-xl-3 col-md-6 mb-3">
                    <div class="card metric-card h-100">
                        <div class="card-body">
                            <h6 class="card-subtitle mb-2 text-muted">Total Tests</h6>
                            <div class="metric-value" id="totalTests">0</div>
                        </div>
                    </div>
                </div>
                <div class="col-xl-3 col-md-6 mb-3">
                    <div class="card metric-card h-100">
                         <div class="card-body">
                            <h6 class="card-subtitle mb-2 text-muted">Pass Rate</h6>
                            <div class="metric-value mb-2" id="passPercentage">0%</div>
                            <div class="progress pass-rate" style="height: 8px;">
                                <div class="progress-bar" id="passRateBar" role="progressbar" style="width: 0%;" aria-valuenow="0" aria-valuemin="0" aria-valuemax="100"></div>
                            </div>
                        </div>
                    </div>
                </div>
                 <div class="col-xl-3 col-md-6 mb-3">
                    <div class="card metric-card h-100">
                        <div class="card-body">
                            <h6 class="card-subtitle mb-2 text-muted">Total Duration</h6>
                            <div class="metric-value" id="totalDuration">0s</div>
                             <small class="text-muted">Seconds</small>
                        </div>
                    </div>
                </div>
                 <div class="col-xl-3 col-md-6 mb-3">
                    <div class="card metric-card h-100">
                        <div class="card-body">
                            <h6 class="card-subtitle mb-2 text-muted">Tests Status</h6>
                            <div id="testStatusChart" style="min-height: 150px;"></div>
                        </div>
                    </div>
                </div>
            </div>
        </section>
        
        <!-- Test Results Section -->
        <section id="test-results" class="mb-4">
             <h4 class="mb-3">Test Results</h4>
             <div class="accordion" id="suitesAccordion">
                 <!-- Suites will be loaded here by JavaScript -->
             </div>
        </section>
        
         <!-- Other Charts/Info Section -->
        <section id="charts-info" class="mb-4">
             <h4 class="mb-3">Additional Information</h4>
             <div class="row">
                 <div class="col-lg-6 mb-3">
                     <div class="chart-container h-100">
                         <h6>Test Status by Tag</h6>
                         <div id="tagStatusChart" style="min-height: 300px;"></div>
                     </div>
                 </div>
                  <div class="col-lg-6 mb-3">
                     <div class="chart-container h-100">
                          <h6>Test Execution Timeline</h6>
                         <div id="timelineChart" style="min-height: 300px;"></div>
                     </div>
                 </div>
             </div>
        </section>
        
        <!-- System Info (Optional - Can be put in a collapsible section) -->
        <section id="system-info" class="mb-4">
            <div class="accordion">
                 <div class="accordion-item">
                    <h2 class="accordion-header">
                      <button class="accordion-button collapsed" type="button" data-bs-toggle="collapse" data-bs-target="#collapseSystemInfo" aria-expanded="false" aria-controls="collapseSystemInfo">
                        <i class="bi bi-info-circle me-2"></i> System & Environment Information
                      </button>
                    </h2>
                    <div id="collapseSystemInfo" class="accordion-collapse collapse">
                      <div class="accordion-body">
                           <div id="systemInfoDetails" class="row"></div>
                      </div>
                    </div>
                 </div>
            </div>
        </section>

    </div> <!-- /container-fluid -->

    <!-- Hidden template for a suite accordion item -->
    <template id="suite-template">
        <div class="accordion-item mb-2">
            <h2 class="accordion-header" id="suite-heading-{suite_id}">
                <button class="accordion-button collapsed" type="button" data-bs-toggle="collapse" data-bs-target="#suite-collapse-{suite_id}" aria-expanded="false" aria-controls="suite-collapse-{suite_id}">
                    <span class="status-badge me-2" id="suite-badge-{suite_id}">STATUS</span>
                    <span id="suite-name-{suite_id}">Suite Name</span>
                    <div class="ms-auto suite-summary" id="suite-summary-{suite_id}">
                         <!-- Summary badges here -->
                    </div>
                </button>
            </h2>
            <div id="suite-collapse-{suite_id}" class="accordion-collapse collapse" aria-labelledby="suite-heading-{suite_id}">
                <div class="accordion-body">
                    <p class="text-muted small">Setup: <span class="status-badge" id="suite-setup-{suite_id}"></span> | Teardown: <span class="status-badge" id="suite-teardown-{suite_id}"></span></p>
                    <div id="suite-content-{suite_id}">
                         <!-- Nested suites or tests table here -->
                    </div>
                </div>
            </div>
        </div>
    </template>

    <!-- Hidden template for a test row -->
     <template id="test-row-template">
         <tr class="test-row">
            <td><span class="toggle-steps-btn" onclick="toggleSteps('steps-{test_id}')"><i class="bi bi-plus-lg me-2"></i></span><span id="test-name-{test_id}">Test Name</span></td>
            <td><span class="status-badge" id="test-status-{test_id}">STATUS</span></td>
            <td id="test-duration-{test_id}">0.00s</td>
            <td id="test-tags-{test_id}">Tags</td>
        </tr>
        <tr class="hidden-steps" id="steps-{test_id}">
            <td colspan="4">
                <div class="card card-body bg-light border-0 py-2 px-3">
                    <h6>Steps:</h6>
                     <p class="text-danger small" id="test-message-{test_id}"></p>
                     <table class="table table-sm steps-table table-borderless">
                         <thead>
                             <tr>
                                 <th>Step (Keyword)</th>
                                 <th>Arguments</th>
                                 <th>Status</th>
                                 <th>Duration</th>
                             </tr>
                         </thead>
                         <tbody id="steps-tbody-{test_id}">
                             <!-- Steps will be added here -->
                         </tbody>
                     </table>
                 </div>
            </td>
         </tr>
     </template>
     
     <!-- Hidden template for a step row -->
     <template id="step-row-template">
         <tr>
             <td class="step-name">
                  <span class="status-badge me-1" id="step-status-badge-{step_id}"></span>
                  <span id="step-name-{step_id}"></span>
                  <div class="step-msgs" id="step-msgs-{step_id}" style="display: none;"></div>
             </td>
             <td class="step-args" id="step-args-{step_id}"></td>
             <td id="step-status-{step_id}"><span class="status-badge"></span></td>
             <td id="step-duration-{step_id}"></td>
         </tr>
     </template>


    <div id="metrics-data" style="display: none;">{{METRICS_DATA}}</div>

    <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.3.2/dist/js/bootstrap.bundle.min.js"></script>
    <script>
        // --- Data Loading & Initial Setup ---
        let metricsData;
        try {
             metricsData = JSON.parse(document.getElementById('metrics-data').textContent || '{}');
             console.log("Metrics Data Loaded:", metricsData);
        } catch (e) {
             console.error("Failed to parse metrics data:", e);
             metricsData = { suites: [], system_info: {}, tags: {}, test_timeline: [] }; // Default empty data
        }
        
        document.getElementById('generationTime').textContent = metricsData.system_info?.timestamp || new Date().toLocaleString();

        // --- Helper Functions ---
        function formatDuration(seconds) {
             if (seconds === undefined || seconds === null) return '-';
             // Adjust threshold for ms display if needed
             if (seconds < 0.0001) return '< 0.1ms'; // Show very small durations
             if (seconds < 0.001) return `${(seconds * 1000).toFixed(1)}ms`;
             if (seconds < 1) return `${(seconds * 1000).toFixed(0)}ms`;
             return `${seconds.toFixed(2)}s`;
        }

        function getStatusBadgeClass(status) {
            status = status?.toUpperCase();
            if (status === 'PASS') return 'bg-status-pass';
            if (status === 'FAIL') return 'bg-status-fail';
            if (status === 'SKIP') return 'bg-status-skip';
            return 'bg-status-notrun'; // Default for NOT RUN or unknown
        }

        function createIcon(iconClass) {
            const icon = document.createElement('i');
            icon.className = `bi ${iconClass} icon`;
            return icon;
        }
        
        function sanitizeHTML(str) {
             if (typeof str !== 'string') str = String(str); // Ensure input is string
             const temp = document.createElement('div');
             temp.textContent = str;
             return temp.innerHTML;
        }

        // --- Chart Initialization ---
        function initializeCharts() {
            try {
                // Test Status Chart (Donut)
                const statusCounts = [
                    metricsData.passed_tests || 0, 
                    metricsData.failed_tests || 0, 
                    metricsData.skipped_tests || 0
                ];
                const statusChartOptions = {
                    series: statusCounts,
                    chart: { type: 'donut', height: '180px', sparkline: { enabled: true } },
                    labels: ['Passed', 'Failed', 'Skipped'],
                    colors: ['#34a853', '#ea4335', '#fbbc05'], // Google colors
                    legend: { show: false },
                    tooltip: { enabled: true, y: { formatter: (val) => val + ' tests' } },
                     plotOptions: { pie: { donut: { size: '70%' } } }
                };
                const statusChartTarget = document.querySelector("#testStatusChart");
                if (statusChartTarget) {
                    const statusChart = new ApexCharts(statusChartTarget, statusChartOptions);
                    if (statusCounts.some(c => c > 0)) statusChart.render();
                } else { console.warn('Element #testStatusChart not found'); }

                // Tag Status Chart (Bar)
                const tagData = Object.entries(metricsData.tags || {}).map(([tag, data]) => ({
                    tag: tag,
                    passed: data.passed || 0,
                    failed: data.failed || 0,
                    skipped: data.skipped || 0
                }));
                const tagChartOptions = {
                    series: [{ name: 'Passed', data: tagData.map(t => t.passed) }, 
                             { name: 'Failed', data: tagData.map(t => t.failed) }, 
                             { name: 'Skipped', data: tagData.map(t => t.skipped) }],
                    chart: { type: 'bar', height: 300, stacked: true, toolbar: { show: false } },
                    xaxis: { categories: tagData.map(t => t.tag) },
                    colors: ['#34a853', '#ea4335', '#fbbc05'],
                    legend: { position: 'top', horizontalAlign: 'left' },
                    plotOptions: { bar: { horizontal: false } },
                    dataLabels: { enabled: false }
                };
                 const tagChartTarget = document.querySelector("#tagStatusChart");
                 if (tagChartTarget) {
                    const tagChart = new ApexCharts(tagChartTarget, tagChartOptions);
                    if (tagData.length > 0) tagChart.render();
                } else { console.warn('Element #tagStatusChart not found'); }

                // Timeline Chart (Range Bar)
                 const timelineData = (metricsData.test_timeline || []).map(test => ({
                    x: test.name,
                    // Ensure timestamps are valid for Date parsing
                    y: [ new Date(test.start_time || 0).getTime(), new Date(test.end_time || 0).getTime() ],
                    fillColor: test.status === 'PASS' ? '#34a853' : (test.status === 'FAIL' ? '#ea4335' : '#fbbc05')
                }));
                const timelineOptions = {
                    series: [{ data: timelineData }],
                    chart: { height: 300, type: 'rangeBar', toolbar: { show: false } },
                    plotOptions: { bar: { horizontal: true, barHeight: '50%', rangeBarGroupRows: true } },
                    colors: ['#34a853', '#ea4335', '#fbbc05'],
                    xaxis: { type: 'datetime', labels: { datetimeUTC: false, format: 'HH:mm:ss' } },
                    yaxis: { show: true, labels: { minWidth: 100, maxWidth: 300 } },
                    legend: { show: false },
                    tooltip: { 
                         enabled: true, 
                         x: { format: 'dd MMM HH:mm:ss' }, // Show date too
                         y: { formatter: (val, { seriesIndex, dataPointIndex, w }) => {
                              const test = metricsData.test_timeline[dataPointIndex];
                              return `Duration: ${formatDuration(test.duration)}`;
                         }} 
                    }
                };
                 const timelineChartTarget = document.querySelector("#timelineChart");
                 if (timelineChartTarget) {
                    const timelineChart = new ApexCharts(timelineChartTarget, timelineOptions);
                    if (timelineData.length > 0) timelineChart.render();
                } else { console.warn('Element #timelineChart not found'); }
            } catch(chartError) {
                console.error("Error initializing charts:", chartError);
            }
        }

        // --- UI Population ---
        function populateOverview() {
            try {
                const total = metricsData.total_tests || 0;
                const passed = metricsData.passed_tests || 0;
                const passRate = total > 0 ? ((passed / total) * 100).toFixed(1) : 0;
                
                document.getElementById('totalTests').textContent = total;
                document.getElementById('passPercentage').textContent = `${passRate}%`;
                const passRateBar = document.getElementById('passRateBar');
                passRateBar.style.width = `${passRate}%`;
                passRateBar.setAttribute('aria-valuenow', passRate);
                document.getElementById('totalDuration').textContent = formatDuration(metricsData.duration);
            } catch (overviewError) {
                 console.error("Error populating overview:", overviewError);
            }
        }
        
        function populateSystemInfo() {
            try {
                 const sysInfo = metricsData.system_info;
                 const container = document.getElementById('systemInfoDetails');
                 container.innerHTML = ''; // Clear existing
                 if (!sysInfo) return;

                 const infoItems = [
                     { label: 'OS', value: `${sysInfo.os || ''} ${sysInfo.os_release || ''}`, icon: 'bi-pc-display-horizontal' },
                     { label: 'Python', value: sysInfo.python_version, icon: 'bi-filetype-py' },
                     { label: 'Node', value: sysInfo.node, icon: 'bi-hdd-network' },
                     { label: 'CPU', value: `${sysInfo.processor || ''} (${sysInfo.cpu_count} cores)`, icon: 'bi-cpu' },
                     { label: 'Memory', value: `${(sysInfo.memory?.percent || 0)}% Used`, icon: 'bi-memory' },
                     { label: 'Disk', value: `${(sysInfo.disk?.percent || 0)}% Used`, icon: 'bi-device-hdd' },
                     { label: 'Timezone', value: sysInfo.timezone, icon: 'bi-clock' },
                 ];

                 infoItems.forEach(item => {
                     if (item.value) {
                         const col = document.createElement('div');
                         col.className = 'col-md-6 col-lg-4 mb-2';
                         col.innerHTML = `<div class="d-flex align-items-center"><i class="${item.icon} me-2 fs-5 text-primary"></i> <div><strong class="d-block">${item.label}</strong><span class="text-muted">${sanitizeHTML(item.value)}</span></div></div>`;
                         container.appendChild(col);
                     }
                 });
                 
                 // Environment Variables
                 const envVars = sysInfo.env_vars || {};
                 if (Object.keys(envVars).length > 0 && Object.values(envVars).some(v => v)) { // Check if any env var has a value
                      const envCol = document.createElement('div');
                      envCol.className = 'col-12 mt-3';
                      let envHtml = '<h6>Environment Variables:</h6><ul class="list-unstyled small">';
                      for (const [key, value] of Object.entries(envVars)) {
                          if (value) { // Only show vars with values
                              envHtml += `<li><strong>${sanitizeHTML(key)}:</strong> ${sanitizeHTML(value)}</li>`;
                          }
                      }
                      envHtml += '</ul>';
                      envCol.innerHTML = envHtml;
                      container.appendChild(envCol);
                 }
            } catch (sysInfoError) {
                 console.error("Error populating system info:", sysInfoError);
            }
        }

        function buildSuiteSummary(suite) {
            const summaryDiv = document.createElement('div');
            summaryDiv.className = 'ms-auto d-flex';
            const items = [
                 { value: suite.passed, icon: 'bi-check-circle-fill', title: 'Passed'},
                 { value: suite.failed, icon: 'bi-x-circle-fill', title: 'Failed'},
                 { value: suite.skipped, icon: 'bi-slash-circle-fill', title: 'Skipped'},
                 { value: formatDuration(suite.duration), icon: 'bi-hourglass-split', title: 'Duration'}
            ];
            items.forEach(item => {
                 const span = document.createElement('span');
                 span.className = 'suite-summary-item';
                 span.title = item.title;
                 span.innerHTML = `<i class="bi ${item.icon} icon"></i> ${sanitizeHTML(item.value)}`;
                 summaryDiv.appendChild(span);
            });
            return summaryDiv;
        }

        function renderSuites(suites, parentElementId, level = 0) {
             const suitesContainer = document.getElementById(parentElementId);
             if (!suitesContainer) { console.error(`Element #${parentElementId} not found for rendering suites.`); return; }
             
             const suiteTemplate = document.getElementById('suite-template');
             const testRowTemplate = document.getElementById('test-row-template');
             if (!suiteTemplate || !testRowTemplate) { console.error('HTML templates not found!'); return; }

             (suites || []).forEach((suite, index) => {
                try {
                     const suiteId = `${parentElementId}-s${index}`;
                     const suiteNode = document.importNode(suiteTemplate.content, true);
                     
                     // Configure suite accordion item
                     suiteNode.querySelector('.accordion-header').id = `suite-heading-${suiteId}`;
                     const button = suiteNode.querySelector('.accordion-button');
                     button.setAttribute('data-bs-target', `#suite-collapse-${suiteId}`);
                     button.setAttribute('aria-controls', `suite-collapse-${suiteId}`);
                     
                     suiteNode.querySelector('.accordion-collapse').id = `suite-collapse-${suiteId}`;
                     suiteNode.querySelector('.accordion-collapse').setAttribute('aria-labelledby', `suite-heading-${suiteId}`);

                     // Populate suite details
                     const badgeElement = suiteNode.querySelector(`[id='suite-badge-${suite_id}']`); // Use querySelector for flexibility
                     if (badgeElement) {
                         badgeElement.textContent = suite.status;
                         badgeElement.className = `status-badge me-2 ${getStatusBadgeClass(suite.status)}`;
                         badgeElement.id = `suite-badge-${suiteId}`; // Set correct ID
                     }
                     const nameElement = suiteNode.querySelector(`[id='suite-name-${suite_id}']`);
                     if (nameElement) {
                         nameElement.textContent = suite.name;
                         nameElement.id = `suite-name-${suiteId}`;
                     }
                     const summaryContainer = suiteNode.querySelector(`[id='suite-summary-${suite_id}']`);
                     if (summaryContainer) {
                         summaryContainer.appendChild(buildSuiteSummary(suite));
                         summaryContainer.id = `suite-summary-${suiteId}`;
                     }
                     const setupBadge = suiteNode.querySelector(`[id='suite-setup-${suite_id}']`);
                     if (setupBadge) {
                         setupBadge.textContent = suite.setup_status;
                         setupBadge.className = `status-badge ${getStatusBadgeClass(suite.setup_status)}`;
                         setupBadge.id = `suite-setup-${suiteId}`;
                     }
                     const teardownBadge = suiteNode.querySelector(`[id='suite-teardown-${suite_id}']`);
                     if (teardownBadge) {
                         teardownBadge.textContent = suite.teardown_status;
                         teardownBadge.className = `status-badge ${getStatusBadgeClass(suite.teardown_status)}`;
                         teardownBadge.id = `suite-teardown-${suiteId}`;
                     }
                     const contentDiv = suiteNode.querySelector(`[id='suite-content-${suite_id}']`);
                     if (!contentDiv) { console.warn('Suite content div not found'); return; }
                     contentDiv.id = `suite-content-${suiteId}`;

                     // Render nested suites first
                     if (suite.suites && suite.suites.length > 0) {
                          const nestedAccordionId = `nested-accordion-${suiteId}`;
                          const nestedAccordion = document.createElement('div');
                          nestedAccordion.className = 'accordion mt-2';
                          nestedAccordion.id = nestedAccordionId;
                          contentDiv.appendChild(nestedAccordion);
                          renderSuites(suite.suites, nestedAccordionId, level + 1);
                     }

                     // Render tests table
                     if (suite.tests && suite.tests.length > 0) {
                         const testTable = document.createElement('table');
                         testTable.className = 'table table-hover table-sm tests-table mt-2';
                         testTable.innerHTML = `<thead><tr><th>Test Case</th><th>Status</th><th>Duration</th><th>Tags</th></tr></thead><tbody></tbody>`;
                         const tbody = testTable.querySelector('tbody');
                         
                         suite.tests.forEach((test, testIndex) => {
                             const testId = `${suiteId}-t${testIndex}`;
                             // --- Test Row --- 
                             const testRow = document.importNode(testRowTemplate.content.querySelector('.test-row'), true);
                             testRow.querySelector('.toggle-steps-btn').setAttribute('onclick', `toggleSteps('steps-${testId}')`);
                             testRow.querySelector(`[id='test-name-${test_id}']`).textContent = test.name;
                             testRow.querySelector(`[id='test-name-${test_id}']`).id = `test-name-${testId}`; // Set ID
                             
                             const statusBadge = testRow.querySelector(`[id='test-status-${test_id}']`);
                             statusBadge.textContent = test.status;
                             statusBadge.className = `status-badge ${getStatusBadgeClass(test.status)}`;
                             statusBadge.id = `test-status-${testId}`;
                             
                             const durationCell = testRow.querySelector(`[id='test-duration-${test_id}']`);
                             durationCell.textContent = formatDuration(test.duration);
                             durationCell.id = `test-duration-${testId}`;
                             
                             const tagsCell = testRow.querySelector(`[id='test-tags-${test_id}']`);
                             tagsCell.textContent = (test.tags || []).join(', ');
                             tagsCell.id = `test-tags-${testId}`;
                             
                             tbody.appendChild(testRow);

                             // --- Steps Row --- 
                             const stepsRow = document.importNode(testRowTemplate.content.querySelector('.hidden-steps'), true);
                             stepsRow.id = `steps-${testId}`; // Set ID for the steps row itself
                             
                             const stepsTbody = stepsRow.querySelector(`[id='steps-tbody-${test_id}']`);
                             stepsTbody.id = `steps-tbody-${testId}`;
                             
                             const msgElement = stepsRow.querySelector(`[id='test-message-${test_id}']`);
                             msgElement.id = `test-message-${testId}`;
                             if (test.status === 'FAIL' && test.message) {
                                  msgElement.textContent = `Failure: ${sanitizeHTML(test.message)}`;
                             } else {
                                  msgElement.style.display = 'none';
                             }
                             
                             renderSteps(test.steps, stepsTbody, testId);
                             tbody.appendChild(stepsRow);
                         });
                         contentDiv.appendChild(testTable);
                     }
                     
                     suitesContainer.appendChild(suiteNode);
                 } catch (renderSuiteError) {
                      console.error("Error rendering suite:", suite.name, renderSuiteError);
                 }
             });
        }
        
        function renderSteps(steps, tbodyElement, testIdPrefix) {
             tbodyElement.innerHTML = ''; // Clear first
             const stepTemplate = document.getElementById('step-row-template');
             if (!stepTemplate) { console.error('Step row template not found!'); return; }
             
             (steps || []).forEach((step, stepIndex) => {
                 try {
                      const stepId = `${testIdPrefix}-step${stepIndex}`;
                      const stepNode = document.importNode(stepTemplate.content, true);
                      
                      const nameCell = stepNode.querySelector('.step-name');
                      const statusBadge = nameCell.querySelector('.status-badge');
                      statusBadge.id = `step-status-badge-${stepId}`;
                      statusBadge.className = `status-badge me-1 ${getStatusBadgeClass(step.status)}`;
                      
                      const nameSpan = nameCell.querySelector('span:nth-child(2)');
                      nameSpan.id = `step-name-${stepId}`;
                      nameSpan.textContent = step.name || '[Unknown Step]';

                      const argsElement = stepNode.querySelector(`[id='step-args-${step_id}']`);
                      argsElement.textContent = (step.arguments || []).join(', ');
                      argsElement.id = `step-args-${stepId}`;
                      
                      const statusCell = stepNode.querySelector(`[id='step-status-${step_id}']`);
                      const innerStatusBadge = statusCell.querySelector('.status-badge');
                      innerStatusBadge.textContent = step.status;
                      innerStatusBadge.className = `status-badge ${getStatusBadgeClass(step.status)}`;
                      statusCell.id = `step-status-${stepId}`;
                       
                      const durationCell = stepNode.querySelector(`[id='step-duration-${step_id}']`);
                      durationCell.textContent = formatDuration(step.duration);
                      durationCell.id = `step-duration-${stepId}`;
                      
                      // Messages
                      const msgsContainer = nameCell.querySelector('.step-msgs');
                      msgsContainer.id = `step-msgs-${stepId}`;
                      if (step.messages && step.messages.length > 0) {
                           msgsContainer.style.display = 'block';
                           step.messages.forEach(msg => {
                                const msgDiv = document.createElement('div');
                                msgDiv.className = `step-msg step-msg-level-${msg.level || 'INFO'}`;
                                const ts = msg.timestamp?.split(' ')[1] || ''; // Extract time part
                                const tsSpan = `<span class="step-msg-ts">${ts}</span>`;
                                const levelSpan = `<span class="fw-bold">${sanitizeHTML(msg.level || 'INFO')}:</span>`;
                                msgDiv.innerHTML = `${tsSpan} ${levelSpan} <span class="step-msg-text">${sanitizeHTML(msg.text)}</span>`;
                                msgsContainer.appendChild(msgDiv);
                           });
                      }
                      
                      tbodyElement.appendChild(stepNode.querySelector('tr'));
                 } catch (renderStepError) {
                     console.error("Error rendering step:", step, renderStepError);
                 }
             });
        }

        function toggleSteps(stepsRowId) {
            const stepsRow = document.getElementById(stepsRowId);
            const testRow = stepsRow?.previousElementSibling;
            const icon = testRow?.querySelector('.toggle-steps-btn i');
            if (stepsRow && icon) {
                if (stepsRow.style.display === 'none') {
                    stepsRow.style.display = 'table-row';
                     icon.classList.replace('bi-plus-lg', 'bi-dash-lg');
                } else {
                    stepsRow.style.display = 'none';
                     icon.classList.replace('bi-dash-lg', 'bi-plus-lg');
                }
            }
        }


        // --- Initialization ---
        document.addEventListener('DOMContentLoaded', () => {
            console.log("[DEBUG] DOM Loaded. Initializing report UI.");
            populateOverview();
            populateSystemInfo();
            renderSuites(metricsData.suites || [], 'suitesAccordion');
            initializeCharts();
            console.log("[DEBUG] Report UI Initialization complete.");
        });

    </script>
</body>
</html>'''
        
        print(f"[DEBUG] Attempting to write template file: {template_path}")
        try:
            with open(template_path, 'w') as f:
                f.write(template_content)
            print(f"[DEBUG] Successfully created/overwrote template file ({len(template_content)} bytes).")
        except Exception as e:
            print(f"*** CRITICAL ERROR ***: Failed to write template file {template_path}: {e}")
            traceback.print_exc()
            raise # Stop execution if template cannot be written


if __name__ == '__main__':
    import argparse
    
    parser = argparse.ArgumentParser(description='Generate test metrics report')
    parser.add_argument('--input', required=True, help='Path to output.xml file')
    parser.add_argument('--output', default='metrics', help='Output directory for the report')
    
    args = parser.parse_args()
    
    metrics = TestMetrics()
    print(metrics.generate_metrics_report(args.input, args.output)) 