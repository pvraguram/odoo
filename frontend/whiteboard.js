// =====================
// Whiteboard Initialization
// =====================
const canvas = new fabric.Canvas("whiteboard", {
    selection: false,
    isDrawingMode: true,
    backgroundColor: "#ffffff"
});

// =====================
// Undo / Redo Stacks
// =====================
let undoStack = [];
let redoStack = [];

// Save current state to undo stack
function saveState() {
    redoStack = []; // clear redo stack on new action
    const json = canvas.toDatalessJSON();
    undoStack.push(json);
}

// Restore a saved state
function loadState(json) {
    canvas.loadFromJSON(json, () => {
        canvas.renderAll();
    });
}

// Save state on every object modification or addition
canvas.on('object:added', saveState);
canvas.on('object:modified', saveState);
canvas.on('object:removed', saveState);

// Initialize with first empty state
saveState();


let currentTool = "pen";
let brushColor = "#000000";
let brushSize = 5;
let drawingShape = false;
let shapeObject = null;
let startX = 0, startY = 0;
let gatePlacement = null; // which gate is being placed
let lastGeneratedFile = null;

canvas.freeDrawingBrush.color = brushColor;
canvas.freeDrawingBrush.width = brushSize;

// =====================
// Tool Handling
// =====================
function setTool(tool) {
    currentTool = tool;
    gatePlacement = null;
    document.querySelectorAll(".tool-btn").forEach(btn => btn.classList.remove("active"));
    document.getElementById(tool + "Tool")?.classList.add("active");

    if (tool === "pen") {
        canvas.isDrawingMode = true;
        canvas.freeDrawingBrush.color = brushColor;
        canvas.freeDrawingBrush.width = brushSize;
    } else if (tool === "eraser") {
        canvas.isDrawingMode = true;
        canvas.freeDrawingBrush.color = "#ffffff";
        canvas.freeDrawingBrush.width = brushSize + 5;
    } else if (tool === "highlighter") {
        canvas.isDrawingMode = true;
        canvas.freeDrawingBrush.color = brushColor + "80";
        canvas.freeDrawingBrush.width = brushSize + 10;
    } else {
        canvas.isDrawingMode = false;
    }
}

// =====================
// Move & Delete Tools
// =====================

// Move tool: select & drag objects
document.getElementById("moveTool")?.addEventListener("click", () => {
    setTool("move");
    canvas.isDrawingMode = false;
    canvas.selection = true;
    canvas.forEachObject(obj => obj.selectable = true);
});

// Delete tool: click to delete
document.getElementById("deleteTool")?.addEventListener("click", () => {
    setTool("delete");
    canvas.isDrawingMode = false;
    canvas.selection = false;
    canvas.forEachObject(obj => obj.selectable = false);
});

// Handle object deletion on click
canvas.on("mouse:down", (opt) => {
    if (currentTool === "delete") {
        const target = opt.target;
        if (target) {
            canvas.remove(target);
            canvas.discardActiveObject();
            canvas.renderAll();
        }
    }
});

function undo() {
    if (undoStack.length > 1) {
        redoStack.push(undoStack.pop()); // move current to redo
        const prev = undoStack[undoStack.length - 1];
        loadState(prev);
    }
}

function redo() {
    if (redoStack.length > 0) {
        const next = redoStack.pop();
        undoStack.push(next);
        loadState(next);
    }
}

document.addEventListener("keydown", (e) => {
    if ((e.ctrlKey || e.metaKey) && e.key === 'z') {
        e.preventDefault();
        undo();
    } else if ((e.ctrlKey || e.metaKey) && e.key === 'y') {
        e.preventDefault();
        redo();
    } else if (e.key === "Delete" || e.key === "Backspace") {
        // Delete selected objects in move mode
        if (currentTool === "move" && canvas.getActiveObjects().length > 0) {
            canvas.getActiveObjects().forEach(obj => canvas.remove(obj));
            canvas.discardActiveObject();
            canvas.renderAll();
            saveState();
        }
    }
});
// =====================

["pen", "eraser", "highlighter", "line"].forEach(tool => {
    document.getElementById(tool + "Tool")?.addEventListener("click", () => setTool(tool));
});

// =====================
// Gate Placement with Image + Fallback
// =====================
const gates = ["and", "or", "not", "nand", "nor", "xor", "xnor"];

gates.forEach(gate => {
    document.getElementById(gate + "Gate")?.addEventListener("click", () => {
        gatePlacement = gate.toUpperCase();
        currentTool = "gate";
        canvas.isDrawingMode = false;
        document.querySelectorAll(".tool-btn").forEach(btn => btn.classList.remove("active"));
        document.getElementById(gate + "Gate")?.classList.add("active");
    });
});

