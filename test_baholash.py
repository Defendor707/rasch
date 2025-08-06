#!/usr/bin/env python3
"""
Baholash mezonlarini test qilish
"""

def assign_grade(score):
    """
    Assign a grade (A+, A, B+, B, C+, C, NC) based on score.
    Rasmiy mezonlar:
    70+ ball – A+ daraja
    65 – 69,9 ball – A daraja
    60 – 64,9 ball – B+ daraja
    55 – 59,9 ball – B daraja
    50 – 54,9 ball – C+ daraja
    46 – 49,9 ball – C daraja
    """
    if score >= 70:
        return 'A+'
    elif score >= 65:
        return 'A'
    elif score >= 60:
        return 'B+'
    elif score >= 55:
        return 'B'
    elif score >= 50:
        return 'C+'
    elif score >= 46:
        return 'C'
    else:
        return 'NC'

# Test ballar
test_scores = [55.4, 65.0, 70.0, 45.0, 50.0, 60.0, 46.0]

print("🎯 Baholash mezonlari testi:")
print("=" * 50)

for score in test_scores:
    grade = assign_grade(score)
    print(f"• {score} ball = {grade} daraja")

print("\n📊 OTM foizi testi (65+ ball):")
otm_scores = [score for score in test_scores if score >= 65]
print(f"• 65+ ball olgan talabalar: {len(otm_scores)} ta")
print(f"• OTM foizi: {(len(otm_scores) / len(test_scores)) * 100:.1f}%") 