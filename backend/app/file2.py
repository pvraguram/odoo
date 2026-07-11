import itertools
import matplotlib.pyplot as plt
import matplotlib.patches as patches
from matplotlib.patches import FancyBboxPatch
import numpy as np
from typing import List, Dict, Tuple, Optional
import re


class SequenceDetector:
    """Base class for sequence detectors"""
    
    def __init__(self, sequence: str, detector_type: str = "mealy"):
        """
        Initialize sequence detector
        
        Args:
            sequence: Binary sequence to detect (e.g., "1010")
            detector_type: "mealy" or "moore"
        """
        self.sequence = sequence
        self.detector_type = detector_type.lower()
        self.states = []
        self.transitions = {}
        self.outputs = {}
        self.state_count = 0
        
        if self.detector_type not in ["mealy", "moore"]:
            raise ValueError("Detector type must be 'mealy' or 'moore'")
        
        self._generate_states()
        self._generate_transitions()
    
    def _generate_states(self):
        """Generate states based on sequence length"""
        if self.detector_type == "mealy":
            # Mealy: states represent partial matches
            self.states = [f"S{i}" for i in range(len(self.sequence) + 1)]
        else:  # Moore
            # Moore: states represent partial matches + output state
            self.states = [f"S{i}" for i in range(len(self.sequence) + 1)]
            # Add output state for Moore
            self.states.append("S_OUT")
        
        self.state_count = len(self.states)
    
    def _generate_transitions(self):
        """Generate state transitions and outputs"""
        if self.detector_type == "mealy":
            self._generate_mealy_transitions()
        else:
            self._generate_moore_transitions()
    
    def _generate_mealy_transitions(self):
        """Generate Mealy machine transitions"""
        for i, state in enumerate(self.states[:-1]):  # Exclude last state
            current_prefix = self.sequence[:i]
            
            # For input 0
            next_state_0, output_0 = self._get_next_state_and_output(current_prefix, "0", i)
            self.transitions[(state, "0")] = next_state_0
            self.outputs[(state, "0")] = output_0
            
            # For input 1
            next_state_1, output_1 = self._get_next_state_and_output(current_prefix, "1", i)
            self.transitions[(state, "1")] = next_state_1
            self.outputs[(state, "1")] = output_1
    
    def _generate_moore_transitions(self):
        """Generate Moore machine transitions"""
        for i, state in enumerate(self.states[:-1]):  # Exclude output state
            current_prefix = self.sequence[:i]
            
            # For input 0
            next_state_0, _ = self._get_next_state_and_output(current_prefix, "0", i)
            self.transitions[(state, "0")] = next_state_0
            
            # For input 1
            next_state_1, _ = self._get_next_state_and_output(current_prefix, "1", i)
            self.transitions[(state, "1")] = next_state_1
        
        # Set outputs for Moore (output depends only on state)
        for state in self.states:
            if state == "S_OUT":
                self.outputs[state] = 1
            else:
                self.outputs[state] = 0
    
    def _get_next_state_and_output(self, current_prefix: str, input_bit: str, current_state_index: int) -> Tuple[str, int]:
        """Determine next state and output for given input"""
        new_prefix = current_prefix + input_bit
        
        # Check if we have a complete match
        if new_prefix == self.sequence:
            if self.detector_type == "mealy":
                return "S0", 1  # Reset to start, output 1
            else:  # Moore
                return "S_OUT", 0  # Go to output state
        
        # Check for partial matches
        for i in range(len(new_prefix), 0, -1):
            suffix = new_prefix[-i:]
            if self.sequence.startswith(suffix):
                next_state_index = i
                if self.detector_type == "mealy":
                    return f"S{next_state_index}", 0
                else:  # Moore
                    return f"S{next_state_index}", 0
        
        # No match, go back to start
        if self.detector_type == "mealy":
            return "S0", 0
        else:  # Moore
            return "S0", 0
    
    def get_state_table(self) -> Dict:
        """Generate state transition table"""
        table = {
            "states": self.states,
            "inputs": ["0", "1"],
            "transitions": {},
            "outputs": {}
        }
        
        for state in self.states:
            for input_bit in ["0", "1"]:
                if (state, input_bit) in self.transitions:
                    next_state = self.transitions[(state, input_bit)]
                    table["transitions"][(state, input_bit)] = next_state
                    
                    if self.detector_type == "mealy":
                        table["outputs"][(state, input_bit)] = self.outputs[(state, input_bit)]
                    else:  # Moore
                        table["outputs"][state] = self.outputs[state]
        
        return table
    
    def detect_sequence(self, input_sequence: str) -> Dict:
        """Detect sequence in input and return trace"""
        current_state = "S0"
        trace = []
        output_sequence = []
        
        for i, input_bit in enumerate(input_sequence):
            if (current_state, input_bit) in self.transitions:
                next_state = self.transitions[(current_state, input_bit)]
                
                if self.detector_type == "mealy":
                    output = self.outputs[(current_state, input_bit)]
                else:  # Moore
                    output = self.outputs[current_state]
                
                trace.append({
                    "step": i + 1,
                    "input": input_bit,
                    "current_state": current_state,
                    "next_state": next_state,
                    "output": output
                })
                
                output_sequence.append(output)
                current_state = next_state
            else:
                # Invalid transition
                trace.append({
                    "step": i + 1,
                    "input": input_bit,
                    "current_state": current_state,
                    "next_state": "ERROR",
                    "output": 0
                })
                output_sequence.append(0)
        
        return {
            "input_sequence": input_sequence,
            "output_sequence": output_sequence,
            "trace": trace,
            "detections": sum(output_sequence)
        }
    
    def generate_state_diagram(self) -> plt.Figure:
        """Generate state diagram visualization"""
        fig, ax = plt.subplots(figsize=(12, 8))
        ax.set_xlim(0, 10)
        ax.set_ylim(0, 8)
        ax.axis('off')
        
        # Calculate positions for states
        state_positions = {}
        n_states = len(self.states)
        
        if n_states <= 4:
            # Arrange in a square
            positions = [(2, 6), (6, 6), (2, 2), (6, 2)]
            for i, state in enumerate(self.states):
                state_positions[state] = positions[i] if i < len(positions) else (4, 4)
        else:
            # Arrange in a circle
            radius = 3
            center_x, center_y = 5, 4
            for i, state in enumerate(self.states):
                angle = 2 * np.pi * i / n_states
                x = center_x + radius * np.cos(angle)
                y = center_y + radius * np.sin(angle)
                state_positions[state] = (x, y)
        
        # Draw states
        for state, pos in state_positions.items():
            x, y = pos
            
            # State circle
            if state == "S0":
                # Initial state (double circle)
                circle1 = plt.Circle((x, y), 0.4, fill=False, color='black', linewidth=2)
                circle2 = plt.Circle((x, y), 0.3, fill=False, color='black', linewidth=2)
                ax.add_patch(circle1)
                ax.add_patch(circle2)
            else:
                circle = plt.Circle((x, y), 0.4, fill=False, color='black', linewidth=2)
                ax.add_patch(circle)
            
            # State label
            ax.text(x, y, state, ha='center', va='center', fontsize=10, fontweight='bold')
            
            # Output label for Moore
            if self.detector_type == "moore":
                output = self.outputs.get(state, 0)
                ax.text(x, y-0.6, f"Z={output}", ha='center', va='center', fontsize=8)
        
        # Draw transitions
        for (state, input_bit), next_state in self.transitions.items():
            if state != next_state:  # Don't draw self-loops for simplicity
                start_pos = state_positions[state]
                end_pos = state_positions[next_state]
                
                # Calculate arrow position
                dx = end_pos[0] - start_pos[0]
                dy = end_pos[1] - start_pos[1]
                length = np.sqrt(dx**2 + dy**2)
                
                if length > 0:
                    # Normalize and scale
                    dx = dx / length * 0.3
                    dy = dy / length * 0.3
                    
                    # Draw arrow
                    ax.annotate('', xy=(end_pos[0] - dx, end_pos[1] - dy),
                              xytext=(start_pos[0] + dx, start_pos[1] + dy),
                              arrowprops=dict(arrowstyle='->', lw=1.5))
                    
                    # Input/output label
                    if self.detector_type == "mealy":
                        output = self.outputs.get((state, input_bit), 0)
                        label = f"{input_bit}/{output}"
                    else:  # Moore
                        label = input_bit
                    
                    # Position label
                    mid_x = (start_pos[0] + end_pos[0]) / 2
                    mid_y = (start_pos[1] + end_pos[1]) / 2
                    ax.text(mid_x, mid_y, label, ha='center', va='center', 
                           fontsize=8, bbox=dict(boxstyle="round,pad=0.2", facecolor="white", alpha=0.8))
        
        # Title
        title = f"{self.detector_type.capitalize()} Sequence Detector for '{self.sequence}'"
        ax.set_title(title, fontsize=14, fontweight='bold', pad=20)
        
        return fig