function placeGate(pointer) {
    const gateImgPath = `/static/gates/${gatePlacement.toLowerCase()}.png`;

    fabric.Image.fromURL(gateImgPath, function (img) {
        if (img) {
            img.set({
                left: pointer.x,
                top: pointer.y,
                scaleX: 0.5,
                scaleY: 0.5,
                hasControls: true,
                hasBorders: true,
                selectable: true
            });
            img.customGate = gatePlacement;
            canvas.add(img);
        }
    }, { crossOrigin: 'anonymous' }, function (err) {
        console.warn(`Image not found for ${gatePlacement}, using fallback rectangle.`);
        // Fallback rectangle with gate text
        const rect = new fabric.Rect({
            left: pointer.x,
            top: pointer.y,
            width: 80,
            height: 50,
            fill: "#d1d5db",
            stroke: "#374151",
            strokeWidth: 2,
            rx: 5,
            ry: 5,
            selectable: true
        });
        const text = new fabric.Text(gatePlacement, {
            left: pointer.x + 10,
            top: pointer.y + 15,
            fontSize: 14,
            fill: "#111827"
        });
        const group = new fabric.Group([rect, text], {
            left: pointer.x,
            top: pointer.y,
            selectable: true
        });
        group.customGate = gatePlacement;
        canvas.add(group);
    });
}

// =====================
// Mouse Events
// =====================
canvas.on("mouse:down", (opt) => {
    const pointer = canvas.getPointer(opt.e);

    if (currentTool === "line") {
        drawingShape = true;
        startX = pointer.x;
        startY = pointer.y;
        shapeObject = new fabric.Line([startX, startY, startX, startY], {
            stroke: brushColor,
            strokeWidth: brushSize,
            selectable: true
        });
        shapeObject.isWire = true;
        canvas.add(shapeObject);
    }
    else if (currentTool === "gate" && gatePlacement) {
        placeGate(pointer);
    }
});

canvas.on("mouse:move", (opt) => {
    if (drawingShape && currentTool === "line" && shapeObject) {
        const pointer = canvas.getPointer(opt.e);
        shapeObject.set({ x2: pointer.x, y2: pointer.y });
        canvas.renderAll();
    }
});

canvas.on("mouse:up", () => {
    drawingShape = false;
    shapeObject = null;
});

// =====================
// Clear Board
// =====================
document.getElementById("clearBoard")?.addEventListener("click", () => {
    canvas.clear();
    canvas.backgroundColor = "#ffffff";
});

// =====================
// Detection
// =====================
function detectGatesAndConnections() {
    const objects = canvas.getObjects();
    const components = [];
    const connections = [];
    let gateCount = 0;

    objects.forEach(obj => {
        if (obj.isWire) {
            connections.push({
                from: `wire_start_${obj.x1}_${obj.y1}`,
                to: `wire_end_${obj.x2}_${obj.y2}`
            });
        } else if (obj.customGate) {
            gateCount++;
            let inputs = (obj.customGate === "NOT") ? 1 : 2;
            components.push({
                id: `G${gateCount}`,
                type: obj.customGate,
                inputs: inputs
            });
        }
    });

    console.log("Detected components:", components);
    console.log("Detected connections:", connections);
    return { components, connections };
}

// =====================
// AI Verilog Generation
// =====================
document.getElementById("aiGenerateVerilog")?.addEventListener("click", async () => {
    const graph = detectGatesAndConnections();
    const outputEl = document.getElementById("verilogOutput");

    if (graph.components.length === 0) {
        outputEl.innerText = "No gates detected! Place gates first.";
        return;
    }

    outputEl.innerText = "Generating Verilog with AI...";

    try {
        const response = await fetch("/ai-generate-verilog", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify(graph)
        });

        const data = await response.json();
        outputEl.innerText = data.verilog || `Error: ${JSON.stringify(data)}`;
        lastGeneratedFile = data.file_url || null;

    } catch (err) {
        console.error(err);
        outputEl.innerText = "Backend not reachable!";
    }
});

// =====================
// Download Verilog
// =====================
document.getElementById("downloadVerilog")?.addEventListener("click", () => {
    if (lastGeneratedFile) {
        const link = document.createElement("a");
        link.href = lastGeneratedFile;
        link.download = lastGeneratedFile.split("/").pop();
        link.click();
    } else {
        const code = document.getElementById("verilogOutput").innerText;
        if (!code.trim()) return alert("Generate Verilog first!");
        const blob = new Blob([code], { type: "text/plain" });
        const link = document.createElement("a");
        link.href = URL.createObjectURL(blob);
        link.download = "circuit.v";
        link.click();
    }
});
