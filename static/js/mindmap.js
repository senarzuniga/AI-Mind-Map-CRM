/**
 * AI Mind Map – D3 v7 force-directed graph
 */

const STATUS_COLORS = {
  lead: "#94a3b8",
  prospect: "#f59e0b",
  customer: "#10b981",
  churned: "#ef4444",
};

const STAGE_COLORS = {
  discovery: "#64748b",
  proposal: "#6366f1",
  negotiation: "#f59e0b",
  closed_won: "#10b981",
  closed_lost: "#ef4444",
};

const TYPE_RADIUS = { hub: 26, contact: 18, deal: 15, tag: 12 };

(function initMindMap() {
  const container = document.getElementById("mindmap-container");
  const tooltip = document.getElementById("node-tooltip");
  const btnReset = document.getElementById("btn-reset");

  const width = container.clientWidth || 900;
  const height = container.clientHeight || 600;

  const svg = d3
    .select(container)
    .append("svg")
    .attr("width", "100%")
    .attr("height", "100%")
    .attr("viewBox", `0 0 ${width} ${height}`)
    .call(
      d3.zoom().scaleExtent([0.3, 3]).on("zoom", (event) => {
        g.attr("transform", event.transform);
      })
    );

  const g = svg.append("g");

  // Arrow marker
  svg
    .append("defs")
    .append("marker")
    .attr("id", "arrow")
    .attr("viewBox", "0 -5 10 10")
    .attr("refX", 22)
    .attr("refY", 0)
    .attr("markerWidth", 6)
    .attr("markerHeight", 6)
    .attr("orient", "auto")
    .append("path")
    .attr("fill", "#475569")
    .attr("d", "M0,-5L10,0L0,5");

  fetch("/api/mindmap-data")
    .then((r) => r.json())
    .then(({ nodes, links }) => {
      const simulation = d3
        .forceSimulation(nodes)
        .force("link", d3.forceLink(links).id((d) => d.id).distance((l) => (l.value === 2 ? 130 : 100)))
        .force("charge", d3.forceManyBody().strength(-320))
        .force("center", d3.forceCenter(width / 2, height / 2))
        .force("collision", d3.forceCollide().radius((d) => TYPE_RADIUS[d.type] + 12));

      // Links
      const link = g
        .append("g")
        .attr("class", "links")
        .selectAll("line")
        .data(links)
        .join("line")
        .attr("stroke", "#334155")
        .attr("stroke-width", (d) => (d.value === 2 ? 2 : 1))
        .attr("stroke-opacity", 0.6)
        .attr("marker-end", "url(#arrow)");

      // Node groups
      const node = g
        .append("g")
        .attr("class", "nodes")
        .selectAll("g")
        .data(nodes)
        .join("g")
        .attr("class", "node")
        .call(
          d3
            .drag()
            .on("start", (event, d) => {
              if (!event.active) simulation.alphaTarget(0.3).restart();
              d.fx = d.x;
              d.fy = d.y;
            })
            .on("drag", (event, d) => {
              d.fx = event.x;
              d.fy = event.y;
            })
            .on("end", (event, d) => {
              if (!event.active) simulation.alphaTarget(0);
              d.fx = null;
              d.fy = null;
            })
        );

      // Circles
      node
        .append("circle")
        .attr("r", (d) => TYPE_RADIUS[d.type])
        .attr("fill", (d) => nodeColor(d))
        .attr("stroke", "#0f172a")
        .attr("stroke-width", 2)
        .style("cursor", "pointer");

      // Labels
      node
        .append("text")
        .attr("dy", (d) => TYPE_RADIUS[d.type] + 13)
        .attr("text-anchor", "middle")
        .attr("font-size", "11px")
        .attr("fill", "#e2e8f0")
        .text((d) => truncate(d.label, 18));

      // Score ring for contacts
      node
        .filter((d) => d.type === "contact" && d.score != null)
        .append("circle")
        .attr("r", (d) => TYPE_RADIUS[d.type] + 4)
        .attr("fill", "none")
        .attr("stroke", (d) => scoreColor(d.score))
        .attr("stroke-width", 2.5)
        .attr("stroke-dasharray", (d) => {
          const circ = 2 * Math.PI * (TYPE_RADIUS[d.type] + 4);
          return `${(d.score / 100) * circ} ${circ}`;
        })
        .attr("stroke-linecap", "round")
        .attr("transform", "rotate(-90)");

      // Hub icon
      node
        .filter((d) => d.type === "hub")
        .append("text")
        .attr("text-anchor", "middle")
        .attr("dominant-baseline", "central")
        .attr("font-size", "16px")
        .text("🧠");

      // Tooltip
      node
        .on("mousemove", (event, d) => {
          tooltip.innerHTML = buildTooltip(d);
          tooltip.style.display = "block";
          tooltip.style.left = event.clientX + 14 + "px";
          tooltip.style.top = event.clientY - 10 + "px";
        })
        .on("mouseleave", () => {
          tooltip.style.display = "none";
        });

      simulation.on("tick", () => {
        link
          .attr("x1", (d) => d.source.x)
          .attr("y1", (d) => d.source.y)
          .attr("x2", (d) => d.target.x)
          .attr("y2", (d) => d.target.y);

        node.attr("transform", (d) => `translate(${d.x},${d.y})`);
      });

      btnReset.addEventListener("click", () => {
        svg
          .transition()
          .duration(600)
          .call(
            d3.zoom().transform,
            d3.zoomIdentity
              .translate(0, 0)
              .scale(1)
          );
        simulation.alpha(0.5).restart();
      });
    });

  function nodeColor(d) {
    if (d.type === "hub") return "#1e293b";
    if (d.type === "contact") return STATUS_COLORS[d.status] || "#6366f1";
    if (d.type === "deal") return STAGE_COLORS[d.stage] || "#6366f1";
    if (d.type === "tag") return d.color || "#10b981";
    return "#6366f1";
  }

  function scoreColor(score) {
    if (score >= 75) return "#10b981";
    if (score >= 45) return "#f59e0b";
    return "#ef4444";
  }

  function truncate(str, max) {
    return str.length > max ? str.slice(0, max - 1) + "…" : str;
  }

  function buildTooltip(d) {
    if (d.type === "hub") return "<strong>CRM Hub</strong>";
    if (d.type === "contact") {
      return `<strong>${d.label}</strong><br/>${d.sub || ""}<br/>
        <span style="color:#94a3b8">Status:</span> ${d.status}<br/>
        <span style="color:#94a3b8">AI Score:</span> ${d.score}`;
    }
    if (d.type === "deal") {
      return `<strong>${d.label}</strong><br/>${d.sub}<br/>
        <span style="color:#94a3b8">Stage:</span> ${d.stage.replace("_", " ")}`;
    }
    if (d.type === "tag") {
      return `<strong>${d.label}</strong>`;
    }
    return d.label;
  }
})();
