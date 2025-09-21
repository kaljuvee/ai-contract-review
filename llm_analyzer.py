"""
LLM-based contract analysis using OpenAI and LangChain.
"""

import os
import json
from typing import Dict, List, Optional
from langchain_openai import ChatOpenAI
from langchain.prompts import ChatPromptTemplate
from pydantic import BaseModel, Field
from dotenv import load_dotenv
from prompts.contract_analysis import (
    CONTRACT_TYPE_DETECTION_PROMPT,
    GOVERNING_LAW_DETECTION_PROMPT,
    KEY_CLAUSES_EXTRACTION_PROMPT,
    CLAUSE_RISK_ASSESSMENT_PROMPT
)

# Load environment variables
load_dotenv()

# Initialize OpenAI model
model = ChatOpenAI(
    model="gpt-4o-mini",
    temperature=0,
    api_key=os.getenv("OPENAI_API_KEY")
)


class ClauseInfo(BaseModel):
    """Information about a contract clause."""
    text: str = Field(description="Exact text of the clause")
    summary: str = Field(description="Brief summary of the clause")


class ClauseRiskAssessment(BaseModel):
    """Risk assessment for a contract clause."""
    risk_level: str = Field(description="Risk level: high, medium, or low")
    issues: List[str] = Field(description="List of specific issues")
    recommendations: List[str] = Field(description="List of recommended changes")
    explanation: str = Field(description="Detailed explanation of the assessment")


def detect_contract_type_llm(text: str) -> str:
    """
    Detect contract type using LLM.
    
    Args:
        text: Contract text content
        
    Returns:
        str: Detected contract type
    """
    try:
        # Limit text length to avoid token limits
        text_sample = text[:4000] if len(text) > 4000 else text
        
        prompt = ChatPromptTemplate.from_template(CONTRACT_TYPE_DETECTION_PROMPT)
        response = model.invoke(prompt.format(text=text_sample))
        
        contract_type = response.content.strip()
        
        # Validate response
        valid_types = ["NDA", "DPA", "Employment", "MSA", "SLA", "License", "Purchase", "Lease", "Commercial"]
        if contract_type in valid_types:
            return contract_type
        else:
            return "Commercial"  # Default fallback
            
    except Exception as e:
        print(f"Error in contract type detection: {e}")
        return "Commercial"


def detect_governing_law_llm(text: str) -> str:
    """
    Detect governing law using LLM.
    
    Args:
        text: Contract text content
        
    Returns:
        str: Detected governing law or "Unknown"
    """
    try:
        # Limit text length to avoid token limits
        text_sample = text[:4000] if len(text) > 4000 else text
        
        prompt = ChatPromptTemplate.from_template(GOVERNING_LAW_DETECTION_PROMPT)
        response = model.invoke(prompt.format(text=text_sample))
        
        governing_law = response.content.strip()
        
        # Clean up common variations
        if governing_law.lower() in ["unknown", "not specified", "not mentioned", "none"]:
            return "Unknown"
        
        return governing_law
        
    except Exception as e:
        print(f"Error in governing law detection: {e}")
        return "Unknown"


def extract_key_clauses_llm(text: str) -> Dict[str, ClauseInfo]:
    """
    Extract key clauses using LLM.
    
    Args:
        text: Contract text content
        
    Returns:
        Dict[str, ClauseInfo]: Dictionary of clause types and their information
    """
    try:
        # For longer texts, we might need to process in chunks
        # For now, limit to first 6000 characters
        text_sample = text[:6000] if len(text) > 6000 else text
        
        prompt = ChatPromptTemplate.from_template(KEY_CLAUSES_EXTRACTION_PROMPT)
        response = model.invoke(prompt.format(text=text_sample))
        
        # Parse JSON response
        try:
            clauses_data = json.loads(response.content)
            clauses = {}
            
            for clause_type, clause_info in clauses_data.items():
                if isinstance(clause_info, dict) and "text" in clause_info:
                    clauses[clause_type] = ClauseInfo(
                        text=clause_info.get("text", ""),
                        summary=clause_info.get("summary", "")
                    )
            
            return clauses
            
        except json.JSONDecodeError as e:
            print(f"Error parsing JSON response: {e}")
            print(f"Response content: {response.content}")
            return {}
            
    except Exception as e:
        print(f"Error in key clauses extraction: {e}")
        return {}


def assess_clause_risk_llm(clause_text: str, contract_type: str, governing_law: str) -> Optional[ClauseRiskAssessment]:
    """
    Assess risk level of a specific clause using LLM.
    
    Args:
        clause_text: Text of the clause to assess
        contract_type: Type of contract
        governing_law: Governing law
        
    Returns:
        ClauseRiskAssessment: Risk assessment or None if failed
    """
    try:
        prompt = ChatPromptTemplate.from_template(CLAUSE_RISK_ASSESSMENT_PROMPT)
        response = model.invoke(prompt.format(
            clause_text=clause_text,
            contract_type=contract_type,
            governing_law=governing_law
        ))
        
        # Parse JSON response
        try:
            response_content = response.content.strip()
            
            # Try to extract JSON if it's embedded in other text
            if "{" in response_content and "}" in response_content:
                start = response_content.find("{")
                end = response_content.rfind("}") + 1
                json_str = response_content[start:end]
                assessment_data = json.loads(json_str)
            else:
                assessment_data = json.loads(response_content)
            
            return ClauseRiskAssessment(
                risk_level=assessment_data.get("risk_level", "medium"),
                issues=assessment_data.get("issues", []),
                recommendations=assessment_data.get("recommendations", []),
                explanation=assessment_data.get("explanation", "")
            )
            
        except (json.JSONDecodeError, ValueError) as e:
            print(f"Error parsing risk assessment JSON: {e}")
            print(f"Response content: {response.content}")
            # Return a default assessment instead of None
            return ClauseRiskAssessment(
                risk_level="medium",
                issues=["Unable to parse detailed risk assessment"],
                recommendations=["Review this clause manually"],
                explanation="Automated risk assessment failed"
            )
            
    except Exception as e:
        print(f"Error in clause risk assessment: {e}")
        return None


def analyze_contract_comprehensive(text: str) -> Dict:
    """
    Perform comprehensive contract analysis using LLM.
    
    Args:
        text: Contract text content
        
    Returns:
        Dict: Comprehensive analysis results
    """
    print("🤖 Starting LLM-based contract analysis...")
    
    # Step 1: Detect contract type
    print("📋 Detecting contract type...")
    contract_type = detect_contract_type_llm(text)
    
    # Step 2: Detect governing law
    print("⚖️ Detecting governing law...")
    governing_law = detect_governing_law_llm(text)
    
    # Step 3: Extract key clauses
    print("🔍 Extracting key clauses...")
    key_clauses = extract_key_clauses_llm(text)
    
    # Step 4: Assess risks for each clause (optional, can be resource intensive)
    clause_risks = {}
    for clause_type, clause_info in key_clauses.items():
        if len(clause_info.text) > 100:  # Only assess substantial clauses
            print(f"⚠️ Assessing risk for {clause_type} clause...")
            risk_assessment = assess_clause_risk_llm(
                clause_info.text, 
                contract_type, 
                governing_law
            )
            if risk_assessment:
                clause_risks[clause_type] = risk_assessment
    
    return {
        "contract_type": contract_type,
        "governing_law": governing_law,
        "key_clauses": key_clauses,
        "clause_risks": clause_risks
    }
