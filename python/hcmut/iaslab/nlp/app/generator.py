from nltk import CFG
import random
import io
def generate_sentence(grammar:CFG, symbol):
    """
    Hàm đệ quy để sinh một câu/cụm từ ngẫu nhiên
    từ một ký hiệu (symbol) cho trước trong văn phạm.
    """
    # Lấy tất cả các quy tắc (productions) cho symbol này
    productions = grammar.productions(lhs=symbol)
    # Chọn ngẫu nhiên một quy tắc
    production = random.choice(productions)
    
    sentence_parts = []
    for sym in production.rhs():
        if isinstance(sym, str):
            # Nếu là terminal (từ vựng), thêm vào câu
            sentence_parts.append(sym)
        else:
            # Nếu là non-terminal (ký hiệu), gọi đệ quy
            sentence_parts.append(generate_sentence(grammar, sym))
            
    return " ".join(sentence_parts)

def generate_sentences(grammar:CFG, SAMPLES_FILE, max_sentences=10000):
    """
    Sinh câu ngẫu nhiên từ văn phạm và lưu vào file.
    Giới hạn tối đa 10,000 câu.
    """
    print(f"--- 2.2: Sinh câu mẫu ra file {SAMPLES_FILE} ---")
    
    generated_sentences = set()
    
    # Thử sinh 50,000 lần để đạt được tối đa 10,000 câu *duy nhất*
    # Văn phạm nhỏ có thể không sinh đủ 10,000 câu duy nhất
    attempts = 0
    max_attempts = max_sentences 

    while len(generated_sentences) < max_sentences and attempts < max_attempts:
        sentence = generate_sentence(grammar, grammar.start())
        # Chuẩn hóa khoảng trắng (vd: " quán... " -> "quán...")
        sentence_normalized = " ".join(sentence.split())
        if sentence_normalized:
            generated_sentences.add(sentence_normalized)
        attempts += 1

    # Ghi các câu đã sinh ra file
    with io.open(SAMPLES_FILE, "w", encoding="utf-8") as f:
        for sentence in generated_sentences:
            f.write(sentence + "\n")
            
    print(f"Đã sinh {len(generated_sentences)} câu duy nhất vào file: {SAMPLES_FILE}\n")