import streamlit as st
import pandas as pd
from groq import Groq
import plotly.express as px
import gspread
from serpapi import GoogleSearch
from google.oauth2 import service_account
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

@st.cache_resource
def get_groq_client():
    api_key = os.getenv("GROQ_API_KEY")
    if not api_key:
        st.error("GROQ_API_KEY not found in environment variables")
        st.stop()
    return Groq(api_key=api_key)

def web_search(query, num_results=3):
    """Perform web search using SerpAPI with debug output"""
    try:
        api_key = os.getenv("SERPAPI_KEY")
        if not api_key:
            st.error("SERPAPI_KEY not found in environment variables")
            return []
            
        st.info(f"Searching for: {query}")  # Debug info
        
        search = GoogleSearch({
            "q": query,
            "api_key": api_key,
            "num": num_results,
            "engine": "google"  # Explicitly set engine
        })
        
        results = search.get_dict()
        
        if "organic_results" not in results:
            st.warning("No organic results found in API response")
            return []
            
        search_results = []
        for result in results["organic_results"][:num_results]:
            search_results.append({
                "title": result.get("title", ""),
                "snippet": result.get("snippet", ""),
                "link": result.get("link", "")
            })
            
        st.info(f"Found {len(search_results)} results")  # Debug info
        st.write(search_results)  # Debug info
        return search_results

        
    except Exception as e:
        st.error(f"Search error: {str(e)}")
        return []

def setup_google_auth():
    try:
        credentials = service_account.Credentials.from_service_account_info(
            st.secrets["gcp_service_account"],
            scopes=['https://spreadsheets.google.com/feeds',
                   'https://www.googleapis.com/auth/spreadsheets',
                   'https://www.googleapis.com/auth/drive']
        )
        return gspread.authorize(credentials)
    except Exception as e:
        st.error(f"Google Sheets authentication failed: {str(e)}")
        return None

def load_google_sheet(url):
    try:
        gc = setup_google_auth()
        if gc:
            sheet = gc.open_by_url(url)
            worksheet = sheet.get_worksheet(0)
            data = worksheet.get_all_records()
            df = pd.DataFrame(data)
            return process_data(df)
    except Exception as e:
        st.error(f"Error loading Google Sheet: {str(e)}")
        return None, None

def load_csv_data(file):
    try:
        df = pd.read_csv(file)
        return process_data(df)
    except Exception as e:
        st.error(f"Error loading CSV file: {str(e)}")
        return None, None

def process_data(df):
    if df.empty:
        st.error("The data is empty.")
        return None, None
    
    stats = {
        "columns": list(df.columns),
        "rows": len(df),
        "summary": df.describe().to_string()
    }
    return df, stats


def ask_about_data(client, question, df, stats, use_web_search):
    try:
        system_context = f"""Analyzing a dataset with {stats['rows']} rows and columns: {', '.join(stats['columns'])}."""
        
        if use_web_search:
            with st.spinner('Searching web...'):
                search_results = web_search(question)
                if search_results:
                    web_context = "\n".join([f"- {r['snippet']}" for r in search_results])
                    system_context += f"\nWeb search results:\n{web_context}"
                else:
                    st.warning("No web search results found")

        completion = client.chat.completions.create(
            model="llama3-8b-8192",
            messages=[
                {"role": "system", "content": system_context},
                {"role": "user", "content": question}
            ],
            temperature=0.7,
            max_tokens=1024,
        )
                # Store result in session state
        new_result = pd.DataFrame({
            'Question': [question],
            'Answer': [completion.choices[0].message.content],
            'Timestamp': [pd.Timestamp.now()]
        })
        
        if 'results' not in st.session_state:
            st.session_state.results = new_result
        else:
            st.session_state.results = pd.concat
            st.session_state.results, new_result, ignore_index=True
            
        return completion.choices[0].message.content
    except Exception as e:
        st.error(f"Error: {str(e)}")
        return None

def main():
    st.title("Data Analysis Assistant")
    
    # Initialize Groq client
    client = get_groq_client()
    
    # Data Source Selection
    data_source = st.radio("Choose your data source:", ["Upload CSV", "Google Sheet"])
    
    df, stats = None, None
    
    if data_source == "Upload CSV":
        uploaded_file = st.file_uploader("Choose a CSV file", type="csv")
        if uploaded_file:
            df, stats = load_csv_data(uploaded_file)
    else:
        sheet_url = st.text_input("Enter Google Sheet URL:")
        if sheet_url:
            df, stats = load_google_sheet(sheet_url)
    
    if df is not None and stats is not None:
        # Data Overview Section
        with st.expander("Data Preview"):
            st.dataframe(df.head())
            st.write(f"Total rows: {stats['rows']}")
            st.write("Columns:", ", ".join(stats['columns']))
        
        # Column Selection
        main_column = st.selectbox("Select main column for analysis:", df.columns)
        
        # Visualization Section
        with st.expander("Data Visualization"):
            numeric_cols = df.select_dtypes(include=['float64', 'int64']).columns
            if len(numeric_cols) > 0:
                numeric_column = st.selectbox("Select column for visualization", numeric_cols)
                try:
                    fig = px.histogram(df, x=numeric_column)
                    st.plotly_chart(fig)
                except Exception as e:
                    st.error(f"Error creating visualization: {str(e)}")
        
        # Statistics Section
        with st.expander("Data Statistics"):
            st.write(df.describe())
        
        # Q&A Section
        st.subheader("Ask Questions About Your Data")
        use_web_search = st.toggle("Include web search results in analysis")
        question = st.text_input("Enter your question:")
        if st.button("Ask"):
            if question:
                with st.spinner('Analyzing...'):
                    answer = ask_about_data(client, question, df, stats, use_web_search)
                    if answer:
                        st.success("Response generated!")
                        st.write("Answer:", answer)
        if 'results' not in st.session_state:
            st.session_state.results = pd.DataFrame()

        # Display results in table
        st.subheader("Analysis Results")
        if not st.session_state.results.empty:
            st.dataframe(st.session_state.results)
            
            # Download CSV button
            csv = st.session_state.results.to_csv(index=False)
            st.download_button(
                label="Download Results as CSV",
                data=csv,
                file_name="analysis_results.csv",
                mime="text/csv"
            )
        
            

if __name__ == "__main__":
    main()