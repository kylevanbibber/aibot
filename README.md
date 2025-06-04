# Insurance Underwriting Chatbot - Setup and Testing Guide

This guide provides instructions for setting up and testing the insurance underwriting chatbot.

## Overview

The chatbot is designed to provide information about insurance policies and underwriting criteria from multiple insurance companies. It uses structured JSON data to respond to queries about eligibility, policy features, and medical underwriting decisions.

## System Requirements

- Node.js (v14 or later)
- NPM (v6 or later)
- 2GB RAM minimum
- Internet connection for API calls

## Installation

1. Clone the repository:
   ```bash
   git clone <repository-url>
   cd aibot
   ```

2. Install dependencies:
   ```bash
   npm install
   ```

3. Set up environment variables by copying the example file:
   ```bash
   cp .env.example .env
   ```

4. Edit the `.env` file to include your API keys and configuration:
   ```
   API_KEY=your_api_key_here
   PORT=3000
   LOG_LEVEL=info
   ```

## Launching the Bot for Testing

1. Start the development server:
   ```bash
   npm run dev
   ```

2. The bot will be available at `http://localhost:3000` (or whatever port you specified in the .env file)

## Testing the Chatbot

### Basic Tests

Try these basic queries to test the bot's functionality:

1. "What insurance companies do you have information about?"
2. "Tell me about the policies offered by Foresters Financial."
3. "What is the eligibility criteria for SimpliNow Legacy Max?"
4. "What medical conditions would make someone ineligible for SBLI coverage?"

### Underwriting Scenario Tests

Test underwriting scenarios with these more complex queries:

1. "Can a 65-year-old with type 2 diabetes (A1C of 7.2) qualify for Corebridge Financial SimpliNow Legacy Max?"
2. "Would a person with stage I breast cancer diagnosed 3 years ago be eligible for Liberty Bankers Life Final Expense coverage?"
3. "What's the impact of tobacco use on Legal & General America coverage for someone with controlled hypertension?"
4. "Can someone with a history of atrial fibrillation get approved for Royal Neighbors of America whole life insurance?"

### Build Chart Tests

Test height/weight chart queries:

1. "Would someone who is 5'8\" and weighs 300 lbs qualify for SBLI coverage?"
2. "What are the weight limits for a person who is 6'0\" tall for Corebridge Financial policies?"
3. "Is there a minimum weight requirement for Liberty Bankers Life coverage?"

## Troubleshooting

- **Bot not responding**: Ensure the server is running and check console for errors
- **Inaccurate responses**: Verify the data in the JSON files under the `data/` directory
- **Missing company information**: Check that the company exists in `companies.json` and has corresponding files

## Data Structure

The bot uses these JSON files for its responses:

- `companies.json`: List of all insurance companies
- `[company_id]_policies.json`: Information about each company's policies
- `[company_id]_eligibility.json`: Eligibility criteria for each policy
- `[company_id]_underwriting.json`: Detailed underwriting criteria including medical conditions and build charts

## Adding New Companies or Policies

To add a new insurance company or policy:

1. Add the company to `companies.json`
2. Create the corresponding company files in the `data/` directory
3. Restart the server to load the new data

## Monitoring and Logs

View logs during testing:

```bash
npm run dev:logs
```

## Support

For questions or issues, please contact the development team at support@example.com. 