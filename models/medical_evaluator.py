import os
import json
import re
from datetime import datetime
from pathlib import Path

class MedicalEvaluator:
    """
    Advanced medical condition evaluator that implements sophisticated rules
    for evaluating medical conditions against company underwriting guidelines.
    """
    
    def __init__(self, data_path=None):
        """Initialize the medical evaluator with underwriting data."""
        self.data_path = data_path or os.path.join(os.path.dirname(__file__), '../data')
        self.underwriting_rules = {}
        self.condition_mappings = {
            # Map user-provided condition names to standard names used in underwriting rules
            "high-blood-pressure": ["hypertension", "high blood pressure", "htn"],
            "diabetes": ["diabetes", "diabetes mellitus", "type 2 diabetes", "type ii diabetes"],
            "heart-disease": ["heart disease", "coronary artery disease", "cad", "heart attack", "myocardial infarction", "mi"],
            "cancer": ["cancer", "malignancy", "malignant neoplasm", "carcinoma"],
            "stroke": ["stroke", "cva", "cerebrovascular accident", "tia", "transient ischemic attack"],
            "copd": ["copd", "chronic obstructive pulmonary disease", "emphysema", "chronic bronchitis"],
            "asthma": ["asthma", "reactive airway disease"],
            "kidney-disease": ["kidney disease", "chronic kidney disease", "ckd", "renal insufficiency", "renal failure"],
            "liver-disease": ["liver disease", "hepatitis", "cirrhosis", "fatty liver"],
            "depression": ["depression", "major depressive disorder", "mdd"],
            "anxiety": ["anxiety", "anxiety disorder", "panic disorder", "gad"],
        }
        
        # Load underwriting data
        self._load_underwriting_data()
    
    def _load_underwriting_data(self):
        """Load underwriting rules from data files."""
        data_dir = Path(self.data_path)
        
        # Find all underwriting files
        underwriting_files = list(data_dir.glob("*_underwriting.json"))
        
        for file_path in underwriting_files:
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    company_id = data.get("company_id")
                    if company_id and "underwriting_criteria" in data:
                        self.underwriting_rules[company_id] = data["underwriting_criteria"]
                        print(f"Loaded underwriting rules for {company_id}")
            except (json.JSONDecodeError, IOError) as e:
                print(f"Error loading underwriting file {file_path}: {e}")
    
    def evaluate_medical_conditions(self, client_data, company_id):
        """
        Evaluate medical conditions against company underwriting rules.
        
        Args:
            client_data (dict): Client information including medical conditions
            company_id (str): Company ID to match against underwriting rules
            
        Returns:
            dict: Evaluation results including eligibility and risk assessment
        """
        if company_id not in self.underwriting_rules:
            return {"eligible": True, "risk_factor": 1.0, "notes": ["No specific underwriting rules found for this company"]}
        
        underwriting = self.underwriting_rules[company_id]
        medical_conditions = client_data.get("medical_conditions", [])
        
        # If no medical conditions provided, return default eligibility
        if not medical_conditions:
            return {"eligible": True, "risk_factor": 1.0, "notes": []}
        
        # Extract condition information
        conditions_info = self._extract_condition_details(medical_conditions)
        
        # Check conditions against underwriting rules
        return self._evaluate_against_rules(conditions_info, underwriting, company_id)
    
    def _extract_condition_details(self, medical_conditions):
        """
        Extract detailed information from medical condition records.
        
        Args:
            medical_conditions (list): List of medical condition records
            
        Returns:
            list: Enhanced condition information with extracted details
        """
        enhanced_conditions = []
        
        for condition in medical_conditions:
            # Basic information
            condition_type = condition.get("type", "")
            details = condition.get("details", "").lower()
            
            # Default values
            status = "current"  # Assume condition is current unless specified
            months_since = 0
            severity = "moderate"  # Default to moderate severity
            
            # Extract status information (current vs. past)
            if "cured" in details or "resolved" in details or "past" in details or "history of" in details:
                status = "past"
            elif "current" in details or "ongoing" in details or "active" in details:
                status = "current"
                
            # Extract time information
            time_patterns = [
                r"diagnosed (\d+) years? ago",
                r"diagnosed (\d+) months? ago",
                r"since (\d{4})",
                r"diagnosed in (\d{4})",
                r"diagnosed (\d+)\/(\d+)\/(\d+)",
                r"diagnosed (\d+)-(\d+)-(\d+)"
            ]
            
            for pattern in time_patterns:
                matches = re.search(pattern, details)
                if matches:
                    if "years ago" in pattern:
                        years = int(matches.group(1))
                        months_since = years * 12
                    elif "months ago" in pattern:
                        months_since = int(matches.group(1))
                    elif "since" in pattern or "in" in pattern:
                        year = int(matches.group(1))
                        current_year = datetime.now().year
                        years_since = current_year - year
                        months_since = years_since * 12
                    else:  # Date format
                        # Simple approximation based on current date
                        # In a real system, we'd parse the exact date and calculate precisely
                        months_since = 24  # Assuming 2 years as a default if date format is detected
                    break
                    
            # Extract severity information
            if any(term in details for term in ["mild", "minor", "slight", "minimal"]):
                severity = "mild"
            elif any(term in details for term in ["severe", "serious", "advanced", "critical"]):
                severity = "severe"
            elif any(term in details for term in ["moderate", "medium"]):
                severity = "moderate"
                
            # Add enhanced condition to the list
            enhanced_conditions.append({
                "type": condition_type,
                "original_details": details,
                "status": status,
                "months_since_diagnosis": months_since,
                "severity": severity
            })
            
        return enhanced_conditions
    
    def _evaluate_against_rules(self, conditions_info, underwriting, company_id):
        """
        Evaluate conditions against company underwriting rules.
        
        Args:
            conditions_info (list): Enhanced condition information
            underwriting (dict): Company underwriting rules
            company_id (str): Company ID
            
        Returns:
            dict: Evaluation results
        """
        # Default response
        result = {
            "eligible": True,
            "risk_factor": 1.0,
            "rate_class": "Standard",
            "notes": []
        }
        
        # Check if we have medical condition rules
        if "medical_conditions" not in underwriting:
            return result
            
        # Get condition rules
        condition_rules = underwriting.get("medical_conditions", {}).get("conditions", [])
        if not condition_rules:
            return result
            
        # Track if any condition makes the client ineligible
        ineligible = False
        
        # Track the highest risk factor
        max_risk_factor = 1.0
        
        # Default rate class order (from best to worst)
        rate_class_order = ["Preferred", "Standard", "Modified", "Decline"]
        
        # Start with best rate class
        best_rate_class = "Preferred"
        
        # Evaluate each condition
        for condition_info in conditions_info:
            condition_type = condition_info["type"]
            status = condition_info["status"]
            months_since = condition_info["months_since_diagnosis"]
            severity = condition_info["severity"]
            
            # Try to match condition against underwriting rules
            condition_rule = self._find_matching_condition(condition_type, condition_rules)
            
            if condition_rule:
                # Parse and apply the guideline
                guideline = condition_rule.get("guideline", "")
                rate_classes = condition_rule.get("rate_classes", [])
                
                # Determine rate class based on guideline and condition details
                rate_class = self._determine_rate_class(guideline, status, months_since, severity, rate_classes)
                
                # Update best rate class (worst one wins)
                if rate_class_order.index(rate_class) > rate_class_order.index(best_rate_class):
                    best_rate_class = rate_class
                
                # Check if this makes the client ineligible
                if rate_class == "Decline":
                    ineligible = True
                    result["notes"].append(f"{condition_type}: Declined based on {company_id} underwriting guidelines")
                else:
                    # Calculate risk factor based on rate class
                    risk_factor = self._calculate_risk_factor(rate_class)
                    max_risk_factor = max(max_risk_factor, risk_factor)
                    
                    if rate_class != "Preferred":
                        result["notes"].append(f"{condition_type}: {rate_class} rating based on {company_id} guidelines")
            else:
                # If we can't find a specific rule, use a conservative approach
                risk_factor = 1.2  # Slight increase in risk
                max_risk_factor = max(max_risk_factor, risk_factor)
                result["notes"].append(f"{condition_type}: No specific guideline found, using standard evaluation")
        
        # Update result
        result["eligible"] = not ineligible
        result["risk_factor"] = max_risk_factor
        result["rate_class"] = best_rate_class if not ineligible else "Decline"
        
        return result
    
    def _find_matching_condition(self, condition_type, condition_rules):
        """Find matching condition in underwriting rules."""
        # Try to find direct match
        for rule in condition_rules:
            if rule.get("condition", "").lower() == condition_type.lower():
                return rule
                
        # Try alternate names using mappings
        standard_names = self.condition_mappings.get(condition_type, [])
        for std_name in standard_names:
            for rule in condition_rules:
                if rule.get("condition", "").lower() == std_name.lower():
                    return rule
                    
        # If no match found, return None
        return None
    
    def _determine_rate_class(self, guideline, status, months_since, severity, rate_classes):
        """Determine rate class based on guideline text and condition details."""
        guideline = guideline.lower()
        
        # Check for automatic decline conditions
        if "decline" in guideline and "any" in guideline and "history" in guideline:
            return "Decline"
            
        # Check time-based rules
        time_patterns = [
            (r"(\d+)[–\-](\d+)\s*months", "months"),  # For ranges like "0-12 months"
            (r"(\d+)[+≥]\s*months", "months_minimum"),  # For minimums like "25+ months"
            (r"(\d+)[–\-](\d+)\s*years", "years"),  # For ranges like "0-2 years"
            (r"(\d+)[+≥]\s*years", "years_minimum")  # For minimums like "2+ years"
        ]
        
        # Track best matching rate class
        if "Decline" in rate_classes and status == "current" and any(x in guideline for x in ["current", "active"]):
            return "Decline"
            
        best_class = None
        
        # Past conditions generally get better ratings
        if status == "past" and "cured" in guideline and months_since > 24:
            if "Preferred" in rate_classes:
                best_class = "Preferred"
            elif "Standard" in rate_classes:
                best_class = "Standard"
        
        # Check time-based rules
        for pattern, time_type in time_patterns:
            matches = re.finditer(pattern, guideline)
            for match in matches:
                if time_type == "months":
                    min_months = int(match.group(1))
                    max_months = int(match.group(2))
                    
                    # Check if the condition's time falls in this range
                    if min_months <= months_since <= max_months:
                        # Find the rate class that corresponds to this time range
                        context = guideline[max(0, match.start()-50):min(len(guideline), match.end()+50)]
                        for rate_class in rate_classes:
                            if rate_class.lower() in context:
                                if best_class is None or rate_class_value(rate_class) > rate_class_value(best_class):
                                    best_class = rate_class
                
                elif time_type == "months_minimum":
                    min_months = int(match.group(1))
                    
                    # Check if the condition's time meets the minimum
                    if months_since >= min_months:
                        # Find the rate class that corresponds to this minimum
                        context = guideline[max(0, match.start()-50):min(len(guideline), match.end()+50)]
                        for rate_class in rate_classes:
                            if rate_class.lower() in context:
                                if best_class is None or rate_class_value(rate_class) > rate_class_value(best_class):
                                    best_class = rate_class
                
                # Similar logic for years-based patterns
                elif time_type == "years":
                    min_years = int(match.group(1))
                    max_years = int(match.group(2))
                    min_months = min_years * 12
                    max_months = max_years * 12
                    
                    if min_months <= months_since <= max_months:
                        context = guideline[max(0, match.start()-50):min(len(guideline), match.end()+50)]
                        for rate_class in rate_classes:
                            if rate_class.lower() in context:
                                if best_class is None or rate_class_value(rate_class) > rate_class_value(best_class):
                                    best_class = rate_class
                
                elif time_type == "years_minimum":
                    min_years = int(match.group(1))
                    min_months = min_years * 12
                    
                    if months_since >= min_months:
                        context = guideline[max(0, match.start()-50):min(len(guideline), match.end()+50)]
                        for rate_class in rate_classes:
                            if rate_class.lower() in context:
                                if best_class is None or rate_class_value(rate_class) > rate_class_value(best_class):
                                    best_class = rate_class
        
        # If we still don't have a rate class, use the most common one in the list
        # (excluding Decline unless it's the only option)
        if best_class is None:
            if len(rate_classes) == 1:
                best_class = rate_classes[0]
            else:
                non_decline = [rc for rc in rate_classes if rc != "Decline"]
                if non_decline:
                    best_class = max(set(non_decline), key=non_decline.count)
                else:
                    best_class = "Decline"
        
        return best_class
    
    def _calculate_risk_factor(self, rate_class):
        """Calculate risk factor based on rate class."""
        risk_factors = {
            "Preferred": 1.0,
            "Standard": 1.25,
            "Modified": 1.5,
            "Decline": 2.0
        }
        return risk_factors.get(rate_class, 1.25)


def rate_class_value(rate_class):
    """Helper function to convert rate class to numeric value for comparison."""
    values = {
        "Preferred": 1,
        "Standard": 2,
        "Modified": 3,
        "Decline": 4
    }
    return values.get(rate_class, 2)  # Default to Standard if unknown 