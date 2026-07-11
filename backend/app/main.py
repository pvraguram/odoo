from fastapi import FastAPI, Form, HTTPException ,Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, FileResponse
from fastapi.staticfiles import StaticFiles
import os
import itertools
import re
import json
import requests
import time
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt


from flipflop import FlipFlopConverter
import logic
import sequence
from typing import Dict, Any

BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
OUTPUT_FOLDER = os.getenv("LOGICLAB_OUTPUT_DIR", os.path.join(BASE_DIR, "outputs"))
FRONTEND_DIR = os.path.join(BASE_DIR, "frontend")
GATES_FOLDER = os.path.join(FRONTEND_DIR, "gates")
STATIC_FOLDER = os.path.join(FRONTEND_DIR, "static")
os.makedirs(OUTPUT_FOLDER, exist_ok=True)

allowed_origins = [
    origin.strip()
    for origin in os.getenv("LOGICLAB_CORS_ORIGINS", "http://localhost:8000,http://127.0.0.1:8000").split(",")
    if origin.strip()
]

# -------------------------
# App Setup
# -------------------------
app = FastAPI(title="LogicLab API", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)
# -------------------------
# Utility Functions
# -------------------------
def validate_expr(expr: str):
    if not expr or not expr.strip():
        raise HTTPException(status_code=400, detail="Expression cannot be empty")

    expr_clean = expr.strip()
    if len(expr_clean) < 1:
        raise HTTPException(status_code=400, detail="Expression is too short")

    valid_chars = set('ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789&|~()+. \'')
    invalid_chars = set(expr_clean) - valid_chars
    if invalid_chars:
        raise HTTPException(status_code=400, detail=f"Invalid characters found: {', '.join(invalid_chars)}")


# -------------------------
# Truth Table
# -------------------------
@app.post("/truth-table")
async def truth_table(expr: str = Form(...)):
    validate_expr(expr)
    variables, table = logic.generate_truth_table(expr)

    formatted_table = []
    for values, result in table:
        input_dict = {var: bool(values[i]) for i, var in enumerate(variables)}
        formatted_table.append({
            "inputs": input_dict,
            "output": bool(result)
        })

    return JSONResponse(content={"variables": variables, "table": formatted_table})


