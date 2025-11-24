import json
import os
import io
from nltk import Tree, ChartParser
from utils import get_terminals, custom_tokenizer
from main import OUTPUT_DIR, GRAMMAR_FILE

# Định nghĩa thư mục input
INPUT_DIR = "input"
SAMPLE_QUERIES_FILE = os.path.join(INPUT_DIR, "sample-queries.txt")

# Định nghĩa file output
QHNN_FILE = os.path.join(OUTPUT_DIR, "qhnn.txt")
QHVP_FILE = os.path.join(OUTPUT_DIR, "qhvp.txt")
LL_FILE = os.path.join(OUTPUT_DIR, "ll.txt")
ANSWER_FILE = os.path.join(OUTPUT_DIR, "answer.txt")

# Load menu data
file_path = os.path.join(os.path.dirname(__file__), "data.json")
with open(file_path, "r", encoding="utf-8") as f:
    db = json.load(f)
menu = {item["name"]: {"price": item["price"], "options": item["options"]} for item in db["menu"]}

# Giỏ hàng: lưu thông tin chi tiết từng món
# current_order = {"phở bò": {"quantity": 2, "attributes": ["tái"], "time": "12 giờ"}}
current_order = {}

# Load grammar
with open(GRAMMAR_FILE, "r", encoding="utf-8") as f:
    grammar_str = f.read()
from nltk import CFG
grammar = CFG.fromstring(grammar_str)
parser = ChartParser(grammar)
terminals = get_terminals(grammar)


def extract_semantics(tree: Tree):
    if not isinstance(tree, Tree):
        return None

    label = tree.label()

    if label == 'S':
        return extract_semantics(tree[0])

    # Commands
    elif label == 'CMD':
        return extract_semantics(tree[0])

    elif label == 'VP_ORDER':
        np = next((sub for sub in tree if isinstance(sub, Tree) and sub.label() == 'NP_QUANTIFIED'), None)
        time = next((sub for sub in tree if isinstance(sub, Tree) and sub.label() == 'TIME_CLAUSE'), None)
        sem = extract_semantics(np) or {}
        sem['type'] = 'order'
        if time:
            sem['time'] = " ".join(time.leaves()).strip()
        return sem

    elif label == 'VP_ADD':
        np = next((sub for sub in tree if isinstance(sub, Tree) and sub.label() == 'NP_QUANTIFIED'), None)
        time = next((sub for sub in tree if isinstance(sub, Tree) and sub.label() == 'TIME_CLAUSE'), None)
        sem = extract_semantics(np) or {}
        sem['type'] = 'add'
        if time:
            sem['time'] = " ".join(time.leaves()).strip()
        return sem

    elif label == 'VP_REMOVE':
        np = next((sub for sub in tree if isinstance(sub, Tree) and sub.label() == 'NP'), None)
        sem = extract_semantics(np) or {}
        sem['type'] = 'remove'
        return sem

    # Queries
    elif label == 'QRY':
        return extract_semantics(tree[0])

    elif label == 'Q_AVAIL':
        np = next((sub for sub in tree if isinstance(sub, Tree) and sub.label() == 'NP'), None)
        np_sem = extract_semantics(np)
        return {'type': 'avail', 'food': np_sem.get('food') if np_sem else None}

    elif label == 'Q_PRICE':
        np = next((sub for sub in tree if isinstance(sub, Tree) and sub.label() == 'NP'), None)
        np_sem = extract_semantics(np)
        return {'type': 'price', 'food': np_sem.get('food') if np_sem else None}

    elif label == 'Q_MENU':
        return {'type': 'menu'}

    elif label == 'Q_STATUS':
        return {'type': 'status'}

    # NP / NP_QUANTIFIED
    elif label in ['NP', 'NP_QUANTIFIED']:
        food_tree = next((sub for sub in tree if isinstance(sub, Tree) and sub.label() == 'FOOD'), None)
        quantity = next((sub for sub in tree if isinstance(sub, Tree) and sub.label() == 'QUANTITY'), None)
        attr = next((sub for sub in tree if isinstance(sub, Tree) and sub.label() == 'ATTRIBUTE'), None)
        unit = next((sub for sub in tree if isinstance(sub, Tree) and sub.label() == 'UNIT'), None)

        food = " ".join(food_tree.leaves()) if food_tree else None
        sem = {'food': food}

        if quantity:
            qty_str = " ".join(quantity.leaves())
            sem['quantity'] = int(qty_str) if qty_str.isdigit() else 1
        if attr:
            sem['attributes'] = [" ".join(attr.leaves())]
        return sem

    for subtree in tree:
        sem = extract_semantics(subtree)
        if sem:
            return sem
    return None


