#!/usr/bin/env python3
"""
Complete Voice-Enabled Trajectory Generation Workflow
Demonstrates the full integration with specification checking, syntax checking,
and complete trajectory analysis and visualization.

This example shows:
1. Voice input to STL specification conversion
2. Trajectory generation with full parameter control
3. Specification checking using GPT
4. Syntax checking for failed trajectories
5. Complete visualization and analysis
6. Error handling and recovery

Author: AI Assistant
"""

import sys
import os
import time
import numpy as np

# Add parent directory to path for imports
sys.path.append(os.path.dirname(os.path.dirname(__file__)))

from voice_enabled_nl_to_stl import VoiceEnabledNLtoSTL
from basics.logger import color_text

def demonstrate_complete_workflow():
    """Demonstrate the complete voice-enabled trajectory generation workflow."""
    
    print("🎤 Complete Voice-Enabled Trajectory Generation Workflow")
    print("=" * 70)
    
    # Check if OpenAI API key is set
    if not os.getenv('OPENAI_API_KEY'):
        print("❌ ERROR: OPENAI_API_KEY environment variable not set!")
        print("Please set your OpenAI API key:")
        print("export OPENAI_API_KEY='your_api_key_here'")
        return 1
    
    # Configuration for different scenarios
    scenarios = [
        {
            "name": "reach_avoid",
            "objects": ["drone", "goal", "obstacle1"],  # Use correct object names
            "N": 50,
            "dt": 0.7,
            "description": "Reach goal while avoiding obstacles"
        },
        {
            "name": "treasure_hunt", 
            "objects": ["drone", "door_key", "chest"],  # Use correct object names
            "N": 60,
            "dt": 0.7,
            "description": "Navigate to treasure through complex environment"
        }
    ]
    
    for i, scenario_config in enumerate(scenarios):
        print(f"\n{'='*20} SCENARIO {i+1}: {scenario_config['name'].upper()} {'='*20}")
        print(f"Description: {scenario_config['description']}")
        print(f"Objects: {scenario_config['objects']}")
        print(f"Time steps: {scenario_config['N']}")
        print(f"Time step size: {scenario_config['dt']}")
        
        try:
            # Initialize voice-enabled system with advanced features
            print(f"\n🔧 Initializing voice system for {scenario_config['name']}...")
            voice_system = VoiceEnabledNLtoSTL(
                objects=scenario_config['objects'],
                N=scenario_config['N'],
                dt=scenario_config['dt'],
                GPT_model="gpt-5-mini",
                scenario_name=scenario_config['name']
            )
            
            # Enable all advanced features
            print("🔧 Enabling advanced features...")
            voice_system.enable_specification_checking(enabled=True, max_iterations=3)
            voice_system.enable_syntax_checking(enabled=True, max_iterations=3)
            
            # Test voice components
            print("🧪 Testing voice components...")
            if not voice_system.test_voice_components():
                print("❌ Voice components test failed! Skipping scenario.")
                continue
            
            print("✅ Voice components test passed!")
            
            # Demonstrate manual trajectory generation with mock specification
            print(f"\n🚁 Demonstrating trajectory generation for {scenario_config['name']}...")
            
            # Create mock specification based on scenario
            if scenario_config['name'] == "reach_avoid":
                mock_spec = "STL_formulas.inside_cuboid(objects['goal'], name='goal').eventually(0, 5) & STL_formulas.outside_cuboid(objects['obstacle1'], name='!obstacle1').always(0, 5)"
            else:  # treasure_hunt
                mock_spec = "STL_formulas.inside_cuboid(objects['chest'], name='chest').eventually(0, 10) & STL_formulas.outside_cuboid(objects['NE_inside_wall'], name='!NE_inside_wall').always(0, 10)"
            
            # Set mock messages
            voice_system.messages = [
                {"role": "system", "content": "You are an assistant guiding a drone..."},
                {"role": "user", "content": f"Task: {scenario_config['description']}"},
                {"role": "assistant", "content": f"Here's the specification: <{mock_spec}>"}
            ]
            
            # Generate and visualize trajectory
            print(f"📋 Using mock specification: {mock_spec}")
            voice_system._generate_and_visualize_trajectory()
            
            # Get results
            trajectory = voice_system.get_current_trajectory()
            if trajectory is not None:
                print(f"✅ Trajectory generated successfully!")
                print(f"   Shape: {trajectory.shape}")
                print(f"   Duration: {trajectory.shape[1] * scenario_config['dt']:.1f} seconds")
                
                # Analyze trajectory properties
                max_pos = np.max(trajectory[:3, :], axis=1)
                min_pos = np.min(trajectory[:3, :], axis=1)
                print(f"   Position range: X[{min_pos[0]:.2f}, {max_pos[0]:.2f}], Y[{min_pos[1]:.2f}, {max_pos[1]:.2f}], Z[{min_pos[2]:.2f}, {max_pos[2]:.2f}]")
                
                # Calculate total distance
                positions = trajectory[:3, :]
                distances = np.sqrt(np.sum(np.diff(positions, axis=1)**2, axis=0))
                total_distance = np.sum(distances)
                print(f"   Total distance: {total_distance:.2f} meters")
                
            else:
                print("❌ No trajectory generated")
            
            # Wait for user to view visualizations
            print(f"\n📊 Visualization windows are open for {scenario_config['name']}.")
            print("Press Enter to continue to next scenario...")
            input()
            
        except Exception as e:
            print(f"❌ Error in scenario {scenario_config['name']}: {e}")
            continue
    
    print("\n" + "="*70)
    print("🎉 Complete workflow demonstration finished!")
    print("="*70)
    
    return 0

