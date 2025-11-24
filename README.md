# NLP Assignment: Grammar and Parser for Online Food Ordering + Semantic representation and Basic Q&A System

## Overview

This project is an implementation for the Natural Language Processing (NLP) assignment (CO3085) at HCMUT, focusing on a restricted domain for online food ordering in Vietnamese. It uses a Context-Free Grammar (CFG) to model user commands and queries related to ordering food, such as placing orders, adding/removing items, checking availability, prices, menu, and order status.

The system:
- Generates a CFG based on menu data from `data.json`.
- Produces random unique sample sentences from the grammar.
- Parses input sentences using a chart parser and outputs parse trees.
- A simple Q&A system with semantic representation, dependency parsing, and database querying to answer user queries.

The project leverages the NLTK library for grammar handling and parsing. It is designed to run in a Python environment and processes inputs/outputs in specified directories.

## Features
- **Grammar Generation**: Dynamically builds a CFG from predefined rules and data (foods, units, numbers, attributes).
- **Sentence Generation**: Generates up to 10,000 unique sentences based on the grammar.
- **Sentence Parsing**: Tokenizes and parses input sentences, producing parse trees or empty results for invalid inputs.
- **Domain-Specific**: Handles Vietnamese phrases for food ordering, e.g., "Tôi muốn đặt 2 phần phở bò giao lúc 12 giờ."
- **Semantic Representation and Q&A**: Builds a dependency grammar parser, extracts semantic relations, integrates with a simulated menu database, generates logical forms, and answers queries like menu listings, prices, availability, order status, and modifications.

## Project Structure
```
.
├── input/                  # Input directory (sample for parsing and Q&A)
├── output/                 # Output directory (grammar.txt, samples.txt, parse-results.txt, qhnn.txt, qhvp.txt, ll.txt, answer.txt)
├── python/                 # Python source code
│   ├── conf/               # Configuration 
│   └── hcmut_iaslab/
│       └── nlp/
│           └── app/
│               ├── __init__.py
│               ├── cli.py          # Entry point to run the CLI (Part II)
│               ├── data.json       # Menu data (foods, units, numbers)
│               ├── generator.py    # Sentence generation logic
│               ├── grammar.py      # Grammar definition and writing
│               ├── main.py         # Entry point to run the program (Part I)
│               ├── parser.py       # Parsing logic using NLTK ChartParser
│               └── utils.py        # Utilities (terminals extraction, tokenizer, preprocessing)
├── .gitignore              # Git ignore file
├── Dockerfile              # Docker configuration 
├── README.md               # This file
├── requirements.txt        # Python dependencies 
├── setup.py                # Setup script 
└── util.sh                 # Utility shell script 
```

## Requirements
- Python 3.12+ (tested on 3.12.3)
- NLTK library
- Other dependencies: Listed in `requirements.txt` 

