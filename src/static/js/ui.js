import { cy } from './graph.js';
import { selectedNode } from './graph.js';
import { priorityInserts } from './graph.js';
import * as Graph from './graph.js';

// UI Functions

// Global
let drawMode = "node";

// Button Elements
const nodeButton = document.getElementById("nodeButton");
const edgeButton = document.getElementById("edgeButton");
const deleteButton = document.getElementById("deleteButton");
const debugButton = document.getElementById("debugButton");
const edgeBox = document.getElementById("edgeBox");
const createGraphButton = document.getElementById("createGraphButton");

const kInput = document.getElementById("kInput");
const kCutsButton = document.getElementById("kCutsButton");
const cutsContainer = document.getElementById("cutsContainer");

const kInput2 = document.getElementById("kInput2");
const kComponentsButton = document.getElementById("kComponentsButton");
const componentsContainer = document.getElementById("kComponentsContainer");


// Event Handlers
nodeButton.addEventListener("click", function() {
    drawMode = "node";
    selectButton(nodeButton);
    Graph.clearSelectedNode();
});
edgeButton.addEventListener("click", function() {
    drawMode = "edge";
    selectButton(edgeButton);
});
deleteButton.addEventListener("click", function() {
    drawMode = "delete";
    selectButton(deleteButton);
    Graph.clearSelectedNode();
});
debugButton.addEventListener("click", function() {
    let out = ""
    console.log("Draw Mode: ", drawMode)
    console.log("Nodes:");
    for (let node of cy.nodes()) {
        out += node.data('id') + " ";
    }
    console.log(out);
    console.log(cy.nodes());
    out = "";
    console.log("Edges:");
    for (let edge of cy.edges()) {
        out += edge.data('id') + " ";
    }
    console.log(out)
    console.log(cy.edges());
    if (selectedNode == null) console.log("selectedNode: Null");
    else console.log("selectedNode:", selectedNode.data('id'));
    console.log("Insert Queue", priorityInserts);
    console.log("Current amount of nodes in list:", cy.nodes().length);
    console.log("Json File:")
    console.log(cy.json());
    console.log("Edge List:")
    console.log(Graph.jsonToEdgeList());
    console.log('Clearing graph')
    Graph.cleanGraph();
});
createGraphButton.addEventListener("click", function() {
    let edges = JSON.parse(edgeBox.value);
    console.log("Creating a graph with", edges)
    try {
        Graph.createGraph(edges);
    }
    catch {
        console.log("Invalid Input")
    }
    
});

// UI Utility Functions
export function updateEdgeOutput() {
    // Outputs the list of edges in the graph
    let edges = JSON.stringify(Graph.jsonToEdgeList())
    edgeBox.value = edges;
}

function selectButton(button) {
    [nodeButton, edgeButton, deleteButton].forEach(button => button.classList.remove('buttonSelected'));
    button.classList.add('buttonSelected');
}

function createCutContainer(k_cuts) {
    cutsContainer.innerHTML = "Cuts:";

    // Check if no cuts
    if (k_cuts.length == 0) {
        const item = document.createElement('div');
        console.log("No Cuts Found")
        item.innerText = "No cuts found."
        cutsContainer.appendChild(item);
    }

    k_cuts.forEach((cut, index) => {

        let text = "";
        cut.forEach(partition => {
            console.log("displaying partition", partition)
            text += "(" + partition.join(", ") + ") ";
        });

        const item = document.createElement('div');
        item.className = 'cutItem';
        item.innerText = text;

        item.addEventListener('mouseenter', () => {
            console.log("Hovering over cut", item.innerText);
            Graph.highlightCut(cut);
        });

        item.addEventListener('mouseleave', () => {
            Graph.cleanGraph();
        });

        cutsContainer.appendChild(item);
    });
}

function createComponentContainer(k_components) {
    componentsContainer.innerHTML = "Components:";

    if (k_components.length == 0) {
        const item = document.createElement('div');
        console.log("No Components Found")
        item.innerText = "No Components found."
        componentsContainer.appendChild(item);
    }

    k_components.forEach((cut, index) => {

        let text = "";
        cut.forEach(partition => {
            console.log("displaying partition", partition)
            text += "(" + partition.join(", ") + ") ";
        });

        const item = document.createElement('div');
        item.className = 'cutItem';
        item.innerText = text;

        item.addEventListener('mouseenter', () => {
            console.log("Hovering over cut", item.innerText, cut);
            Graph.highlightAny(cut);
        });

        item.addEventListener('mouseleave', () => {
            Graph.cleanGraph();
        });

        componentsContainer.appendChild(item);
    });
}

// API CALLS

//Find k cuts
kCutsButton.addEventListener("click", async () => {
    let k = kInput.value;
    const body = {
        data: Graph.jsonToEdgeList(),
        k: parseInt(k) 
    }
    console.log("POST: sending ", body);
    try {
        const response = await fetch("/algorithm-kcut", {
            method: "POST",
            headers: {
                "Content-Type": "application/json"
            },
            body: JSON.stringify(body)
        });

        let k_cuts = await response.json();
        console.log("Response:", k_cuts);
        // Create cut container
        createCutContainer(k_cuts);

    } catch (err) {
        console.error("Error:", err);
    }
}); 

//Find k components
kComponentsButton.addEventListener("click", async () => {
    let k = kInput2.value;
    const body = {
        data: Graph.jsonToEdgeList(),
        k: parseInt(k) 
    }
    console.log("POST: sending ", body);
    try {
        const response = await fetch("/algorithm-kcomponents", {
            method: "POST",
            headers: {
                "Content-Type": "application/json"
            },
            body: JSON.stringify(body)
        });

        let k_components = await response.json();
        console.log("Response:", k_components);

        createComponentContainer(k_components);

    } catch (err) {
        console.error("Error:", err);
    }
}); 



// Graph Interaction
cy.on('tap', function(event)
{   
    if (drawMode == "node"){
        Graph.drawNode(event);
    }

    else if (drawMode == 'edge'){
        Graph.drawEdge(event);
    }

    else if (drawMode == "delete") {
        Graph.deleteElement(event);
    }
    updateEdgeOutput();
    });

// Hotkeys
addEventListener("keydown", (event) => {})
onkeydown = (event) => {
    if (event.key == 'v') {
        console.log('v pressed, switching draw mode to node');
        drawMode="node";
    Graph.clearSelectedNode();
    } else if (event.key == 'e') {
        console.log('e pressed, switching draw mode to edge');
        drawMode="edge";
    Graph.clearSelectedNode();
    } else if (event.key == 'd') {
        console.log('d pressed, switching draw mode to delete');
        drawMode="delete";
    Graph.clearSelectedNode();
    } 
}
