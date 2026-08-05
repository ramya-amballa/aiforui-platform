"use client";

import { useEffect, useMemo, useRef, useState } from "react";
import { forceSimulation, forceLink, forceManyBody, forceCenter, forceCollide, type SimulationNodeDatum } from "d3-force";
import { useRouter } from "next/navigation";
import { graph } from "@/lib/data";
import { ENTITY_LABEL, ENTITY_TYPES, CONFIDENCE_ORDER, ENTITY_ROUTE, type EntityType, type Confidence } from "@/lib/types";
import { ENTITY_COLOR } from "@/lib/entity-colors";

interface SimNode extends SimulationNodeDatum {
  id: string;
  entity_type: EntityType;
  title: string;
  confidence: Confidence;
  degree: number;
  frameworks: string[];
}

interface SimLink {
  source: string | SimNode;
  target: string | SimNode;
  type: string;
}

const BASE_RADIUS = 4;

function useGraphLayout() {
  return useMemo(() => {
    const nodes: SimNode[] = graph.nodes.map((n) => ({
      id: n.id,
      entity_type: n.entity_type,
      title: n.title,
      confidence: n.confidence,
      degree: n.relationships_out.length + n.relationships_in.length,
      frameworks: n.related_frameworks,
    }));
    const links: SimLink[] = graph.nodes.flatMap((n) => n.relationships_out.map((r) => ({ source: n.id, target: r.other_id, type: r.type })));

    const sim = forceSimulation(nodes)
      .force(
        "link",
        forceLink<SimNode, SimLink>(links)
          .id((d) => d.id)
          .distance(60)
          .strength(0.25),
      )
      .force("charge", forceManyBody().strength(-90))
      .force("center", forceCenter(0, 0))
      .force(
        "collide",
        forceCollide<SimNode>().radius((d) => BASE_RADIUS + Math.min(d.degree, 10) * 1.1 + 3),
      )
      .stop();

    for (let i = 0; i < 300; i++) sim.tick();

    return { nodes, links };
  }, []);
}