def create_sequence_detector(sequence: str, detector_type: str = "mealy") -> SequenceDetector:
    """Factory function to create sequence detector"""
    return SequenceDetector(sequence, detector_type)


def analyze_sequence_detector(sequence: str, detector_type: str = "mealy", test_sequence: str = "") -> Dict:
    """Complete analysis of sequence detector"""
    try:
        # Create detector
        detector = create_sequence_detector(sequence, detector_type)
        
        # Get state table
        state_table = detector.get_state_table()
        
        # Generate state diagram
        fig = detector.generate_state_diagram()
        
        # Test with provided sequence or generate default test
        if not test_sequence:
            # Create a test sequence that includes the target sequence
            test_sequence = f"001{sequence}010{sequence}1"
        
        detection_result = detector.detect_sequence(test_sequence)
        
        return {
            "success": True,
            "sequence": sequence,
            "detector_type": detector_type,
            "state_table": state_table,
            "state_count": detector.state_count,
            "test_sequence": test_sequence,
            "detection_result": detection_result,
            "analysis": {
                "min_states_required": len(sequence) + 1,
                "complexity": "O(n)" if detector_type == "mealy" else "O(n+1)",
                "advantages": {
                    "mealy": "Faster response, fewer states",
                    "moore": "More stable outputs, easier to debug"
                }[detector_type]
            }
        }
        
    except Exception as e:
        return {
            "success": False,
            "error": str(e),
            "sequence": sequence,
            "detector_type": detector_type
        }


