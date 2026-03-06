// Code for initializing the cy instance and graph functiosn

import * as Utils from './utils.js';


// Global
export let selectedNode = null;
export let priorityInserts = []; // Stores removed node ids that have reinsert priority

// Create cytoscape instance
export const cy = cytoscape({
    container: document.getElementById('cy'),
    zoom: 1.5,
    selector: 'node:active',
    style: {
        'overlay-opacity': 0,
        'overlay-color': 'transparent',
        'overlay-padding': 0,
    },
        style: [ 
        {
        selector: 'node', style: {
            'background-color': '#fff',
            'border-width': 2,
            'border-color': '#000',
            'label': 'data(id)',
            'text-valign': 'center',
            'text-halign': 'center',
            'color': '#000',
        }
        },
        {
        selector: 'edge',
        style: {
            'width': 3,
            'line-color': '#ccc',
            'target-arrow-color': '#ccc',
            'target-arrow-shape': 'none',
            'curve-style': 'bezier'
        }
        },
        {
            selector: '.blueNode',
            style: {
                'background-color': '#ADD8E6',
                'border-width': 2,
                'border-color': 'black'
            }
        },
        {
            selector: '.redNode',
            style: {
                'background-color': '#ff8080',
                'border-width': 2,
                'border-color': 'black'
            }
        },
        {
            selector: '.selectedNode',
            style: {
                'border-width': 4,
                'border-color': 'black'
            }
        },
    ],
    layout: {
        name: 'grid',
        rows: 1
    }
});

// Graph Utility Functions
export function clearSelectedNode() {
    // Clears selected node and removes styling
    selectedNode.removeClass('selectedNode');
    selectedNode = null;
}

export function jsonToEdgeList() {
    // Converts cytoscape json into an edge list for api calling
    let output = [];
    let data = cy.json();
    let edges = data.elements.edges
    if (edges) {
        for (let edge of edges) {
            let s = parseInt(edge.data.source);
            let t = parseInt(edge.data.target);
            output.push([s,t]);
        }
}
    return output
}

export function highlightCut(partitions) {     
    // Given 2 partition of nodes, highlights them in different colors
let A = partitions[0]
let B = partitions[1]
console.log("Highlighting partitions:");
console.log(A);
console.log(B);
for (let nodeId of A) {
    console.log(nodeId);
    cy.getElementById(nodeId).addClass('redNode');
}
for (let nodeId of B) {
    cy.getElementById(nodeId).addClass('blueNode');
    console.log(cy.getElementById(nodeId))
}

}

export function cleanGraph() {
    // Removes classes from every node
    cy.nodes().removeClass('redNode blueNode');
}

export function createGraph(edges) {
    cy.elements().remove();
    let nodes = new Set();
    edges.forEach(([u,v]) => {
        if (!nodes.has(u)) {
            cy.add({group: 'nodes', data: {id: u}});
        }
        if (!nodes.has(v)) {
            cy.add({group: 'nodes', data: {id: v}});
        }
        cy.add({group:'edges', data: {source: u, target: v}});
    }
)
    const layout = cy.layout({ name: 'cose' });
    layout.on('layoutstop', function() {
        cy.zoom(cy.zoom() * 0.7);
        cy.center();
    });
    layout.run();

    // Repopulate Priority List
    console.log("repopulating list");
    let nodeIds =  cy.nodes().map(node => parseInt(node.id()));
    const maxVal = Math.max(...nodeIds);
    console.log(maxVal);
    nodeIds = new Set(nodeIds);
    console.log(nodeIds);
    for (let i = 1; i <= maxVal; i++) {
        if (!nodeIds.has(i)) {
            priorityInserts.push(i);
        }
    }

}

// Draw Functions
export function drawNode(event) {
    let nodeId;
    if (priorityInserts.length > 0) {
        nodeId = priorityInserts.shift();
    } else {
        nodeId = cy.nodes().length+1;
    }
    cy.add({
        group: 'nodes',
        data: { id : nodeId },
        position: event.position
    })
    console.log("created node", cy.nodes().length);
    }


export function drawEdge(event) {
    // Connect selected node with tapped node. If no tapped node, then select -> tapped
    if (event.target != null && event.target != cy && event.target.isNode()) {
    if (selectedNode == null) {
        selectedNode = event.target;
        selectedNode.addClass('selectedNode');
        console.log("selected node", selectedNode.id());
    } else {
        // Standardizing edges so its min to max id
        let source = Math.min(selectedNode.id(),event.target.id());
        let target = Math.max(selectedNode.id(),event.target.id());
        console.log('source', source);
        console.log('target', target);

        // Edge ids are in the form source,sink
        let edgeId = source.toString() + "," + target.toString();
        if (cy.getElementById(edgeId).length > 0) {
            console.log("edge", edgeId, "exists");
        }
        else {
            console.log("creating edge", edgeId);
            cy.add({
                group: 'edges',
                data: {id : edgeId, source: source, target: target}
            });
        }
        clearSelectedNode();

    }
    }
}

export function deleteElement(event) {
    if (event.target != null && event.target != cy && (event.target.isNode() || event.target.isEdge())) {
            console.log("Removing ", event.target.data('id'));
            let removedID = event.target.data('id');
            cy.remove(event.target);
            console.log('removed node', removedID);
            if (event.target.isNode()) {
                Utils.insertInOrder(priorityInserts, removedID);
                console.log('current removed list: ', priorityInserts);
            }
}
}