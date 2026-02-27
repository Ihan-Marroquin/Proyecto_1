import json
import argparse
from graphviz import Digraph
from collections import defaultdict

def gen_macro_graph(m, basename='diagram', formats=('svg', 'png')):
    g = Digraph(name=basename, format='svg')
    g.attr(rankdir='LR')
    g.node('start', shape='plaintext')
    steps = m.get('macro_steps', [])
    prev = 'start'
    for i, step in enumerate(steps):
        node_id = f"step_{i}"
        label = f"{i}: {step.get('op')}"
        # include args compactamente
        args = step.get('args', {})
        if args:
            # short repr
            argstr = ', '.join(f"{k}={v}" for k, v in args.items())
            label += f"\\n({argstr})"
        g.node(node_id, label=label, shape='box')
        g.edge(prev, node_id)
        prev = node_id
    g.node('halt', shape='doublecircle', label='halt')
    g.edge(prev, 'halt')
    # render for each format
    for fmt in formats:
        outpath = f"{basename}.{fmt}"
        # graphviz will write files when using render; use format override
        d = Digraph(name=basename, format=fmt)
        d.body = g.body[:]  # copy body
        try:
            d.render(filename=basename, cleanup=True)
            print(f"Generado: {outpath}")
        except Exception as e:
            # try pipe fallback
            try:
                data = g.pipe(format=fmt)
                with open(outpath, 'wb') as f:
                    f.write(data)
                print(f"Generado (pipe): {outpath}")
            except Exception as e2:
                print(f"ERROR generando {fmt}: {e} / fallback: {e2}")

def gen_lowlevel_graph(m, basename='diagram', formats=('svg', 'png'), detailed=False):
    g = Digraph(name=basename, format='svg')
    g.attr(rankdir='LR')
    # states
    transitions = m.get('transitions', [])
    states = set()
    accept_states = set(m.get('accept_states', []))
    # aggregate edges (state->new_state) with labels
    edge_labels = defaultdict(list)  # (s,t)->list(labels)
    for t in transitions:
        s = t.get('state')
        sym = t.get('symbol')
        ns = t.get('new_state')
        write = t.get('write')
        move = t.get('move')
        states.add(s); states.add(ns)
        lab = f"{sym}→{write},{move}"
        key = (s, ns)
        edge_labels[key].append(lab)
    # nodes
    for st in states:
        if st in accept_states:
            g.node(st, shape='doublecircle')
        else:
            g.node(st, shape='circle')
    # edges
    for (s, ns), labs in edge_labels.items():
        if detailed or len(labs) <= 3:
            label = '\\n'.join(labs)
        else:
            # collapse long label
            label = ', '.join(labs[:3]) + f", (+{len(labs)-3} más)"
        g.edge(s, ns, label=label)
    # start indicator
    start = m.get('start_state')
    if start:
        g.node('start', shape='plaintext')
        g.edge('start', start, label='start')
    # render
    for fmt in formats:
        outpath = f"{basename}.{fmt}"
        try:
            # render using a copy to override format
            d = Digraph(name=basename, format=fmt)
            d.body = g.body[:]
            d.render(filename=basename, cleanup=True)
            print(f"Generado: {outpath}")
        except Exception as e:
            try:
                data = g.pipe(format=fmt)
                with open(outpath, 'wb') as f:
                    f.write(data)
                print(f"Generado (pipe): {outpath}")
            except Exception as e2:
                print(f"ERROR generando {fmt}: {e} / fallback: {e2}")

def main():
    parser = argparse.ArgumentParser(description="Generador de diagramas para TM JSON")
    parser.add_argument("machine_file", help="Archivo JSON de la máquina (tipo macro o lowlevel)")
    parser.add_argument("--out", default="diagram", help="Nombre base de los archivos de salida (sin extensión)")
    parser.add_argument("--format", default="svg,png", help="Formatos a generar (csv), ej: svg,png")
    parser.add_argument("--detailed", action='store_true', help="Mostrar labels detalladas para lowlevel")
    args = parser.parse_args()

    with open(args.machine_file, 'r', encoding='utf-8') as f:
        m = json.load(f)

    formats = tuple(fmt.strip() for fmt in args.format.split(',') if fmt.strip())

    typ = m.get('type', 'macro')
    if typ == 'macro':
        gen_macro_graph(m, basename=args.out, formats=formats)
    elif typ == 'lowlevel':
        gen_lowlevel_graph(m, basename=args.out, formats=formats, detailed=args.detailed)
    else:
        print("Tipo de máquina desconocido en el JSON:", typ)

if __name__ == "__main__":
    main()