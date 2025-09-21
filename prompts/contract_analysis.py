"""
LLM prompts for contract analysis tasks.
"""

CONTRACT_TYPE_DETECTION_PROMPT = """You are an expert contract analyst. Analyze the following contract text and determine its type.

Contract types to consider:
- NDA (Non-Disclosure Agreement)
- DPA (Data Processing Agreement) 
- Employment (Employment Contract)
- MSA (Master Service Agreement)
- SLA (Service Level Agreement)
- License (License Agreement)
- Purchase (Purchase Agreement)
- Lease (Lease Agreement)
- Commercial (General Commercial Contract)

Return only the contract type from the list above, nothing else.

Contract text:
{text}

Contract type:"""

GOVERNING_LAW_DETECTION_PROMPT = """You are an expert contract analyst. Analyze the following contract text and identify the governing law or jurisdiction.

Look for phrases like:
- "governed by the laws of"
- "subject to the laws of"
- "jurisdiction of"
- "courts of"

Return only the country or jurisdiction name (e.g., "United States", "United Kingdom", "California", "Delaware"). If no governing law is mentioned, return "Unknown".

Contract text:
{text}

Governing law:"""

KEY_CLAUSES_EXTRACTION_PROMPT = """You are an expert contract analyst. Analyze the following contract text and extract key clauses.

Identify and extract the following types of clauses if present:
1. Termination clauses
2. Liability/Limitation of liability clauses
3. Indemnification clauses
4. Confidentiality clauses
5. Governing law clauses
6. Payment terms clauses
7. Intellectual property clauses
8. Force majeure clauses
9. Dispute resolution clauses
10. Non-compete/Non-solicitation clauses

For each clause type found, provide:
- The exact text of the clause
- A brief summary of what it covers

Return your response as a JSON object with this structure:
{{
    "clause_type": {{
        "text": "exact clause text",
        "summary": "brief summary of the clause"
    }}
}}

If no clauses of a particular type are found, omit that clause type from the response.

Contract text:
{text}

Key clauses (JSON format):"""

CLAUSE_RISK_ASSESSMENT_PROMPT = """You are an expert contract attorney. Analyze the following contract clause and assess its risk level and potential issues.

Consider:
- Unusual or one-sided terms
- Missing standard protections
- Overly broad language
- Compliance issues
- Industry best practices

Clause text:
{clause_text}

Contract type: {contract_type}
Governing law: {governing_law}

Provide your assessment in JSON format:
{{
    "risk_level": "high|medium|low",
    "issues": ["list of specific issues"],
    "recommendations": ["list of recommended changes"],
    "explanation": "detailed explanation of the assessment"
}}

Risk assessment:"""
