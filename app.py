
import os
import io
import pandas as pd
import streamlit as st
import plotly.express as px
from dotenv import load_dotenv
from google import genai

load_dotenv()
st.set_page_config(page_title="AnalystGPT", layout="wide")

api=os.getenv("GEMINI_API_KEY","")
client=genai.Client(api_key=api) if api else None

st.title("🤖 AnalystGPT")

st.caption(
    "AI-Powered Business Intelligence Platform | Upload • Analyze • Visualize • Chat with Data"
)

def ai(prompt):
    if not client:
        return "Missing GEMINI_API_KEY."
    try:
        resp=client.models.generate_content(
            model="models/gemini-3.6-flash",
            contents=prompt
        )
        return resp.text
    except Exception as e:
        return f"AI Error: {e}"

up=st.file_uploader("Upload CSV or Excel",type=["csv","xlsx"])
if up:
    try:
        if up.name.endswith(".csv"):
            df=pd.read_csv(up)
        else:
            df=pd.read_excel(up)
    except Exception as e:
        st.error(str(e)); st.stop()

    c1,c2,c3,c4=st.columns(4)
    c1.metric("Rows",len(df))
    c2.metric("Columns",len(df.columns))
    c3.metric("Missing",int(df.isna().sum().sum()))
    c4.metric("Duplicates",int(df.duplicated().sum()))

    st.subheader("Preview")
    st.dataframe(df,use_container_width=True)

    st.subheader("Column Information")
    info=pd.DataFrame({
        "Column":df.columns,
        "Type":[str(t) for t in df.dtypes],
        "Missing":df.isna().sum().values,
        "Unique":df.nunique().values
    })
    st.dataframe(info,use_container_width=True)

    nums=df.select_dtypes(include="number").columns.tolist()
    cats=df.select_dtypes(exclude="number").columns.tolist()

    st.subheader("Automatic Charts")
    if nums:
        n=st.selectbox("Numeric Column",nums)
        col1,col2=st.columns(2)
        with col1:
            st.plotly_chart(px.histogram(df,x=n),use_container_width=True)
        with col2:
            st.plotly_chart(px.box(df,y=n),use_container_width=True)
    if cats:
        c=st.selectbox("Category Column",cats)
        vc=df[c].value_counts().head(15).reset_index()
        vc.columns=[c,"Count"]
        st.plotly_chart(px.bar(vc,x=c,y="Count"),use_container_width=True)

    st.subheader("AI Business Analysis")
    if st.button("Generate Analysis"):
        summary=f"""
Dataset shape:{df.shape}
Columns:{list(df.columns)}
Dtypes:{df.dtypes.astype(str).to_dict()}
Missing:{df.isna().sum().to_dict()}
Describe:
{df.describe(include='all').fillna('').to_string()}
"""
        prompt = f"""
You are an expert Chief Business Intelligence Officer with 15+ years of experience.

Analyze the dataset like a senior consultant at McKinsey, BCG, Deloitte, or Accenture.

Use the provided dataset summary to generate a professional business report.

Dataset Information:
{summary}

Generate the report using the following structure:

# 📌 Executive Summary
Provide a concise overview of the business performance.

# 📊 Key Business Insights
Identify the most important trends, opportunities, and risks.

# 📈 KPI Highlights
Mention important metrics whenever possible.

# ⚠️ Risks & Challenges
Explain what is hurting the business.

# 💡 Strategic Recommendations
Provide actionable recommendations with expected business impact.

# 🧹 Data Quality Assessment
Mention missing values, inconsistent data, datatype issues, duplicates, and improvements.

Keep the report professional, concise, and suitable for executive leadership.
"""
        with st.spinner("🤖 AnalystGPT Ash is analyzing your business data..."):
            report = ai(prompt)
            st.markdown(report)
            st.download_button(
        "📥 Download AI Report",
        report,
        file_name="AnalystGPT_Report.md",
        mime="text/markdown"
    )

    st.subheader("💬 Chat with Dataset")
    q = st.text_input("Ask a business question")
    if st.button("Ask AI", use_container_width=True):
        if q.strip():
            summary = []

            summary.append(f"Dataset Shape: {df.shape[0]} rows × {df.shape[1]} columns")
            summary.append(f"Columns: {', '.join(df.columns)}")

            summary.append("\nMissing Values:")
            summary.append(df.isnull().sum().to_string())

            summary.append("\nNumeric Statistics:")
            summary.append(
                df.describe(include="number").round(2).to_string()
            )

            cat_cols = df.select_dtypes(include="object").columns

            summary.append("\nTop Categories:")

            for col in cat_cols[:8]:
                summary.append(f"\n{col}")
                summary.append(
                    df[col].value_counts().head(5).to_string()
                )

            if "Sales" in df.columns:
                summary.append(
                    f"\nTotal Sales: ${df['Sales'].sum():,.2f}"
                )

            if "Profit" in df.columns:
                summary.append(
                    f"Total Profit: ${df['Profit'].sum():,.2f}"
                )

            if "Discount" in df.columns:
                summary.append(
                    f"Average Discount: {df['Discount'].mean()*100:.2f}%"
                )

            if "Quantity" in df.columns:
                summary.append(
                    f"Total Quantity Sold: {df['Quantity'].sum():,.0f}"
                )

            dataset_context = "\n".join(summary)

            prompt = f"""
    You are a Senior Business Intelligence Consultant.

    You have access to a summarized profile of the dataset.

    Dataset Summary:

    {dataset_context}

    Question:

    {q}

    Answer professionally.

    Explain your reasoning.

    Provide actionable business recommendations whenever appropriate.
    """

            with st.spinner("🤖 AnalystGPT is analyzing your dataset..."):

                report = ai(prompt)
                st.markdown(report)
                st.download_button(
        "📥 Download AI Report",
        report,
        file_name="AnalystGPT_Report.md",
        mime="text/markdown")

        else:

            st.warning("Please enter a question.")
else:
    st.info("Upload a CSV or Excel dataset to begin.")
