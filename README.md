# KM Stock Technical Analysis Agent

This repository contains a Stock Technical Analysis Agent built with Google ADK and a Streamlit web frontend for easy interaction.

## Repository Structure

- `/tool_agent/`: Contains the ADK agent for stock technical analysis
- `/scripts/`: Helper scripts for the agent
- `/streamlit/`: Streamlit web application for interacting with the agent

## Stock Technical Analysis Agent

The agent provides comprehensive stock analysis capabilities:

- Technical indicators (SMA, EMA, RSI, MACD, etc.)
- Momentum analysis with scoring
- Volume analysis
- Stock price information

## Streamlit Web App

The Streamlit application provides a chat interface to interact with the stock analysis capabilities:

### Features

- Interactive chat interface
- Quick selection sidebar for common stocks and analysis types
- Real-time stock data analysis
- Technical indicators support
- Momentum analysis with scoring
- Volume analysis

### Usage

To run the Streamlit app locally:

```bash
cd streamlit
./run_local.sh
```

Or visit the deployed version at: [https://demochatbot-ta.streamlit.app/](https://demochatbot-ta.streamlit.app/)

## Deployment

The Streamlit app can be deployed directly from this repository. Just point Streamlit Cloud to the `streamlit/app.py` file.

## API Key

This project uses Tiingo API for stock data. You'll need to configure your API key in the Streamlit secrets.

## License

MIT License
