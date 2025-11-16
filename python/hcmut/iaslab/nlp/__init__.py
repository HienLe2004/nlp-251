#!/usr/bin/env python3
# nlp_food_system_v3.py
# Phiên bản nâng cao: nhận diện mệnh lệnh imperative và thao tác sửa đơn (add/cancel/modify)
# Chạy: python nlp_food_system_v3.py
# Ghi các file: output/grammar.txt, samples.txt, parse-results.txt, qhnn.txt, qhvp.txt, ll.txt, answer.txt

import os, re
from itertools import product
from random import shuffle

OUTDIR = "output"
os.makedirs(OUTDIR, exist_ok=True)

# --- Menu and grammar (kept simple) ---
MENU_DB = [
    {"name": "phở bò", "price": 45000, "options": ["ít hành", "nhiều hành"]},
    {"name": "bún chả", "price": 50000, "options": []},
    {"name": "gà rán", "price": 60000, "options": ["cay", "không cay"]},
    {"name": "trà sữa", "price": 30000, "options": ["ít đường", "đặc biệt"]},
    {"name": "cơm tấm", "price": 40000, "options": ["sườn", "chả"]},
]
ITEM_NAMES = [m["name"] for m in MENU_DB]

GRAMMAR = {
    "ORDER": ["Tôi muốn đặt QUANTITY ITEM TIME", "Cho tôi QUANTITY ITEM", "Cho mình QUANTITY ITEM"],
    "MODIFY": ["Đổi ITEM thành QUANTITY UNIT", "Thay ITEM bằng QUANTITY UNIT", "Thay đổi ITEM thành QUANTITY"],
    "CANCEL": ["Bỏ ITEM đi", "Hủy ITEM", "Xóa ITEM khỏi đơn"],
    "ASK_MENU": ["Có những món nào trong menu?", "Cho tôi xem menu"],
    "ASK_PRICE": ["ITEM giá bao nhiêu?", "Giá ITEM"],
}

# --- Utilities ---
def normalize(s):
    s = s.strip().lower()
    s = re.sub(r'[^\w\s\d:àáảãạăắằẳẵặâầấẩẫậèéẹẻẽêềếểễệìíỉĩịòóỏõọôồốổỗộơờớởỡợùúủũụưừứửữựýỳỷỹỵđ-]', ' ', s)
    s = re.sub(r'\bmột\b', '1', s); s = re.sub(r'\bhai\b', '2', s); s = re.sub(r'\bba\b', '3', s)
    s = re.sub(r'\s+', ' ', s).strip()
    return s

def match_item(s):
    for item in sorted(ITEM_NAMES, key=lambda x: -len(x)):
        if re.search(r'\b' + re.escape(item) + r'\b', s):
            return item
    return None

def extract_quantity(s):
    m = re.search(r'\b(\d+)\b', s)
    return int(m.group(1)) if m else None

def extract_time(s):
    m = re.search(r'(\b\d{1,2}[:h]\d{0,2}\b|\b\d{1,2}\s*giờ\b|\bvào \d{1,2}\b|\bgiao lúc \d{1,2}\b)', s)
    return m.group(0) if m else None

# --- In-memory cart ---
CART = []

def add_to_cart(item, qty, price):
    for c in CART:
        if c["item"] == item:
            c["quantity"] += qty
            return
    CART.append({"item": item, "quantity": qty, "price": price})

def set_item_quantity(item, qty):
    for c in CART:
        if c["item"] == item:
            if qty <= 0:
                CART.remove(c)
            else:
                c["quantity"] = qty
            return True
    return False

def remove_from_cart(item):
    for i, c in enumerate(CART):
        if c["item"] == item:
            del CART[i]; return True
    return False

def find_menu_item(name):
    for m in MENU_DB:
        if m["name"] == name:
            return m
    return None

