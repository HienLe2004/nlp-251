import io
from nltk import ChartParser
from utils import get_terminals, custom_tokenizer
def build_parser(grammar, input_file, output_file):
    """
    Phân tích cú pháp các câu trong input/sentences.txt
    và ghi kết quả ra output/parse-results.txt
    """
    print(f"--- 2.3: Phân tích cú pháp file {input_file} ---")
    
    parser = ChartParser(grammar)
    terminals = get_terminals(grammar)
    results = []

    try:
        with io.open(input_file, "r", encoding="utf-8") as f_in:
            sentences = f_in.readlines()
            
        for sentence in sentences:
            sentence = sentence.strip()
            if not sentence:
                continue
                
            # Tokenize câu dựa trên văn phạm
            tokens = custom_tokenizer(sentence, terminals)
            if tokens is None:
                # Lỗi tokenize (từ không xác định)
                results.append("()\n")
                continue
                
            # Phân tích cú pháp
            try:
                # parser.parse() trả về một generator
                parse_trees = list(parser.parse(tokens))
                
                if not parse_trees:
                    # Không có cây cú pháp nào hợp lệ
                    results.append("()\n")
                else:
                    # Lấy cây cú pháp đầu tiên 
                    tree_str = " ".join(str(parse_trees[0]).split()) 
                    results.append(tree_str + "\n")
                    
            except ValueError as e:
                results.append("()\n")

    except FileNotFoundError:
        print(f"Lỗi: Không tìm thấy file {input_file}")
        return

    # Ghi kết quả ra file
    with io.open(output_file, "w", encoding="utf-8") as f_out:
        f_out.writelines(results)
        
    print(f"Đã phân tích và ghi kết quả ra file: {output_file}\n")