## Installation
1. Clone the [repository](https://github.com/HienLe2004/nlp-251) (if not have):
   ```
   git clone <repository-url>
   cd <project-directory>
   ```

2. Create and activate a virtual environment:
   ```
   python -m venv venv
   source venv/bin/activate  # On Unix/Mac
   venv\Scripts\activate     # On Windows
   ```

3. Install dependencies:
   ```
   pip install -r requirements.txt
   ```

## Usage
### Part I - Grammar and Parser:
The program runs from `main.py`, which executes all steps sequentially.

1. Ensure input files are prepared:
   - `input/sentences.txt`: Add sentences (one per line) to parse, e.g.:
     ```
     Tôi muốn đặt 2 phần phở bò giao lúc 12 giờ.
     Có món bún chả không?
     Thêm 1 trà sữa ít đường vào đơn nhé.
     ```

2. Run the program:
   ```
   python python/hcmut/iaslab/nlp/app/main.py
   ```

3. Output:
   - `output/grammar.txt`: Generated CFG rules.
   - `output/samples.txt`: Up to 10,000 unique generated sentences.
   - `output/parse-results.txt`: Parse trees for each input sentence (or `()` for invalid ones).

   Example console output:
   ```
   Khởi tạo môi trường
   --- 2.1: Viết grammar ra file output/grammar.txt ---
   Đã viết grammar thành công vào file: output/grammar.txt

   --- 2.2: Sinh câu mẫu ra file output/samples.txt ---
   Đã sinh <number> câu duy nhất vào file: output/samples.txt

   --- 2.3: Phân tích cú pháp file input/sentences.txt ---
   Đã phân tích và ghi kết quả ra file: output/parse-results.txt

   HOÀN TẤT
   Kiểm tra kết quả trong thư mục 'output'.
   ```
### Part II - Semantic representation and Q&A
The program runs from `cli.py`, which executes all steps sequentially.

1. Ensure input files are prepared:
   - `input/sample-queries.txt`: Add sentences (one per line) to parse, e.g.:
     ```
      Có những món nào trong menu?
      Phở bò giá bao nhiêu?
      Có món gà rán không?
      Tôi đã đặt những món gì?
      Thêm 1 ly trà sữa vào đơn.
     ```

2. Run the program:
   ```
   python python/hcmut/iaslab/nlp/app/cli.py
   ```

3. Output:
   - `output/qhnn.txt`: Semantic relations from dependency parsing of query sentences.
   - `output/qhvp.txt`: Grammar relations integrated with the database.
   - `output/ll.txt`: Logical forms and procedural semantics.
   - `output/answer.txt`: Answers to the query sentences.

   Example console output:
   ```
         === HỆ THỐNG ĐẶT MÓN ĂN Q&A ===
      Đọc câu hỏi mẫu từ: input\sample-queries.txt
      Đã xử lý 5 câu hỏi.
      Kết quả được lưu trong thư mục: output

      Nhập câu lệnh (hoặc 'exit' để thoát):
      > menu có gì 
      Menu có: phở bò (50000đ), bún chả (40000đ), trà sữa (30000đ), gà rán (60000đ), cơm rang (35000đ), nem (20000đ), bánh mì (15000đ), cà phê sữa đá (25000đ), bánh cuốn (45000đ), chả giò (30000đ), cơm tấm (40000đ), hủ tiếu (45000đ), mì xào (38000đ), bánh xèo (35000đ), sinh tố dâu (28000đ), nước ép cam (25000đ), cơm chiên dương châu (42000đ), lẩu thái (180000đ), bò kho (55000đ), cá kho tộ (48000đ), thịt nướng (70000đ), salad trộn (32000đ), súp cua (35000đ), chè ba màu (20000đ), bánh flan (15000đ), kem vani (18000đ), trà chanh (20000đ), cơm gà xối mỡ (45000đ), bánh canh (40000đ), mì quảng (42000đ), bún bò huế (50000đ), cơm cháy (30000đ), gỏi cuốn (25000đ), bánh tráng nướng (20000đ), tôm chiên xù (65000đ), cánh gà chiên nước mắm (55000đ), khoai tây chiên (25000đ), trà đào (28000đ), sữa chua mít (22000đ), bánh tiramisu (35000đ).
      > cho tôi 1 phần kem vani
      Đã đặt 1 kem vani vào đơn hàng thành công!
      > đơn hàng có gì 
      Đơn hàng của bạn:
      • 1 trà sữa → 30.000đ
      • 1 kem vani → 18.000đ

      Tổng tiền: 48.000 VND
      > xóa trà sữa 
      Đã xóa trà sữa khỏi đơn hàng.
      > đơn hàng có gì 
      Đơn hàng của bạn:
      • 1 kem vani → 18.000đ

      Tổng tiền: 18.000 VND
      > cho tôi 1 phở bò tái giao lúc 5 giờ chiều 
      Đã đặt 1 phở bò lúc giao lúc 5 giờ chiều vào đơn hàng thành công!
      > đơn hàng có gì
      Đơn hàng của bạn:
      • 1 kem vani → 18.000đ
      • 1 phở bò (tái) – Giao lúc giao lúc 5 giờ chiều → 50.000đ

      Tổng tiền: 68.000 VND
      > ^X

      Tạm biệt!
   ```
## Customization
- **Modify Menu**: Edit `data.json` to add/remove foods, options, units, or numbers. Re-run `main.py` to update the grammar.
- **Max Sentences**: Adjust `max_sentences` in `generator.py` (default: 10,000).
- **Input Sentences**: Populate `input/sentences.txt` and `input/sample-queries.txt` with test sentences.

## Limitations
- The grammar is limited to the defined domain (food ordering in Vietnamese).
- Parsing uses a greedy tokenizer; unknown words result in failed parses.
- No semantic interpretation (only syntactic parsing).
- For larger grammars, generation/parsing may be slow due to recursion and randomness.
- The Q&A system uses a simulated database and handles specific query types; it may not generalize to all variations.

## Assignment Reference
This project fulfills Part I and Part II (Option 1: Simple Q&A System) of the NLP assignment (CO3085, Semester 1, 2025-2026):
- Part I:
1. 2.1: Write grammar to `output/grammar.txt`.
2. 2.2: Generate samples to `output/samples.txt`.
3. 2.3: Parse inputs to `output/parse-results.txt`.
- Part II:
1. Build dependency grammar parser.
2. Parse and output semantic relations to output/qhnn.txt.
3. Create grammar relations with database to output/qhvp.txt.
4. Create logical forms and procedural semantics to output/ll.txt.
5. Query database and answer queries to output/answer.txt.

## Author
- Lê Ngọc Hiền - 2211024
- Date: 11/2025

## License
This project is for educational purposes. No license specified.