# NLP Assignment: Grammar and Parser for Online Food Ordering

## Overview

This project is an implementation for the Natural Language Processing (NLP) assignment (CO3085) at HCMUT, focusing on a restricted domain for online food ordering in Vietnamese. It uses a Context-Free Grammar (CFG) to model user commands and queries related to ordering food, such as placing orders, adding/removing items, checking availability, prices, menu, and order status.

The system:
- Generates a CFG based on menu data from `data.json`.
- Produces random unique sample sentences from the grammar.
- Parses input sentences using a chart parser and outputs parse trees.

The project leverages the NLTK library for grammar handling and parsing. It is designed to run in a Python environment and processes inputs/outputs in specified directories.

## Features
- **Grammar Generation**: Dynamically builds a CFG from predefined rules and data (foods, units, numbers, attributes).
- **Sentence Generation**: Generates up to 10,000 unique sentences based on the grammar.
- **Sentence Parsing**: Tokenizes and parses input sentences, producing parse trees or empty results for invalid inputs.
- **Domain-Specific**: Handles Vietnamese phrases for food ordering, e.g., "Tôi muốn đặt 2 phần phở bò giao lúc 12 giờ."

## Project Structure
```
.
├── input/                  # Input directory (sentences.txt for parsing)
├── output/                 # Output directory (grammar.txt, samples.txt, parse-results.txt)
├── python/                 # Python source code
│   ├── conf/               # Configuration 
│   └── hcmut_iaslab/
│       └── nlp/
│           └── app/
│               ├── __init__.py
│               ├── data.json       # Menu data (foods, units, numbers)
│               ├── generator.py    # Sentence generation logic
│               ├── grammar.py      # Grammar definition and writing
│               ├── main.py         # Entry point to run the program
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
1. Clone the repository[https://github.com/HienLe2004/nlp-251] (if not have):
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

## Customization
- **Modify Menu**: Edit `data.json` to add/remove foods, options, units, or numbers. Re-run `main.py` to update the grammar.
- **Max Sentences**: Adjust `max_sentences` in `generator.py` (default: 10,000).
- **Input Sentences**: Populate `input/sentences.txt` with test sentences.

## Limitations
- The grammar is limited to the defined domain (food ordering in Vietnamese).
- Parsing uses a greedy tokenizer; unknown words result in failed parses.
- No semantic interpretation (only syntactic parsing).
- For larger grammars, generation/parsing may be slow due to recursion and randomness.

## Assignment Reference
This project fulfills Part I of the NLP assignment (CO3085, Semester 1, 2025-2026):
- 2.1: Write grammar to `output/grammar.txt`.
- 2.2: Generate samples to `output/samples.txt`.
- 2.3: Parse inputs to `output/parse-results.txt`.

## Author
- Lê Ngọc Hiền
- Date: 11/2025

## License
This project is for educational purposes. No license specified.