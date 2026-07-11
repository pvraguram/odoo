import os
from graphviz import Digraph
import pandas as pd
import matplotlib
matplotlib.use("Agg")
from sympy import symbols, SOPform
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle

# Unified output folder (matches main.py)
OUTPUT_DIR = "outputs"
os.makedirs(OUTPUT_DIR, exist_ok=True)


class SequenceDetector:
    def __init__(self, target_sequence: str):
        self.sequence = target_sequence.strip()
        self.states = self.build_states()
        self.transitions = self.build_transitions()

    def build_states(self):
        return [self.sequence[:i] for i in range(len(self.sequence) + 1)]

    def build_transitions(self):
        transitions = {}
        for state in self.states:
            for bit in ['0', '1']:
                next_state = (state + bit)[-len(self.sequence):]
                for i in range(len(self.sequence), 0, -1):
                    if next_state.endswith(self.sequence[:i]):
                        next_state = self.sequence[:i]
                        break
                else:
                    next_state = ''
                transitions[(state, bit)] = next_state
        return transitions

    def draw_state_diagram(self, filename='state_diagram'):
        dot = Digraph(comment="State Diagram")
        dot.attr(size="8,6")
        dot.attr(dpi="200")   
        for state in self.states:
            shape = 'doublecircle' if state == self.sequence else 'circle'
            dot.node(state if state else 'S0', state if state else 'S0', shape=shape)
        for (src, bit), dst in self.transitions.items():
            dot.edge(src if src else 'S0', dst if dst else 'S0', label=bit)
        output_path = os.path.join(OUTPUT_DIR, filename)
        dot.render(output_path, format='png', cleanup=True)
        return output_path + ".png"

    def simulate(self, input_stream: str):
        current_state = ''
        detections = []
        for i, bit in enumerate(input_stream):
            current_state = self.transitions[(current_state, bit)]
            if current_state == self.sequence:
                detections.append(i - len(self.sequence) + 1)
        return detections


def xor(a, b):
    return '1' if a != b else '0'


def generate_flipflop_truth_table(sequence, flipflop_type='T'):
    flipflop_type = flipflop_type.upper()
    states = [sequence[:i] for i in range(len(sequence) + 1)]
    num_bits = len(bin(len(states) - 1)[2:])
    state_encoding = {s: format(i, f'0{num_bits}b') for i, s in enumerate(states)}

    table = []
    for (src, bit), dst in SequenceDetector(sequence).build_transitions().items():
        row = {'X': bit}
        ps = state_encoding[src].rjust(num_bits, '0')
        ns = state_encoding[dst].rjust(num_bits, '0')
        for i in range(num_bits):
            row[f'Q{i}'] = ps[num_bits - 1 - i]
            row[f'Q{i}+'] = ns[num_bits - 1 - i]
        row['Y'] = '1' if dst == sequence else '0'

        if flipflop_type == 'T':
            for i in range(num_bits):
                row[f'T{i+1}'] = xor(row[f'Q{i}'], row[f'Q{i}+'])
        elif flipflop_type == 'D':
            for i in range(num_bits):
                row[f'D{i+1}'] = row[f'Q{i}+']
        elif flipflop_type == 'JK':
            for i in range(num_bits):
                q = row[f'Q{i}']
                qn = row[f'Q{i}+']
                row[f'J{i+1}'] = '1' if q == '0' and qn == '1' else ('0' if q == '0' and qn == '0' else '-')
                row[f'K{i+1}'] = '1' if q == '1' and qn == '0' else ('0' if q == '1' and qn == '1' else '-')

        table.append(row)

    df = pd.DataFrame(table)
    df.fillna('-', inplace=True)
    return df