# --- Parser with imperative/mapping rules ---
def parse_sentence(sent):
    orig = sent
    s = normalize(sent)
    parse = {"sentence": orig, "valid": True, "intent": None, "slots": {}}

    # 1) Modify pattern: "đổi ITEM thành 3 phần" / "đổi X thành Y"
    m_mod = re.search(r'\b(đổi|thay|thay đổi)\b\s+(.*?)\s+\b(thành|thanh)\b\s+(\d+)', s)
    if m_mod:
        item_text = m_mod.group(2)
        item = match_item(item_text) or match_item(s)
        qty = int(m_mod.group(4))
        if item:
            parse.update({"intent": "modify_item", "slots": {"item": item, "quantity": qty}})
            return parse

    # 2) Cancel imperative: verbs like "bỏ", "hủy", "xóa" with item -> cancel
    if re.search(r'\b(bỏ|hủy|huy|xóa|xoa|xoa bỏ)\b', s):
        item = match_item(s)
        if item:
            parse.update({"intent": "cancel_item", "slots": {"item": item}})
            return parse
        else:
            parse.update({"intent": "cancel_request", "slots": {}})
            return parse

    # 3) Add/order imperative: verbs like "cho", "thêm", "đặt", "mua", e.g., "cho mình 1 cơm tấm" / "cho 1 cơm tấm"
    if re.search(r'\b(cho|thêm|đặt|mua|mua giúp)\b', s):
        item = match_item(s)
        qty = extract_quantity(s) or 1
        time = extract_time(s)
        if item:
            parse.update({"intent": "add_item", "slots": {"item": item, "quantity": qty, "time": time}})
            return parse

    # 4) Short imperative like "cho mình 1 cơm tấm" without explicit verb captured above
    # if starts with number + item e.g., "1 cơm tấm" or "cho 1 cơm tấm"
    if re.match(r'^\d+\s+', s) and match_item(s):
        qty = extract_quantity(s) or 1
        item = match_item(s)
        parse.update({"intent": "add_item", "slots": {"item": item, "quantity": qty}})
        return parse

    # 5) Cancel phrase "bỏ gà rán đi" handled; fallback: if sentence contains "bỏ" + item word anywhere already handled

    # 6) Ask price / availability / menu / show cart / total
    if re.search(r'\b(menu|những món nào|xem menu)\b', s):
        parse.update({"intent": "ask_menu", "slots": {}}); return parse
    item = match_item(s)
    if item and re.search(r'\b(giá|bao nhiêu)\b', s):
        parse.update({"intent": "ask_price", "slots": {"item": item}}); return parse
    if re.search(r'\b(có .* không|có .* ko|có không|có ko|có)\b', s) and item:
        parse.update({"intent": "ask_availability", "slots": {"item": item}}); return parse
    if re.search(r'\b(đơn hàng của tôi|tôi đã đặt|xem đơn|đơn của tôi)\b', s):
        parse.update({"intent": "ask_my_order", "slots": {}}); return parse
    if re.search(r'\b(tổng|tổng tiền|tổng cộng)\b', s):
        parse.update({"intent": "ask_total", "slots": {}}); return parse

    # Fallback: if item present but no verb, decide likely intent: treat as add if sentence starts with verbless imperative words like "cho", else availability
    if item:
        # if sentence begins with "cho" or contains "mua" earlier handled; by default treat as add if begins with an imperative word or numeric
        if re.match(r'^(cho|thêm|mua)\b', s) or re.match(r'^\d+\b', s):
            qty = extract_quantity(s) or 1
            parse.update({"intent": "add_item", "slots": {"item": item, "quantity": qty}}); return parse
        else:
            parse.update({"intent": "ask_availability", "slots": {"item": item}}); return parse

    # nothing matched
    parse["valid"] = False; return parse

# --- Semantic relations, mapping, logical forms ---
def semantic_relations_from_parse(p):
    rels = []
    if not p["valid"]: return rels
    it = p["intent"]; s = p["slots"]
    if it == "add_item":
        rels.append("intent(order)")
        rels.append(f"order_item(item:{s.get('item')}, quantity:{s.get('quantity',1)})")
        if s.get("time"): rels.append(f"deliver_time({s.get('time')})")
    elif it == "cancel_item":
        rels.append("intent(cancel_item)"); rels.append(f"cancel_item(item:{s.get('item')})")
    elif it == "cancel_request":
        rels.append("intent(cancel_request)")
    elif it == "modify_item":
        rels.append("intent(modify_item)"); rels.append(f"modify_item(item:{s.get('item')}, quantity:{s.get('quantity')})")
    elif it == "ask_price":
        rels.append("intent(ask_price)"); rels.append(f"ask_price(item:{s.get('item')})")
    elif it == "ask_menu":
        rels.append("intent(ask_menu)")
    elif it == "ask_availability":
        rels.append("intent(ask_availability)"); rels.append(f"ask_availability(item:{s.get('item')})")
    elif it == "ask_my_order":
        rels.append("intent(ask_my_order)")
    elif it == "ask_total":
        rels.append("intent(ask_total)")
    return rels

