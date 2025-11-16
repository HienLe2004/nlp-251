import re
from nltk import CFG

def get_terminals(grammar:CFG):
    """
    Trích xuất tất cả các từ vựng (terminals) từ văn phạm.
    """
    terminals = set()
    for production in grammar.productions():
        if production.is_lexical():
            for term in production.rhs():
                terminals.add(term)
    return sorted(list(terminals), key=len, reverse=True)

def preprocess_text(text:str):
    """
    Tiền xử lý văn bản (chữ thường, xóa dấu câu, khoảng trắng)
    """
    text = text.lower()
    text = re.sub(r'[.,!?:;]', '', text) 
    text = re.sub(r'[\n\t]', ' ', text)
    text = re.sub(r'\s+', ' ', text).strip()
    return text

def custom_tokenizer(sentence:str, terminals):
    """
    Hàm tham lam để tokenize câu dựa trên các
    từ vựng đã định nghĩa trong văn phạm.
    """
    sentence = preprocess_text(sentence) # Chuẩn hóa
    tokens = []
    while sentence:
        found_match = False
        for term in terminals:
            if sentence.startswith(term):
                tokens.append(term)
                # Cắt bỏ phần đã khớp và khoảng trắng sau nó
                sentence = sentence[len(term):].strip() 
                found_match = True
                break

        
        if not found_match:
            return None # Trả về None để báo lỗi
            
    return tokens