def generate_kmap_from_truth_table(truth_df, flipflop_type='T'):
    flipflop_type = flipflop_type.upper()
    input_vars = sorted([col for col in truth_df.columns if col.startswith('Q') and '+' not in col], reverse=True)
    input_vars.append('X')

    if flipflop_type == 'T':
        columns = [col for col in truth_df.columns if col.startswith('T')]
    elif flipflop_type == 'D':
        columns = [col for col in truth_df.columns if col.startswith('D')]
    elif flipflop_type == 'JK':
        columns = [col for col in truth_df.columns if col.startswith('J') or col.startswith('K')]
    else:
        columns = []

    kmap = {}
    for col in columns:
        on_minterms = []
        for _, row in truth_df.iterrows():
            if row[col] == '1':
                binary_input = ''.join(row[var] for var in input_vars)
                on_minterms.append(int(binary_input, 2))
        kmap[col] = on_minterms
    return kmap


def simplify_kmap(kmap_dict, num_bits):
    num_vars = num_bits + 1  # flip-flops + input X
    var_names = [f'Q{i}' for i in range(num_bits-1, -1, -1)] + ['X']
    vars_sym = symbols(' '.join(var_names))

    simplifications = {}
    for name, minterms in kmap_dict.items():
        if minterms:
            try:
                simplified_expr = SOPform(vars_sym, minterms)
                simplifications[name] = str(simplified_expr)
            except Exception:
                simplifications[name] = '0'
        else:
            simplifications[name] = '0'
    return simplifications


def save_truth_table_as_image(df, filename='truth_table.png'):
    fig, ax = plt.subplots(figsize=(len(df.columns) * 1.2, len(df) * 0.6))
    ax.axis('off')
    table = ax.table(cellText=df.values, colLabels=df.columns, loc='center')
    table.auto_set_font_size(False)
    table.set_fontsize(10)
    table.scale(1.2, 1.2)
    plt.tight_layout()
    save_path = os.path.join(OUTPUT_DIR, filename)
    plt.savefig(save_path)
    plt.close()
    return save_path


def draw_kmap(minterms, name, num_vars):
    rows = 2 ** (num_vars // 2)
    cols = 2 ** (num_vars - num_vars // 2)
    grid = [['0'] * cols for _ in range(rows)]

    for m in minterms:
        r = (m >> (num_vars - num_vars // 2)) & (rows - 1)
        c = m & (cols - 1)
        grid[r][c] = '1'

    fig, ax = plt.subplots()
    ax.set_xlim(0, cols)
    ax.set_ylim(0, rows)
    ax.set_title(f"K-Map for {name}")
    ax.axis('off')
    for y in range(rows):
        for x in range(cols):
            ax.add_patch(Rectangle((x, rows - y - 1), 1, 1, fill=True, edgecolor='black', facecolor='white'))
            ax.text(x + 0.5, rows - y - 0.5, grid[y][x], ha='center', va='center', fontsize=14)

    save_path = os.path.join(OUTPUT_DIR, f'kmap_{name}.png')
    plt.savefig(save_path)
    plt.close()
    return save_path


def analyze_sequence_backend(sequence_str: str, test_sequence: str = "", ff_type='D'):
    detector = SequenceDetector(sequence_str)
    detections = detector.simulate(test_sequence) if test_sequence else []

    # Save diagram
    detector.draw_state_diagram("state_diagram")

    # Flip-flop truth table
    truth_df = generate_flipflop_truth_table(sequence_str, flipflop_type=ff_type)
    save_truth_table_as_image(truth_df)

    # Determine flip-flop count
    states = [sequence_str[:i] for i in range(len(sequence_str) + 1)]
    num_bits = len(bin(len(states) - 1)[2:])
    num_vars = num_bits + 1

    # K-map & Simplification
    kmap = generate_kmap_from_truth_table(truth_df, flipflop_type=ff_type)
    simplified_logic = simplify_kmap(kmap, num_bits)
    kmap_images = {ff: draw_kmap(minterms, ff, num_vars=num_vars) for ff, minterms in kmap.items()}

    return {
        "sequence": sequence_str,
        "detections": detections,
        "diagram": "/outputs/state_diagram.png",
        "truth_table": truth_df.to_dict(orient='records'),
        "truth_table_image": "/outputs/truth_table.png",
        "kmap_minterms": kmap,
        "simplified_logic": simplified_logic,
        "kmap_images": {ff: f"/outputs/kmap_{ff}.png" for ff in kmap.keys()}
    }
