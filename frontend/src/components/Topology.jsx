import React, { useEffect, useState } from "react";
import {
  ReactFlow,
  Background,
  Controls,
  MiniMap,
  Handle,
  Position,
  MarkerType,
} from "@xyflow/react";

import "@xyflow/react/dist/style.css";

const API_BASE =
  import.meta.env.VITE_API_BASE_URL || "http://127.0.0.1:8000";

function KafkaNode() {
  return (
    <div className="flow-node kafka-node">
      <Handle
        type="source"
        position={Position.Bottom}
      />

      <div className="flow-node-icon">K</div>

      <div>
        <strong>Apache Kafka</strong>
        <span>Event Source</span>
      </div>

      <div className="node-status">
        <span />
        Connected
      </div>
    </div>
  );
}

function WorkerNode({ data }) {
  return (
    <div className="flow-node worker-flow-node">
      <Handle
        type="target"
        position={Position.Top}
      />

      <Handle
        type="source"
        position={Position.Bottom}
      />

      <div className="worker-flow-icon">
        <span>W</span>
      </div>

      <div className="worker-flow-content">
        <strong>{data.label}</strong>
        <span>Partition {data.partition}</span>
      </div>

      <div className="worker-flow-status">
        <span />
        {data.status || "Running"}
      </div>
    </div>
  );
}

function AggregatorNode() {
  return (
    <div className="flow-node aggregator-node">
      <Handle
        type="target"
        position={Position.Top}
      />

      <Handle
        type="source"
        position={Position.Bottom}
      />

      <div className="flow-node-icon aggregator">
        5M
      </div>

      <div>
        <strong>5-Min Aggregator</strong>
        <span>Tumbling Window</span>
      </div>
    </div>
  );
}

function RocksNode() {
  return (
    <div className="flow-node rocks-node">
      <Handle
        type="target"
        position={Position.Top}
      />

      <div className="flow-node-icon rocks">
        DB
      </div>

      <div>
        <strong>RocksDB</strong>
        <span>State Storage</span>
      </div>
    </div>
  );
}

const nodeTypes = {
  kafka: KafkaNode,
  worker: WorkerNode,
  aggregator: AggregatorNode,
  rocksdb: RocksNode,
};

export default function Topology() {
  const [nodes, setNodes] = useState([]);
  const [edges, setEdges] = useState([]);

  useEffect(() => {
    loadTopology();

    const interval = setInterval(loadTopology, 5000);

    return () => clearInterval(interval);
  }, []);

  const loadTopology = async () => {
    try {
      const response = await fetch(
        `${API_BASE}/api/topology`
      );

      if (!response.ok) {
        throw new Error("Topology API failed");
      }

      const data = await response.json();

      const kafka = {
        id: "kafka",
        type: "kafka",
        position: {
          x: 380,
          y: 20,
        },
      };

      const workerNodes = data.nodes
        .filter((node) => node.type === "worker")
        .map((node, index) => ({
          id: node.id,
          type: "worker",
          position: {
            x: 70 + (index % 5) * 190,
            y: 180 + Math.floor(index / 5) * 115,
          },
          data: {
            label: node.label,
            partition: node.partition,
            status: node.status,
          },
        }));

      const aggregator = {
        id: "aggregator",
        type: "aggregator",
        position: {
          x: 380,
          y: 560,
        },
      };

      const rocksdb = {
        id: "rocksdb",
        type: "rocksdb",
        position: {
          x: 380,
          y: 700,
        },
      };

      setNodes([
        kafka,
        ...workerNodes,
        aggregator,
        rocksdb,
      ]);

      setEdges(
        data.edges.map((edge, index) => ({
          id: `edge-${index}`,
          source: edge.source,
          target: edge.target,
          animated: true,
          style: {
            stroke: "#64748b",
            strokeWidth: 2,
          },
          markerEnd: {
            type: MarkerType.ArrowClosed,
            color: "#64748b",
          },
        }))
      );
    } catch (error) {
      console.error("Topology error:", error);
    }
  };

  return (
    <div className="topology-wrapper">
      <ReactFlow
        nodes={nodes}
        edges={edges}
        nodeTypes={nodeTypes}
        fitView
        minZoom={0.25}
        maxZoom={1.5}
        nodesDraggable
        nodesConnectable={false}
        proOptions={{
          hideAttribution: true,
        }}
      >
        <Background
          gap={22}
          size={1}
          color="#263246"
        />

        <Controls />

        <MiniMap
          nodeColor={(node) => {
            if (node.type === "kafka") return "#8b5cf6";
            if (node.type === "worker") return "#3b82f6";
            if (node.type === "aggregator")
              return "#f59e0b";
            if (node.type === "rocksdb")
              return "#10b981";

            return "#64748b";
          }}
        />
      </ReactFlow>
    </div>
  );
}