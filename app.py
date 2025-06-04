import os
from flask import Flask, request, jsonify, render_template
from flask_cors import CORS
from dotenv import load_dotenv
from models.underwriting_engine import UnderwritingEngine
from models.policy_matcher import PolicyMatcher

# Load environment variables
load_dotenv()

# Initialize Flask app
app = Flask(__name__)
CORS(app)

# Initialize our models
underwriting_engine = UnderwritingEngine()
policy_matcher = PolicyMatcher()

@app.route('/')
def index():
    """Render the main interface."""
    return render_template('index.html')

@app.route('/api/chat', methods=['POST'])
def chat():
    """Process chat messages and return responses."""
    data = request.json
    message = data.get('message', '')
    chat_history = data.get('chat_history', [])
    
    # Process the message using our underwriting engine
    response = underwriting_engine.process_message(message, chat_history)
    
    return jsonify({
        'response': response
    })

@app.route('/api/companies', methods=['GET'])
def get_companies():
    """Get the list of available insurance companies and their policy counts."""
    # Get age parameter if provided
    age_param = request.args.get('age')
    age = int(age_param) if age_param and age_param.isdigit() else None
    
    # Get coverage range parameters if provided
    coverage_min_param = request.args.get('coverage_min')
    coverage_min = int(coverage_min_param) if coverage_min_param and coverage_min_param.isdigit() else None
    
    coverage_max_param = request.args.get('coverage_max')
    coverage_max = int(coverage_max_param) if coverage_max_param and coverage_max_param.isdigit() else None
    
    # Get policy types parameter if provided
    policy_types_param = request.args.get('policy_types')
    requested_policy_types = policy_types_param.split(',') if policy_types_param else None
    
    companies_data = []
    
    # Get the companies from our policy matcher
    for company in policy_matcher.companies:
        company_id = company["id"]
        company_name = company["name"]
        
        # Get all policies for this company
        policies = policy_matcher.policies.get(company_id, [])
        
        # Filter policies by age if age is provided
        if age is not None:
            eligible_policies = []
            for policy in policies:
                policy_id = policy.get("id", "")
                # Get criteria for this policy
                criteria = policy_matcher.eligibility_criteria.get(company_id, {}).get(policy_id, {})
                
                # Check age eligibility
                age_min = criteria.get("age_min", criteria.get("min_age", 0))
                age_max = criteria.get("age_max", criteria.get("max_age", 100))
                
                if age_min <= age <= age_max:
                    eligible_policies.append(policy)
            
            policies = eligible_policies
        
        # Filter policies by coverage range if provided
        if coverage_min is not None or coverage_max is not None:
            coverage_eligible_policies = []
            for policy in policies:
                policy_min = policy.get("coverage_min", 0)
                policy_max = policy.get("coverage_max", float('inf'))
                
                # Check if there's overlap between requested range and policy range
                range_overlap = True
                
                if coverage_min is not None and policy_max < coverage_min:
                    # Policy's max coverage is less than requested min
                    range_overlap = False
                
                if coverage_max is not None and policy_min > coverage_max:
                    # Policy's min coverage is more than requested max
                    range_overlap = False
                
                if range_overlap:
                    coverage_eligible_policies.append(policy)
            
            policies = coverage_eligible_policies
        
        # Filter by policy types if requested
        if requested_policy_types:
            policies = [p for p in policies if p.get("type", "") in requested_policy_types]
        
        policy_count = len(policies)
        
        # Only include companies that have at least one policy
        if policy_count > 0:
            # Get unique policy types for this company
            policy_types = list(set(policy.get("type", "") for policy in policies if "type" in policy))
            
            # Get age range for this company (min and max across all policies)
            age_ranges = []
            for policy in policies:
                policy_id = policy.get("id", "")
                criteria = policy_matcher.eligibility_criteria.get(company_id, {}).get(policy_id, {})
                age_min = criteria.get("age_min", criteria.get("min_age", 0))
                age_max = criteria.get("age_max", criteria.get("max_age", 100))
                age_ranges.append((age_min, age_max))
            
            if age_ranges:
                company_age_min = min(min_age for min_age, max_age in age_ranges)
                company_age_max = max(max_age for min_age, max_age in age_ranges)
                age_range = f"{company_age_min}-{company_age_max}"
            else:
                age_range = "18-85"  # Default range
            
            # Get coverage range for this company (min and max across filtered policies)
            coverage_ranges = [(p.get("coverage_min", 10000), p.get("coverage_max", 1000000)) for p in policies]
            
            if coverage_ranges:
                company_coverage_min = min(min_coverage for min_coverage, max_coverage in coverage_ranges)
                company_coverage_max = max(max_coverage for min_coverage, max_coverage in coverage_ranges)
                coverage_range = f"${company_coverage_min:,}-${company_coverage_max:,}"
            else:
                coverage_range = "$10,000-$1,000,000"  # Default range
            
            companies_data.append({
                "id": company_id,
                "name": company_name,
                "policy_count": policy_count,
                "policy_types": policy_types,
                "age_range": age_range,
                "coverage_range": coverage_range
            })
    
    # Sort by name
    companies_data.sort(key=lambda x: x["name"])
    
    return jsonify({
        'companies': companies_data
    })

