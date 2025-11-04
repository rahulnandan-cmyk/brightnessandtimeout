#!/usr/bin/env python3
"""
Debug script to validate YAML configuration for Mobly
Run this to check if your YAML file is properly formatted
"""

import yaml
import sys
from pprint import pprint

def validate_yaml(yaml_file):
    """Validate and display YAML structure"""
    print("=" * 70)
    print("YAML VALIDATION SCRIPT")
    print("=" * 70)
    print(f"File: {yaml_file}\n")

    try:
        # 1. Check if file exists
        print("✓ Step 1: Checking file exists...")
        with open(yaml_file, 'r') as f:
            content = f.read()
        print(f"  File size: {len(content)} bytes")
        print(f"  Lines: {len(content.splitlines())}")

        # 2. Check for tabs
        print("\n✓ Step 2: Checking for tab characters...")
        if '\t' in content:
            print("  ⚠️  WARNING: Tab characters found! Replace with spaces.")
            lines_with_tabs = [i+1 for i, line in enumerate(content.splitlines()) if '\t' in line]
            print(f"  Lines with tabs: {lines_with_tabs}")
        else:
            print("  ✓ No tabs found")

        # 3. Parse YAML
        print("\n✓ Step 3: Parsing YAML...")
        with open(yaml_file, 'r') as f:
            data = yaml.safe_load(f)

        if data is None:
            print("  ✗ ERROR: YAML file is empty or invalid")
            return False

        print("  ✓ YAML parsed successfully")

        # 4. Check structure
        print("\n✓ Step 4: Checking structure...")

        if 'TestBeds' not in data:
            print("  ✗ ERROR: 'TestBeds' key not found!")
            print(f"  Found keys: {list(data.keys())}")
            return False

        print("  ✓ 'TestBeds' key found")

        test_beds = data['TestBeds']
        if not isinstance(test_beds, list):
            print(f"  ✗ ERROR: 'TestBeds' should be a list, got {type(test_beds)}")
            return False

        print(f"  ✓ TestBeds is a list with {len(test_beds)} item(s)")

        if len(test_beds) == 0:
            print("  ✗ ERROR: TestBeds list is empty!")
            return False

        # 5. Check each test bed
        print("\n✓ Step 5: Validating test bed entries...")
        for i, bed in enumerate(test_beds):
            print(f"\n  Test Bed #{i+1}:")

            if 'Name' not in bed:
                print("    ✗ ERROR: 'Name' field missing")
                continue

            name = bed['Name']
            print(f"    Name: {name}")

            if 'Controllers' in bed:
                print(f"    ✓ Controllers: {list(bed['Controllers'].keys())}")
            else:
                print("    ⚠️  WARNING: No Controllers defined")

            if 'TestParams' in bed:
                params = bed['TestParams']
                print(f"    ✓ TestParams: {list(params.keys())}")
            else:
                print("    ⚠️  WARNING: No TestParams defined")

        # 6. Display full structure
        print("\n" + "=" * 70)
        print("FULL YAML STRUCTURE:")
        print("=" * 70)
        pprint(data, width=70, compact=False)

        print("\n" + "=" * 70)
        print("✓ VALIDATION COMPLETE - YAML appears valid!")
        print("=" * 70)
        return True

    except FileNotFoundError:
        print(f"✗ ERROR: File not found: {yaml_file}")
        return False
    except yaml.YAMLError as e:
        print("✗ ERROR: YAML parsing failed!")
        print(f"  {e}")
        return False
    except Exception as e:
        print(f"✗ ERROR: Unexpected error: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python3 debug_yaml.py <yaml_file>")
        sys.exit(1)

    yaml_file = sys.argv[1]
    success = validate_yaml(yaml_file)
    sys.exit(0 if success else 1)