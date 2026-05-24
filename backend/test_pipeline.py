import sys
import os

# Include D:/DocuStreamAI/backend in Python PATH
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.schema import LogIngestRequest, LogMetrics
from app.ai_processor import parse_log_fallback
from app.database import get_words, compute_jaccard_similarity

def run_tests():
    print("==================================================")
    print("RUNNING DOCUSTREAM AI PIPELINE UNIT TESTS")
    print("==================================================")

    # Test 1: Test pattern matching log fallback parsing
    print("Test 1: Testing Local Heuristic Log Parser...")
    raw_log = "CRITICAL: NeuralLink synaptogenesis failure. Memory overflow in temporal sector 7B."
    parsed = parse_log_fallback(raw_log, "Unit Test Run")
    
    assert parsed.error_level == "CRITICAL", f"Expected CRITICAL, got {parsed.error_level}"
    assert parsed.service_name == "neural-link", f"Expected neural-link, got {parsed.service_name}"
    assert parsed.severity_score >= 9.0, f"Expected severity >= 9.0, got {parsed.severity_score}"
    assert parsed.alert_triggered == True, "Expected alert_triggered to be True"
    print("SUCCESS: Local Heuristic Log Parser passes successfully!")

    # Test 2: Word extract parsing
    print("\nTest 2: Testing Tokenizer & Similarity Metrics...")
    text1 = "Database connection pool DNS timeout shard-98"
    text2 = "temporary DNS timeout between clusters in database"
    
    jaccard_score = compute_jaccard_similarity(text1, text2)
    print(f"Jaccard similarity between:\n - '{text1}'\n - '{text2}'\nSimilarity Score: {jaccard_score:.4f}")
    assert jaccard_score > 0.0, "Expected Jaccard similarity to be greater than 0.0"
    print("SUCCESS: Jaccard Similarity matches correctly!")

    # Test 3: Standard Info Log parsing
    print("\nTest 3: Testing Info Log parsing...")
    info_log = "INFO: Slipped db-pool connection shard-98 re-established after 340ms."
    parsed_info = parse_log_fallback(info_log, "Unit Test Run")
    
    assert parsed_info.error_level == "INFO", f"Expected INFO, got {parsed_info.error_level}"
    assert parsed_info.service_name == "db-pool", f"Expected db-pool, got {parsed_info.service_name}"
    assert parsed_info.severity_score <= 2.0, f"Expected severity <= 2.0, got {parsed_info.severity_score}"
    assert parsed_info.alert_triggered == False, "Expected alert_triggered to be False"
    print("SUCCESS: Info Log Parser passes successfully!")

    print("\n==================================================")
    print("ALL PIPELINE DIAGNOSTIC TESTS PASSED!")
    print("==================================================")

if __name__ == "__main__":
    run_tests()
