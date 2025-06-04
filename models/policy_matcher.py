import os
import json
import pandas as pd
import numpy as np
from sklearn.preprocessing import StandardScaler
from pathlib import Path
from .medical_evaluator import MedicalEvaluator

class PolicyMatcher:
    """
    Matches client information with available insurance policies
    to find the best fits based on eligibility and client needs.
    """
    
    def __init__(self, data_path=None):
        """Initialize the policy matcher with insurance company data."""
        self.data_path = data_path or os.path.join(os.path.dirname(__file__), '../data')
        self.companies = []
        self.policies = {}
        self.eligibility_criteria = {}
        
        # Initialize medical evaluator
        self.medical_evaluator = MedicalEvaluator(self.data_path)
        
        # Load insurance company data
        self._load_data()
    
    def _load_data(self):
        """Load insurance policy data from files."""
        data_dir = Path(self.data_path)
        
        # Create data directory if it doesn't exist
        if not data_dir.exists():
            data_dir.mkdir(parents=True)
            self._create_sample_data()
        
        # Load companies
        companies_file = data_dir / 'companies.json'
        if companies_file.exists():
            with open(companies_file, 'r', encoding='utf-8') as f:
                self.companies = json.load(f)
        
        print(f"Loaded {len(self.companies)} companies from companies.json")
        
        # Keep track of companies with issues
        companies_with_issues = []
        
        # Load policies and criteria for each company
        for company in self.companies:
            company_id = company["id"]
            company_has_issues = False
            
            # Load policies - try multiple potential file patterns
            policies = []
            policy_files = [
                data_dir / f'{company_id}_policies.json',
                data_dir / f'{company_id}policies.json',
                data_dir / f'{company_id}-policies.json'
            ]
            
            policy_file_found = False
            for policy_file in policy_files:
                if policy_file.exists():
                    policy_file_found = True
                    try:
                        with open(policy_file, 'r', encoding='utf-8') as f:
                            file_content = f.read().strip()
                            if not file_content or file_content == "[]" or file_content == "{}":
                                print(f"Warning: Empty policy file for {company['name']} ({policy_file})")
                                company_has_issues = True
                                continue
                                
                            policies = json.loads(file_content)
                            if isinstance(policies, list) and len(policies) > 0:
                                self.policies[company_id] = policies
                                print(f"Loaded {len(policies)} policies for {company['name']}")
                                break
                            else:
                                print(f"Warning: No valid policies in {policy_file}")
                                company_has_issues = True
                    except json.JSONDecodeError:
                        print(f"Error: Invalid JSON in {policy_file}")
                        company_has_issues = True
                    except Exception as e:
                        print(f"Error reading {policy_file}: {e}")
                        company_has_issues = True
            
            if not policy_file_found:
                print(f"Warning: No policy file found for {company['name']}")
                company_has_issues = True
            
            # Load eligibility criteria - check all possible naming conventions
            criteria = {}
            criteria_files = [
                data_dir / f'{company_id}_criteria.json',
                data_dir / f'{company_id}_eligibility.json',
                data_dir / f'{company_id}-criteria.json',
                data_dir / f'{company_id}-eligibility.json',
                data_dir / f'{company_id}criteria.json',
                data_dir / f'{company_id}eligibility.json'
            ]
            
            criteria_file_found = False
            for criteria_file in criteria_files:
                if criteria_file.exists():
                    criteria_file_found = True
                    try:
                        with open(criteria_file, 'r', encoding='utf-8') as f:
                            file_content = f.read().strip()
                            if not file_content or file_content == "[]" or file_content == "{}":
                                print(f"Warning: Empty criteria file for {company['name']} ({criteria_file})")
                                continue
                                
                            criteria_data = json.loads(file_content)
                            if criteria_data:
                                criteria = criteria_data
                                print(f"Loaded criteria from {criteria_file}")
                                break
                            else:
                                print(f"Warning: No valid criteria in {criteria_file}")
                    except json.JSONDecodeError:
                        print(f"Error: Invalid JSON in {criteria_file}")
                    except Exception as e:
                        print(f"Error reading {criteria_file}: {e}")
            
            if not criteria_file_found:
                print(f"Warning: No eligibility criteria file found for {company['name']}")
                company_has_issues = True
            
            # If we found criteria, add them to our dictionary
            if criteria:
                self.eligibility_criteria[company_id] = criteria
            else:
                # Create a default criteria that allows everyone
                print(f"Creating default eligibility criteria for {company['name']}")
                default_criteria = {}
                
                # If we have policies, create default criteria for each policy
                if company_id in self.policies:
                    for policy in self.policies[company_id]:
                        policy_id = policy["id"]
                        default_criteria[policy_id] = {
                            "age_min": 18,
                            "age_max": 85,
                            "income_min": 0,
                            "health_conditions_max": 100,  # Allow many health conditions
                            "smoker_eligible": True
                        }
                    
                    self.eligibility_criteria[company_id] = default_criteria
                    print(f"Created default criteria for {len(default_criteria)} policies from {company['name']}")
                else:
                    company_has_issues = True
            
            if company_has_issues:
                companies_with_issues.append(company["name"])
        
        # Print summary
        print(f"Successfully loaded {len(self.policies)} company policy sets and {len(self.eligibility_criteria)} eligibility criteria sets")
        
        if companies_with_issues:
            print(f"WARNING: {len(companies_with_issues)} companies had issues loading data: {', '.join(companies_with_issues)}")
    
    def _create_sample_data(self):
        """Create sample data for demonstration purposes."""
        data_dir = Path(self.data_path)
        
        # Sample insurance companies
        companies = [
            {"id": "global_life", "name": "Global Life Insurance", "rating": 4.5},
            {"id": "secure_health", "name": "Secure Health Insurance", "rating": 4.2},
            {"id": "family_first", "name": "Family First Insurance", "rating": 4.7}
        ]
        
        # Write companies data
        with open(data_dir / 'companies.json', 'w', encoding='utf-8') as f:
            json.dump(companies, f, indent=2)
        
        self.companies = companies
        
        # Create sample policies for each company
        for company in companies:
            company_id = company["id"]
            
            # Sample policies
            if company_id == "global_life":
                policies = [
                    {
                        "id": "gl_term10",
                        "name": "Term Life 10",
                        "type": "term_life",
                        "term_years": 10,
                        "coverage_min": 50000,
                        "coverage_max": 1000000,
                        "premium_factor": 1.2,
                        "features": ["Convertible", "Renewable"]
                    },
                    {
                        "id": "gl_term20",
                        "name": "Term Life 20",
                        "type": "term_life",
                        "term_years": 20,
                        "coverage_min": 100000,
                        "coverage_max": 2000000,
                        "premium_factor": 1.5,
                        "features": ["Convertible", "Renewable", "Living Benefits"]
                    },
                    {
                        "id": "gl_whole",
                        "name": "Whole Life",
                        "type": "whole_life",
                        "coverage_min": 250000,
                        "coverage_max": 5000000,
                        "premium_factor": 2.8,
                        "features": ["Cash Value", "Fixed Premiums", "Dividend Eligible"]
                    }
                ]
            elif company_id == "secure_health":
                policies = [
                    {
                        "id": "sh_term15",
                        "name": "Term Life 15",
                        "type": "term_life",
                        "term_years": 15,
                        "coverage_min": 75000,
                        "coverage_max": 1500000,
                        "premium_factor": 1.3,
                        "features": ["Convertible", "Critical Illness Rider"]
                    },
                    {
                        "id": "sh_universal",
                        "name": "Universal Life",
                        "type": "universal_life",
                        "coverage_min": 100000,
                        "coverage_max": 3000000,
                        "premium_factor": 2.4,
                        "features": ["Flexible Premiums", "Cash Value", "Death Benefit Options"]
                    }
                ]
            else:  # family_first
                policies = [
                    {
                        "id": "ff_term30",
                        "name": "Term Life 30",
                        "type": "term_life",
                        "term_years": 30,
                        "coverage_min": 100000,
                        "coverage_max": 3000000,
                        "premium_factor": 1.7,
                        "features": ["Convertible", "Return of Premium Option"]
                    },
                    {
                        "id": "ff_whole_plus",
                        "name": "Whole Life Plus",
                        "type": "whole_life",
                        "coverage_min": 200000,
                        "coverage_max": 10000000,
                        "premium_factor": 3.0,
                        "features": ["Cash Value", "Fixed Premiums", "Accelerated Death Benefit", "Long-term Care Rider"]
                    }
                ]
            
            # Write policies data
            with open(data_dir / f'{company_id}_policies.json', 'w', encoding='utf-8') as f:
                json.dump(policies, f, indent=2)
            
            self.policies[company_id] = policies
            
            # Sample eligibility criteria
            if company_id == "global_life":
                criteria = {
                    "gl_term10": {
                        "age_min": 18,
                        "age_max": 65,
                        "income_min": 30000,
                        "health_conditions_max": 2,
                        "smoker_eligible": True,
                        "smoker_premium_factor": 1.5
                    },
                    "gl_term20": {
                        "age_min": 18,
                        "age_max": 60,
                        "income_min": 40000,
                        "health_conditions_max": 1,
                        "smoker_eligible": True,
                        "smoker_premium_factor": 1.8
                    },
                    "gl_whole": {
                        "age_min": 20,
                        "age_max": 65,
                        "income_min": 75000,
                        "health_conditions_max": 0,
                        "smoker_eligible": False
                    }
                }
            elif company_id == "secure_health":
                criteria = {
                    "sh_term15": {
                        "age_min": 18,
                        "age_max": 60,
                        "income_min": 35000,
                        "health_conditions_max": 2,
                        "smoker_eligible": True,
                        "smoker_premium_factor": 1.6
                    },
                    "sh_universal": {
                        "age_min": 25,
                        "age_max": 70,
                        "income_min": 60000,
                        "health_conditions_max": 1,
                        "smoker_eligible": True,
                        "smoker_premium_factor": 2.0
                    }
                }
            else:  # family_first
                criteria = {
                    "ff_term30": {
                        "age_min": 18,
                        "age_max": 50,
                        "income_min": 50000,
                        "health_conditions_max": 1,
                        "smoker_eligible": True,
                        "smoker_premium_factor": 1.9
                    },
                    "ff_whole_plus": {
                        "age_min": 30,
                        "age_max": 75,
                        "income_min": 100000,
                        "health_conditions_max": 1,
                        "smoker_eligible": True,
                        "smoker_premium_factor": 2.2
                    }
                }
            
            # Write eligibility criteria data
            with open(data_dir / f'{company_id}_criteria.json', 'w', encoding='utf-8') as f:
                json.dump(criteria, f, indent=2)
            
            self.eligibility_criteria[company_id] = criteria
    
    def find_best_match(self, client_data):
        """
        Find the best policy matches for a client based on their data.
        
        Args:
            client_data (dict): Client information including age, income, health, etc.
            
        Returns:
            list: Ranked list of policy recommendations with match scores
        """
        # Initialize results
        results = []
        
        # Track companies and policies processed
        companies_processed = 0
        policies_processed = 0
        policies_eligible = 0
        
        # Check if we need to filter by specific policy types
        policy_types_filter = None
        if 'policy_types' in client_data:
            policy_types_filter = client_data['policy_types']
        elif 'coverage_type' in client_data:
            policy_types_filter = [client_data['coverage_type']]
        
        # Get coverage range from client data
        client_min_coverage = client_data.get('coverage_min', 0)
        client_max_coverage = client_data.get('coverage_max', float('inf'))
        
        # Check eligibility for each policy across all companies
        for company in self.companies:
            company_id = company["id"]
            company_name = company["name"]
            
            # Skip companies with no policies
            if company_id not in self.policies:
                print(f"Skipping {company_name} - no policies available")
                continue
            
            companies_processed += 1
            company_policies = self.policies.get(company_id, [])
            company_criteria = self.eligibility_criteria.get(company_id, {})
            
            # Evaluate medical conditions against company underwriting guidelines
            medical_evaluation = self.medical_evaluator.evaluate_medical_conditions(client_data, company_id)
            
            # Skip this company if client is medically ineligible for all policies
            if not medical_evaluation["eligible"] and medical_evaluation.get("rate_class") == "Decline":
                print(f"Skipping {company_name} - client medically ineligible for all policies")
                continue
            
            for policy in company_policies:
                policies_processed += 1
                policy_id = policy["id"]
                policy_type = policy.get("type")
                
                # Skip if this policy type is not in the requested types
                if policy_types_filter and policy_type not in policy_types_filter:
                    print(f"Skipping {company_name} policy {policy['name']} - type {policy_type} not in requested types {policy_types_filter}")
                    continue
                
                # Skip if policy doesn't meet coverage requirements
                if client_min_coverage > 0 and policy["coverage_max"] < client_min_coverage:
                    # Policy's maximum coverage is less than client's minimum requirement
                    print(f"Skipping {company_name} policy {policy['name']} - max coverage ${policy['coverage_max']} is less than client min ${client_min_coverage}")
                    continue
                
                if client_max_coverage < float('inf') and policy["coverage_min"] > client_max_coverage:
                    # Policy's minimum coverage is more than client's maximum requirement
                    print(f"Skipping {company_name} policy {policy['name']} - min coverage ${policy['coverage_min']} is greater than client max ${client_max_coverage}")
                    continue
                
                # Get criteria for this policy
                criteria = company_criteria.get(policy_id, {})
                
                # Check eligibility - even if no specific criteria found, assume eligible
                if not criteria or self._is_eligible(client_data, criteria):
                    # Check medical eligibility for this specific policy
                    policy_medical_eval = self._check_policy_specific_medical(policy_id, medical_evaluation)
                    if not policy_medical_eval["eligible"]:
                        continue
                    
                    # Calculate match score (adjusting for medical conditions)
                    match_score = self._calculate_match_score(client_data, policy, criteria)
                    
                    # Apply medical risk factor to match score
                    match_score = match_score * (1.0 / policy_medical_eval["risk_factor"])
                    
                    # Add to results
                    result = {
                        "company_name": company_name,
                        "policy_name": policy["name"],
                        "policy_type": policy["type"],
                        "match_score": match_score,
                        "coverage_range": f"${policy['coverage_min']:,} - ${policy['coverage_max']:,}",
                        "features": policy.get("features", []),
                        "medical_notes": policy_medical_eval.get("notes", [])
                    }
                    
                    # Add medical notes to result
                    if "notes" not in result:
                        result["notes"] = []
                    result["notes"].extend(policy_medical_eval.get("notes", []))
                    
                    results.append(result)
                    policies_eligible += 1
        
        # Sort by match score (descending)
        results.sort(key=lambda x: x["match_score"], reverse=True)
        
        print(f"Processed {companies_processed} companies, {policies_processed} policies, found {policies_eligible} eligible policies")
        
        return results
    
    def _calculate_match_score(self, client_data, policy, criteria):
        """Calculate how well a policy matches client needs and preferences."""
        score = 0.0
        
        # Coverage range match
        policy_min = policy["coverage_min"]
        policy_max = policy["coverage_max"]
        
        client_min = client_data.get("coverage_min", 0)
        client_max = client_data.get("coverage_max", 0)
        
        # If client provided a coverage range
        if client_min > 0 and client_max > 0:
            # Perfect match: policy range completely contains client's desired range
            if policy_min <= client_min and policy_max >= client_max:
                score += 30.0
            # Partial match: policy range overlaps with client's desired range
            elif (policy_min <= client_max and policy_max >= client_min):
                # Calculate overlap percentage
                overlap_start = max(policy_min, client_min)
                overlap_end = min(policy_max, client_max)
                overlap_size = overlap_end - overlap_start
                
                client_range_size = client_max - client_min
                overlap_percentage = overlap_size / client_range_size
                
                # Score based on overlap percentage
                score += 30.0 * overlap_percentage
            # No overlap
            else:
                score += 0.0
        # Fallback to old single coverage amount logic if no range provided
        elif "coverage_amount" in client_data:
            desired_coverage = client_data.get("coverage_amount", 0)
            if policy["coverage_min"] <= desired_coverage <= policy["coverage_max"]:
                score += 30.0
            elif desired_coverage < policy["coverage_min"]:
                # Coverage minimum is higher than desired
                ratio = desired_coverage / policy["coverage_min"]
                score += 30.0 * ratio
            elif desired_coverage > policy["coverage_max"]:
                # Coverage maximum is lower than desired
                ratio = policy["coverage_max"] / desired_coverage
                score += 30.0 * ratio
        # Default if no coverage info provided
        else:
            # Assume medium coverage
            score += 15.0
        
        # Policy type match - revised to handle policy_types array
        if "policy_types" in client_data:
            policy_types = client_data["policy_types"]
            if policy["type"] in policy_types:
                # If it's one of multiple selected types
                if len(policy_types) == 1:
                    score += 40.0  # Full points for exact match
                else:
                    score += 40.0 / len(policy_types)  # Partial points based on number of options
        elif "coverage_type" in client_data:
            if client_data["coverage_type"] == policy["type"]:
                score += 40.0
            elif client_data["coverage_type"] == "any":
                score += 20.0
        else:
            # No preference specified
            score += 20.0
        
        # Age-appropriate term length (if applicable)
        if "term_years" in policy and policy["term_years"] is not None and "age" in client_data:
            age = client_data["age"]
            term_years = policy["term_years"]
            
            # If term would exceed age 80, reduce score
            if age + term_years > 80:
                score -= 10.0
        
        # Feature match bonus
        desired_features = client_data.get("desired_features", [])
        policy_features = policy.get("features", [])
        if desired_features:
            matching_features = [f for f in desired_features if f in policy_features]
            feature_score = 30.0 * (len(matching_features) / max(len(desired_features), 1))
            score += feature_score
        
        return min(100.0, max(0.0, score))
    
    def _is_eligible(self, client_data, criteria):
        """Check if client is eligible for a policy based on criteria."""
        # If no criteria provided, consider eligible
        if not criteria:
            return True
        
        # Handle age criteria - different files might use different field names
        age = client_data.get("age")
        if age is not None:
            age_min = criteria.get("age_min", criteria.get("min_age", 0))
            age_max = criteria.get("age_max", criteria.get("max_age", 100))
            
            if age < age_min or age > age_max:
                # print(f"Rejected due to age: {age} not in range {age_min}-{age_max}")
                return False
        
        # Handle income criteria if present
        income = client_data.get("income")
        if income is not None and "income_min" in criteria:
            if income < criteria.get("income_min", 0):
                # print(f"Rejected due to income: {income} < {criteria.get('income_min')}")
                return False
        
        # Handle health conditions
        health_conditions = client_data.get("health_conditions", [])
        medical_conditions = client_data.get("medical_conditions", [])
        
        # If we have medical_conditions but not health_conditions, extract the types
        if not health_conditions and medical_conditions:
            health_conditions = [condition.get("type") for condition in medical_conditions if condition.get("type")]
        
        # If we have a maximum number of conditions limit
        if "health_conditions_max" in criteria:
            max_conditions = criteria.get("health_conditions_max", 0)
            # Only reject if max is reasonable (not 0 for all conditions)
            if max_conditions > 0 and len(health_conditions) > max_conditions:
                # print(f"Rejected due to too many health conditions: {len(health_conditions)} > {criteria.get('health_conditions_max')}")
                return False
        
        # Handle specific health condition exclusions if present
        excluded_conditions = criteria.get("excluded_conditions", [])
        for condition in health_conditions:
            if condition in excluded_conditions:
                # print(f"Rejected due to excluded condition: {condition}")
                return False
        
        # Handle smoker status - check multiple field names
        is_smoker = False
        if client_data.get("smoking_status") == "smoker":
            is_smoker = True
        elif client_data.get("tobacco_status") in ["smoker", "former-smoker"]:
            is_smoker = True
        
        # Check if smokers are allowed
        smoker_eligible = criteria.get("smoker_eligible", criteria.get("tobacco_eligible", True))
        if is_smoker and not smoker_eligible:
            # print(f"Rejected due to smoker status")
            return False
        
        # Handle BMI restrictions if present
        if "min_bmi" in criteria and "max_bmi" in criteria and "bmi" in client_data:
            bmi = float(client_data["bmi"])
            if bmi < criteria["min_bmi"] or bmi > criteria["max_bmi"]:
                # print(f"Rejected due to BMI: {bmi} not in range {criteria['min_bmi']}-{criteria['max_bmi']}")
                return False
        
        # All criteria passed
        return True
    
    def _check_policy_specific_medical(self, policy_id, medical_evaluation):
        """Check medical eligibility for a specific policy."""
        # Default to the company-level evaluation
        policy_eval = dict(medical_evaluation)
        
        # If medical evaluation is too strict, make more lenient for specific policy types
        # For example, final expense policies might accept more medical conditions
        if "rate_class" in policy_eval and policy_eval["rate_class"] == "Decline":
            # If this is a final expense policy, they're generally more lenient
            if policy_id.lower().startswith("fe_") or "final" in policy_id.lower() or "expense" in policy_id.lower():
                policy_eval["rate_class"] = "Modified"
                policy_eval["eligible"] = True
                policy_eval["risk_factor"] = 1.5
                policy_eval["notes"].append("Final expense policy available despite medical conditions")
        
        # For guaranteed issue policies, always mark as eligible
        if policy_id.lower().startswith("gi_") or "guaranteed" in policy_id.lower():
            policy_eval["eligible"] = True
            policy_eval["risk_factor"] = 2.0
            policy_eval["notes"].append("Guaranteed issue policy available regardless of medical history")
        
        return policy_eval 