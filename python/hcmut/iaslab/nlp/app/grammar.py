import io
import json
def write_grammar(GRAMMAR_FILE):
    """
    Định nghĩa CFG và lưu vào file output/grammar.txt.
    """
    print(f"--- 2.1: Viết grammar ra file {GRAMMAR_FILE} ---")
    
    # Đọc dữ liệu từ data.json
    with open("data/data.json", "r", encoding="utf-8") as f:
        data = json.load(f)

    # Trích xuất dữ liệu

    foods = [item["name"] for item in data["menu"]]
    food_rules = " | ".join(f'"{food}"' for food in foods)

    attributes = set(opt for item in data["menu"] for opt in item["options"])
    attribute_rules = " | ".join(f'"{attr}"' for attr in attributes)

    unit_rules = " | ".join(f'"{unit}"' for unit in data["unit"])

    number_rules = " | ".join(f'"{num}"' for num in data["number"])

    grammar_str = r"""
    # --- START ---
    S -> CMD | QRY

    # --- 1. CÁC LOẠI CÂU MỆNH LỆNH (COMMAND) ---
    CMD -> VP_ORDER | VP_ADD | VP_REMOVE

    # 1.1. Đặt hàng (ORDER)
    VP_ORDER -> POLITE_PREFIX V_ORDER_ACTION NP_QUANTIFIED TIME_CLAUSE | POLITE_PREFIX V_ORDER_ACTION NP_QUANTIFIED 
    V_ORDER_ACTION -> "đặt" | "lấy" | "cho"
    
    # 1.2. Thêm món (ADD)
    VP_ADD -> V_ADD_ACTION NP_QUANTIFIED | V_ADD_ACTION NP_QUANTIFIED SUFFIX
    V_ADD_ACTION -> "thêm" | "cho thêm" | "thêm vào"
    
    # 1.3. Hủy món (REMOVE)
    VP_REMOVE -> POLITE_PREFIX V_REMOVE_ACTION NP | POLITE_PREFIX V_REMOVE_ACTION NP SUFFIX
    V_REMOVE_ACTION -> "hủy" | "bỏ" | "xóa"

    # --- 2. CÁC LOẠI CÂU HỎI (QUERY) ---
    QRY -> Q_AVAIL | Q_PRICE | Q_MENU | Q_STATUS

    # 2.1. Hỏi còn món (AVAILABILITY)
    Q_AVAIL -> Q_PREFIX Q_AVAIL_INFIX NP Q_AVAIL_SUFFIX | Q_AVAIL_INFIX NP Q_AVAIL_SUFFIX
    
    # 2.2. Hỏi giá (PRICE)
    Q_PRICE -> NP Q_PRICE_SUFFIX
    
    # 2.3. Hỏi menu (MENU)
    Q_MENU -> "menu có gì" | "có những món nào" | "có những món nào trong menu"
    
    # 2.4. Hỏi trạng thái đơn (ORDER STATUS)
    Q_STATUS -> "tôi đã đặt những món gì" | "đơn hàng của tôi có gì"

    # --- 3. CÁC THÀNH PHẦN CÚ PHÁP (CONSTITUENTS) ---

    # Cụm danh từ (chỉ món ăn)
    NP -> ITEM_PREFIX FOOD | FOOD
    
    # Cụm danh từ có số lượng
    NP_QUANTIFIED -> QUANTITY UNIT FOOD ATTRIBUTE | QUANTITY FOOD ATTRIBUTE | QUANTITY UNIT FOOD | QUANTITY FOOD
    QUANTITY -> NUMBER

    # Mệnh đề thời gian
    TIME_CLAUSE -> TIME_PREFIX TIME | TIME
    TIME -> NUMBER TIME_SUFFIX_0 | NUMBER TIME_SUFFIX_0 TIME_SUFFIX_1

    # --- 4. TỪ VỰNG (LEXICON / TERMINALS) ---
    
    # Tiền tố/Hậu tố lịch sự
    POLITE_PREFIX -> "tôi muốn" | "cho tôi" | "làm ơn cho tôi" | "làm ơn cho"
    SUFFIX -> "vào đơn" | "vào đơn nhé" | "trong đơn hàng" | "giúp tôi"
    Q_PREFIX -> "quán" | "nhà hàng" | "ở đây"
    Q_PRICE_SUFFIX -> "giá bao nhiêu" | "bao nhiêu tiền"
    Q_AVAIL_SUFFIX -> "không"
    Q_AVAIL_INFIX -> "có"
    
    # Tiền tố món
    ITEM_PREFIX -> "món"

    # Danh sách món ăn
    FOOD -> %s

    # Số lượng
    NUMBER -> %s

    # Đơn vị
    UNIT -> %s

    # Thuộc tính món
    ATTRIBUTE -> %s

    # Hậu tố thời gian
    TIME_SUFFIX_0 -> "giờ"
    TIME_SUFFIX_1 -> "sáng" | "trưa" | "chiều" | "tối"

    # Tiền tố thời gian
    TIME_PREFIX -> "giao lúc" | "vào lúc" | "vào" | "lúc" | "giao"
    """%(food_rules, number_rules, unit_rules, attribute_rules)

    # Ghi văn phạm ra file
    with io.open(GRAMMAR_FILE, "w", encoding="utf-8") as f:
        f.write(grammar_str)
        
    print(f"Đã viết grammar thành công vào file: {GRAMMAR_FILE}\n")
    return grammar_str