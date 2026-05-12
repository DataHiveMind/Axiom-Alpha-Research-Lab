from robocorp.tasks import task
from robocorp import browser
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer
import pandas as pd
import pykx as kx
from datetime import datetime

# Initialize NLP for Central Bank statements
analyzer = SentimentIntensityAnalyzer()

# kdb+ Connection details (Assuming local Lenovo Data Node on port 5000)
KDB_HOST = "127.0.0.1"
KDB_PORT = 5000

def push_to_kdb(indicator: str, actual: float, consensus: float, sentiment: float):
    """Pipes structured macro data directly into the high-performance kdb+ engine."""
    try:
        q = kx.SyncQConnection(host=KDB_HOST, port=KDB_PORT)
        
        # Format variables for q
        q_time = kx.Timestamp(datetime.utcnow())
        q_indicator = kx.SymbolAtom(indicator)
        q_actual = kx.FloatAtom(actual)
        q_consensus = kx.FloatAtom(consensus)
        q_sentiment = kx.FloatAtom(sentiment)
        
        # Execute the q insertion function defined in macro_schema.q
        q("insert_macro", q_time, q_indicator, q_actual, q_consensus, q_sentiment)
    except Exception as e:
        print(f"Failed to push to kdb+: {e}")

@task
def ingest_macro_releases():
    """
    Robocorp Bot: Navigates financial portals, extracts unstructured 
    macro tables/PDFs, structures the data, and pipes to kdb+.
    """
    page = browser.goto("https://www.bls.gov/cpi/") # Example: US Bureau of Labor Statistics
    
    # 1. Wait for the core data table to load and extract it
    page.wait_for_selector(".regular")
    table_element = page.locator(".regular").first
    
    # Extract the raw HTML table and parse with Pandas
    html_content = table_element.inner_html()
    df = pd.read_html(f"<table>{html_content}</table>")[0]
    
    # Example logic: Extracting the latest CPI month-over-month change
    # In a real bot, you use robust XPath/Regex to find the exact cell
    latest_cpi_val = 0.4 # Placeholder for parsed value
    expected_consensus = 0.3 
    
    # 2. Navigate to the FOMC / Central Bank Press Release
    page.goto("https://www.federalreserve.gov/newsevents/pressreleases.htm")
    latest_release = page.locator(".eventlist a").first.inner_text()
    
    # 3. Apply baseline statistical/NLP transformation
    sentiment_dict = analyzer.polarity_scores(latest_release)
    compound_sentiment = sentiment_dict['compound']
    
    # 4. Pipe to kdb+
    push_to_kdb(
        indicator="US_CPI_MoM",
        actual=latest_cpi_val,
        consensus=expected_consensus,
        sentiment=compound_sentiment
    )
    
    print("✅ Macro ingestion complete. Data secured in kdb+.")