import math
import random
import json

class Node:
    def __init__(self, method=None, parent=None):
        self.method = method
        self.parent = parent
        self.children = []
        self.visits = 0
        self.value = 0

    def add_child(self, child_node):
        self.children.append(child_node)

    def update(self, result):
        self.visits += 1
        self.value += result

class MCTS:
    def __init__(self, methods, pros_cons):
        self.methods = methods
        self.pros_cons = pros_cons
        self.root = Node()
        for method in methods:
            self.root.add_child(Node(method=method, parent=self.root))
        self.history = []

    def select(self, node):
        while node.children:
            if any(child.visits == 0 for child in node.children):
                return self.expand(node)
            else:
                node = self.best_child(node)
        return node

    def expand(self, node):
        unvisited_children = [child for child in node.children if child.visits == 0]
        return random.choice(unvisited_children)

    def simulate(self, node):
        if not node.method:
            return 0
        return sum(weight for _, weight in self.pros_cons[node.method])

    def backpropagate(self, node, result):
        while node:
            node.update(result)
            node = node.parent

    def best_child(self, node, c_param=1.4):
        choices_weights = [
            (child.value / child.visits) + c_param * math.sqrt((2 * math.log(node.visits) / child.visits))
            if child.visits > 0 else float('inf')
            for child in node.children
        ]
        return node.children[choices_weights.index(max(choices_weights))]

    def search(self, num_simulations):
        for i in range(num_simulations):
            leaf = self.select(self.root)
            simulation_result = self.simulate(leaf)
            self.backpropagate(leaf, simulation_result)
            self.history.append(self.tree_to_dict(self.root))

        return self.best_child(self.root, c_param=0)

    def tree_to_dict(self, node):
        return {
            "name": node.method if node.method else "Root",
            "visits": node.visits,
            "value": round(node.value, 2),
            "children": [self.tree_to_dict(child) for child in node.children]
        }

def generate_html(tree_history, methods, pros_cons):
    html_content = """
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="utf-8">
        <title>MCTS Search Process Visualization</title>
        <script src="https://d3js.org/d3.v6.min.js"></script>
        <style>
            .node circle {
                fill: #fff;
                stroke: steelblue;
                stroke-width: 3px;
            }
            .node text { font: 12px sans-serif; }
            .link { fill: none; stroke: #ccc; stroke-width: 2px; }
            #controls { margin-bottom: 20px; }
            #iteration-info { margin-top: 20px; }
        </style>
    </head>
    <body>
        <div id="controls">
            <button id="prev">Previous</button>
            <button id="next">Next</button>
            <span id="iteration">Iteration: 0</span>
        </div>
        <div id="tree-container"></div>
        <div id="iteration-info"></div>
        <script>
        const treeHistory = %s;
        const methods = %s;
        const prosCons = %s;

        let currentIteration = 0;

        function updateTree(data) {
            d3.select("#tree-container").selectAll("*").remove();

            const width = 1200;
            const height = 600;
            const margin = {top: 20, right: 90, bottom: 30, left: 90};

            const svg = d3.select("#tree-container").append("svg")
                .attr("width", width + margin.left + margin.right)
                .attr("height", height + margin.top + margin.bottom)
                .append("g")
                .attr("transform", `translate(${margin.left},${margin.top})`);

            const tree = d3.tree().size([height, width - 200]);
            const root = d3.hierarchy(data);
            tree(root);

            const link = svg.selectAll(".link")
                .data(root.links())
                .enter().append("path")
                .attr("class", "link")
                .attr("d", d3.linkHorizontal()
                    .x(d => d.y)
                    .y(d => d.x));

            const node = svg.selectAll(".node")
                .data(root.descendants())
                .enter().append("g")
                .attr("class", "node")
                .attr("transform", d => `translate(${d.y},${d.x})`);

            node.append("circle")
                .attr("r", 10);

            node.append("text")
                .attr("dy", ".35em")
                .attr("x", d => d.children ? -13 : 13)
                .style("text-anchor", d => d.children ? "end" : "start")
                .text(d => `${d.data.name} (${d.data.visits}, ${d.data.value})`);

            updateIterationInfo();
        }

        function updateIterationInfo() {
            const infoDiv = document.getElementById("iteration-info");
            let infoHTML = "<h3>Method Scores:</h3><ul>";
            for (const method of methods) {
                const score = prosCons[method].reduce((sum, [_, weight]) => sum + weight, 0);
                infoHTML += `<li>${method}: ${score.toFixed(2)}</li>`;
            }
            infoHTML += "</ul>";
            infoDiv.innerHTML = infoHTML;
        }

        function updateIteration(delta) {
            currentIteration += delta;
            currentIteration = Math.max(0, Math.min(currentIteration, treeHistory.length - 1));
            document.getElementById("iteration").textContent = `Iteration: ${currentIteration}`;
            updateTree(treeHistory[currentIteration]);
        }

        document.getElementById("prev").addEventListener("click", () => updateIteration(-1));
        document.getElementById("next").addEventListener("click", () => updateIteration(1));

        updateTree(treeHistory[0]);
        </script>
    </body>
    </html>
    """ % (json.dumps(tree_history), json.dumps(methods), json.dumps(pros_cons))

    with open("./resources/mcts/mcts_search_process.html", "w") as f:
        f.write(html_content)

# Define methods and their pros/cons with weights
methods = ['LDA', 'NMF', 'LSA', 'HDP']
pros_cons = {
    'LDA': [('Interpretable results', 0.8), ('Works well with large datasets', 0.7),
            ('Can handle unseen documents', 0.6), ('Requires specifying number of topics', -0.5),
            ('Sensitive to parameter settings', -0.4)],
    'NMF': [('Produces coherent topics', 0.9), ('Fast for small/medium datasets', 0.6),
            ('Less effective on large datasets', -0.7), ('Sensitive to initialization', -0.5)],
    'LSA': [('Simple and fast', 0.8), ('Works well for synonymy', 0.7),
            ('Topics can be less interpretable', -0.6), ('Assumes normal word distribution', -0.5)],
    'HDP': [('Auto-determines number of topics', 1.0), ('Models hierarchical structure', 0.8),
            ('Computationally intensive', -0.9), ('Difficult to implement and tune', -0.7)]
}

# Run MCTS
mcts = MCTS(methods, pros_cons)
best_method = mcts.search(100).method  # Reduced to 100 iterations for visualization clarity

print(f"The best method according to MCTS is: {best_method}")

# Generate HTML visualization
generate_html(mcts.history, methods, pros_cons)

print("HTML visualization has been generated as 'mcts_search_process.html'")

# Calculate and print scores for all methods
for method in methods:
    score = sum(weight for _, weight in pros_cons[method])
    print(f"{method} score: {score}")