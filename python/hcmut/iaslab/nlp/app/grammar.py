import io
import json
import os
def write_grammar(GRAMMAR_FILE):
    """
    Định nghĩa CFG và lưu vào file output/grammar.txt.
    """
    print(f"--- 2.1: Viết grammar ra file {GRAMMAR_FILE} ---")
    # Đọc dữ liệu từ data.json
    file_path = os.path.join(os.path.dirname(__file__), "data.json")
    with open(file_path, "r", encoding="utf-8") as f:
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
    VP_ORDER -> POLITE_PREFIX V_ORDER_ACTION NP_QUANTIFIED TIME_CLAUSE | POLITE_PREFIX V_ORDER_ACTION NP_QUANTIFIED | TIME_CLAUSE NP_QUANTIFIED
    V_ORDER_ACTION -> "đặt" | "lấy" | "cho" |
    
    # 1.2. Thêm món (ADD)
    VP_ADD -> POLITE_PREFIX V_ADD_ACTION NP_QUANTIFIED | POLITE_PREFIX V_ADD_ACTION NP_QUANTIFIED ADD_SUFFIX 
    V_ADD_ACTION -> V_ADD_ACTION_PREFIX | V_ADD_ACTION_PREFIX ORDER
    V_ADD_ACTION_PREFIX -> "thêm" | "cho thêm" | "thêm vào" | "cho thêm vào" | "lấy thêm"
    
    # 1.3. Hủy món (REMOVE)
    VP_REMOVE -> POLITE_PREFIX V_REMOVE_ACTION NP | POLITE_PREFIX V_REMOVE_ACTION NP REMOVE_SUFFIX
    V_REMOVE_ACTION -> "hủy" | "bỏ" | "xóa"

    # --- 2. CÁC LOẠI CÂU HỎI (QUERY) ---
    QRY -> Q_AVAIL | Q_PRICE | Q_MENU | Q_STATUS

    # 2.1. Hỏi còn món (AVAILABILITY)
    Q_AVAIL -> Q_PREFIX Q_AVAIL_INFIX NP Q_AVAIL_SUFFIX | Q_AVAIL_INFIX NP Q_AVAIL_SUFFIX
    
    # 2.2. Hỏi giá (PRICE)
    Q_PRICE -> NP Q_PRICE_SUFFIX
    
    # 2.3. Hỏi menu (MENU)
    Q_MENU -> Q_PREFIX Q_MENU_SUFFIX | Q_MENU_SUFFIX
    
    # 2.4. Hỏi trạng thái đơn (ORDER STATUS)
    Q_STATUS -> Q_STATUS_PREFIX Q_STATUS_SUFFIX | Q_STATUS_PREFIX | ORDER Q_STATUS_PREFIX Q_STATUS_SUFFIX | ORDER Q_STATUS_PREFIX 
    Q_STATUS_PREFIX -> "tôi đã đặt những món gì" | "tôi đã đặt những gì" | "có gì" | "có những gì" | "có những món gì"
    Q_STATUS_SUFFIX -> "rồi"

    # --- 3. CÁC THÀNH PHẦN CÚ PHÁP (CONSTITUENTS) ---

    # Cụm danh từ (chỉ món ăn)
    NP -> ITEM_PREFIX FOOD ATTRIBUTE | ITEM_PREFIX FOOD | FOOD ATTRIBUTE | FOOD
    
    # Cụm danh từ có số lượng
    NP_QUANTIFIED -> QUANTITY UNIT FOOD ATTRIBUTE | QUANTITY FOOD ATTRIBUTE | QUANTITY UNIT FOOD | QUANTITY FOOD
    QUANTITY -> NUMBER

    # Mệnh đề thời gian
    TIME_CLAUSE -> TIME_PREFIX TIME | TIME
    TIME -> NUMBER TIME_SUFFIX_0 | NUMBER TIME_SUFFIX_0 TIME_SUFFIX_1

    
    
    # Tiền tố/Hậu tố lịch sự
    POLITE_PREFIX -> "tôi muốn" | "cho tôi" | "làm ơn cho tôi" | "làm ơn cho" | 
    ADD_SUFFIX -> ADD_SUFFIX_1 ORDER SUFFIX | ADD_SUFFIX_1 ORDER | SUFFIX
    ADD_SUFFIX_1 -> "vào" | "trong" 
    REMOVE_SUFFIX -> REMOVE_SUFFIX_1 ORDER SUFFIX | REMOVE_SUFFIX_1 ORDER | SUFFIX
    REMOVE_SUFFIX_1 -> "khỏi" | "ra khỏi" | "trong" 
    SUFFIX -> "nhé" | "dùm tôi" | "giúp tôi" | "ạ" | "đi" 
    Q_PREFIX -> "quán" | "nhà hàng" | "ở đây" | ""
    Q_PRICE_SUFFIX -> "giá bao nhiêu" | "bao nhiêu tiền"
    Q_AVAIL_SUFFIX -> "không"
    Q_AVAIL_INFIX -> "có"
    Q_MENU_SUFFIX -> "menu có gì" | "có những món nào" | "có những món gì" | "có món nào" | "có món gì" | "có những món nào trong menu" | "có những món gì trong menu"
    
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
    TIME_PREFIX -> "giao lúc" | "vào lúc" | "vào" | "lúc" | "giao" | "giao vào lúc"

    # Từ chỉ đơn hàng
    ORDER -> "đơn hàng" | "đơn" | "đơn hàng của tôi" | "đơn của tôi" | "đơn hàng tôi" | "đơn tôi"
    """%(food_rules, number_rules, unit_rules, attribute_rules)

    # Ghi văn phạm ra file
    with io.open(GRAMMAR_FILE, "w", encoding="utf-8") as f:
        f.write(grammar_str)
        
    print(f"Đã viết grammar thành công vào file: {GRAMMAR_FILE}\n")
    return grammar_str