def demonstrate_error_handling():
    """Demonstrate error handling and recovery features."""
    
    print("\n🛠️  Error Handling and Recovery Demonstration")
    print("=" * 50)
    
    try:
        # Initialize system
        voice_system = VoiceEnabledNLtoSTL(
            objects=["drone", "goal", "obstacle"],
            N=50,
            dt=0.7,
            GPT_model="gpt-5-mini",
            scenario_name="reach_avoid"
        )
        
        # Enable error handling features
        voice_system.enable_specification_checking(enabled=True, max_iterations=2)
        voice_system.enable_syntax_checking(enabled=True, max_iterations=2)
        
        # Test with invalid specification
        print("🧪 Testing error handling with invalid specification...")
        
        # Create invalid specification
        invalid_spec = "invalid_stl_formula"
        voice_system.messages = [
            {"role": "system", "content": "You are an assistant..."},
            {"role": "user", "content": "Test invalid specification"},
            {"role": "assistant", "content": f"Here's the specification: <{invalid_spec}>"}
        ]
        
        # This should trigger error handling
        print("📋 Testing with invalid specification...")
        voice_system._generate_and_visualize_trajectory()
        
        print("✅ Error handling demonstration completed")
        
    except Exception as e:
        print(f"❌ Error handling test failed: {e}")
    
    return 0

def main():
    """Main function."""
    
    print("🎤 Complete Voice-Enabled Trajectory Generation System")
    print("=" * 60)
    print("This demonstration shows the full integration capabilities:")
    print("• Voice input to STL specification conversion")
    print("• Complete trajectory generation workflow")
    print("• Specification checking and validation")
    print("• Syntax checking and error recovery")
    print("• Full visualization and analysis")
    print("• Error handling and recovery")
    print("=" * 60)
    
    # Run complete workflow demonstration
    result = demonstrate_complete_workflow()
    
    if result == 0:
        # Run error handling demonstration
        demonstrate_error_handling()
    
    print("\n🎯 Demonstration completed!")
    print("The voice-enabled system now includes:")
    print("✅ Complete trajectory generation workflow")
    print("✅ Specification checking using GPT")
    print("✅ Syntax checking for error recovery")
    print("✅ Full visualization and analysis")
    print("✅ Error handling and recovery")
    print("✅ Integration with original NL_to_STL system")
    
    return 0

if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)