def map_relations_to_db(rels):
    ops = []
    for r in rels:
        if r.startswith("order_item"):
            m = re.match(r'order_item\(item:(.*), quantity:(\d+)\)', r)
            if m:
                item = m.group(1); q = int(m.group(2)); me = find_menu_item(item)
                if me: ops.append(f"order_db_add(item:{item}, price:{me['price']}, quantity:{q})")
                else: ops.append(f"order_db_add(item:{item}, price:unknown, quantity:{q})")
        elif r.startswith("cancel_item"):
            m = re.match(r'cancel_item\(item:(.*)\)', r)
            if m: ops.append(f"order_db_remove(item:{m.group(1)})")
        elif r.startswith("modify_item"):
            m = re.match(r'modify_item\(item:(.*), quantity:(\d+)\)', r)
            if m: ops.append(f"order_db_modify(item:{m.group(1)}, quantity:{m.group(2)})")
        elif r == "intent(ask_menu)":
            ops.append("db_query_all_menu")
        elif r.startswith("ask_price"):
            m = re.match(r'ask_price\(item:(.*)\)', r)
            if m: me = find_menu_item(m.group(1)); ops.append(f"db_query_price(item:{m.group(1)}, price:{me['price'] if me else 'unknown'})")
        elif r == "intent(ask_my_order)":
            ops.append("order_db_list")
        elif r == "intent(ask_total)":
            ops.append("order_db_total")
        else:
            ops.append(r)
    return ops

def find_menu_item(name):
    if not name: return None
    for m in MENU_DB:
        if m["name"] == name:
            return m
    return None

# --- Logical form / procedural semantics ---
def logical_form_from_relations(rels):
    lf = []; proc = []
    for r in rels:
        if r == "intent(order)":
            lf.append("OrderIntent()"); proc.append("procedure: create_order(session)")
        if r.startswith("order_item"):
            m = re.match(r'order_item\(item:(.*), quantity:(\d+)\)', r)
            if m:
                item = m.group(1); q = m.group(2)
                lf.append(f"Order(item='{item}', quantity={q})"); proc.append(f"procedure: add_to_cart(item='{item}', qty={q})")
        if r.startswith("deliver_time"):
            m = re.match(r'deliver_time\((.*)\)', r)
            if m: lf.append(f"DeliverTime('{m.group(1)}')"); proc.append(f"procedure: set_delivery_time('{m.group(1)}')")
        if r.startswith("cancel_item"):
            m = re.match(r'cancel_item\(item:(.*)\)', r)
            if m: lf.append(f"Cancel(item='{m.group(1)}')"); proc.append(f"procedure: remove_from_cart('{m.group(1)}')")
        if r.startswith("order_db_modify") or r.startswith("modify_item"):
            m = re.match(r'.*modify.*item:(.*)[, ]+quantity:?(\d+)', r)
            if m:
                item = m.group(1); q = int(m.group(2))
                lf.append(f"Modify(item='{item}', quantity={q})"); proc.append(f"procedure: set_item_quantity('{item}', {q})")
        if r == "intent(ask_menu)":
            lf.append("AskMenu()"); proc.append("procedure: list_menu()")
        if r.startswith("ask_price"):
            m = re.match(r'ask_price\(item:(.*)\)', r)
            if m: lf.append(f"AskPrice(item='{m.group(1)}')"); proc.append(f"procedure: query_price('{m.group(1)}')")
        if r == "intent(ask_my_order)":
            lf.append("AskMyOrder()"); proc.append("procedure: show_cart()")
        if r == "intent(ask_total)":
            lf.append("AskTotal()"); proc.append("procedure: compute_total()")
    return lf, proc

