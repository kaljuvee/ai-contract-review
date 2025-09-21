"""
LangChain integration for AI-powered contract review.
"""

import os
from typing import List
from pydantic import BaseModel, Field
from langchain_openai import ChatOpenAI
from langchain.prompts import ChatPromptTemplate
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Initialize OpenAI model
model = ChatOpenAI(
    model="gpt-4o-mini",
    temperature=0,
    api_key=os.getenv("OPENAI_API_KEY")
)

class RiskItem(BaseModel):
    """Represents a risk identified in a contract."""
    text: str = Field(description="The problematic text from the contract")
    issue: str = Field(description="Description of the issue")
    suggestion: str = Field(description="Suggested improvement")
    risk_level: str = Field(description="Risk level: high, medium, or low")

RISK_ANALYSIS_PROMPT = """You are an expert contract attorney. Analyze the following contract text and identify potential risks and issues.

Contract Type: {contract_type}
Governing Law: {country}
Regulatory Hints: {regulatory_hints}

Contract Text:
{text}

Please identify specific risks in the contract. For each risk, provide:
1. The exact problematic text from the contract
2. A clear description of the issue
3. A specific suggestion for improvement
4. A risk level (high, medium, or low)

Focus on:
- Unusual or one-sided terms
- Missing standard protections
- Overly broad language
- Compliance issues with the governing law
- Industry best practices

Return your analysis as a structured list of risks. If no significant risks are found, return an empty list.

Example format:
Risk 1: [problematic text] - Issue: [description] - Suggestion: [improvement] - Level: [high/medium/low]
"""

def llm_review(text: str, contract_type: str, country: str, regulatory_hints: List[str]) -> List[RiskItem]:
    """
    Perform LLM-based contract review to identify risks.
    
    Args:
        text: Contract text content
        contract_type: Type of contract
        country: Governing law country
        regulatory_hints: List of regulatory considerations
        
    Returns:
        List[RiskItem]: List of identified risks
    """
    try:
        # Limit text length to avoid token limits
        text_sample = text[:8000] if len(text) > 8000 else text
        
        # Format regulatory hints
        hints_text = "\n".join(f"- {hint}" for hint in regulatory_hints)
        
        prompt = ChatPromptTemplate.from_template(RISK_ANALYSIS_PROMPT)
        response = model.invoke(prompt.format(
            text=text_sample,
            contract_type=contract_type,
            country=country,
            regulatory_hints=hints_text
        ))
        
        # Parse the response to extract risks
        risks = []
        response_text = response.content.strip()
        
        if not response_text or "no significant risks" in response_text.lower():
            return risks
        
        # Simple parsing of the response
        lines = response_text.split('\n')
        current_risk = {}
        
        for line in lines:
            line = line.strip()
            if not line:
                continue
                
            if line.startswith('Risk') and ':' in line:
                # New risk found, save previous if exists
                if current_risk:
                    risks.append(create_risk_item(current_risk))
                    current_risk = {}
                
                # Parse the risk line
                parts = line.split(' - ')
                if len(parts) >= 4:
                    text_part = parts[0].split(': ', 1)[1] if ': ' in parts[0] else ""
                    issue_part = parts[1].replace('Issue: ', '') if parts[1].startswith('Issue: ') else parts[1]
                    suggestion_part = parts[2].replace('Suggestion: ', '') if parts[2].startswith('Suggestion: ') else parts[2]
                    level_part = parts[3].replace('Level: ', '') if parts[3].startswith('Level: ') else parts[3]
                    
                    current_risk = {
                        'text': text_part.strip(),
                        'issue': issue_part.strip(),
                        'suggestion': suggestion_part.strip(),
                        'risk_level': level_part.strip().lower()
                    }
        
        # Add the last risk if exists
        if current_risk:
            risks.append(create_risk_item(current_risk))
        
        # If parsing failed, create a general risk
        if not risks and response_text:
            risks.append(RiskItem(
                text="General contract review",
                issue="Contract requires detailed legal review",
                suggestion="Have this contract reviewed by qualified legal counsel",
                risk_level="medium"
            ))
        
        return risks
        
    except Exception as e:
        print(f"Error in LLM review: {e}")
        return [
            RiskItem(
                text="Contract analysis error",
                issue="Unable to complete automated analysis",
                suggestion="Please review this contract manually with legal counsel",
                risk_level="medium"
            )
        ]

def create_risk_item(risk_data: dict) -> RiskItem:
    """Create a RiskItem from parsed data."""
    return RiskItem(
        text=risk_data.get('text', 'Unknown text'),
        issue=risk_data.get('issue', 'Issue identified'),
        suggestion=risk_data.get('suggestion', 'Review with legal counsel'),
        risk_level=risk_data.get('risk_level', 'medium')
    )