def compare_mealy_moore(sequence: str, test_sequence: str = "") -> Dict:
    """Compare Mealy and Moore implementations for the same sequence"""
    mealy_result = analyze_sequence_detector(sequence, "mealy", test_sequence)
    moore_result = analyze_sequence_detector(sequence, "moore", test_sequence)
    
    return {
        "sequence": sequence,
        "test_sequence": test_sequence,
        "mealy": mealy_result,
        "moore": moore_result,
        "comparison": {
            "state_count": {
                "mealy": mealy_result.get("state_count", 0),
                "moore": moore_result.get("state_count", 0)
            },
            "detections": {
                "mealy": mealy_result.get("detection_result", {}).get("detections", 0),
                "moore": moore_result.get("detection_result", {}).get("detections", 0)
            }
        }
    }


# Example usage and testing functions
def test_sequence_detectors():
    """Test function for sequence detectors"""
    test_cases = [
        ("1010", "mealy"),
        ("1010", "moore"),
        ("110", "mealy"),
        ("110", "moore")
    ]
    
    results = []
    for sequence, detector_type in test_cases:
        result = analyze_sequence_detector(sequence, detector_type)
        results.append(result)
        print(f"Testing {detector_type} detector for sequence '{sequence}':")
        print(f"  States: {result.get('state_count', 0)}")
        print(f"  Success: {result.get('success', False)}")
        if result.get('success'):
            detections = result.get('detection_result', {}).get('detections', 0)
            print(f"  Detections in test: {detections}")
        print()
    
    return results


def analyze_flip_flops(sequence: str, detector_type: str) -> dict:
    """Analyze and recommend flip-flops for sequence detection"""
    # Calculate number of states needed
    states = generate_states(sequence, detector_type)
    state_count = len(states)
    flip_flop_count = (state_count - 1).bit_length()  # Number of bits needed to encode states

    # Generate state transitions
    transitions = generate_state_transitions(states, sequence)
    
    # Analyze state transitions for each flip-flop type
    ff_analysis = {
        'JK': analyze_jk_transitions(transitions),
        'D': analyze_d_transitions(transitions),
        'T': analyze_t_transitions(transitions),
        'SR': analyze_sr_transitions(transitions)
    }

    # Select optimal flip-flop type based on complexity
    recommended = select_optimal_flip_flop(ff_analysis)

    return {
        "recommended": recommended,
        "state_count": state_count,
        "flip_flop_count": flip_flop_count,
        "analysis": ff_analysis
    }

