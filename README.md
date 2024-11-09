# [Sisyphus - AI-Powered Data Analysis Assistant[(https://sisyphus.streamlit.app/)

## Overview
Sisyphus is a powerful data analysis tool that combines Streamlit's interactive interface with Groq's AI capabilities and web search integration. It allows users to analyze data from CSV files or Google Sheets while leveraging AI for insights.

## Key Features
🔄 Data Import
- CSV file upload
- Google Sheets integration
- Data preview and statistics

🤖 AI Analysis
- Natural language queries
- Web search integration
- Contextual responses

📊 Visualization
- Interactive charts
- Column selection
- Data statistics

## Quick Start

### Local Setup
```bash
# Clone repository
git clone https://github.com/unworld11/sisyphus.git
cd sisyphus

# Create virtual environment
python -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r [requirements.txt](http://_vscodecontentref_/0)
```

### Environment Setup
1. Create .env file :
```bash
    GROQ_API_KEY=your_groq_api_key
    SERPAPI_KEY=your_serp_api_key
```
2. Setup Google Sheets (optional)
```bash
cp .streamlit/secrets.toml.template .streamlit/secrets.toml
```

### API Configuration
1. Groq API
    - Get API key from Groq
    - Add to .env file

2. SerpAPI
    - Register at SerpAPI
    - Add API key to .env

3. Google Sheets
    - Enable Google Sheets API in GCP Console
    - Create Service Account
    - Download credentials
    - Add to secrets.toml

## Project Demo

Watch the project walkthrough: [Loom Video](https://www.loom.com/share/8159c85d39bd4e9d9d28abd4997317d5?sid=f82d052f-7b78-4202-ac68-e27b8bfec244)

In this video, we cover:
- The overall purpose of the project
- Key features and how the dashboard works
- Notable code implementations and challenges encountered
