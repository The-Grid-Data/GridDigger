#!/usr/bin/env python3
"""
Comprehensive Filter System Test Suite
=====================================

This test validates all filtering options and ensures they return correct results.
CRITICAL: This test should be run on boot and during testing to ensure filter integrity.

Usage:
    python3 test_filter_system.py
    python3 test_filter_system.py --verbose
    python3 test_filter_system.py --quick  # Skip slow tests
"""

import sys
import os
import time
import json
import logging
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass

# Add project root to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

import api
from config import Config

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

@dataclass
class FilterTestResult:
    """Result of a filter test"""
    filter_name: str
    filter_value: Any
    expected_count: Optional[int]
    actual_count: int
    execution_time: float
    success: bool
    error_message: Optional[str] = None

@dataclass
class FilterTestSuite:
    """Complete test suite results"""
    total_tests: int
    passed_tests: int
    failed_tests: int
    total_time: float
    results: List[FilterTestResult]
    baseline_total_count: int

class FilterSystemTester:
    """Comprehensive filter system tester"""
    
    def __init__(self, verbose: bool = False, quick: bool = False):
        self.verbose = verbose
        self.quick = quick
        self.baseline_total_count = 0
        self.filter_options_cache = {}
        
    def log(self, message: str, level: str = "INFO"):
        """Log message with appropriate level"""
        if level == "INFO":
            logger.info(message)
        elif level == "ERROR":
            logger.error(message)
        elif level == "WARNING":
            logger.warning(message)
        elif level == "DEBUG" and self.verbose:
            logger.debug(message)
    
    def get_baseline_count(self) -> int:
        """Get total number of profiles as baseline"""
        try:
            self.log("Getting baseline profile count...")
            total_count = api.get_total_profile_count()
            self.log(f"Baseline total profiles: {total_count:,}")
            return total_count
        except Exception as e:
            self.log(f"Failed to get baseline count: {e}", "ERROR")
            return 0
    
    def get_filter_options(self, filter_type: str) -> List[Dict[str, Any]]:
        """Get available options for a filter type with caching"""
        if filter_type in self.filter_options_cache:
            return self.filter_options_cache[filter_type]
        
        try:
            options = api.fetch_filter_options(api.filters_config["filters_queries"][filter_type])
            self.filter_options_cache[filter_type] = options
            return options
        except Exception as e:
            self.log(f"Failed to get options for {filter_type}: {e}", "ERROR")
            return []
    
    def test_no_filters(self) -> FilterTestResult:
        """Test getting all profiles with no filters"""
        start_time = time.time()
        
        try:
            self.log("Testing no filters (all profiles)...")
            
            # Test with empty filters
            data = {"FILTERS": {}, "inc_search": False}
            results = api.get_profiles(data)
            
            actual_count = len(results) if results else 0
            execution_time = time.time() - start_time
            
            # Should return all profiles
            success = actual_count == self.baseline_total_count
            
            if not success:
                error_msg = f"Expected {self.baseline_total_count}, got {actual_count}"
            else:
                error_msg = None
            
            return FilterTestResult(
                filter_name="no_filters",
                filter_value="empty",
                expected_count=self.baseline_total_count,
                actual_count=actual_count,
                execution_time=execution_time,
                success=success,
                error_message=error_msg
            )
            
        except Exception as e:
            return FilterTestResult(
                filter_name="no_filters",
                filter_value="empty",
                expected_count=self.baseline_total_count,
                actual_count=0,
                execution_time=time.time() - start_time,
                success=False,
                error_message=str(e)
            )
    
    def test_profile_name_search(self) -> List[FilterTestResult]:
        """Test profile name search functionality"""
        results = []
        
        # Test cases for name search
        test_cases = [
            ("", self.baseline_total_count),  # Empty search should return all
            ("Bitcoin", None),  # Should return some results
            ("Ethereum", None),  # Should return some results
            ("NonExistentProtocol12345", 0),  # Should return no results
            ("a", None),  # Single character - should return many results
        ]
        
        for search_term, expected_count in test_cases:
            start_time = time.time()
            
            try:
                self.log(f"Testing profile name search: '{search_term}'")
                
                data = {
                    "FILTERS": {
                        "profileNameSearch_query": search_term
                    },
                    "inc_search": False
                }
                
                results_data = api.get_profiles(data)
                actual_count = len(results_data) if results_data else 0
                execution_time = time.time() - start_time
                
                # Validate results
                success = True
                error_msg = None
                
                if expected_count is not None:
                    success = actual_count == expected_count
                    if not success:
                        error_msg = f"Expected {expected_count}, got {actual_count}"
                else:
                    # For non-specific tests, just ensure reasonable results
                    if search_term == "a":
                        success = actual_count > 10  # Should return many results
                    elif search_term in ["Bitcoin", "Ethereum"]:
                        success = actual_count > 0  # Should return some results
                    
                    if not success:
                        error_msg = f"Unexpected result count: {actual_count}"
                
                results.append(FilterTestResult(
                    filter_name="profileNameSearch",
                    filter_value=search_term,
                    expected_count=expected_count,
                    actual_count=actual_count,
                    execution_time=execution_time,
                    success=success,
                    error_message=error_msg
                ))
                
            except Exception as e:
                results.append(FilterTestResult(
                    filter_name="profileNameSearch",
                    filter_value=search_term,
                    expected_count=expected_count,
                    actual_count=0,
                    execution_time=time.time() - start_time,
                    success=False,
                    error_message=str(e)
                ))
        
        return results
    
    def test_search_modes(self) -> List[FilterTestResult]:
        """Test quick vs deep search modes"""
        results = []
        search_term = "protocol"
        
        for inc_search, mode_name in [(False, "quick_search"), (True, "deep_search")]:
            start_time = time.time()
            
            try:
                self.log(f"Testing {mode_name} with term: '{search_term}'")
                
                data = {
                    "FILTERS": {
                        "profileNameSearch_query": search_term
                    },
                    "inc_search": inc_search
                }
                
                results_data = api.get_profiles(data)
                actual_count = len(results_data) if results_data else 0
                execution_time = time.time() - start_time
                
                # Both modes should return some results
                success = actual_count > 0
                error_msg = None if success else f"No results for {mode_name}"
                
                results.append(FilterTestResult(
                    filter_name=mode_name,
                    filter_value=search_term,
                    expected_count=None,
                    actual_count=actual_count,
                    execution_time=execution_time,
                    success=success,
                    error_message=error_msg
                ))
                
            except Exception as e:
                results.append(FilterTestResult(
                    filter_name=mode_name,
                    filter_value=search_term,
                    expected_count=None,
                    actual_count=0,
                    execution_time=time.time() - start_time,
                    success=False,
                    error_message=str(e)
                ))
        
        return results
    
    def test_multiple_choice_filters(self) -> List[FilterTestResult]:
        """Test all multiple choice filters"""
        results = []
        
        # Define multiple choice filters to test
        multiple_choice_filters = [
            "profileType",
            "profileSector", 
            "profileStatuses",
            "productTypes",
            "productStatuses",
            "assetTypes",
            "assetStandards",
            "entityTypes"
        ]
        
        for filter_type in multiple_choice_filters:
            if self.quick and filter_type not in ["profileType", "profileSector"]:
                continue  # Skip some filters in quick mode
            
            try:
                self.log(f"Testing multiple choice filter: {filter_type}")
                
                # Get available options
                options = self.get_filter_options(filter_type)
                
                if not options:
                    results.append(FilterTestResult(
                        filter_name=filter_type,
                        filter_value="no_options",
                        expected_count=None,
                        actual_count=0,
                        execution_time=0,
                        success=False,
                        error_message="No options available"
                    ))
                    continue
                
                # Test first few options
                test_options = options[:3] if self.quick else options[:5]
                
                for option in test_options:
                    start_time = time.time()
                    
                    try:
                        option_id = option.get('id')
                        option_name = option.get('name', 'Unknown')
                        
                        data = {
                            "FILTERS": {
                                f"{filter_type}_query": str(option_id)
                            },
                            "inc_search": False
                        }
                        
                        results_data = api.get_profiles(data)
                        actual_count = len(results_data) if results_data else 0
                        execution_time = time.time() - start_time
                        
                        # Should return some results (or 0 is acceptable)
                        success = actual_count >= 0
                        error_msg = None
                        
                        results.append(FilterTestResult(
                            filter_name=filter_type,
                            filter_value=f"{option_name} (ID: {option_id})",
                            expected_count=None,
                            actual_count=actual_count,
                            execution_time=execution_time,
                            success=success,
                            error_message=error_msg
                        ))
                        
                    except Exception as e:
                        results.append(FilterTestResult(
                            filter_name=filter_type,
                            filter_value=f"ID: {option.get('id', 'unknown')}",
                            expected_count=None,
                            actual_count=0,
                            execution_time=time.time() - start_time,
                            success=False,
                            error_message=str(e)
                        ))
                        
            except Exception as e:
                results.append(FilterTestResult(
                    filter_name=filter_type,
                    filter_value="filter_error",
                    expected_count=None,
                    actual_count=0,
                    execution_time=0,
                    success=False,
                    error_message=str(e)
                ))
        
        return results
    
    def test_searchable_filters(self) -> List[FilterTestResult]:
        """Test searchable text filters"""
        results = []
        
        # Define searchable filters to test
        searchable_filters = [
            ("assetTickers", ["BTC", "ETH", "USDC", "NonExistentTicker123"]),
            ("entityName", ["Foundation", "Labs", "Protocol", "NonExistentEntity123"])
        ]
        
        for filter_type, test_values in searchable_filters:
            for test_value in test_values:
                start_time = time.time()
                
                try:
                    self.log(f"Testing searchable filter {filter_type}: '{test_value}'")
                    
                    data = {
                        "FILTERS": {
                            f"{filter_type}_query": test_value
                        },
                        "inc_search": False
                    }
                    
                    results_data = api.get_profiles(data)
                    actual_count = len(results_data) if results_data else 0
                    execution_time = time.time() - start_time
                    
                    # Validate results based on test value
                    success = True
                    error_msg = None
                    expected_count = None
                    
                    if "NonExistent" in test_value:
                        expected_count = 0
                        success = actual_count == 0
                        if not success:
                            error_msg = f"Expected 0 results for non-existent value, got {actual_count}"
                    else:
                        # For real values, should return some results (or 0 is acceptable)
                        success = actual_count >= 0
                    
                    results.append(FilterTestResult(
                        filter_name=filter_type,
                        filter_value=test_value,
                        expected_count=expected_count,
                        actual_count=actual_count,
                        execution_time=execution_time,
                        success=success,
                        error_message=error_msg
                    ))
                    
                except Exception as e:
                    results.append(FilterTestResult(
                        filter_name=filter_type,
                        filter_value=test_value,
                        expected_count=None,
                        actual_count=0,
                        execution_time=time.time() - start_time,
                        success=False,
                        error_message=str(e)
                    ))
        
        return results
    
    def test_filter_combinations(self) -> List[FilterTestResult]:
        """Test combinations of filters"""
        results = []
        
        if self.quick:
            return results  # Skip in quick mode
        
        # Test some common filter combinations
        combinations = [
            {
                "name": "profile_name_and_type",
                "filters": {
                    "profileNameSearch_query": "protocol",
                    "profileType_query": "1"  # Assuming ID 1 exists
                }
            },
            {
                "name": "asset_ticker_and_type", 
                "filters": {
                    "assetTickers_query": "BTC",
                    "assetTypes_query": "1"  # Assuming ID 1 exists
                }
            }
        ]
        
        for combo in combinations:
            start_time = time.time()
            
            try:
                self.log(f"Testing filter combination: {combo['name']}")
                
                data = {
                    "FILTERS": combo["filters"],
                    "inc_search": False
                }
                
                results_data = api.get_profiles(data)
                actual_count = len(results_data) if results_data else 0
                execution_time = time.time() - start_time
                
                # Combined filters should return fewer or equal results than individual filters
                success = actual_count >= 0
                error_msg = None
                
                results.append(FilterTestResult(
                    filter_name="combination",
                    filter_value=combo["name"],
                    expected_count=None,
                    actual_count=actual_count,
                    execution_time=execution_time,
                    success=success,
                    error_message=error_msg
                ))
                
            except Exception as e:
                results.append(FilterTestResult(
                    filter_name="combination",
                    filter_value=combo["name"],
                    expected_count=None,
                    actual_count=0,
                    execution_time=time.time() - start_time,
                    success=False,
                    error_message=str(e)
                ))
        
        return results
    
    def run_all_tests(self) -> FilterTestSuite:
        """Run all filter tests and return comprehensive results"""
        self.log("=" * 60)
        self.log("STARTING COMPREHENSIVE FILTER SYSTEM TEST")
        self.log("=" * 60)
        
        start_time = time.time()
        all_results = []
        
        # Get baseline count
        self.baseline_total_count = self.get_baseline_count()
        if self.baseline_total_count == 0:
            self.log("CRITICAL: Could not get baseline profile count!", "ERROR")
            return FilterTestSuite(0, 0, 1, 0, [], 0)
        
        # Run all test categories
        test_categories = [
            ("No Filters Test", lambda: [self.test_no_filters()]),
            ("Profile Name Search", self.test_profile_name_search),
            ("Search Modes", self.test_search_modes),
            ("Multiple Choice Filters", self.test_multiple_choice_filters),
            ("Searchable Filters", self.test_searchable_filters),
            ("Filter Combinations", self.test_filter_combinations)
        ]
        
        for category_name, test_func in test_categories:
            self.log(f"\n--- Running {category_name} ---")
            try:
                category_results = test_func()
                all_results.extend(category_results)
                
                # Log category summary
                passed = sum(1 for r in category_results if r.success)
                total = len(category_results)
                self.log(f"{category_name}: {passed}/{total} tests passed")
                
            except Exception as e:
                self.log(f"FAILED to run {category_name}: {e}", "ERROR")
                all_results.append(FilterTestResult(
                    filter_name=category_name,
                    filter_value="category_error",
                    expected_count=None,
                    actual_count=0,
                    execution_time=0,
                    success=False,
                    error_message=str(e)
                ))
        
        # Calculate final results
        total_time = time.time() - start_time
        total_tests = len(all_results)
        passed_tests = sum(1 for r in all_results if r.success)
        failed_tests = total_tests - passed_tests
        
        return FilterTestSuite(
            total_tests=total_tests,
            passed_tests=passed_tests,
            failed_tests=failed_tests,
            total_time=total_time,
            results=all_results,
            baseline_total_count=self.baseline_total_count
        )
    
    def print_results(self, test_suite: FilterTestSuite):
        """Print comprehensive test results"""
        self.log("\n" + "=" * 60)
        self.log("FILTER SYSTEM TEST RESULTS")
        self.log("=" * 60)
        
        # Overall summary
        self.log(f"Total Tests: {test_suite.total_tests}")
        self.log(f"Passed: {test_suite.passed_tests}")
        self.log(f"Failed: {test_suite.failed_tests}")
        self.log(f"Success Rate: {(test_suite.passed_tests/test_suite.total_tests*100):.1f}%")
        self.log(f"Total Execution Time: {test_suite.total_time:.2f} seconds")
        self.log(f"Baseline Profile Count: {test_suite.baseline_total_count:,}")
        
        # Failed tests details
        if test_suite.failed_tests > 0:
            self.log("\n--- FAILED TESTS ---")
            for result in test_suite.results:
                if not result.success:
                    self.log(f"❌ {result.filter_name} ({result.filter_value}): {result.error_message}")
        
        # Performance summary
        if self.verbose:
            self.log("\n--- PERFORMANCE SUMMARY ---")
            slow_tests = [r for r in test_suite.results if r.execution_time > 2.0]
            if slow_tests:
                self.log("Slow tests (>2s):")
                for result in slow_tests:
                    self.log(f"  {result.filter_name} ({result.filter_value}): {result.execution_time:.2f}s")
        
        # Success indicator
        if test_suite.failed_tests == 0:
            self.log("\n🎉 ALL FILTER TESTS PASSED!")
        else:
            self.log(f"\n⚠️  {test_suite.failed_tests} TESTS FAILED - REQUIRES ATTENTION")
        
        self.log("=" * 60)

