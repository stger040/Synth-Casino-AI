import streamlit as st
import pandas as pd
import openai
import os
import matplotlib.pyplot as plt
from dotenv import load_dotenv

# Load API key from .env file
load_dotenv()
openai.api_key = os.getenv("OPENAI_API_KEY")

# Load dataset
casino_df = pd.read_csv("IntelliCasino_Finances.csv")

# Generate data summary
data_summary = casino_df.describe().to_string()

# Streamlit App UI
st.title("🎰 Casino AI Chatbot")
st.write("Ask the AI questions about the casino's revenue, hotel occupancy, and trends.")

st.write("Example questions you can ask:")
st.write("- What was the highest slot revenue recorded in the past year?")
st.write("- Compare hotel occupancy on weekends versus weekdays.")
st.write("- How does player retention rate impact total revenue?")
st.write("- Show a line chart of total revenue trends over the last 6 months.")
st.write("- Generate a bar chart comparing food & beverage revenue vs. costs.")
st.write("- Create a new column analyzing profit margins over time.")

# Spacer to push input box to the bottom
st.write("\n" * 15)

# User input field at the bottom
user_query = st.text_input("Enter your question:", key="user_input")

# Function to generate charts based on user request
def generate_chart(chart_type, x_data, y_data, title, xlabel, ylabel, line_color='blue', marker_color='blue'):
    fig, ax = plt.subplots(figsize=(10, 5))  # Adjust size for better readability
    
    if chart_type == "line":
        ax.plot(x_data, y_data, marker='o', linestyle='-', color=line_color, markerfacecolor=marker_color)
    elif chart_type == "bar":
        ax.bar(x_data, y_data, color=line_color)
    
    ax.set_title(title)
    ax.set_xlabel(xlabel)
    ax.set_ylabel(ylabel)
    ax.tick_params(axis='x', rotation=45)  # Rotate x-axis labels for better visibility
    
    # Save figure for download
    image_path = "chart.png"
    fig.savefig(image_path)
    st.pyplot(fig)
    
    # Provide download link
    with open(image_path, "rb") as file:
        btn = st.download_button(
            label="Download Chart",
            data=file,
            file_name="casino_chart.png",
            mime="image/png"
        )

# Function to query OpenAI
def query_llm(prompt):
    client = openai.OpenAI()
    response = client.chat.completions.create(
        model="gpt-4",
        messages=[{"role": "system", "content": "You are an AI assistant for casino finance analysis."},
                  {"role": "user", "content": prompt}]
    )
    return response.choices[0].message.content

# Handle user query
if user_query:
    formatted_prompt = f"""
    You are an AI analyzing casino financial data. Below is a summary of the dataset:

    {data_summary}

    If the user asks for a data visualization, specify:
    - The chart type (line, bar, scatter, etc.).
    - The column to use for X and Y axes.
    - A brief title and axis labels.
    - If the user requests a modification to a previous chart, adjust the parameters accordingly.
    - If the user specifies colors, provide the requested line and marker colors.
    
    If the user asks for dataset modifications, specify:
    - The new column to be created.
    - The transformation or calculation required.
    - How this new column helps in analysis.

    User query: {user_query}
    """
    
    response = query_llm(formatted_prompt)
    
    line_color = 'blue'
    marker_color = 'blue'
    
    if "red" in user_query.lower():
        line_color = "red"
    if "purple" in user_query.lower():
        marker_color = "purple"
    
    if "line chart" in user_query.lower():
        generate_chart("line", casino_df["Date"], casino_df["Slot Revenue"], "Slot Revenue Over Time", "Date", "Revenue", line_color, marker_color)
    elif "bar chart" in user_query.lower():
        generate_chart("bar", casino_df["Date"], casino_df["Hotel Occupancy (%)"], "Hotel Occupancy by Day", "Date", "Occupancy (%)", line_color)
    elif "seasonality" in user_query.lower():
        casino_df["Seasonality"] = casino_df["Slot Revenue"].rolling(window=7).mean()
        st.write("New column 'Seasonality' has been added to the dataset!")
        st.write(casino_df.head())
    else:
        st.write("**Response:**", response)
