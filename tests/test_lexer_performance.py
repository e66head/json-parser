import time
import pytest
from jsonparser.lexer import JsonLexer

def test_lexer_tokenize_performance(monster_file):
    """Measures the time it takes to tokenize the monster JSON file."""
    with open(monster_file, "r") as f:
        content = f.read()
    
    file_size_mb = len(content) / (1024 * 1024)
    print(f"\n[Lexer Performance Test] File Size: {file_size_mb:.2f} MB")

    # Benchmark: Pure Tokenization
    start_time = time.perf_counter()
    
    lexer = JsonLexer(content)
    token_count = 0
    for _ in lexer.tokenize():
        token_count += 1
        
    duration = time.perf_counter() - start_time
    
    tokens_per_second = token_count / duration
    mb_per_second = file_size_mb / duration
    
    print(f"[Lexer Performance Test] Tokenized {token_count} tokens in {duration:.4f} seconds.")
    print(f"[Lexer Performance Test] Speed: {tokens_per_second:,.0f} tokens/sec ({mb_per_second:.2f} MB/sec)")

    assert token_count > 0
