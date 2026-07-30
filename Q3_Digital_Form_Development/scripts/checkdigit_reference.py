#!/usr/bin/env python3
"""
Reference implementation of the specimen label check digit scheme stated in
reference_media/specimen_label_allocation.csv:
"Modulus 11, weights 2 to 7 applied right to left, remainder 10 recorded as X".

This is a plain-Python mirror of the XPath calculation implemented in the
XLSForm (form/HH2026_v1.xlsx, fields label_digits/label_checksum/
label_check_expected) -- used to independently generate and verify the test
vectors quoted in documentation/04_specimen_label_validation.md and
test_plan.csv, without relying on ODK Collect to check its own arithmetic.
"""


def check_digit(body6: str) -> str:
    if len(body6) != 6 or not body6.isdigit():
        raise ValueError("body must be exactly 6 digits")
    digits = [int(c) for c in body6]
    weights = [7, 6, 5, 4, 3, 2]  # left to right; rightmost digit gets weight 2
    checksum = sum(d * w for d, w in zip(digits, weights))
    remainder = checksum % 11
    return "X" if remainder == 10 else str(remainder)


def full_label(body6: str) -> str:
    return f"BSN{body6}-{check_digit(body6)}"


if __name__ == "__main__":
    vectors = ["480000", "480001", "480012", "480021", "480899", "480900"]
    for body in vectors:
        print(f"{body} -> {full_label(body)}")
