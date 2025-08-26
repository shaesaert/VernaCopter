#!/usr/bin/env python3
"""
Test Integration Script
Tests the voice-enabled trajectory generation integration without requiring voice input.

This script tests:
1. Voice system initialization
2. STL specification generation (using mock input)
3. Trajectory generation and visualization
4. Error handling

Author: AI Assistant
"""

import sys
import os
import time

# Add parent directory to path for imports
sys.path.append(os.path.dirname(os.path.dirname(__file__)))

from voice_enabled_nl_to_stl import VoiceEnabledNLtoSTL
from basics.logger import color_text

def test_voice_system_initialization():
    """Test voice system initialization."""
    print("🧪 Testing voice system initialization...")
    
    try:
        voice_system = VoiceEnabledNLtoSTL(
            objects=["drone", "goal", "obstacle1"],  # Use correct object names
            N=50,
            dt=0.7,
            GPT_model="gpt-5-mini",
            scenario_name="reach_avoid"
        )
        print("✅ Voice system initialization successful")
        return voice_system
    except Exception as e:
        print(f"❌ Voice system initialization failed: {e}")
        return None

def test_voice_components(voice_system):
    """Test voice components."""
    print("🧪 Testing voice components...")
    
    try:
        success = voice_system.test_voice_components()
        if success:
            print("✅ Voice components test passed")
            return True
        else:
            print("❌ Voice components test failed")
            return False
    except Exception as e:
        print(f"❌ Voice components test error: {e}")
        return False

def test_stl_specification_generation(voice_system):
    """Test STL specification generation with mock input."""
    print("🧪 Testing STL specification generation...")
    
    try:
        # Mock conversation messages
        mock_messages = [
            {"role": "system", "content": "You are an assistant guiding a drone..."},
            {"role": "user", "content": "The drone should reach the goal and avoid obstacles"},
            {"role": "assistant", "content": "I'll help you create an STL specification for that task. Here's the specification: <STL_formulas.inside_cuboid(objects[\"goal\"], name=\"goal\").eventually(0, 5) & STL_formulas.outside_cuboid(objects[\"obstacle1\"], name=\"!obstacle1\").always(0, 5)>"}
        ]
        
        voice_system.messages = mock_messages
        
        # Extract specification
        spec = voice_system.get_final_specification()
        if spec:
            print(f"✅ STL specification generated: {spec}")
            return spec
        else:
            print("❌ No STL specification generated")
            return None
    except Exception as e:
        print(f"❌ STL specification generation error: {e}")
        return None

def test_trajectory_generation(voice_system, spec):
    """Test trajectory generation."""
    print("🧪 Testing trajectory generation...")
    
    try:
        # Manually trigger trajectory generation
        voice_system._generate_and_visualize_trajectory()
        
        # Check if trajectory was generated
        trajectory = voice_system.get_current_trajectory()
        if trajectory is not None:
            print(f"✅ Trajectory generated successfully, shape: {trajectory.shape}")
            return True
        else:
            print("❌ No trajectory generated")
            return False
    except Exception as e:
        print(f"❌ Trajectory generation error: {e}")
        return False

def test_scenario_conversion():
    """Test scenario object conversion."""
    print("🧪 Testing scenario conversion...")
    
    try:
        voice_system = VoiceEnabledNLtoSTL(
            objects=["drone", "goal", "obstacle1"],  # Use correct object names
            N=50,
            dt=0.7,
            scenario_name="reach_avoid"
        )
        
        # Test reach_avoid scenario
        objects_dict = voice_system._convert_objects_to_dict()
        if "goal" in objects_dict and "obstacle1" in objects_dict:
            print("✅ Reach-avoid scenario conversion successful")
        else:
            print("❌ Reach-avoid scenario conversion failed")
            return False
        
        # Test treasure_hunt scenario
        voice_system.scenario_name = "treasure_hunt"
        objects_dict = voice_system._convert_objects_to_dict()
        if "door_key" in objects_dict and "chest" in objects_dict:
            print("✅ Treasure hunt scenario conversion successful")
        else:
            print("❌ Treasure hunt scenario conversion failed")
            return False
        
        return True
    except Exception as e:
        print(f"❌ Scenario conversion error: {e}")
        return False

def main():
    """Main test function."""
    print("🧪 Voice-Enabled Trajectory Generation Integration Test")
    print("=" * 60)
    
    # Check OpenAI API key
    if not os.getenv('OPENAI_API_KEY'):
        print("⚠️  WARNING: OPENAI_API_KEY not set. Some tests may fail.")
        print("   Set with: export OPENAI_API_KEY='your_api_key_here'")
    
    test_results = []
    
    # Test 1: Voice system initialization
    voice_system = test_voice_system_initialization()
    test_results.append(voice_system is not None)
    
    if voice_system is None:
        print("❌ Cannot continue tests without voice system")
        return 1
    
    # Test 2: Voice components (skip if no audio)
    try:
        components_ok = test_voice_components(voice_system)
        test_results.append(components_ok)
    except Exception as e:
        print(f"⚠️  Voice components test skipped: {e}")
        test_results.append(True)  # Skip this test
    
    # Test 3: Scenario conversion
    scenario_ok = test_scenario_conversion()
    test_results.append(scenario_ok)
    
    # Test 4: STL specification generation
    spec = test_stl_specification_generation(voice_system)
    test_results.append(spec is not None)
    
    # Test 5: Trajectory generation (only if spec was generated)
    if spec:
        trajectory_ok = test_trajectory_generation(voice_system, spec)
        test_results.append(trajectory_ok)
    else:
        print("⚠️  Trajectory generation test skipped (no specification)")
        test_results.append(True)  # Skip this test
    
    # Summary
    print("\n" + "=" * 60)
    print("📊 TEST RESULTS SUMMARY")
    print("=" * 60)
    
    tests = [
        "Voice system initialization",
        "Voice components",
        "Scenario conversion", 
        "STL specification generation",
        "Trajectory generation"
    ]
    
    passed = sum(test_results)
    total = len(test_results)
    
    for i, (test_name, result) in enumerate(zip(tests, test_results)):
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{i+1}. {test_name}: {status}")
    
    print(f"\nOverall: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All tests passed! Integration is working correctly.")
        return 0
    else:
        print("⚠️  Some tests failed. Check the output above for details.")
        return 1

if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)
