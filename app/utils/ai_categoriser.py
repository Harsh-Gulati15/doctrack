import json
import os
from flask import current_app
from app.models import db, Department, User


def categorise_document(ocr_text):
    """Use Gemini AI to categorise a document based on OCR text.
    
    Returns dict with keys:
        - suggested_department_code: str
        - suggested_department_id: int or None
        - suggested_user_id: int or None
        - document_type: str
        - confidence_score: float
        - reasoning: str
        - auto_route: bool
    """
    departments = Department.query.filter_by(is_active=True).all()
    if not departments:
        return _fallback_result(ocr_text)
    
    dept_list = '\n'.join([
        f'- {d.department_code}: {d.department_name}' for d in departments
    ])
    
    api_key = current_app.config.get('GEMINI_API_KEY')
    threshold = current_app.config.get('AI_CONFIDENCE_THRESHOLD', 0.75)
    
    if not api_key:
        current_app.logger.warning('GEMINI_API_KEY not set, using keyword fallback')
        return _fallback_result(ocr_text)
    
    try:
        import google.generativeai as genai
        genai.configure(api_key=api_key)
        
        prompt = f"""You are a document classification assistant for a government office.
The following text was extracted from an incoming physical document:
---
{ocr_text[:4000]}
---
The office has the following departments:
{dept_list}
Analyse the document text and return ONLY a valid JSON object with these keys:
- suggested_department_code: the department code most likely to be the intended recipient
- suggested_recipient_hint: any name or designation mentioned as addressee (null if not found)
- document_type: one of [circular, legal_notice, tender, bill, correspondence, audit, other]
- confidence_score: float between 0 and 1
- reasoning: one sentence explaining your suggestion
Return only the JSON. No explanation outside the JSON."""
        
        model = genai.GenerativeModel('gemini-1.5-flash')
        response = model.generate_content(prompt)
        
        # Parse JSON from response
        response_text = response.text.strip()
        # Remove markdown code fences if present
        if response_text.startswith('```'):
            lines = response_text.split('\n')
            response_text = '\n'.join(lines[1:-1])
        
        result = json.loads(response_text)
        
        # Map department code to department_id
        dept_code = result.get('suggested_department_code', '')
        dept = Department.query.filter_by(department_code=dept_code, is_active=True).first()
        
        suggested_dept_id = dept.department_id if dept else None
        suggested_user_id = None
        
        if dept:
            # Find a user in this department
            user = User.query.filter_by(
                department_id=dept.department_id, is_active=True, role='dept_user'
            ).first()
            if user:
                suggested_user_id = user.user_id
        
        confidence = float(result.get('confidence_score', 0.0))
        doc_type = result.get('document_type', 'other')
        valid_types = ['circular', 'legal_notice', 'tender', 'bill',
                       'correspondence', 'audit', 'other']
        if doc_type not in valid_types:
            doc_type = 'other'
        
        return {
            'suggested_department_code': dept_code,
            'suggested_department_id': suggested_dept_id,
            'suggested_user_id': suggested_user_id,
            'document_type': doc_type,
            'confidence_score': confidence,
            'reasoning': result.get('reasoning', 'AI analysis complete.'),
            'auto_route': confidence >= threshold and suggested_dept_id is not None and suggested_user_id is not None
        }
        
    except Exception as e:
        current_app.logger.error(f'Gemini API failed: {e}')
        return _fallback_result(ocr_text)


def _fallback_result(ocr_text):
    """Keyword-based fallback when AI is unavailable."""
    departments = Department.query.filter_by(is_active=True).all()
    text_lower = (ocr_text or '').lower()
    
    # Keyword matching
    best_dept = None
    best_score = 0
    
    keywords_map = {
        'finance': ['finance', 'budget', 'expenditure', 'payment', 'bill', 'invoice',
                    'salary', 'accounts', 'audit', 'revenue', 'tax'],
        'hr': ['human resource', 'hr', 'recruitment', 'employee', 'staff',
               'leave', 'transfer', 'posting', 'pension', 'retirement'],
        'it': ['information technology', 'it ', 'computer', 'software', 'hardware',
               'network', 'server', 'database', 'website', 'digital', 'cyber'],
        'legal': ['legal', 'law', 'court', 'notice', 'petition', 'case',
                  'advocate', 'judgment', 'order', 'compliance'],
    }
    
    for dept in departments:
        dept_name_lower = dept.department_name.lower()
        dept_code_lower = dept.department_code.lower()
        score = 0
        
        # Direct name/code match
        if dept_name_lower in text_lower or dept_code_lower in text_lower:
            score += 5
        
        # Keyword matching
        for key, words in keywords_map.items():
            if key in dept_name_lower or key in dept_code_lower:
                for word in words:
                    if word in text_lower:
                        score += 1
        
        if score > best_score:
            best_score = score
            best_dept = dept
    
    # Determine document type from keywords
    doc_type = 'other'
    type_keywords = {
        'circular': ['circular', 'memorandum', 'memo', 'notification', 'office order'],
        'legal_notice': ['legal notice', 'court', 'summons', 'petition', 'writ'],
        'tender': ['tender', 'bid', 'quotation', 'rfp', 'request for proposal'],
        'bill': ['bill', 'invoice', 'payment', 'amount due', 'receipt'],
        'correspondence': ['letter', 'correspondence', 'communication', 'ref no'],
        'audit': ['audit', 'inspection', 'compliance', 'review report'],
    }
    for dtype, words in type_keywords.items():
        for word in words:
            if word in text_lower:
                doc_type = dtype
                break
    
    suggested_user_id = None
    if best_dept:
        user = User.query.filter_by(
            department_id=best_dept.department_id, is_active=True, role='dept_user'
        ).first()
        if user:
            suggested_user_id = user.user_id
    
    confidence = min(best_score * 0.15, 0.6) if best_dept else 0.1
    
    return {
        'suggested_department_code': best_dept.department_code if best_dept else '',
        'suggested_department_id': best_dept.department_id if best_dept else None,
        'suggested_user_id': suggested_user_id,
        'document_type': doc_type,
        'confidence_score': confidence,
        'reasoning': 'Categorised using keyword matching (AI unavailable).',
        'auto_route': False  # Never auto-route with fallback
    }
