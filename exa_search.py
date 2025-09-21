"""
Exa.ai search integration for regulatory and legal research.
"""

import os
from typing import List
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def search_regulatory_hints(contract_type: str, country: str) -> List[str]:
    """
    Search for regulatory hints using Exa.ai.
    
    Args:
        contract_type: Type of contract (e.g., "NDA", "MSA")
        country: Governing law country
        
    Returns:
        List[str]: List of regulatory hints and legal considerations
    """
    try:
        # For now, return some basic regulatory hints based on contract type and country
        # In a full implementation, this would use the Exa API
        
        hints = []
        
        # Contract type specific hints
        if contract_type == "NDA":
            hints.extend([
                "Ensure confidentiality period is reasonable and enforceable",
                "Consider mutual vs unilateral disclosure obligations",
                "Include proper exceptions for publicly available information"
            ])
        elif contract_type == "Employment":
            hints.extend([
                "Verify compliance with local employment laws",
                "Check non-compete clause enforceability",
                "Ensure proper termination procedures"
            ])
        elif contract_type == "MSA":
            hints.extend([
                "Include clear scope of work definitions",
                "Specify payment terms and dispute resolution",
                "Address intellectual property ownership"
            ])
        
        # Country specific hints
        if "California" in country or "United States" in country:
            hints.extend([
                "Consider California's strict non-compete restrictions",
                "Ensure compliance with US data privacy laws",
                "Review indemnification clause enforceability"
            ])
        elif "United Kingdom" in country or "UK" in country:
            hints.extend([
                "Consider GDPR compliance requirements",
                "Review unfair contract terms regulations",
                "Ensure proper governing law clauses"
            ])
        
        # General hints
        hints.extend([
            "Review limitation of liability clauses for reasonableness",
            "Ensure termination clauses are clearly defined",
            "Consider force majeure provisions"
        ])
        
        return hints[:5]  # Return top 5 hints
        
    except Exception as e:
        print(f"Error in regulatory search: {e}")
        return [
            "Review contract with qualified legal counsel",
            "Ensure compliance with applicable local laws",
            "Consider industry-specific regulations"
        ]