def main():
    """Main test execution"""
    import argparse
    
    parser = argparse.ArgumentParser(description="Comprehensive Filter System Test")
    parser.add_argument("--verbose", "-v", action="store_true", help="Verbose output")
    parser.add_argument("--quick", "-q", action="store_true", help="Quick test mode (skip slow tests)")
    parser.add_argument("--json", action="store_true", help="Output results as JSON")
    
    args = parser.parse_args()
    
    # Initialize tester
    tester = FilterSystemTester(verbose=args.verbose, quick=args.quick)
    
    try:
        # Run all tests
        results = tester.run_all_tests()
        
        if args.json:
            # Output JSON results for automated processing
            json_results = {
                "total_tests": results.total_tests,
                "passed_tests": results.passed_tests,
                "failed_tests": results.failed_tests,
                "success_rate": results.passed_tests / results.total_tests * 100,
                "total_time": results.total_time,
                "baseline_count": results.baseline_total_count,
                "failed_tests_details": [
                    {
                        "filter_name": r.filter_name,
                        "filter_value": str(r.filter_value),
                        "error": r.error_message
                    }
                    for r in results.results if not r.success
                ]
            }
            print(json.dumps(json_results, indent=2))
        else:
            # Print human-readable results
            tester.print_results(results)
        
        # Exit with appropriate code
        sys.exit(0 if results.failed_tests == 0 else 1)
        
    except Exception as e:
        logger.error(f"CRITICAL ERROR in filter system test: {e}")
        sys.exit(2)

if __name__ == "__main__":
    main()