export function GraphView() {
  const router = useRouter();
  const canvasRef = useRef<HTMLCanvasElement>(null);
  const containerRef = useRef<HTMLDivElement>(null);
  const { nodes, links } = useGraphLayout();

  const [size, setSize] = useState({ w: 800, h: 600 });
  const [transform, setTransform] = useState({ x: 0, y: 0, k: 1 });
  const [hoverId, setHoverId] = useState<string | null>(null);
  const [typeFilter, setTypeFilter] = useState<Set<EntityType>>(new Set(ENTITY_TYPES));
  const [confidenceFilter, setConfidenceFilter] = useState<Set<Confidence>>(new Set(CONFIDENCE_ORDER));
  const [frameworkFilter, setFrameworkFilter] = useState<string>("");

  const dragState = useRef<{ dragging: boolean; lastX: number; lastY: number }>({ dragging: false, lastX: 0, lastY: 0 });
  const hasAutoFit = useRef(false);

  useEffect(() => {
    function onResize() {
      if (!containerRef.current) return;
      const rect = containerRef.current.getBoundingClientRect();
      setSize({ w: rect.width, h: Math.max(480, window.innerHeight - 320) });
    }
    onResize();
    window.addEventListener("resize", onResize);
    return () => window.removeEventListener("resize", onResize);
  }, []);

  const nodeById = useMemo(() => new Map(nodes.map((n) => [n.id, n])), [nodes]);

  useEffect(() => {
    if (hasAutoFit.current || size.w === 0) return;
    const xs = nodes.map((n) => n.x ?? 0);
    const ys = nodes.map((n) => n.y ?? 0);
    const minX = Math.min(...xs);
    const maxX = Math.max(...xs);
    const minY = Math.min(...ys);
    const maxY = Math.max(...ys);
    const graphW = Math.max(maxX - minX, 1);
    const graphH = Math.max(maxY - minY, 1);
    const k = Math.min(3, Math.max(0.15, Math.min(size.w / (graphW + 80), size.h / (graphH + 80))));
    const cx = (minX + maxX) / 2;
    const cy = (minY + maxY) / 2;
    setTransform({ x: -cx * k, y: -cy * k, k });
    hasAutoFit.current = true;
  }, [nodes, size]);

  const adjacency = useMemo(() => {
    const map = new Map<string, Set<string>>();
    for (const l of links) {
      const s = typeof l.source === "string" ? l.source : l.source.id;
      const t = typeof l.target === "string" ? l.target : l.target.id;
      if (!map.has(s)) map.set(s, new Set());
      if (!map.has(t)) map.set(t, new Set());
      map.get(s)!.add(t);
      map.get(t)!.add(s);
    }
    return map;
  }, [links]);

  const visibleIds = useMemo(() => {
    let baseIds: Set<string>;
    if (frameworkFilter) {
      const controlIds = new Set(graph.frameworks.find((f) => f.slug === frameworkFilter)?.control_ids ?? []);
      const withNeighbors = new Set<string>(controlIds);
      for (const id of controlIds) for (const nb of adjacency.get(id) ?? []) withNeighbors.add(nb);
      baseIds = withNeighbors;
    } else {
      baseIds = new Set(nodes.map((n) => n.id));
    }
    const result = new Set<string>();
    for (const id of baseIds) {
      const n = nodeById.get(id);
      if (!n) continue;
      if (!typeFilter.has(n.entity_type)) continue;
      if (!confidenceFilter.has(n.confidence)) continue;
      result.add(id);
    }
    return result;
  }, [nodes, nodeById, adjacency, typeFilter, confidenceFilter, frameworkFilter]);

  const neighborIds = useMemo(() => {
    if (!hoverId) return null;
    const set = new Set<string>([hoverId]);
    for (const nb of adjacency.get(hoverId) ?? []) set.add(nb);
    return set;
  }, [hoverId, adjacency]);

  // Draw
  useEffect(() => {
    const canvas = canvasRef.current;
    if (!canvas) return;
    const dpr = window.devicePixelRatio || 1;
    canvas.width = size.w * dpr;
    canvas.height = size.h * dpr;
    canvas.style.width = `${size.w}px`;
    canvas.style.height = `${size.h}px`;
    const ctx = canvas.getContext("2d");
    if (!ctx) return;
    ctx.setTransform(dpr, 0, 0, dpr, 0, 0);
    ctx.clearRect(0, 0, size.w, size.h);
    ctx.save();
    ctx.translate(size.w / 2 + transform.x, size.h / 2 + transform.y);
    ctx.scale(transform.k, transform.k);

    // edges
    for (const l of links) {
      const s = typeof l.source === "string" ? nodeById.get(l.source) : (l.source as SimNode);
      const t = typeof l.target === "string" ? nodeById.get(l.target) : (l.target as SimNode);
      if (!s || !t || s.x == null || t.x == null) continue;
      if (!visibleIds.has(s.id) || !visibleIds.has(t.id)) continue;
      const dimmed = neighborIds ? !(neighborIds.has(s.id) && neighborIds.has(t.id)) : false;
      ctx.beginPath();
      ctx.moveTo(s.x, s.y!);
      ctx.lineTo(t.x, t.y!);
      ctx.strokeStyle = dimmed ? "rgba(180,186,196,0.15)" : "rgba(140,148,163,0.55)";
      ctx.lineWidth = dimmed ? 0.5 : 0.8;
      ctx.stroke();
    }

    // nodes
    for (const n of nodes) {
      if (n.x == null || !visibleIds.has(n.id)) continue;
      const dimmed = neighborIds ? !neighborIds.has(n.id) : false;
      const r = BASE_RADIUS + Math.min(n.degree, 10) * 1.1;
      ctx.beginPath();
      ctx.arc(n.x, n.y!, r, 0, Math.PI * 2);
      ctx.fillStyle = dimmed ? "rgba(180,186,196,0.35)" : ENTITY_COLOR[n.entity_type].hex;
      ctx.globalAlpha = dimmed ? 0.5 : 1;
      ctx.fill();
      if (hoverId === n.id) {
        ctx.lineWidth = 2;
        ctx.strokeStyle = "#171c27";
        ctx.stroke();
      }
      ctx.globalAlpha = 1;
    }
    ctx.restore();
  }, [nodes, links, size, transform, hoverId, neighborIds, visibleIds, nodeById]);

  function toScreen(clientX: number, clientY: number) {
    const rect = canvasRef.current!.getBoundingClientRect();
    const x = clientX - rect.left;
    const y = clientY - rect.top;
    const gx = (x - size.w / 2 - transform.x) / transform.k;
    const gy = (y - size.h / 2 - transform.y) / transform.k;
    return { gx, gy };
  }

  function hitTest(clientX: number, clientY: number): SimNode | null {
    const { gx, gy } = toScreen(clientX, clientY);
    let closest: SimNode | null = null;
    let closestDist = Infinity;
    for (const n of nodes) {
      if (n.x == null || !visibleIds.has(n.id)) continue;
      const r = BASE_RADIUS + Math.min(n.degree, 10) * 1.1 + 3;
      const d = Math.hypot(n.x - gx, n.y! - gy);
      if (d < r && d < closestDist) {
        closest = n;
        closestDist = d;
      }
    }
    return closest;
  }

  function onWheel(e: React.WheelEvent) {
    e.preventDefault();
    const factor = e.deltaY > 0 ? 0.9 : 1.1;
    setTransform((t) => ({ ...t, k: Math.min(4, Math.max(0.2, t.k * factor)) }));
  }

  function onMouseDown(e: React.MouseEvent) {
    dragState.current = { dragging: true, lastX: e.clientX, lastY: e.clientY };
  }
  function onMouseMove(e: React.MouseEvent) {
    if (dragState.current.dragging) {
      const dx = e.clientX - dragState.current.lastX;
      const dy = e.clientY - dragState.current.lastY;
      dragState.current.lastX = e.clientX;
      dragState.current.lastY = e.clientY;
      setTransform((t) => ({ ...t, x: t.x + dx, y: t.y + dy }));
    } else {
      const hit = hitTest(e.clientX, e.clientY);
      setHoverId(hit?.id ?? null);
    }
  }
  function onMouseUp() {
    dragState.current.dragging = false;
  }
  function onClick(e: React.MouseEvent) {
    const hit = hitTest(e.clientX, e.clientY);
    if (hit) {
      const full = graph.nodes.find((n) => n.id === hit.id);
      if (full) router.push(`/${ENTITY_ROUTE[hit.entity_type]}/${full.slug}/`);
    }
  }

  function toggleType(t: EntityType) {
    setTypeFilter((s) => {
      const next = new Set(s);
      if (next.has(t)) next.delete(t);
      else next.add(t);
      return next;
    });
  }
  function toggleConfidence(c: Confidence) {
    setConfidenceFilter((s) => {
      const next = new Set(s);
      if (next.has(c)) next.delete(c);
      else next.add(c);
      return next;
    });
  }

  const hoveredNode = hoverId ? nodeById.get(hoverId) : null;

  return (
    <div>
      <div className="mb-4 flex flex-wrap items-center gap-4 rounded-md border border-ink-200 bg-ink-50 p-3">
        <div className="flex flex-wrap items-center gap-1.5">
          <span className="field-label mr-1">Type</span>
          {ENTITY_TYPES.map((t) => (
            <button
              key={t}
              onClick={() => toggleType(t)}
              className={`rounded border px-2 py-1 text-xs font-medium ${
                typeFilter.has(t) ? `${ENTITY_COLOR[t].bg} ${ENTITY_COLOR[t].text} ${ENTITY_COLOR[t].border}` : "border-ink-200 text-ink-300"
              }`}
            >
              {ENTITY_LABEL[t]}
            </button>
          ))}
        </div>
        <div className="flex flex-wrap items-center gap-1.5">
          <span className="field-label mr-1">Confidence</span>
          {CONFIDENCE_ORDER.map((c) => (
            <button
              key={c}
              onClick={() => toggleConfidence(c)}
              className={`rounded border px-2 py-1 text-xs font-medium ${
                confidenceFilter.has(c) ? "border-ink-300 text-ink-700 bg-white" : "border-ink-200 text-ink-300"
              }`}
            >
              {c}
            </button>
          ))}
        </div>
        <label className="flex items-center gap-1.5 text-xs">
          <span className="field-label">Framework</span>
          <select
            value={frameworkFilter}
            onChange={(e) => setFrameworkFilter(e.target.value)}
            className="rounded border border-ink-200 bg-white px-2 py-1 text-xs text-ink-700"
          >
            <option value="">All</option>
            {graph.frameworks
              .filter((f) => f.control_ids.length > 0)
              .map((f) => (
                <option key={f.slug} value={f.slug}>
                  {f.label}
                </option>
              ))}
          </select>
        </label>
        <button
          onClick={() => setTransform({ x: 0, y: 0, k: 1 })}
          className="btn ml-auto"
        >
          Reset view
        </button>
      </div>

      <div ref={containerRef} className="relative overflow-hidden rounded-md border border-ink-200 bg-white">
        <canvas
          ref={canvasRef}
          onWheel={onWheel}
          onMouseDown={onMouseDown}
          onMouseMove={onMouseMove}
          onMouseUp={onMouseUp}
          onMouseLeave={onMouseUp}
          onClick={onClick}
          className="cursor-grab active:cursor-grabbing"
        />
        {hoveredNode && (
          <div className="pointer-events-none absolute left-3 top-3 max-w-xs rounded border border-ink-200 bg-white px-3 py-2 text-xs shadow-sm">
            <div className="id-tag">{hoveredNode.id}</div>
            <div className="mt-0.5 font-medium text-ink-900">{hoveredNode.title}</div>
            <div className="mt-0.5 text-ink-400">{hoveredNode.degree} connection{hoveredNode.degree === 1 ? "" : "s"} · click to open</div>
          </div>
        )}
        <div className="pointer-events-none absolute bottom-3 right-3 text-[11px] text-ink-300">scroll to zoom · drag to pan</div>
      </div>
    </div>
  );
}
