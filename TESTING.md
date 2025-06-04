# Insurance Underwriting Chatbot - Testing Guide

This document provides detailed testing scenarios to verify the functionality of the insurance underwriting chatbot.

## Testing Approach

Testing the chatbot should focus on three key areas:
1. General information retrieval
2. Policy eligibility assessment
3. Underwriting decision accuracy

## Test Scenarios

### 1. Company and Policy Information Retrieval

| Test ID | Description | Sample Query | Expected Response |
|---------|-------------|--------------|-------------------|
| INFO-01 | List all companies | "What insurance companies do you work with?" | Bot should list all 12 companies in the database |
| INFO-02 | Get specific company details | "Tell me about SBLI" | Bot should provide information about SBLI |
| INFO-03 | List policies for a company | "What policies does Foresters Financial offer?" | Bot should list all Foresters Financial policies |
| INFO-04 | Get specific policy details | "What is the SimpliNow Legacy Max policy?" | Bot should describe the Corebridge Financial SimpliNow Legacy Max policy |

### 2. Basic Eligibility Queries

| Test ID | Description | Sample Query | Expected Response |
|---------|-------------|--------------|-------------------|
| ELIG-01 | Age eligibility | "What is the age range for Liberty Bankers Life Final Expense?" | Bot should state 50-85 years |
| ELIG-02 | Coverage amounts | "What is the maximum coverage for SBLI term life?" | Bot should provide the correct maximum coverage amount |
| ELIG-03 | Smoker eligibility | "Can smokers get Legal & General America coverage?" | Bot should confirm smokers are eligible but may have restrictions |
| ELIG-04 | Build/weight limits | "What are the height and weight limits for Corebridge Financial?" | Bot should explain the build chart criteria |

### 3. Complex Underwriting Scenarios

| Test ID | Description | Sample Query | Expected Response |
|---------|-------------|--------------|-------------------|
| UW-01 | Diabetes scenario | "Can someone with diabetes (A1C 7.0) who doesn't use insulin qualify for Corebridge SimpliNow Legacy Max?" | Bot should indicate this would qualify for Level benefits |
| UW-02 | Cancer history | "Is someone with Stage I breast cancer 4 years ago eligible for Liberty Bankers Life coverage?" | Bot should provide appropriate eligibility information |
| UW-03 | Heart condition | "Would a non-smoker who had a heart attack 18 months ago qualify for Corebridge coverage?" | Bot should indicate this would qualify for Level benefits |
| UW-04 | Multiple conditions | "Can someone with controlled hypertension and COPD who is a non-smoker get coverage?" | Bot should analyze both conditions and provide appropriate assessment |

### 4. Build Chart Assessment

| Test ID | Description | Sample Query | Expected Response |
|---------|-------------|--------------|-------------------|
| BUILD-01 | Standard build | "I'm 5'10" and weigh 180 lbs. Which companies would offer me their best rates?" | Bot should identify companies where this build qualifies for preferred rates |
| BUILD-02 | Borderline build | "Would someone who is 5'6" and weighs 290 lbs qualify for any coverage?" | Bot should identify appropriate coverage options if available |
| BUILD-03 | Company comparison | "Which company has the most lenient build requirements for someone who is 6'2" and 280 lbs?" | Bot should compare build charts and identify the most favorable company |

### 5. Edge Cases and Special Situations

| Test ID | Description | Sample Query | Expected Response |
|---------|-------------|--------------|-------------------|
| EDGE-01 | Declined conditions | "What medical conditions automatically decline coverage with SBLI?" | Bot should list decline conditions for SBLI |
| EDGE-02 | Medication impact | "How would taking Coumadin affect underwriting with Corebridge?" | Bot should explain the impact on underwriting |
| EDGE-03 | Non-medical factors | "Do felony convictions affect Liberty Bankers Life eligibility?" | Bot should explain the impact of felony convictions |
| EDGE-04 | Foreign nationals | "Are non-US citizens eligible for SimpliNow Legacy policies?" | Bot should explain eligibility requirements for non-US citizens |

## Test Execution

When executing these tests, follow this process:
1. Start the chatbot application
2. Enter the test query exactly as written
3. Compare the response to the expected result
4. Document any discrepancies

## Reporting Issues

When reporting issues, please include:
- Test ID
- Exact query used
- Actual response received
- Expected response
- Any relevant screenshots

## Data Validation

Periodically, the underlying JSON data should be validated to ensure:
- All companies have complete files
- Medical condition information is up-to-date
- Build charts are accurate
- Policy information is current

## Performance Testing

For performance testing, measure:
- Response time for simple queries (should be < 2 seconds)
- Response time for complex underwriting scenarios (should be < 5 seconds)
- System resource usage during peak load

## Regression Testing

After any updates to the bot or underlying data, all critical path tests (INFO-01, ELIG-01, UW-01, BUILD-01, EDGE-01) should be re-run to ensure continued functionality. 