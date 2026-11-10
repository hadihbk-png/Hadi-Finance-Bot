# Financial Advisor Bot

An AI-powered financial guidance chatbot built with Flask and Azure OpenAI.

## Features

- 💰 Budgeting guidance
- 💳 Debt payoff strategies
- 🏦 Savings planning
- 🏠 Loan analysis
- 📊 Financial tools and calculations
- 🔄 Conversation history per session

## Local Development

### Prerequisites

- Python 3.8+
- Azure OpenAI API key
- Azure OpenAI Endpoint

### Setup

1. Clone the repository:
```bash
git clone https://github.com/hadihbk-png/Hadi-Finance-Bot.git
cd Hadi-Finance-Bot
```

2. Create `.env` file (copy from `.env.example`):
```bash
cp .env.example .env
```

3. Fill in your Azure OpenAI credentials in `.env`

4. Install dependencies:
```bash
pip install -r requirements.txt
```

5. Run locally:
```bash
python web.py
```

Visit `http://localhost:8000` in your browser.

## Deployment to Netlify

### Steps

1. **Fork/Push to GitHub**
   - Ensure code is pushed to your GitHub repository

2. **Connect to Netlify**
   - Go to [netlify.com](https://netlify.com)
   - Click "New site from Git"
   - Connect your GitHub account
   - Select this repository

3. **Configure Environment Variables**
   - In Netlify dashboard: Site Settings → Environment
   - Add these variables:
     - `AZURE_OPENAI_API_KEY` (your API key)
     - `AZURE_OPENAI_ENDPOINT` (your endpoint)
     - `AZURE_OPENAI_DEPLOYMENT` (e.g., gpt-5-mini)
     - `OPENAI_API_VERSION` (2024-12-01-preview)

4. **Deploy**
   - Netlify will automatically deploy when you push to `main`
   - Your app will be available at `https://your-site-name.netlify.app`

## Architecture

- **Frontend**: Static HTML/CSS/JavaScript in `/static`
- **Backend**: Netlify Functions (serverless) in `/netlify/functions`
- **Logic**: Python advisor and financial tools in `advisor.py` and `finance_tools.py`

## API Endpoints

- `/.netlify/functions/chat` - Send message and get financial advice
- `/.netlify/functions/reset` - Reset conversation

## License

MIT