def generate_states(sequence: str, detector_type: str) -> list:
    """Generate all possible states for the sequence detector"""
    states = ['IDLE']
    current = ''
    
    for bit in sequence:
        current += bit
        states.append(f'S{len(current)}')
    
    if detector_type.lower() == 'moore':
        states.append('FOUND')  # Additional state for Moore machine
    
    return states

def generate_state_transitions(states: list, sequence: str) -> list:
    """Generate state transitions for all possible inputs"""
    transitions = []
    seq_len = len(sequence)
    
    for current_state in states:
        for input_bit in ['0', '1']:
            next_state = calculate_next_state(current_state, input_bit, sequence)
            transitions.append((current_state, input_bit, next_state))
    
    return transitions

def calculate_next_state(current_state: str, input_bit: str, sequence: str) -> str:
    """Calculate the next state based on current state and input"""
    if current_state == 'IDLE':
        return 'S1' if input_bit == sequence[0] else 'IDLE'
    
    if current_state.startswith('S'):
        state_num = int(current_state[1:])
        if state_num < len(sequence):
            if input_bit == sequence[state_num]:
                return f'S{state_num + 1}'
            else:
                return 'IDLE'
        else:
            return 'FOUND' if input_bit == sequence[-1] else 'IDLE'
    
    return 'IDLE'

def analyze_jk_transitions(transitions: list) -> dict:
    """Analyze transitions for JK flip-flops"""
    j_conditions = []
    k_conditions = []
    
    for prev, input_bit, next_state in transitions:
        if prev == '0' and next_state == '1':
            j_conditions.append(f"({prev}&{input_bit})")
        if prev == '1' and next_state == '0':
            k_conditions.append(f"({prev}&{input_bit})")
    
    return {
        "equations": {
            "J": " + ".join(j_conditions) if j_conditions else "0",
            "K": " + ".join(k_conditions) if k_conditions else "0"
        },
        "complexity": len(j_conditions) + len(k_conditions)
    }

def analyze_d_transitions(transitions: list) -> dict:
    """Analyze transitions for D flip-flops"""
    d_conditions = []
    
    for prev, input_bit, next_state in transitions:
        if next_state == '1':
            d_conditions.append(f"({prev}&{input_bit})")
    
    return {
        "equations": {
            "D": " + ".join(d_conditions) if d_conditions else "0"
        },
        "complexity": len(d_conditions)
    }

def analyze_t_transitions(transitions: list) -> dict:
    """Analyze transitions for T flip-flops"""
    t_conditions = []
    
    for prev, input_bit, next_state in transitions:
        if prev != next_state:
            t_conditions.append(f"({prev}&{input_bit})")
    
    return {
        "equations": {
            "T": " + ".join(t_conditions) if t_conditions else "0"
        },
        "complexity": len(t_conditions)
    }

def analyze_sr_transitions(transitions: list) -> dict:
    """Analyze transitions for SR flip-flops"""
    s_conditions = []
    r_conditions = []
    
    for prev, input_bit, next_state in transitions:
        if prev == '0' and next_state == '1':
            s_conditions.append(f"({prev}&{input_bit})")
        if prev == '1' and next_state == '0':
            r_conditions.append(f"({prev}&{input_bit})")
    
    return {
        "equations": {
            "S": " + ".join(s_conditions) if s_conditions else "0",
            "R": " + ".join(r_conditions) if r_conditions else "0"
        },
        "complexity": len(s_conditions) + len(r_conditions)
    }

def select_optimal_flip_flop(ff_analysis: dict) -> str:
    """Select the optimal flip-flop type based on equation complexity"""
    complexities = {
        ff_type: analysis["complexity"]
        for ff_type, analysis in ff_analysis.items()
    }
    
    # Select flip-flop with minimum complexity
    return min(complexities.items(), key=lambda x: x[1])[0]


if __name__ == "__main__":
    # Run tests
    test_sequence_detectors()