@app.route('/api/recommend-policy', methods=['POST'])
def recommend_policy():
    """Find the best policy match based on client information."""
    client_data = request.json
    
    # Log client data for debugging
    print(f"Client data received: {client_data}")
    
    # Transform client data for the policy matcher
    transformed_data = transform_client_data(client_data)
    
    # Use the policy matcher to find the best policy
    best_policies = policy_matcher.find_best_match(transformed_data)
    
    # Debug output - count policies by type
    policy_types_count = {}
    for policy in best_policies:
        policy_type = policy.get("policy_type", "unknown")
        policy_types_count[policy_type] = policy_types_count.get(policy_type, 0) + 1
    
    print(f"Policy recommendations by type: {policy_types_count}")
    print(f"Selected policy types filter: {transformed_data.get('policy_types', 'none')}")
    
    # If we have medical conditions that might affect the recommendation, process them
    if client_data.get('medical_conditions'):
        best_policies = apply_medical_underwriting(best_policies, client_data)
    
    # Apply criminal history filter if necessary
    if client_data.get('criminal_history') == 'yes':
        best_policies = apply_criminal_history_filter(best_policies, client_data)
    
    # Apply tobacco status adjustment
    if client_data.get('tobacco_status') in ['smoker', 'former-smoker']:
        best_policies = apply_tobacco_adjustment(best_policies, client_data)
    
    # Generate recommendations summary
    recommendations_summary = generate_recommendations_summary(best_policies)
    
    return jsonify({
        'recommendations': best_policies,
        'summary': recommendations_summary
    })

def transform_client_data(client_data):
    """Transform client data from the form format to the policy matcher format."""
    # Extract basic information
    transformed = {
        'age': client_data.get('age', 35),
        'sex': client_data.get('sex', 'male'),
        'state': client_data.get('state', 'CA'),
        'smoking_status': client_data.get('tobacco_status', 'non-smoker'),
    }
    
    # Add height/weight/BMI if provided
    if client_data.get('height') and client_data.get('weight'):
        transformed['height'] = client_data.get('height', 70)
        transformed['weight'] = client_data.get('weight', 170)
        transformed['bmi'] = float(client_data.get('bmi', 25))
    
    # Set coverage range 
    if client_data.get('coverage_min') and client_data.get('coverage_max'):
        transformed['coverage_min'] = int(client_data.get('coverage_min', 100000))
        transformed['coverage_max'] = int(client_data.get('coverage_max', 500000))
        print(f"Coverage range set to: ${transformed['coverage_min']} - ${transformed['coverage_max']}")
    # Fallback to single coverage amount if that's all we have
    elif client_data.get('coverage_amount'):
        transformed['coverage_amount'] = int(client_data.get('coverage_amount', 250000))
        print(f"Using single coverage amount: ${transformed['coverage_amount']}")
    else:
        print("No coverage range or amount specified, using defaults")
    
    # Set coverage type based on policy_types preference (defaulting to all if not specified)
    if client_data.get('policy_types') and len(client_data['policy_types']) == 1:
        # If only one policy type is selected, use that as the preferred type
        transformed['coverage_type'] = client_data['policy_types'][0]
        print(f"Single policy type selected: {transformed['coverage_type']}")
    else:
        # If multiple or none are selected, keep them all as options
        transformed['policy_types'] = client_data.get('policy_types', ['term_life', 'whole_life'])
        print(f"Multiple policy types selected: {transformed['policy_types']}")
    
    # Transform medical conditions
    health_conditions = []
    if client_data.get('medical_conditions'):
        for condition in client_data['medical_conditions']:
            health_conditions.append(condition['type'])
    
    transformed['health_conditions'] = health_conditions
    
    # Add any prescriptions as features to consider
    desired_features = []
    if client_data.get('prescriptions') and len(client_data['prescriptions']) > 0:
        desired_features.append('Prescription Coverage')
    
    transformed['desired_features'] = desired_features
    
    return transformed