# --- Procedure execution & answers ---
def execute_procedures(proc_list):
    answers = []
    for p in proc_list:
        if p.startswith("procedure: create_order"):
            answers.append("Đã tạo đơn. (session-local, chưa thanh toán)")
        elif p.startswith("procedure: add_to_cart"):
            m = re.search(r"add_to_cart\(item='([^']+)', qty=(\d+)\)", p)
            if m:
                item = m.group(1); qty = int(m.group(2)); me = find_menu_item(item)
                if me:
                    add_to_cart(item, qty, me["price"])
                    answers.append(f"Đã thêm {qty} x {item} vào đơn (giá mỗi món {me['price']} VND)")
                else:
                    answers.append(f"Không thể thêm {item}: không có trong menu")
        elif p.startswith("procedure: remove_from_cart"):
            m = re.search(r"remove_from_cart\('([^']+)'\)", p)
            if m:
                item = m.group(1)
                if remove_from_cart(item): answers.append(f"Đã hủy {item} khỏi đơn")
                else: answers.append(f"Không tìm thấy {item} trong đơn để hủy")
        elif p.startswith("procedure: set_item_quantity"):
            m = re.search(r"set_item_quantity\('([^']+)',\s*(\d+)\)", p)
            if m:
                item = m.group(1); qty = int(m.group(2))
                if set_item_quantity(item, qty):
                    answers.append(f"Đã cập nhật {item} thành {qty} phần trong đơn")
                else:
                    # If item not in cart, add it with that qty (reasonable behavior)
                    me = find_menu_item(item)
                    if me:
                        add_to_cart(item, qty, me["price"])
                        answers.append(f"Không có {item} trong đơn, đã thêm {qty} x {item} vào đơn")
                    else:
                        answers.append(f"Không thể cập nhật {item}: không có trong menu")
        elif p.startswith("procedure: set_delivery_time"):
            m = re.search(r"set_delivery_time\('([^']+)'\)", p)
            if m: answers.append(f"Thời gian giao hàng được đặt là {m.group(1)}")
        elif p.startswith("procedure: query_price"):
            m = re.search(r"query_price\('([^']+)'\)", p)
            if m:
                item = m.group(1); me = find_menu_item(item)
                if me: answers.append(f"{item} giá {me['price']} VND")
                else: answers.append(f"Không tìm thấy món {item} trong menu")
        elif p.startswith("procedure: list_menu"):
            items = [f"{m['name']} ({m['price']} VND)" for m in MENU_DB]
            answers.append("Menu: " + "; ".join(items))
        elif p.startswith("procedure: show_cart"):
            if not CART: answers.append("Bạn chưa đặt món nào.")
            else:
                lines = []; total = 0
                for c in CART:
                    lines.append(f"{c['quantity']} x {c['item']} ({c['price']} VND mỗi món)")
                    total += c['quantity'] * c['price']
                answers.append("Trong đơn: " + "; ".join(lines) + f". Tổng: {total} VND")
        elif p.startswith("procedure: compute_total"):
            total = sum(c['quantity']*c['price'] for c in CART)
            answers.append(f"Tổng tiền hiện tại: {total} VND")
    return answers

# --- I/O helpers ---
def write_file(path, lines):
    with open(path, "w", encoding="utf8") as f:
        f.write("\n".join(lines))

def write_grammar(path):
    lines = ["# grammar (compact)"]
    for k,v in GRAMMAR.items():
        lines.append(f"{k} -> {' | '.join(v)}")
    write_file(path, lines)

def write_samples(path, samples):
    write_file(path, samples)

def write_parse_results(path, parses):
    lines = []
    for p in parses:
        if not p["valid"]: lines.append("()")
        else:
            slots = ",".join(f"{k}:{v}" for k,v in p["slots"].items())
            lines.append(f"({p['intent']} {slots})")
    write_file(path, lines)