def semantics_to_logical_form(sem):
    if not sem:
        return "invalid()"
    typ = sem['type']
    food = sem.get('food', '')
    qty = sem.get('quantity', 1)
    attrs = sem.get('attributes', [])
    time = sem.get('time', '')
    if typ in ['order', 'add']:
        return f"{typ}({food}, {qty}, {attrs}, \"{time}\")"
    elif typ == 'remove':
        return f"remove({food})"
    elif typ == 'avail':
        return f"avail({food})"
    elif typ == 'price':
        return f"price({food})"
    elif typ == 'menu':
        return "menu()"
    elif typ == 'status':
        return "status()"
    return "unknown()"


def map_to_db_query(sem):
    if not sem:
        return "INVALID QUERY"
    typ = sem['type']
    food = sem.get('food')
    if typ == 'avail':
        return f"EXISTS IN MENU: {food}"
    elif typ == 'price':
        return f"SELECT price FROM menu WHERE name = '{food}'"
    elif typ == 'menu':
        return "SELECT name, price FROM menu"
    elif typ == 'status':
        return "SELECT * FROM current_order"
    elif typ in ['order', 'add']:
        return f"INSERT/UPDATE order: {food} × {sem.get('quantity',1)}"
    elif typ == 'remove':
        return f"DELETE FROM order: {food}"
    return "NO QUERY"


def execute_query(sem):
    if not sem:
        return "Câu lệnh không hợp lệ."

    typ = sem['type']
    food = sem.get('food')
    qty = sem.get('quantity', 1)
    attrs = sem.get('attributes', [])
    time = sem.get('time', '')

    if typ == 'menu':
        items = ", ".join([f"{name} ({menu[name]['price']}đ)" for name in menu])
        return f"Menu có: {items}."

    elif typ == 'price':
        if food in menu:
            return f"{food.capitalize()} giá {menu[food]['price']:,} VND.".replace(",", ".")
        return f"Không có món {food} trong menu."

    elif typ == 'avail':
        if food in menu:
            return f"Có món {food}."
        return f"Không có món {food}."

    elif typ == 'status':
        if not current_order:
            return "Bạn chưa đặt món nào."

        lines = ["Đơn hàng của bạn:"]
        total = 0
        delivery_times = set()

        for food_name, info in current_order.items():
            q = info['quantity']
            price = menu[food_name]['price']
            subtotal = q * price
            total += subtotal
            attr_str = f" ({', '.join(info['attributes'])})" if info['attributes'] else ""
            time_str = f" – Giao lúc {info['time']}" if info['time'] else ""
            delivery_times.add(info['time'])
            lines.append(f"• {q} {food_name}{attr_str}{time_str} → {subtotal:,}đ".replace(",", "."))

        # Tổng tiền và thời gian giao
        lines.append(f"\nTổng tiền: {total:,} VND".replace(",", "."))
        if delivery_times and '' not in delivery_times:
            times_str = " và ".join(delivery_times) if len(delivery_times) <= 2 else ", ".join(list(delivery_times)[:-1]) + " và " + list(delivery_times)[-1]
            lines.append(f"Thời gian giao hàng: {times_str}")

        return "\n".join(lines)

    elif typ in ['order', 'add']:
        if food not in menu:
            return f"Không có món {food} trong menu."
        if food in current_order:
            current_order[food]['quantity'] += qty
            current_order[food]['attributes'].extend(attrs)
            if time:
                current_order[food]['time'] = time  # Cập nhật thời gian mới nhất
        else:
            current_order[food] = {
                'quantity': qty,
                'attributes': attrs,
                'time': time
            }
        action = "thêm" if typ == 'add' else "đặt"
        time_str = f" lúc {time}" if time else ""
        return f"Đã {action} {qty} {food}{time_str} vào đơn hàng thành công!"

    elif typ == 'remove':
        if food in current_order:
            del current_order[food]
            return f"Đã xóa {food} khỏi đơn hàng."
        return f"Không có {food} trong đơn hàng để xóa."

    return "Không hiểu yêu cầu của bạn."