def apply_medical_underwriting(policies, client_data):
    """Apply medical underwriting rules to filter or adjust policies."""
    adjusted_policies = []
    
    # Extract medical conditions and their details for better analysis
    medical_conditions = []
    for condition in client_data.get('medical_conditions', []):
        medical_conditions.append({
            'type': condition['type'],
            'details': condition.get('details', '')
        })
    
    # Group conditions by severity for more nuanced adjustments
    high_risk_conditions = ['cancer', 'heart-disease', 'stroke', 'kidney-disease', 'liver-disease']
    medium_risk_conditions = ['diabetes', 'high-blood-pressure', 'copd']
    low_risk_conditions = ['asthma', 'depression', 'anxiety']
    
    for policy in policies:
        # Deep copy the policy to avoid modifying the original
        adjusted_policy = dict(policy)
        
        # Initialize notes if not present
        if 'notes' not in adjusted_policy:
            adjusted_policy['notes'] = []
        
        # Add medical notes from the policy if present
        if 'medical_notes' in policy:
            for note in policy['medical_notes']:
                if note not in adjusted_policy['notes']:
                    adjusted_policy['notes'].append(note)
        
        # Check for condition-specific adjustments
        score_adjustment = 0
        
        for condition in medical_conditions:
            condition_type = condition['type']
            details = condition['details'].lower()
            
            # Current conditions have higher impact than past conditions
            is_current = True
            if 'cured' in details or 'resolved' in details or 'past' in details or 'history of' in details:
                is_current = False
            
            # Apply condition-specific adjustments
            if condition_type in high_risk_conditions:
                if is_current:
                    score_adjustment -= 15
                    adjusted_policy['notes'].append(f"Match score adjusted for current {condition_type} condition")
                else:
                    score_adjustment -= 5
                    adjusted_policy['notes'].append(f"Match score adjusted for history of {condition_type}")
            
            elif condition_type in medium_risk_conditions:
                if is_current:
                    score_adjustment -= 8
                    adjusted_policy['notes'].append(f"Match score adjusted for current {condition_type} condition")
                else:
                    score_adjustment -= 3
                    adjusted_policy['notes'].append(f"Match score adjusted for history of {condition_type}")
            
            elif condition_type in low_risk_conditions:
                if is_current:
                    score_adjustment -= 3
                    adjusted_policy['notes'].append(f"Match score adjusted for current {condition_type} condition")
                else:
                    score_adjustment -= 1
                    adjusted_policy['notes'].append(f"Match score adjusted for history of {condition_type}")
        
        # Apply the adjustment
        adjusted_policy['match_score'] = max(0, policy['match_score'] + score_adjustment)
        
        adjusted_policies.append(adjusted_policy)
    
    # Sort adjusted policies by match score
    adjusted_policies.sort(key=lambda x: x['match_score'], reverse=True)
    
    return adjusted_policies

