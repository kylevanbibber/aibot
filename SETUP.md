# Insurance Underwriting Chatbot - Developer Setup Guide

This guide provides detailed setup instructions for developers working on the insurance underwriting chatbot.

## Development Environment Setup

### Prerequisites

- Node.js (v14.x or later)
- npm (v6.x or later)
- Git
- A code editor (VS Code recommended)
- API keys for external services (if applicable)

### Initial Setup

1. Clone the repository:
   ```bash
   git clone https://github.com/your-organization/aibot.git
   cd aibot
   ```

2. Install dependencies:
   ```bash
   npm install
   ```

3. Create environment configuration:
   ```bash
   cp env.example .env
   ```

4. Edit the `.env` file with your development configuration:
   ```
   # Core Configuration
   PORT=3000
   NODE_ENV=development
   LOG_LEVEL=debug
   
   # API Keys
   AI_API_KEY=your_api_key_here
   
   # Database Configuration (if applicable)
   DB_HOST=localhost
   DB_PORT=27017
   DB_NAME=insurance_bot
   ```

## Project Structure

```
aibot/
├── data/                  # JSON data files for insurance companies
│   ├── companies.json     # Master list of insurance companies
│   ├── [company_id]_*.json # Company-specific JSON files
├── src/
│   ├── api/               # API endpoints
│   ├── models/            # Data models
│   ├── services/          # Business logic
│   ├── utils/             # Utility functions
│   ├── config/            # Configuration files
│   ├── app.js             # Main application entry point
├── tests/                 # Test suite
├── .env                   # Environment variables
├── package.json           # Project dependencies
├── README.md              # General readme
└── TESTING.md             # Testing guide
```

## Data Structure

The chatbot relies on structured JSON data organized as follows:

1. `companies.json` - Master list of all insurance companies:
   ```json
   [
     {
       "id": "company_id",
       "name": "Company Name",
       "rating": 4.0
     }
   ]
   ```

2. `[company_id]_policies.json` - Policies offered by each company:
   ```json
   [
     {
       "id": "company_id_policy_name",
       "name": "Policy Name",
       "type": "policy_type",
       "term_years": null,
       "coverage_min": 25000,
       "coverage_max": 1000000,
       "premium_factor": 1.5,
       "features": [
         "Feature 1",
         "Feature 2"
       ]
     }
   ]
   ```

3. `[company_id]_eligibility.json` - Eligibility criteria for each policy:
   ```json
   {
     "company_id_policy_name": {
       "age_min": 18,
       "age_max": 65,
       "income_min": 30000,
       "health_conditions_max": 2,
       "smoker_eligible": true,
       "smoker_premium_factor": 1.5
     }
   }
   ```

4. `[company_id]_underwriting.json` - Detailed underwriting criteria:
   ```json
   {
     "company_id": "company_id",
     "underwriting_criteria": {
       "build_chart": { /* build chart data */ },
       "medical_conditions": { /* medical conditions data */ },
       "laboratory_requirements": { /* lab requirements data */ },
       "risk_classes": { /* risk classes data */ },
       "tobacco_guidelines": { /* tobacco guidelines data */ },
       "financial_underwriting": { /* financial underwriting data */ },
       "special_considerations": { /* special considerations data */ }
     }
   }
   ```

## Adding a New Insurance Company

To add a new insurance company to the system:

1. Add the company to `companies.json`
2. Create three required JSON files:
   - `[company_id]_policies.json`
   - `[company_id]_eligibility.json`
   - `[company_id]_underwriting.json`
3. Ensure all files follow the schema described above
4. Restart the application to load the new data

## Development Workflow

1. Create a new branch for your feature or fix:
   ```bash
   git checkout -b feature/new-feature
   ```

2. Make your changes and test them locally:
   ```bash
   npm run dev
   ```

3. Run automated tests:
   ```bash
   npm test
   ```

4. Commit your changes with a descriptive message:
   ```bash
   git commit -m "Add feature: description of changes"
   ```

5. Push your branch and create a pull request:
   ```bash
   git push origin feature/new-feature
   ```

## API Documentation

The chatbot exposes the following API endpoints:

- `POST /api/query` - Submit a natural language query
- `GET /api/companies` - Get all available insurance companies
- `GET /api/companies/:id/policies` - Get policies for a specific company
- `GET /api/policies/:id/eligibility` - Get eligibility for a specific policy
- `POST /api/underwriting/evaluate` - Evaluate a profile against underwriting criteria

## External Services Integration

If the chatbot requires integration with external services (e.g., NLP APIs, authentication services), ensure your environment has the necessary configuration:

1. Obtain API keys for the required services
2. Add the keys to your `.env` file
3. Use the integration utilities in `src/utils/integrations/`

## Debugging

For effective debugging:

1. Set the log level in `.env`:
   ```
   LOG_LEVEL=debug
   ```

2. Use the logger utility for all logging:
   ```javascript
   const logger = require('../utils/logger');
   logger.debug('Detailed information');
   logger.error('Error message', error);
   ```

3. For NLP/AI-related issues, check the integration logs:
   ```bash
   npm run dev:logs
   ```

## Deployment

To prepare the application for deployment:

1. Build the production version:
   ```bash
   npm run build
   ```

2. Set environment variables for production:
   ```
   NODE_ENV=production
   LOG_LEVEL=info
   ```

3. Start the production server:
   ```bash
   npm start
   ```

## Common Issues

- **JSON Parse Errors**: Check the syntax of your JSON files, especially when adding new insurance companies
- **API Rate Limiting**: If using external AI services, implement rate limiting to avoid hitting API quotas
- **Memory Usage**: Monitor memory usage when loading large JSON data files

## Best Practices

- Keep the data structure consistent across all insurance companies
- Implement comprehensive error handling
- Write unit tests for all business logic
- Document any changes to the data schema
- Use type checking for data structures (consider TypeScript) 