def write_qhnn(path, all_rels):
    lines = []
    for i, rels in enumerate(all_rels):
        lines.append(f"# Sentence {i+1}")
        if not rels: lines.append("()")
        else:
            for r in rels: lines.append(r)
        lines.append("")
    write_file(path, lines)

def write_qhvp(path, all_ops):
    lines = []
    for i, ops in enumerate(all_ops):
        lines.append(f"# Sentence {i+1}")
        if not ops: lines.append("()")
        else:
            for o in ops: lines.append(o)
        lines.append("")
    write_file(path, lines)

def write_ll(path, all_ll):
    lines = []
    for i, (lf, proc) in enumerate(all_ll):
        lines.append(f"# Sentence {i+1}")
        lines.append("# Logical form")
        if not lf: lines.append("()")
        else: lines.extend(lf)
        lines.append("# Procedural semantics")
        if not proc: lines.append("()")
        else: lines.extend(proc)
        lines.append("")
    write_file(path, lines)

def write_answer(path, all_answers):
    lines = []
    for i, ans in enumerate(all_answers):
        lines.append(f"# Sentence {i+1}")
        if not ans: lines.append("No answer.")
        else: lines.extend(ans)
        lines.append("")
    write_file(path, lines)

# --- Sample generator (small) ---
def generate_samples(max_sent=500):
    templates = []
    for k in GRAMMAR: templates.extend(GRAMMAR[k])
    samples = set()
    quantities = ["1","2","3"]
    times = ["","vào 12 giờ","giao lúc 12"]
    for t in templates:
        if "QUANTITY" in t or "ITEM" in t:
            for it in ITEM_NAMES:
                for q in quantities:
                    for time in times:
                        s = t.replace("QUANTITY", q).replace("ITEM", it).replace("TIME", time)
                        samples.add(re.sub(r'\s+',' ', s).strip())
        else:
            samples.add(t)
        if len(samples) >= max_sent: break
    samples = list(samples); shuffle(samples)
    return samples[:max_sent]

# --- Main workflow ---
def main():
    # write grammar & samples
    write_grammar(os.path.join(OUTDIR, "grammar.txt"))
    samples = generate_samples(1000)
    write_samples(os.path.join(OUTDIR, "samples.txt"), samples)

    # read input sentences if available, else default list including problematic examples
    input_path = os.path.join("input", "sentences.txt")
    if os.path.exists(input_path):
        with open(input_path, "r", encoding="utf8") as f: inputs = [l.strip() for l in f if l.strip()]
    else:
        inputs = [
            "Tôi muốn đặt 2 phần phở bò giao lúc 12 giờ.",
            "Có món bún chả không?",
            "Thêm 1 trà sữa ít đường vào đơn nhé.",
            "Tôi muốn hủy món gà rán trong đơn hàng.",
            "Phở bò giá bao nhiêu?",
            "Có những món nào trong menu?",
            "Tôi đã đặt những món gì?",
            # problematic cases to ensure correct semantics
            "cho mình 1 cơm tấm",
            "bỏ gà rán đi",
            "đổi phở bò thành 3 phần",
        ]

    parses = []; all_sem = []; all_ops = []; all_ll = []; all_answers = []
    global CART; CART = []

    for sent in inputs:
        p = parse_sentence(sent); parses.append(p)
        sem = semantic_relations_from_parse(p); all_sem.append(sem)
        ops = map_relations_to_db(sem); all_ops.append(ops)
        lf, proc = logical_form_from_relations(sem); all_ll.append((lf, proc))
        # If logical procedural list doesn't include modification procedure for modify_item, create one
        # (logical_form_from_relations already handles modify_item -> set_item_quantity)
        answers = execute_procedures(proc)
        all_answers.append(answers)

    # outputs
    write_parse_results(os.path.join(OUTDIR, "parse-results.txt"), parses)
    write_qhnn(os.path.join(OUTDIR, "qhnn.txt"), all_sem)
    write_qhvp(os.path.join(OUTDIR, "qhvp.txt"), all_ops)
    write_ll(os.path.join(OUTDIR, "ll.txt"), all_ll)
    write_answer(os.path.join(OUTDIR, "answer.txt"), all_answers)

    print("Outputs written to", OUTDIR)

if __name__ == "__main__":
    main()