# -------------------------
# K-Map
# -------------------------
@app.post("/kmap")
async def kmap(expr: str = Form(...)):
    validate_expr(expr)
    try:
        minimized, fig = logic.generate_kmap_and_minimize(expr)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc))

    timestamp = str(int(time.time() * 1000))
    kmap_filename = f"kmap_{timestamp}.png"
    kmap_path = os.path.join(OUTPUT_FOLDER, kmap_filename)
    kmap_default_path = os.path.join(OUTPUT_FOLDER, "kmap.png")
    
    fig.savefig(kmap_path, bbox_inches="tight")
    fig.savefig(kmap_default_path, bbox_inches="tight")
    plt.close(fig)

    parsed_expr = logic.parse_boolean_expr(expr)
    vars_list = sorted(parsed_expr.free_symbols, key=lambda x: x.name)

    if len(vars_list) <= 3:
        rows = 2 ** (len(vars_list) // 2)
        cols = 2 ** (len(vars_list) - len(vars_list) // 2)
        kmap_grid = []
        row_bits = len(vars_list) // 2
        col_bits = len(vars_list) - row_bits
        row_order = gray_code_order(row_bits)
        col_order = gray_code_order(col_bits)
        for r, row_value in enumerate(row_order):
            row = []
            for col_value in col_order:
                values = tuple(row_value + col_value)
                val_dict = dict(zip(vars_list, values))
                result = int(bool(parsed_expr.subs(val_dict)))
                row.append(str(result))
            kmap_grid.append(row)
    else:
        kmap_grid = [["N/A"]]

    return JSONResponse({
        "kmap": kmap_grid,
        "simplified": str(minimized),
        "image": f"/{kmap_filename}",
        "image_url": f"/kmap.png?t={timestamp}",  # Cache-busting URL
        "timestamp": timestamp
    })


@app.get("/kmap.png")
async def get_kmap_image():
    return FileResponse(os.path.join(OUTPUT_FOLDER, "kmap.png"))

@app.get("/kmap_{timestamp}.png")
async def get_timestamped_kmap_image(timestamp: str):
    kmap_filename = f"kmap_{timestamp}.png"
    kmap_path = os.path.join(OUTPUT_FOLDER, kmap_filename)
    if os.path.exists(kmap_path):
        return FileResponse(kmap_path)
    else:
        # Fallback to default kmap.png
        return FileResponse(os.path.join(OUTPUT_FOLDER, "kmap.png"))

# Serve all output files (images, diagrams, etc.)
@app.get("/outputs/{filename}")
async def get_output_file(filename: str):
    if filename != os.path.basename(filename):
        raise HTTPException(status_code=400, detail="Invalid filename")
    file_path = os.path.join(OUTPUT_FOLDER, filename)
    if os.path.exists(file_path):
        return FileResponse(file_path)
    else:
        raise HTTPException(status_code=404, detail="File not found")


# -------------------------
# Boolean Expression Simplifier
# -------------------------
@app.post("/simplify")
async def simplify_expression(expr: str = Form(...)):
    validate_expr(expr)
    try:
        result = logic.simplify_boolean_expression(expr)
        return JSONResponse(content=result)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Simplification failed: {str(e)}")


# -------------------------
# Circuit Generation
# -------------------------
@app.post("/circuit")
async def circuit(expr: str = Form(...)):
    validate_expr(expr)
    try:
        parsed_expr = logic.parse_boolean_expr(expr)
        variables = sorted([v.name for v in parsed_expr.free_symbols])

        circuit_text = generate_simple_circuit_text(expr, variables)

        return JSONResponse({
            "circuit_text": circuit_text,
            "variables": variables,
            "gate_count": estimate_gate_count(expr),
            "expression": expr
        })
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Circuit generation failed: {str(e)}")


def generate_simple_circuit_text(expr: str, variables: list) -> str:
    expr_clean = expr.replace("AND", "&").replace("OR", "|").replace("NOT", "~")
    expr_clean = expr_clean.replace(".", "&").replace("+", "|")

    and_count = expr_clean.count("&")
    or_count = expr_clean.count("|")
    not_count = expr_clean.count("~")

    circuit_text = f"""
Circuit Diagram for: {expr}

Inputs: {', '.join(variables)}

Gates Required:
- AND gates: {and_count}
- OR gates: {or_count}
- NOT gates: {not_count}
- Total gates: {and_count + or_count + not_count}

Circuit Structure:
"""

    if and_count > 0:
        circuit_text += f"- {and_count} AND gate(s) for product terms\n"
    if or_count > 0:
        circuit_text += f"- {or_count} OR gate(s) for sum terms\n"
    if not_count > 0:
        circuit_text += f"- {not_count} NOT gate(s) for inversions\n"

    circuit_text += f"\nOutput: Connected to final OR gate (if multiple terms) or final AND gate"
    return circuit_text


def estimate_gate_count(expr: str) -> int:
    expr_clean = expr.replace("AND", "&").replace("OR", "|").replace("NOT", "~")
    expr_clean = expr_clean.replace(".", "&").replace("+", "|")
    return expr_clean.count("&") + expr_clean.count("|") + expr_clean.count("~")


# -------------------------
# Sequence Detector
# -------------------------
@app.post("/sequence-detector")
async def sequence_detector(
    sequence_str: str = Form(...),
    test_sequence: str = Form(""),
    detector_type: str = Form("mealy")
):
    seq = sequence_str.strip()
    test_seq = test_sequence.strip() if test_sequence else ""

    if not seq or not re.fullmatch(r"[01]+", seq):
        return JSONResponse({"success": False, "error": "Sequence must contain only 0s and 1s"})
    if test_seq and not re.fullmatch(r"[01]+", test_seq):
        return JSONResponse({"success": False, "error": "Test sequence must contain only 0s and 1s"})

    result = sequence.analyze_sequence_backend(seq, test_seq)

    state_table = []
    detector = sequence.SequenceDetector(seq)
    for (state, bit), next_state in detector.transitions.items():
        state_table.append({
            "current_state": state if state else "S0",
            "input": bit,
            "next_state": next_state if next_state else "S0",
            "is_output": next_state == seq
        })

    # Add cache-busting timestamps to image URLs
    import time
    timestamp = str(int(time.time() * 1000))
    
    # Update image URLs with cache-busting
    if "diagram" in result:
        result["diagram"] = f"{result['diagram']}?t={timestamp}"
    if "truth_table_image" in result:
        result["truth_table_image"] = f"{result['truth_table_image']}?t={timestamp}"
    if "kmap_images" in result:
        for key in result["kmap_images"]:
            result["kmap_images"][key] = f"{result['kmap_images'][key]}?t={timestamp}"

    return JSONResponse({
        "success": True,
        "message": "Sequence detector analysis completed successfully",
        "data": {
            **result,
            "state_table": state_table,
            "detector_type": detector_type,
            "timestamp": timestamp
        }
    })


@app.post("/compare-sequences")
async def compare_sequences(
    sequence_a: str = Form(...),
    sequence_b: str = Form(...),
    test_sequence: str = Form("")
):
    sequence_a = sequence_a.strip()
    sequence_b = sequence_b.strip()
    test_sequence = test_sequence.strip()

    for label, value in {"sequence_a": sequence_a, "sequence_b": sequence_b}.items():
        if not value or not re.fullmatch(r"[01]+", value):
            raise HTTPException(status_code=400, detail=f"{label} must contain only 0s and 1s")
    if test_sequence and not re.fullmatch(r"[01]+", test_sequence):
        raise HTTPException(status_code=400, detail="test_sequence must contain only 0s and 1s")

    detector_a = sequence.SequenceDetector(sequence_a)
    detector_b = sequence.SequenceDetector(sequence_b)
    return {
        "sequence_a": sequence_a,
        "sequence_b": sequence_b,
        "states_a": len(detector_a.states),
        "states_b": len(detector_b.states),
        "detections_a": detector_a.simulate(test_sequence) if test_sequence else [],
        "detections_b": detector_b.simulate(test_sequence) if test_sequence else [],
    }
# -------------------------
# Flip-Flop Analysis
# -------------------------

# --- Flip-Flop Tables ---
characteristic_tables = {
    "D": [
        {"Qn":0,"D":0,"Qn+1":0},
        {"Qn":0,"D":1,"Qn+1":1},
        {"Qn":1,"D":0,"Qn+1":0},
        {"Qn":1,"D":1,"Qn+1":1},
    ],
    "T": [
        {"Qn":0,"T":0,"Qn+1":0},
        {"Qn":0,"T":1,"Qn+1":1},
        {"Qn":1,"T":0,"Qn+1":1},
        {"Qn":1,"T":1,"Qn+1":0},
    ],
    "JK":[
        {"Qn":0,"J":0,"K":0,"Qn+1":0},
        {"Qn":0,"J":1,"K":0,"Qn+1":1},
        {"Qn":1,"J":0,"K":1,"Qn+1":0},
        {"Qn":1,"J":1,"K":0,"Qn+1":1},
    ],
    "SR":[
        {"Qn":0,"S":0,"R":0,"Qn+1":0},
        {"Qn":0,"S":1,"R":0,"Qn+1":1},
        {"Qn":1,"S":0,"R":0,"Qn+1":1},
        {"Qn":1,"S":0,"R":1,"Qn+1":0},
    ]
}

excitation_tables = {
    "D":[
        {"Qn":0,"Qn+1":0,"D":0},
        {"Qn":0,"Qn+1":1,"D":1},
        {"Qn":1,"Qn+1":0,"D":0},
        {"Qn":1,"Qn+1":1,"D":1},
    ],
    "T":[
        {"Qn":0,"Qn+1":0,"T":0},
        {"Qn":0,"Qn+1":1,"T":1},
        {"Qn":1,"Qn+1":0,"T":1},
        {"Qn":1,"Qn+1":1,"T":0},
    ],
    "JK":[
        {"Qn":0,"Qn+1":0,"J":0,"K":0},
        {"Qn":0,"Qn+1":1,"J":1,"K":0},
        {"Qn":1,"Qn+1":0,"J":0,"K":1},
        {"Qn":1,"Qn+1":1,"J":1,"K":0},
    ],
    "SR":[
        {"Qn":0,"Qn+1":0,"S":0,"R":0},
        {"Qn":0,"Qn+1":1,"S":1,"R":0},
        {"Qn":1,"Qn+1":0,"S":0,"R":1},
        {"Qn":1,"Qn+1":1,"S":0,"R":0},
    ]
}


def derive_boolean_expression(available_ff: str, required_ff: str):
    """
    Simple derivation: maps required FF output (Qn+1) to available FF input equations.
    This is a basic placeholder for actual K-map simplification logic.
    """
    exc_table = excitation_tables[available_ff]
    req_table = characteristic_tables[required_ff]

    inputs = [k for k in exc_table[0].keys() if k not in ["Qn","Qn+1"]]
    expressions = {inp: "" for inp in inputs}

    # Build canonical expressions (minterms) for each available FF input
    for inp in inputs:
        terms = []
        for row in exc_table:
            Qn = row["Qn"]
            Qnext = row["Qn+1"]
            val = row[inp]
            # Determine required FF input for this transition
            for req in req_table:
                if req["Qn"] == Qn and req["Qn+1"] == Qnext:
                    # Use required FF variable(s)
                    for key in req.keys():
                        if key not in ["Qn","Qn+1"]:
                            var = key
                            var_expr = var if req[var] == 1 else f"{var}'"
                            if val == 1:
                                # Basic sum-of-products style
                                term = var_expr
                                if Qn == 1:
                                    term += " * Qn"
                                else:
                                    term += " * Qn'"
                                terms.append(term)
        expressions[inp] = " + ".join(terms) if terms else "0"

    return expressions


@app.post("/flipflop-convert")
async def convert_flipflop(available_ff: str = Form(...), required_ff: str = Form(...)):
    available_ff = available_ff.upper()
    required_ff = required_ff.upper()
    if available_ff not in characteristic_tables or required_ff not in characteristic_tables:
        raise HTTPException(status_code=400, detail="Flip-flop type must be one of D, T, JK, SR")

    # Step 1
    step1 = f"Available Flip-Flop: {available_ff}, Required Flip-Flop: {required_ff}"

    # Step 2: Characteristic table of required FF
    char_table = characteristic_tables.get(required_ff, [])

    # Step 3: Excitation table of available FF
    exc_table = excitation_tables.get(available_ff, [])

    # Step 4: Real Boolean expressions
    expressions = derive_boolean_expression(available_ff, required_ff)

    # Step 5: Circuit diagram image integration (matches your filenames)
    key = f"{available_ff.lower()}_to_{required_ff.lower()}"
    file_path = os.path.join(STATIC_FOLDER, "diagrams", f"{key}.png")
    step5_diagram = f"/static/diagrams/{key}.png" if os.path.exists(file_path) else "/static/diagrams/default.png"

    return JSONResponse({
        "step1": step1,
        "step2_characteristic_table": char_table,
        "step3_excitation_table": exc_table,
        "step4_boolean_equations": expressions,
        "step5_circuit_image": step5_diagram
    })


@app.post("/flipflops")
async def flipflops_alias(available_ff: str = Form(...), required_ff: str = Form(...)):
    return await convert_flipflop(available_ff, required_ff)
# -------------------------
# Health Check
# -------------------------
@app.get("/health")
async def health_check():
    return {"status": "healthy", "endpoints": [
        "/truth-table", "/kmap", "/circuit", "/simplify",
        "/sequence-detector", "/compare-sequences", "/flipflop-convert", "/flipflops"
    ]}
# Map gate types to Verilog primitives
GATE_MAP = {
    "AND": "and",
    "OR": "or",
    "NOT": "not",
    "NAND": "nand",
    "NOR": "nor",
    "XOR": "xor",
    "XNOR": "xnor"
}

OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY", "")
OPENROUTER_URL = "https://openrouter.ai/api/v1/chat/completions"

# -------------------------
# AI Verilog Generation Endpoint
@app.post("/ai-generate-verilog")
async def ai_generate_verilog(request: Request):
    import time

    graph = await request.json()
    components = graph.get("components", [])
    connections = graph.get("connections", [])

    if not components:
        return {"verilog": "Error: No components detected. Draw at least one gate."}
    if not OPENROUTER_API_KEY:
        return {"verilog": "Error: OPENROUTER_API_KEY is not configured on the server."}

    # Convert graph to safe JSON string for the LLM
    description = json.dumps({"components": components, "connections": connections}, indent=2)

    payload = {
        "model": "mistralai/mistral-small-3.1-24b-instruct:free",  # ✅ New model
        "messages": [
            {
                "role": "system",
                "content": (
                    "You are an expert hardware designer. "
                    "Generate clean, syntactically correct gate-level Verilog code. "
                    "Use only primitive gates: AND, OR, NOT, NAND, NOR, XOR, XNOR. "
                    "Include module and endmodule."
                    "Ensure all inputs and outputs are defined."
                    "Just give the Verilog code & the code description without any additional text or comments."
                    "Remove the qoutes , Bold the Verilog Code ."
                )
            },
            {
                "role": "user",
                "content": f"Generate Verilog gate-level code for this logic graph:\n{description}"
            }
        ],
        "max_tokens": 450
    }

    headers = {
        "Authorization": f"Bearer {OPENROUTER_API_KEY}",
        "Content-Type": "application/json",
        "HTTP-Referer": "http://localhost",
        "X-Title": "Whiteboard AI"
    }

    # Retry & timeout logic
    max_retries = 3
    delay_seconds = 2
    last_error = None

    for attempt in range(1, max_retries + 1):
        try:
            response = requests.post(
                OPENROUTER_URL,
                headers=headers,
                json=payload,
                timeout=20
            )

            print(f"[AI CALL] Attempt {attempt} - Status {response.status_code}")

            if response.status_code == 200:
                try:
                    data = response.json()
                    verilog = data["choices"][0]["message"]["content"].strip()

                    if verilog:
                        # ✅ Auto-save to .v file
                        timestamp = int(time.time())
                        file_name = f"generated_{timestamp}.v"
                        file_path = os.path.join(OUTPUT_FOLDER, file_name)

                        with open(file_path, "w") as f:
                            f.write(verilog)

                        return {
                            "verilog": verilog,
                            "file_url": f"/outputs/{file_name}"
                        }
                    else:
                        last_error = "Empty AI response"
                except Exception as parse_error:
                    last_error = f"Parse Error: {str(parse_error)}"
            else:
                last_error = f"OpenRouter HTTP {response.status_code}: {response.text}"

        except requests.exceptions.Timeout:
            last_error = "AI request timed out."
        except Exception as e:
            last_error = f"AI call failed: {str(e)}"

        if attempt < max_retries:
            print(f"[AI CALL] Retrying in {delay_seconds}s...")
            time.sleep(delay_seconds)

    # All retries failed
    return {"verilog": f"Error: {last_error or 'Unknown AI failure'}"}
# -------------------------
# Static Files Setup
app.mount("/outputs", StaticFiles(directory=OUTPUT_FOLDER), name="outputs")

app.mount("/static/gates", StaticFiles(directory=GATES_FOLDER), name="gates")
app.mount("/static", StaticFiles(directory=STATIC_FOLDER), name="static")


# Serve frontend folder (DIGITAL) at root
app.mount("/", StaticFiles(directory=FRONTEND_DIR, html=True), name="frontend")


def gray_code_order(width: int):
    if width == 0:
        return [()]
    return [tuple(int(bit) for bit in format(i ^ (i >> 1), f"0{width}b")) for i in range(2 ** width)]


# -------------------------
# Server Startup
# -------------------------
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
