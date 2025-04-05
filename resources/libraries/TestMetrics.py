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
import re
import logging

# Set up logging
logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# --- Determine Absolute Path for Template (relative to this file) ---
_SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
_TEMPLATE_PATH = os.path.join(_SCRIPT_DIR, 'templates', 'report_template.html')
logger.debug(f"Template path determined: {_TEMPLATE_PATH}")


class TestMetrics(ResultVisitor):
    """
    Generates comprehensive test metrics from Robot Framework output.xml using ResultVisitor.
    Includes system info, test stats, keyword usage, timeline, and tag analysis.
    """
    
    ROBOT_LIBRARY_SCOPE = 'GLOBAL'
    
    def __init__(self):
        logger.debug("Initializing TestMetrics instance.")
        self._reset_state()

    def _reset_state(self):
        """Resets the internal state for processing a new result file."""
        self.start_time = time.time()
        self.metrics = { # Initialize structure clearly
                'generation_info': {
                    'version': '1.3.0', # Updated version for template change
                    'timestamp': datetime.now(timezone.utc).isoformat(),
                    'processing_time_sec': 0.0
                },
                'total_tests': 0, 'passed_tests': 0, 'failed_tests': 0, 'skipped_tests': 0,
                'duration': 0.0, 'suites': [], 'tags': {},
                'test_timeline': [], 'critical_failures': [],
                'system_info': {}, # Populated at the end of processing
                'all_keywords': {}
            }
        self._suite_stack = [] 
        self._current_test_metrics = None
        self._keyword_stack = []
        logger.debug("Internal metrics state reset.")
        
    def _get_system_info(self):
        """Gather system information."""
        logger.debug("Gathering system info...")
        try:
            uname = platform.uname()
            mem = psutil.virtual_memory()
            disk = psutil.disk_usage('/')
            tz = time.tzname[0] if time.daylight == 0 else time.tzname[1]
            
            # Get relevant environment variables
            env_vars = {
                var: os.environ.get(var, '') for var in [
                    'PYTHONPATH', 'ROBOT_OPTIONS', 'BROWSER', 'HEADLESS', 
                    'TEST_ENV', 'CI_PIPELINE_ID', 'CI_JOB_ID', 'GITHUB_RUN_ID', 'BUILD_NUMBER'
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
                'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                'timezone': tz,
                'env_vars': {k: v for k, v in env_vars.items() if v} # Filter empty env vars
            }
        except Exception as e:
             logger.error(f"Error gathering system info: {e}", exc_info=True)
             return {'error': str(e)}

    # -- Visitor Methods --
    
    def start_suite(self, suite):
        logger.debug(f"Starting suite: {suite.name}")
        suite_metrics = {
            'name': suite.name,
            'source': str(suite.source) if suite.source else 'N/A',
            'doc': suite.doc,
            'status': '', # Updated at end_suite
            'total': 0, # Updated at end_suite
            'passed': 0, # Updated at end_suite
            'failed': 0, # Updated at end_suite
            'skipped': 0, # Updated at end_suite
            'duration': 0.0, # Updated at end_suite
            'setup_status': suite.setup.status if suite.setup else 'NOT RUN',
            'teardown_status': suite.teardown.status if suite.teardown else 'NOT RUN',
            'keywords': {}, # Keywords specific to this suite
            'tests': [],
            'suites': []
        }
        if not self._suite_stack: self.metrics['suites'].append(suite_metrics)
        else: self._suite_stack[-1]['suites'].append(suite_metrics)
        self._suite_stack.append(suite_metrics)

    def end_suite(self, suite):
        if not self._suite_stack:
             logger.error("Attempted to end suite, but stack is empty.")
             return
             
        current_suite_metrics = self._suite_stack.pop()
        logger.debug(f"Ending suite: {suite.name} - Status: {suite.status}")
        current_suite_metrics['status'] = suite.status
        current_suite_metrics['duration'] = suite.elapsedtime / 1000.0
        stats = suite.statistics # Use Robot's aggregated stats
        current_suite_metrics['total'] = stats.total
        current_suite_metrics['passed'] = stats.passed
        current_suite_metrics['failed'] = stats.failed
        current_suite_metrics['skipped'] = stats.skipped

        # Calculate keyword stats for this suite level
        self._calculate_keyword_stats(current_suite_metrics.get('keywords', {}))

        # If this was the root suite ending
        if not self._suite_stack:
            logger.info("Finalizing global metrics.")
            self.metrics['total_tests'] = stats.total
            self.metrics['passed_tests'] = stats.passed
            self.metrics['failed_tests'] = stats.failed
            self.metrics['skipped_tests'] = stats.skipped
            self.metrics['duration'] = current_suite_metrics['duration'] # Root duration
            self.metrics['system_info'] = self._get_system_info() # Get system info at the very end
            processing_time = time.time() - self.start_time
            self.metrics['generation_info']['processing_time_sec'] = round(processing_time, 3)
            logger.info(f"Total processing time: {processing_time:.3f}s")
            # Global keyword calculation happens in generate_metrics_report now

    def start_test(self, test):
        if not self._suite_stack:
             logger.error(f"Cannot start test '{test.name}' - no active suite.")
             return
             
        logger.debug(f"Starting test: {test.name}")
        self._current_test_metrics = {
            'name': test.name,
            'status': '', # Updated at end_test
            'tags': list(test.tags),
            'duration': 0.0, # Updated at end_test
            'message': test.message or '',
            'start_time': str(test.starttime), # Store as string
            'end_time': str(test.endtime),   # Store as string
            'steps': []
        }
        self._keyword_stack = [] # Reset keyword stack for the new test

    def end_test(self, test):
        if not self._current_test_metrics or not self._suite_stack:
             logger.error(f"Cannot end test '{test.name}' - context missing.")
             return
             
        logger.debug(f"Ending test: {test.name} - Status: {test.status}")
        self._current_test_metrics['status'] = test.status
        self._current_test_metrics['duration'] = test.elapsedtime / 1000.0
        self._current_test_metrics['message'] = test.message or ''
        parent_suite_metrics = self._suite_stack[-1]
        parent_suite_metrics['tests'].append(self._current_test_metrics)
        
        status = test.status
        # Aggregate Tag Stats
        for tag in list(test.tags):
            tag_stats = self.metrics['tags'].setdefault(tag, {'passed': 0, 'failed': 0, 'skipped': 0, 'total': 0})
            tag_stats['total'] += 1
            if status == 'PASS': tag_stats['passed'] += 1
            elif status == 'FAIL': tag_stats['failed'] += 1
            else: tag_stats['skipped'] += 1
            
        # Add to Timeline
        self.metrics['test_timeline'].append({
            'name': test.name,
            'suite': parent_suite_metrics['name'],
            'status': status,
            'start_time': str(test.starttime),
            'end_time': str(test.endtime),
            'duration': test.elapsedtime / 1000.0
        })
        
        # Check for Critical Failures
        if status == 'FAIL' and test.critical == 'yes':
             logger.warning(f"Critical failure detected in test: {test.name}")
             self.metrics['critical_failures'].append({
                  'test_name': test.name,
                  'suite_name': parent_suite_metrics['name'],
                  'message': test.message or '',
                  'timestamp': str(test.endtime)
             })
             
        self._current_test_metrics = None # Clear context
        self._keyword_stack = [] # Clear keyword stack

    def start_keyword(self, keyword):
         # Only track keywords if within a test context
         if not self._current_test_metrics:
              # logger.debug(f"Skipping keyword '{keyword.name}' (type: {keyword.type}) - not inside a test.")
              return
              
         logger.debug(f"Starting step/keyword: {keyword.kwname or keyword.type} (Type: {keyword.type})")
         keyword_metrics = {
                'name': keyword.kwname or f"({keyword.type})", # Use kwname for keywords, type for control
                'type': keyword.type,
                'lib': keyword.libname if hasattr(keyword, 'libname') else 'N/A',
                'status': '', # Updated at end_keyword
                'duration': 0.0, # Updated at end_keyword
                'messages': [],
                'arguments': list(keyword.args),
                'assign': list(keyword.assign)
            }
            
         # Append to current test steps or parent keyword's children
         if not self._keyword_stack:
             self._current_test_metrics['steps'].append(keyword_metrics)
         else:
             parent_keyword_metrics = self._keyword_stack[-1]
             parent_keyword_metrics.setdefault('children', []).append(keyword_metrics)
             
         self._keyword_stack.append(keyword_metrics)

    def end_keyword(self, keyword):
         if not self._keyword_stack:
             # logger.debug(f"Skipping end_keyword '{keyword.name}' (type: {keyword.type}) - stack empty (likely outside test).")
             return
             
         current_keyword_metrics = self._keyword_stack.pop()
         logger.debug(f"Ending step/keyword: {current_keyword_metrics['name']} - Status: {keyword.status}")
         current_keyword_metrics['status'] = keyword.status
         current_keyword_metrics['duration'] = keyword.elapsedtime / 1000.0
         
         # Aggregate keyword stats (only for actual keywords, not control structures)
         if keyword.type in ('KEYWORD', 'SETUP', 'TEARDOWN'):
             kw_name = current_keyword_metrics['name']
             # Use library name if available and not a built-in like 'BuiltIn'
             if current_keyword_metrics['lib'] not in ('N/A', '', 'BuiltIn'):
                  kw_name = f"{current_keyword_metrics['lib']}.{kw_name}" 
             self._aggregate_keyword_stats(kw_name, current_keyword_metrics['duration'], keyword.status)

    # log_message is deprecated, use message
    # def log_message(self, msg): self.message(msg)

    def message(self, msg):
        # Add message to the currently executing keyword
        if self._keyword_stack:
            logger.debug(f"Adding message to step '{self._keyword_stack[-1]['name']}': [{msg.level}] {msg.message[:100]}...")
            self._keyword_stack[-1]['messages'].append({
                'level': msg.level,
                'timestamp': str(msg.timestamp),
                'text': msg.message,
                'html': msg.html
            })
        # else: Message outside a keyword context, maybe log it separately? 
        #     logger.debug(f"Message outside keyword context: [{msg.level}] {msg.message}")
            
    def close(self):
        logger.debug("ResultVisitor closing.")
        # Final calculations if needed after all visits are done
        pass

    def _aggregate_keyword_stats(self, name, duration_secs, status):
         """Aggregates stats for a specific keyword globally and for the current suite."""
         if not name: return
         is_pass = status == 'PASS'
         logger.debug(f"Aggregating stats for keyword: '{name}', Duration: {duration_secs:.3f}, Status: {status}")
         
         # Global Stats
         stats_global = self.metrics['all_keywords'].setdefault(name, 
             {'count': 0, 'passed': 0, 'failed': 0, 'min_duration': float('inf'), 'max_duration': 0.0, 'total_duration': 0.0})
         stats_global['count'] += 1
         stats_global['total_duration'] += duration_secs
         stats_global['min_duration'] = min(stats_global['min_duration'], duration_secs)
         stats_global['max_duration'] = max(stats_global['max_duration'], duration_secs)
         if is_pass: stats_global['passed'] += 1
         else: stats_global['failed'] += 1
         
         # Current Suite Stats
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
         else:
              logger.warning(f"Cannot aggregate suite stats for keyword '{name}' - no active suite.")
             
    def _calculate_keyword_stats(self, keyword_dict):
        """Calculates avg duration and success rate for a dictionary of keywords."""
        logger.debug(f"Calculating final stats for {len(keyword_dict)} keywords.")
        for name, stats in keyword_dict.items():
            count = stats['count']
            stats['success_rate'] = round((stats['passed'] / count * 100), 2) if count > 0 else 0
            stats['avg_duration'] = round((stats['total_duration'] / count), 3) if count > 0 else 0.0
            if stats['min_duration'] == float('inf'): stats['min_duration'] = 0.0 # Handle case where keyword never ran?
            # Round durations for final display
            stats['min_duration'] = round(stats['min_duration'], 3)
            stats['max_duration'] = round(stats['max_duration'], 3)
            stats['total_duration'] = round(stats['total_duration'], 3)

    # --- Report Generation --- 

    def generate_metrics_report(self, output_xml, report_dir='metrics'):
        """
        Orchestrates parsing the XML and generating JSON and HTML reports.
        """
        logger.info(f"--- Starting Metrics Report Generation ({datetime.now()}) ---")
        logger.info(f"Input XML: {output_xml}")
        logger.info(f"Output Directory: {report_dir}")
        
        # Validate input path
        if not os.path.exists(output_xml):
            logger.error(f"CRITICAL ERROR: Input XML file not found: {output_xml}")
            return None
        
        # Prepare output directory
        report_dir = os.path.abspath(report_dir)
        try:
            os.makedirs(report_dir, exist_ok=True)
            logger.debug(f"Report directory ensured: {report_dir}")
        except OSError as e_mkdir:
             logger.error(f"CRITICAL ERROR: Failed to create report directory {report_dir}: {e_mkdir}", exc_info=True)
             return None
        
        # --- Reset state and Parse XML using visitor --- 
        self._reset_state() # CRUCIAL: Ensure clean state before parsing
        logger.debug(f"Starting XML Parsing: {output_xml}")
        try:
            result = ExecutionResult(output_xml)
            result.visit(self) # Populates self.metrics via visitor methods
        except Exception as parse_e:
             logger.error(f"CRITICAL ERROR: Failed to parse {output_xml}: {parse_e}", exc_info=True)
             return None
        logger.debug("XML Parsing finished successfully.")
        
        # --- Finalize Metrics --- 
        if not self.metrics or not self.metrics.get('suites'):
             logger.error("CRITICAL ERROR: Metrics data appears empty after parsing. Visitor logic might be flawed.")
             return None
             
        # Calculate final global keyword stats AFTER all visits are done
        self._calculate_keyword_stats(self.metrics.get('all_keywords', {}))
        logger.debug(f"Metrics finalized. Overall duration: {self.metrics['duration']:.3f}s")

        # --- Save JSON Report --- 
        metrics_json_path = os.path.join(report_dir, 'metrics.json')
        logger.debug(f"Attempting to save JSON to: {metrics_json_path}")
        try:
            with open(metrics_json_path, 'w', encoding='utf-8') as f:
                json.dump(self.metrics, f, indent=2)
            logger.debug("Successfully saved JSON data.")
        except Exception as e:
             # Log error but continue to HTML generation if possible
             logger.error(f"ERROR: Failed to save metrics JSON: {e}", exc_info=True)
        
        # --- Generate HTML Report --- 
        report_html_path = os.path.join(report_dir, 'index.html')
        logger.debug(f"Attempting to generate HTML report to: {report_html_path}")
        try:
            self._generate_html_report(report_html_path) # Pass only the output path
            
            # --- Final Summary Output --- 
            logger.info(f"------------------------------------------")
            logger.info(f"  Metrics Report Generation Complete")
            logger.info(f"------------------------------------------")
            logger.info(f"  Input XML:      {os.path.relpath(output_xml)}")
            logger.info(f"  JSON Data:      {os.path.relpath(metrics_json_path)}")
            logger.info(f"  HTML Report:    {os.path.relpath(report_html_path)}")
            logger.info(f"  Total Tests:    {self.metrics.get('total_tests', 'N/A')}")
            # Status of the root suite
            overall_status = self.metrics.get('suites', [{}])[0].get('status', 'N/A') 
            logger.info(f"  Overall Status: {overall_status}")
            logger.info(f"------------------------------------------")
            return report_html_path # Return path on success
            
        except Exception as e:
             # Log the error and return None to indicate failure
             logger.error(f"CRITICAL ERROR: Failed during HTML report generation: {e}", exc_info=True)
             return None

    # --- NEW: Generate HTML from External Template --- 
    def _generate_html_report(self, report_html_path):
        """Generate HTML report from self.metrics into the specified file path using the external template."""
        template_path = _TEMPLATE_PATH # Use the path defined at the top
        logger.debug(f"Using template path for HTML generation: {template_path}")
        
        # Step 1: Read the template content
        logger.debug(f"Reading template file content from: {template_path}")
        try:
            with open(template_path, 'r', encoding='utf-8') as f:
                template_content = f.read()
            logger.debug(f"Successfully read template file ({len(template_content)} bytes).")
        except FileNotFoundError:
             logger.error(f"CRITICAL ERROR: HTML template file not found at {template_path}! Cannot generate report.")
             raise # Re-raise the exception to stop the process
        except Exception as e:
            logger.error(f"CRITICAL ERROR: Failed to read template file {template_path}: {e}", exc_info=True)
            raise # Re-raise

        # Step 2: Prepare JSON data for injection
        logger.debug(f"Preparing metrics JSON string (approx {len(str(self.metrics))} chars) for HTML replacement.")
        try:
             # Use compact JSON for injection, handle potential non-serializable data gracefully
             metrics_json_string = json.dumps(self.metrics, default=str, separators=(',', ':')) 
        except Exception as json_e:
             logger.error(f"ERROR: Failed to serialize metrics data to JSON string: {json_e}", exc_info=True)
             # Create a JSON object indicating the error for embedding
             error_data = {'error': f"Failed to serialize metrics data: {json_e}"}
             metrics_json_string = json.dumps(error_data) 
             
        # Step 3: Replace placeholder
        placeholder = '{{METRICS_DATA}}'
        logger.debug(f"Replacing '{placeholder}' placeholder in HTML content.")
        if placeholder not in template_content:
             # Log an error but try to proceed, the JS will likely fail
             logger.error(f"CRITICAL ERROR: Placeholder '{placeholder}' not found in template file {template_path}. Report will be incomplete.")
             html_content = template_content + f"\n<!-- ERROR: Placeholder {placeholder} not found! -->\n<script>console.error('Template placeholder {placeholder} missing!');</script>" 
        else:
            html_content = template_content.replace(placeholder, metrics_json_string)
            logger.debug(f"Placeholder '{placeholder}' replaced successfully.")
        
        # Step 4: Write the final report
        logger.debug(f"Writing final HTML report to: {report_html_path}")
        try:
            with open(report_html_path, 'w', encoding='utf-8') as f:
                f.write(html_content)
            logger.debug(f"Successfully wrote HTML report ({len(html_content)} bytes).")
        except Exception as e:
            logger.error(f"CRITICAL ERROR: Failed to write final HTML report file {report_html_path}: {e}", exc_info=True)
            raise # Re-raise
            
    # --- REMOVED OLD TEMPLATE METHODS --- 
    # def _create_or_verify_template(self): ... (REMOVED)
    # def _create_default_template(self): ... (REMOVED)

# --- Main execution block (for testing or direct use) ---
if __name__ == '__main__':
    import argparse
    import sys
    
    parser = argparse.ArgumentParser(description='Generate test metrics report from output.xml')
    parser.add_argument('input_xml', help='Path to Robot Framework output.xml file')
    parser.add_argument('-o', '--output_dir', default='metrics_report', 
                        help='Directory to save metrics.json and index.html (default: metrics_report)')
    parser.add_argument('-v', '--verbose', action='store_true', help='Enable debug logging')
    
    args = parser.parse_args()
    
    # Adjust logging level based on verbosity flag
    if args.verbose:
         log_level = logging.DEBUG
    else:
         log_level = logging.INFO
    logging.getLogger().setLevel(log_level) 
    # Reconfigure root logger level if needed (optional, depends on setup)
    # for handler in logging.root.handlers[:]:
    #    logging.root.removeHandler(handler)
    # logging.basicConfig(level=log_level, format='%(asctime)s - %(levelname)s - %(message)s')
    
    logger.debug("Verbose logging enabled." if args.verbose else "Standard logging level.")

    logger.info(f"Processing input file: {args.input_xml}")
    logger.info(f"Report output directory: {args.output_dir}")
    
    # Instantiate and run the report generation
    metrics_processor = TestMetrics()
    report_file = metrics_processor.generate_metrics_report(args.input_xml, args.output_dir)
    
    # Exit with appropriate status code
    if report_file:
         logger.info(f"Successfully generated report: {report_file}")
         sys.exit(0)
    else:
         logger.error("Report generation failed.")
         sys.exit(1) 