def process_query(query):
    tokens = custom_tokenizer(query, terminals)
    if tokens is None:
        return "Token error", "No query", "invalid()", "Lỗi tokenize."

    try:
        parse_trees = list(parser.parse(tokens))
        if not parse_trees:
            return "No parse", "No query", "invalid()", "Câu không hợp lệ với văn phạm."
        tree = parse_trees[0]
    except Exception as e:
        return "Parse error", "No query", "invalid()", f"Lỗi phân tích: {e}"

    sem = extract_semantics(tree)
    qhnn = str(sem)
    qhvp = map_to_db_query(sem)
    ll = semantics_to_logical_form(sem)
    answer = execute_query(sem)

    return qhnn, qhvp, ll, answer


def main_cli():
    print("=== HỆ THỐNG ĐẶT MÓN ĂN Q&A ===")
    print("Đọc câu hỏi mẫu từ:", SAMPLE_QUERIES_FILE)

    # Đọc file sample-queries.txt
    if not os.path.exists(SAMPLE_QUERIES_FILE):
        print(f"Không tìm thấy file {SAMPLE_QUERIES_FILE}")
        print("Vui lòng tạo file input/sample-queries.txt với các câu hỏi (mỗi dòng một câu).")
        return

    with open(SAMPLE_QUERIES_FILE, "r", encoding="utf-8") as f:
        sample_queries = [line.strip() for line in f if line.strip()]

    # Xử lý và ghi kết quả
    with io.open(QHNN_FILE, "w", encoding="utf-8") as f_qhnn, \
         io.open(QHVP_FILE, "w", encoding="utf-8") as f_qhvp, \
         io.open(LL_FILE, "w", encoding="utf-8") as f_ll, \
         io.open(ANSWER_FILE, "w", encoding="utf-8") as f_answer:

        f_qhnn.write("=== QUAN HỆ NGỮ NGHĨA (qhnn.txt) ===\n\n")
        f_qhvp.write("=== QUAN HỆ VĂN PHẠM - DB (qhvp.txt) ===\n\n")
        f_ll.write("=== DẠNG LUẬN LÝ (ll.txt) ===\n\n")
        f_answer.write("=== TRẢ LỜI NGƯỜI DÙNG (answer.txt) ===\n\n")

        for query in sample_queries:
            qhnn, qhvp, ll, answer = process_query(query)

            f_qhnn.write(f"Câu: {query}\n→ {qhnn}\n\n")
            f_qhvp.write(f"Câu: {query}\n→ {qhvp}\n\n")
            f_ll.write(f"Câu: {query}\n→ {ll}\n\n")
            f_answer.write(f"Q: {query}\nA: {answer}\n\n")

    print(f"Đã xử lý {len(sample_queries)} câu hỏi.")
    print(f"Kết quả được lưu trong thư mục: {OUTPUT_DIR}")

    # Vòng lặp tương tác
    print("\nNhập câu lệnh (hoặc 'exit' để thoát):")
    while True:
        try:
            user_input = input("> ").strip()
            if user_input.lower() in ['exit', 'quit', 'thoát']:
                print("Tạm biệt!")
                break
            if not user_input:
                continue
            _, _, _, answer = process_query(user_input)
            print(answer)
        except KeyboardInterrupt:
            print("\nTạm biệt!")
            break
        except Exception as e:
            print(f"Lỗi: {e}")


if __name__ == "__main__":
    main_cli()