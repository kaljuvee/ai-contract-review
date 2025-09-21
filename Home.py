"""
AI Contract Review Application - Enhanced with LLM Analysis
A Streamlit app for analyzing contracts using AI and highlighting risks.
"""

import streamlit as st
import pandas as pd
import json
import os
from typing import List
from parsers_llm import extract_text, detect_contract_type, detect_country, convert_text_to_markdown, clean_text, extract_key_clauses, analyze_contract_full
from exa_search import search_regulatory_hints
from chain import llm_review, RiskItem

# Page configuration
st.set_page_config(
    page_title="AI Contract Review",
    page_icon="📋",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for better styling
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        font-weight: bold;
        color: #1f77b4;
        text-align: center;
        margin-bottom: 2rem;
    }
    .info-box {
        background-color: #f0f2f6;
        padding: 1rem;
        border-radius: 0.5rem;
        border-left: 4px solid #1f77b4;
        margin: 1rem 0;
    }
    .risk-high {
        background-color: #ffebee;
        border-left: 4px solid #f44336;
        padding: 1rem;
        margin: 0.5rem 0;
        border-radius: 0.25rem;
    }
    .risk-medium {
        background-color: #fff3e0;
        border-left: 4px solid #ff9800;
        padding: 1rem;
        margin: 0.5rem 0;
        border-radius: 0.25rem;
    }
    .risk-low {
        background-color: #f3e5f5;
        border-left: 4px solid #9c27b0;
        padding: 1rem;
        margin: 0.5rem 0;
        border-radius: 0.25rem;
    }
