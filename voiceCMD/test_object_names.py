#!/usr/bin/env python3
"""
Test Object Names
Simple test to verify that object names are correctly configured.

Author: AI Assistant
"""

import sys
import os

# Add parent directory to path for imports
sys.path.append(os.path.dirname(os.path.dirname(__file__)))

from voice_enabled_nl_to_stl import VoiceEnabledNLtoSTL
from basics.scenarios import Scenarios
from basics.logger import color_text

def test_object_names():
    """Test that object names are correctly configured."""
    
    print("🧪 Testing Object Names Configuration")
    print("=" * 50)
    
    # Test scenarios
    scenarios_to_test = ["reach_avoid", "treasure_hunt"]
    
    for scenario_name in scenarios_to_test:
        print(f"\n📋 Testing scenario: {scenario_name}")
        
        # Get objects from Scenarios class (the source of truth)
        scenario = Scenarios(scenario_name)
        scenario_objects = scenario.objects
        print(f"   Scenario objects: {list(scenario_objects.keys())}")
        
        # Get objects from voice system
        voice_system = VoiceEnabledNLtoSTL(
            objects=["drone", "goal", "obstacle1"],  # These are just for initialization
            N=50,
            dt=0.7,
            scenario_name=scenario_name
        )
        
        voice_objects = voice_system._convert_objects_to_dict()
        print(f"   Voice system objects: {list(voice_objects.keys())}")
        
        # Check if they match
        if set(scenario_objects.keys()) == set(voice_objects.keys()):
            print(f"   ✅ Object names match!")
        else:
            print(f"   ❌ Object names don't match!")
            missing_in_voice = set(scenario_objects.keys()) - set(voice_objects.keys())
            extra_in_voice = set(voice_objects.keys()) - set(scenario_objects.keys())
            if missing_in_voice:
                print(f"      Missing in voice system: {missing_in_voice}")
            if extra_in_voice:
                print(f"      Extra in voice system: {extra_in_voice}")
        
        # Test a simple STL specification
        print(f"   🧪 Testing STL specification...")
        try:
            # Create a simple specification using the first goal object
            goal_objects = [k for k in scenario_objects.keys() if 'goal' in k.lower() or 'chest' in k.lower()]
            obstacle_objects = [k for k in scenario_objects.keys() if 'obstacle' in k.lower() or 'wall' in k.lower()]
            
            if goal_objects and obstacle_objects:
                test_spec = f"STL_formulas.inside_cuboid(objects['{goal_objects[0]}'], name='{goal_objects[0]}').eventually(0, 5)"
                print(f"      Test spec: {test_spec}")
                
                # Test that the objects exist in the dictionary
                if goal_objects[0] in voice_objects:
                    print(f"      ✅ Goal object '{goal_objects[0]}' found in voice system")
                else:
                    print(f"      ❌ Goal object '{goal_objects[0]}' NOT found in voice system")
                    
            else:
                print(f"      ⚠️  No suitable goal/obstacle objects found for testing")
                
        except Exception as e:
            print(f"      ❌ Error testing STL specification: {e}")
    
    print("\n" + "=" * 50)
    print("🎯 Object names test completed!")
    
    return 0

def main():
    """Main function."""
    return test_object_names()

if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)
