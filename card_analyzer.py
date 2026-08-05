import re

def analyze_card_text(text):
    """
    تحليل تفصيلي لكل حرف ورمز وحقل داخل البطاقة (هوية، بنك، أو بطاقة شخصية)
    """
    if not text or not text.strip():
        return {"error": "النص فارغ أو غير مقروء"}

    # تنظيف النص واستخراج كل كلمة وحرف
    cleaned_text = text.strip()
    
    # استخراج الأرقام الطويلة (مثل أرقام البطاقات أو الحسابات)
    card_numbers = re.findall(r'\b(?:\d[ -]*){13,19}\b', cleaned_text)
    
    # استخراج تواريخ انتهاء الصلاحية (مثل MM/YY أو MM-YYYY)
    expiry_dates = re.findall(r'\b(0[1-9]|1[0-2])[-/]([0-9]{2,4})\b', cleaned_text)
    
    # استخراج الكلمات الحرفية الكبيرة (غالباً الاسم أو البنك أو الجهة)
    capital_words = re.findall(r'\b[A-Z][A-Z\s]{2,}\b', cleaned_text)
    
    # استخراج الحروف والأرقام المختلطة (مثل الرقم التسلسلي أو الـ CVV)
    alpha_numerics = re.findall(r'\b[A-Z0-9]{3,12}\b', cleaned_text)

    return {
        "raw_length": len(cleaned_text),
        "card_numbers": [n.strip() for n in card_numbers],
        "expiry_dates": [f"{m}/{y}" for m, y in expiry_dates],
        "names_or_entities": [w.strip() for w in capital_words if len(w.strip()) > 3][:3],
        "codes": [an for an in alpha_numerics if not an.isdigit()][:4],
        "full_text_preview": cleaned_text[:300]  # عينة من النص المستخرج حرفياً
    }
