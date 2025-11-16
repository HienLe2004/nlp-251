from nltk import CFG
import os
import io
from grammar import write_grammar
from generator import generate_sentences
from parser import build_parser

OUTPUT_DIR = "output"
INPUT_DIR = "input"
GRAMMAR_FILE = os.path.join(OUTPUT_DIR, "grammar.txt")
SAMPLES_FILE = os.path.join(OUTPUT_DIR, "samples.txt")
INPUT_SENTENCES_FILE = os.path.join(INPUT_DIR, "sentences.txt")
PARSE_RESULTS_FILE = os.path.join(OUTPUT_DIR, "parse-results.txt")

def main():
    # Tạo các thư mục và file input mẫu 
    print("Khởi tạo môi trường")
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    os.makedirs(INPUT_DIR, exist_ok=True)

    # 2.1: Tạo Grammar 
    grammar_str = write_grammar(GRAMMAR_FILE)
    
    # Load grammar từ string
    try:
        grammar:CFG = CFG.fromstring(grammar_str)
    except ValueError as e:
        print(f"Lỗi khi nạp văn phạm: {e}")
        return

    # 2.2: Sinh câu 
    generate_sentences(grammar, SAMPLES_FILE, max_sentences=10000)

    # 2.3: Phân tích cú pháp 
    build_parser(grammar, INPUT_SENTENCES_FILE, PARSE_RESULTS_FILE)

    print("HOÀN TẤT")
    print(f"Kiểm tra kết quả trong thư mục '{OUTPUT_DIR}'.")

if __name__ == "__main__":
    main()