</style>
""", unsafe_allow_html=True)

def highlight_risks_in_text(text: str, risks: List[RiskItem]) -> str:
    """
    Highlight risky text segments with color coding.
    
    Args:
        text: Original contract text
        risks: List of identified risks
        
    Returns:
        str: HTML with highlighted text
    """
    highlighted_text = text
    
    # Sort risks by position to avoid overlapping highlights
    sorted_risks = sorted(risks, key=lambda x: text.find(x.text) if x.text in text else 0, reverse=True)
    
    for risk in sorted_risks:
        if risk.text in highlighted_text:
            color = {
                "high": "#ffcdd2",
                "medium": "#ffe0b2", 
                "low": "#f3e5f5"
            }.get(risk.risk_level, "#f3e5f5")
            
            highlighted_text = highlighted_text.replace(
                risk.text,
                f'<mark style="background-color: {color}; padding: 2px 4px; border-radius: 3px;">{risk.text}</mark>'
            )
    
    return highlighted_text


def main():
    """Main application function."""
    
    # Header
    st.markdown('<h1 class="main-header">🤖 AI Contract Review Assistant</h1>', unsafe_allow_html=True)
    
    st.markdown("""
    <div class="info-box">
        <strong>📋 Enhanced LLM-Based Analysis:</strong><br>
        Upload your contract and get intelligent AI analysis with risk assessment, clause extraction, and improvement recommendations.
        <br><br>
        <strong>✨ New Features:</strong> LLM-powered contract type detection, governing law identification, and advanced clause analysis.
    </div>
    """, unsafe_allow_html=True)
    
    # Sidebar
    with st.sidebar:
        st.header("📁 Upload Contract")
        uploaded_file = st.file_uploader(
            "Choose a contract file",
            type=['pdf', 'docx', 'txt'],
            help="Upload PDF, DOCX, or TXT files"
        )
        
        if uploaded_file:
            st.success(f"✅ File uploaded: {uploaded_file.name}")
            st.info(f"📊 File size: {uploaded_file.size:,} bytes")
        
        st.header("ℹ️ About")
        st.markdown("""
        **AI Contract Review** uses advanced LLM analysis to:
        - 🔍 Detect contract types intelligently
        - ⚖️ Identify governing law automatically  
        - 📋 Extract key clauses with summaries
        - ⚠️ Assess individual clause risks
        - 🔗 Research regulatory information
        - 💡 Provide improvement suggestions
        """)
        
        st.header("🎯 Risk Levels")
        st.markdown("""
        - 🔴 **High Risk**: Critical issues requiring immediate attention
        - 🟠 **Medium Risk**: Important concerns to address
        - 🟡 **Low Risk**: Minor suggestions for improvement
        """)
    
    # Main content area
    if not uploaded_file:
        st.info("👆 Please upload a contract file to begin analysis.")
        
        # Sample contract for testing
        st.header("🧪 Try with Sample Contract")
        if st.button("Load Sample NDA"):
            sample_text = """
            NON-DISCLOSURE AGREEMENT
            
            This Non-Disclosure Agreement is entered into between TechCorp Inc. and DataSolutions LLC.
            
            CONFIDENTIALITY
            The Receiving Party agrees to hold and maintain the Confidential Information in strict confidence for a period of five years.
            
            TERMINATION
            This Agreement may be terminated by either party with 30 days written notice.
            
            GOVERNING LAW
            This Agreement shall be governed by and construed in accordance with the laws of the State of California.
            
            LIABILITY
            In no event shall either party be liable for any indirect, special, or consequential damages exceeding $100,000.
            """
            
            # Create a temporary file-like object for the sample
            import io
            sample_file = io.StringIO(sample_text)
            sample_file.name = "sample_nda.txt"
            
            # Process the sample
            process_contract(sample_file, sample_text)
        
        return
    
    # Process uploaded file
    with st.spinner("📄 Extracting text from document..."):
        try:
            text = extract_text(uploaded_file)
            text = clean_text(text)
            
            if not text.strip():
                st.error("❌ Could not extract text from the uploaded file. Please check the file format and try again.")
                return
                
        except Exception as e:
            st.error(f"❌ Error extracting text: {str(e)}")
            return
    
    process_contract(uploaded_file, text)


def process_contract(uploaded_file, text: str):
    """Process the contract text and display analysis results."""
    
    # Show text preview
    with st.expander("📄 Document Preview", expanded=False):
        st.text_area("Extracted Text:", text[:2000] + "..." if len(text) > 2000 else text, height=200, disabled=True)
    
    # Analyze contract using LLM
    with st.spinner("🤖 Running comprehensive LLM-based contract analysis..."):
        analysis_results = analyze_contract_full(text)
        contract_type = analysis_results.get("contract_type", "Commercial")
        country = analysis_results.get("governing_law", "Unknown")
        key_clauses_info = analysis_results.get("key_clauses", {})
        clause_risks = analysis_results.get("clause_risks", {})
        
        # Convert to format expected by UI
        key_clauses = {}
        for clause_type, clause_info in key_clauses_info.items():
            key_clauses[clause_type] = [clause_info.text]
    
    # Display analysis results
    st.markdown(f"""
    <div class="info-box">
        <strong>📊 Contract Analysis Results:</strong><br>
        <strong>Contract Type:</strong> {contract_type}<br>
        <strong>Governing Law:</strong> {country}<br>
        <strong>Key Clauses Found:</strong> {', '.join(key_clauses.keys()) if key_clauses else 'None detected'}
    </div>
    """, unsafe_allow_html=True)
    
    # Show key clauses if found
    if key_clauses_info:
        with st.expander("🔍 Key Clauses Detected (LLM Analysis)", expanded=False):
            for clause_type, clause_info in key_clauses_info.items():
                st.subheader(f"📋 {clause_type.replace('_', ' ').title()}")
                
                # Show clause summary
                if hasattr(clause_info, 'summary') and clause_info.summary:
                    st.markdown(f"**Summary:** {clause_info.summary}")
                
                # Show clause text
                clause_text = clause_info.text if hasattr(clause_info, 'text') else str(clause_info)
                st.text_area(
                    "Clause Text:", 
                    clause_text[:800] + "..." if len(clause_text) > 800 else clause_text, 
                    height=150, 
                    disabled=True, 
                    key=f"clause_{clause_type}"
                )
                
                # Show risk assessment if available
                if clause_type in clause_risks:
                    risk_info = clause_risks[clause_type]
                    risk_level = risk_info.risk_level if hasattr(risk_info, 'risk_level') else 'medium'
                    
                    # Color code risk level
                    risk_color = {"high": "🔴", "medium": "🟡", "low": "🟢"}.get(risk_level, "🟡")
                    st.markdown(f"**Risk Level:** {risk_color} {risk_level.upper()}")
                    
                    if hasattr(risk_info, 'issues') and risk_info.issues:
                        st.markdown("**Issues:**")
                        for issue in risk_info.issues:
                            st.markdown(f"• {issue}")
                    
                    if hasattr(risk_info, 'recommendations') and risk_info.recommendations:
                        st.markdown("**Recommendations:**")
                        for rec in risk_info.recommendations:
                            st.markdown(f"• {rec}")
                
                st.divider()
    
    # Perform AI review
    with st.spinner("🧠 Running AI risk analysis and regulatory search..."):
        # Get regulatory hints
        regulatory_hints = search_regulatory_hints(contract_type, country)
        
        # Perform LLM review
        risks = llm_review(text, contract_type, country, regulatory_hints)
    
    # Create two columns for results
    col1, col2 = st.columns([1, 1])
    
    with col1:
        st.header("📋 Original Contract")
        if risks:
            highlighted_text = highlight_risks_in_text(text, risks)
            st.markdown(highlighted_text, unsafe_allow_html=True)
        else:
            st.text_area("Contract Text:", text, height=600, disabled=True)
    
    with col2:
        st.header("⚠️ Risk Analysis")
        
        if not risks:
            st.info("✅ No significant risks detected in this contract.")
        else:
            # Group risks by level
            risk_counts = {"high": 0, "medium": 0, "low": 0}
            
            for risk in risks:
                risk_counts[risk.risk_level] += 1
                
                # Display risk with appropriate styling
                risk_class = f"risk-{risk.risk_level}"
                risk_icon = {"high": "🔴", "medium": "🟠", "low": "🟡"}[risk.risk_level]
                
                st.markdown(f"""
                <div class="{risk_class}">
                    <strong>{risk_icon} {risk.risk_level.upper()} RISK</strong><br>
                    <strong>Issue:</strong> {risk.issue}<br>
                    <strong>Text:</strong> "{risk.text[:200]}..."<br>
                    <strong>Suggestion:</strong> {risk.suggestion}
                </div>
                """, unsafe_allow_html=True)
    
    # Risk summary metrics
    if risks:
        st.header("📊 Risk Summary")
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric("Total Risks", len(risks), delta=None)
        with col2:
            st.metric("High Risk", risk_counts["high"], delta=None)
        with col3:
            st.metric("Medium Risk", risk_counts["medium"], delta=None)
        with col4:
            st.metric("Low Risk", risk_counts["low"], delta=None)
    
    # Download section
    st.header("💾 Download Results")
    
    col1, col2 = st.columns(2)
    
    with col1:
        # Prepare download data
        download_data = {
            "contract_analysis": {
                "filename": uploaded_file.name,
                "contract_type": contract_type,
                "governing_law": country,
                "key_clauses": list(key_clauses.keys()) if key_clauses else [],
                "analysis_date": pd.Timestamp.now().isoformat()
            },
            "risks": [risk.dict() for risk in risks],
            "summary": {
                "total_risks": len(risks),
                "high_risk_count": risk_counts.get("high", 0),
                "medium_risk_count": risk_counts.get("medium", 0),
                "low_risk_count": risk_counts.get("low", 0)
            }
        }
        
        json_str = json.dumps(download_data, indent=2)
        
        st.download_button(
            label="📥 Download Analysis (JSON)",
            data=json_str,
            file_name=f"contract_review_{uploaded_file.name}_{pd.Timestamp.now().strftime('%Y%m%d_%H%M%S')}.json",
            mime="application/json"
        )
    
    with col2:
        # Convert to markdown and offer download
        markdown_content = convert_text_to_markdown(text, f"Contract Analysis: {uploaded_file.name}")
        
        st.download_button(
            label="📄 Download as Markdown",
            data=markdown_content,
            file_name=f"contract_{uploaded_file.name}_{pd.Timestamp.now().strftime('%Y%m%d_%H%M%S')}.md",
            mime="text/markdown"
        )


if __name__ == "__main__":
    main()