def apply_criminal_history_filter(policies, client_data):
    """Apply criminal history filter to adjust policy recommendations."""
    adjusted_policies = []
    criminal_details = client_data.get('criminal_details', '').lower()
    
    for policy in policies:
        # Deep copy the policy to avoid modifying the original
        adjusted_policy = dict(policy)
        
        # Severe criminal history might make some policies unavailable
        if 'felony' in criminal_details or 'violent' in criminal_details:
            # Reduce match score significantly
            adjusted_policy['match_score'] = max(0, policy['match_score'] - 30)
            
            if 'notes' not in adjusted_policy:
                adjusted_policy['notes'] = []
            adjusted_policy['notes'].append('Policy availability may be limited due to criminal history')
        else:
            # Minor offenses have less impact
            adjusted_policy['match_score'] = max(0, policy['match_score'] - 5)
            
            if 'notes' not in adjusted_policy:
                adjusted_policy['notes'] = []
            adjusted_policy['notes'].append('Policy availability may be affected by criminal history')
        
        adjusted_policies.append(adjusted_policy)
    
    # Sort adjusted policies by match score
    adjusted_policies.sort(key=lambda x: x['match_score'], reverse=True)
    
    return adjusted_policies

def apply_tobacco_adjustment(policies, client_data):
    """Apply tobacco status adjustment to policy match scores."""
    adjusted_policies = []
    tobacco_status = client_data.get('tobacco_status')
    
    for policy in policies:
        # Deep copy the policy to avoid modifying the original
        adjusted_policy = dict(policy)
        
        if tobacco_status == 'smoker':
            # Smokers typically have lower match scores
            adjusted_policy['match_score'] = max(0, policy['match_score'] - 15)
            
            if 'notes' not in adjusted_policy:
                adjusted_policy['notes'] = []
            adjusted_policy['notes'].append('Match score adjusted for tobacco use')
        elif tobacco_status == 'former-smoker':
            # Former smokers have smaller adjustments
            adjusted_policy['match_score'] = max(0, policy['match_score'] - 5)
            
            if 'notes' not in adjusted_policy:
                adjusted_policy['notes'] = []
            adjusted_policy['notes'].append('Match score adjusted for former tobacco use')
        
        adjusted_policies.append(adjusted_policy)
    
    # Sort adjusted policies by match score
    adjusted_policies.sort(key=lambda x: x['match_score'], reverse=True)
    
    return adjusted_policies

def generate_recommendations_summary(policies):
    """Generate a summary of policy recommendations."""
    if not policies or len(policies) == 0:
        return "We couldn't find any suitable policies based on your information. Some policies may have been filtered out due to not meeting your coverage requirements or due to medical conditions. Please adjust your criteria or contact an agent for assistance."
    
    top_policies = policies[:3]  # Get top 3 policies
    
    # Check if we have medical notes to mention
    has_medical_notes = any(policy.get("medical_notes") for policy in top_policies)
    
    if len(top_policies) == 1:
        policy = top_policies[0]
        summary = f"We recommend {policy['company_name']} {policy['policy_name']} ({policy['policy_type'].replace('_', ' ')}) with coverage range {policy['coverage_range']}."
        
        # Add medical notes context if present
        if has_medical_notes and policy.get("medical_notes"):
            summary += " This recommendation takes into account your medical history."
    else:
        summary = "We recommend going with "
        
        # Primary recommendation
        primary = top_policies[0]
        summary += f"{primary['company_name']} {primary['policy_name']} ({primary['policy_type'].replace('_', ' ')}). "
        
        # Alternative options
        if len(top_policies) > 1:
            summary += "If declined, we can pivot to "
            alternatives = []
            for i in range(1, len(top_policies)):
                policy = top_policies[i]
                alternatives.append(f"{policy['company_name']} {policy['policy_name']} ({policy['policy_type'].replace('_', ' ')})")
            
            summary += " or ".join(alternatives) + "."
        
        # Add medical notes context if present
        if has_medical_notes:
            summary += " These recommendations take into account your medical history and provide appropriate options based on company underwriting guidelines."
    
    return summary

if __name__ == '__main__':
    app.run(debug=True, port=5000) 