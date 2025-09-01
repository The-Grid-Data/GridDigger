#!/usr/bin/env python3
"""
Boot Filter Test Integration
============================

This script runs the comprehensive filter test on boot/startup to ensure
the filtering system is working correctly before the bot starts serving users.

This should be integrated into the startup sequence to catch filter issues early.
"""

import sys
import os
import logging
import json
from datetime import datetime

# Add project root to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from test_filter_system import FilterSystemTester

# Configure logging for boot testing
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - BOOT_TEST - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class BootFilterTest:
    """Boot-time filter testing with integration hooks"""
    
    def __init__(self):
        self.test_results = None
        self.start_time = datetime.now()
    
    def run_boot_test(self) -> bool:
        """
        Run filter tests suitable for boot time
        Returns True if all critical tests pass, False otherwise
        """
        logger.info("=" * 60)
        logger.info("STARTING BOOT FILTER SYSTEM VALIDATION")
        logger.info("=" * 60)
        
        try:
            # Run quick test mode for boot (faster)
            tester = FilterSystemTester(verbose=False, quick=True)
            self.test_results = tester.run_all_tests()
            
            # Log results
            self._log_boot_results()
            
            # Determine if boot should continue
            critical_failure = self._check_critical_failures()
            
            if critical_failure:
                logger.error("CRITICAL FILTER FAILURES DETECTED - BOOT SHOULD BE ABORTED")
                return False
            
            if self.test_results.failed_tests > 0:
                logger.warning(f"NON-CRITICAL FILTER ISSUES DETECTED ({self.test_results.failed_tests} failures)")
                logger.warning("Boot can continue but issues should be investigated")
            else:
                logger.info("ALL FILTER TESTS PASSED - SYSTEM READY")
            
            return True
            
        except Exception as e:
            logger.error(f"CRITICAL ERROR during boot filter test: {e}")
            return False
    
    def _log_boot_results(self):
        """Log boot test results in a concise format"""
        if not self.test_results:
            return
        
        logger.info(f"Filter Test Results:")
        logger.info(f"  Total Tests: {self.test_results.total_tests}")
        logger.info(f"  Passed: {self.test_results.passed_tests}")
        logger.info(f"  Failed: {self.test_results.failed_tests}")
        logger.info(f"  Success Rate: {(self.test_results.passed_tests/self.test_results.total_tests*100):.1f}%")
        logger.info(f"  Execution Time: {self.test_results.total_time:.2f}s")
        logger.info(f"  Baseline Profile Count: {self.test_results.baseline_total_count:,}")
        
        # Log failed tests
        if self.test_results.failed_tests > 0:
            logger.warning("Failed Tests:")
            for result in self.test_results.results:
                if not result.success:
                    logger.warning(f"  ❌ {result.filter_name} ({result.filter_value}): {result.error_message}")
    
    def _check_critical_failures(self) -> bool:
        """
        Check if there are critical failures that should prevent boot
        Returns True if critical failures exist
        """
        if not self.test_results:
            return True
        
        # Define critical tests that must pass for boot to continue
        critical_tests = [
            "no_filters",  # Must be able to get all profiles
            "profileNameSearch"  # Basic search must work
        ]
        
        critical_failures = []
        for result in self.test_results.results:
            if not result.success and result.filter_name in critical_tests:
                critical_failures.append(result)
        
        # Also check if baseline count is 0 (database connection issue)
        if self.test_results.baseline_total_count == 0:
            logger.error("CRITICAL: Baseline profile count is 0 - database connection issue")
            return True
        
        return len(critical_failures) > 0
    
    def save_boot_test_report(self, filepath: str = "boot_filter_test_report.json"):
        """Save detailed boot test report for debugging"""
        if not self.test_results:
            return
        
        try:
            report = {
                "timestamp": self.start_time.isoformat(),
                "test_summary": {
                    "total_tests": self.test_results.total_tests,
                    "passed_tests": self.test_results.passed_tests,
                    "failed_tests": self.test_results.failed_tests,
                    "success_rate": self.test_results.passed_tests / self.test_results.total_tests * 100,
                    "total_time": self.test_results.total_time,
                    "baseline_count": self.test_results.baseline_total_count
                },
                "failed_tests": [
                    {
                        "filter_name": r.filter_name,
                        "filter_value": str(r.filter_value),
                        "expected_count": r.expected_count,
                        "actual_count": r.actual_count,
                        "execution_time": r.execution_time,
                        "error_message": r.error_message
                    }
                    for r in self.test_results.results if not r.success
                ],
                "all_results": [
                    {
                        "filter_name": r.filter_name,
                        "filter_value": str(r.filter_value),
                        "expected_count": r.expected_count,
                        "actual_count": r.actual_count,
                        "execution_time": r.execution_time,
                        "success": r.success,
                        "error_message": r.error_message
                    }
                    for r in self.test_results.results
                ]
            }
            
            with open(filepath, 'w') as f:
                json.dump(report, f, indent=2)
            
            logger.info(f"Boot test report saved to: {filepath}")
            
        except Exception as e:
            logger.error(f"Failed to save boot test report: {e}")

def main():
    """Main boot test execution"""
    boot_tester = BootFilterTest()
    
    try:
        # Run boot test
        success = boot_tester.run_boot_test()
        
        # Save report for debugging
        boot_tester.save_boot_test_report()
        
        # Exit with appropriate code
        if success:
            logger.info("BOOT FILTER TEST COMPLETED SUCCESSFULLY")
            sys.exit(0)
        else:
            logger.error("BOOT FILTER TEST FAILED - SYSTEM NOT READY")
            sys.exit(1)
            
    except Exception as e:
        logger.error(f"CRITICAL ERROR in boot filter test: {e}")
        sys.exit(2)

# Integration functions for use in other boot scripts
def validate_filters_on_boot() -> bool:
    """
    Simple function to validate filters during boot process
    Returns True if filters are working, False otherwise
    
    Usage in main boot script:
        from boot_test_filters import validate_filters_on_boot
        
        if not validate_filters_on_boot():
            logger.error("Filter validation failed - aborting startup")
            sys.exit(1)
    """
    try:
        boot_tester = BootFilterTest()
        return boot_tester.run_boot_test()
    except Exception as e:
        logger.error(f"Filter validation error: {e}")
        return False

def quick_filter_health_check() -> dict:
    """
    Quick health check for filters - returns status dict
    
    Returns:
        {
            "healthy": bool,
            "total_profiles": int,
            "basic_search_works": bool,
            "error": str or None
        }
    """
    try:
        import api
        
        # Check basic functionality
        total_count = api.get_total_profile_count()
        
        # Test basic search
        data = {"FILTERS": {"profileNameSearch_query": "protocol"}, "inc_search": False}
        search_results = api.get_profiles(data)
        search_works = search_results is not None and len(search_results) >= 0
        
        return {
            "healthy": total_count > 0 and search_works,
            "total_profiles": total_count,
            "basic_search_works": search_works,
            "error": None
        }
        
    except Exception as e:
        return {
            "healthy": False,
            "total_profiles": 0,
            "basic_search_works": False,
            "error": str(e)
        }

if __name__ == "__main__":
    main()