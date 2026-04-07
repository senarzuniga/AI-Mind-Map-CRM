import ReactFlow, {
  Node,
  Edge,
  Background,
  Controls,
  MiniMap,
  useNodesState,
  useEdgesState,
} from 'reactflow';
import 'reactflow/dist/style.css';
import type { MindMapData } from '@/types';
import { useEffect } from 'react';

function treeToFlow(
  node: MindMapData,
  x = 0,
  y = 0,
  parentId?: string,
): { nodes: Node[]; edges: Edge[] } {
  const nodes: Node[] = [];
  const edges: Edge[] = [];

  nodes.push({
    id: node.id,
    data: { label: node.label },
    position: { x, y },
    type: node.type === 'root' ? 'input' : 'default',
    style: {
      background: node.type === 'root' ? '#4f46e5' : '#fff',
      color: node.type === 'root' ? '#fff' : '#1f2937',
      border: '1px solid #e5e7eb',
      borderRadius: 8,
      padding: '8px 16px',
      fontSize: 13,
    },
  });

  if (parentId) {
    edges.push({
      id: `e-${parentId}-${node.id}`,
      source: parentId,
      target: node.id,
      style: { stroke: '#a5b4fc' },
    });
  }

  const children = node.children ?? [];
  const spread = 200;
  const startX = x - ((children.length - 1) * spread) / 2;

  children.forEach((child, i) => {
    const { nodes: cn, edges: ce } = treeToFlow(
      child,
      startX + i * spread,
      y + 120,
      node.id,
    );
    nodes.push(...cn);
    edges.push(...ce);
  });

  return { nodes, edges };
}

interface Props {
  data: MindMapData;
}

export default function MindMapViewer({ data }: Props) {
  const { nodes: initialNodes, edges: initialEdges } = treeToFlow(data);
  const [nodes, setNodes, onNodesChange] = useNodesState(initialNodes);
  const [edges, setEdges, onEdgesChange] = useEdgesState(initialEdges);

  useEffect(() => {
    const { nodes: n, edges: e } = treeToFlow(data);
    setNodes(n);
    setEdges(e);
  }, [data, setNodes, setEdges]);

  return (
    <div style={{ height: '100%', width: '100%' }}>
      <ReactFlow
        nodes={nodes}
        edges={edges}
        onNodesChange={onNodesChange}
        onEdgesChange={onEdgesChange}
        fitView
      >
        <Background color="#e0e7ff" gap={20} />
        <Controls />
        <MiniMap />
      </ReactFlow>
    </div>
  );
}
