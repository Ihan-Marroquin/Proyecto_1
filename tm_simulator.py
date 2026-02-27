import json
import time
import math
from collections import defaultdict

BLANK = '_'
LEFT = 'L'
RIGHT = 'R'
STAY = 'S'

class Tape:
    def __init__(self, content="", blank=BLANK):
        self.blank = blank
        self.cells = defaultdict(lambda: self.blank)
        for i, ch in enumerate(content):
            self.cells[i] = ch
        self.min_index = 0
        self.max_index = max(len(content)-1, 0)

    def read(self, pos):
        return self.cells.get(pos, self.blank)

    def write(self, pos, symbol):
        self.cells[pos] = symbol
        self.min_index = min(self.min_index, pos)
        self.max_index = max(self.max_index, pos)

    def as_str_window(self, head, radius=30):
        lo = head - radius
        hi = head + radius
        s = []
        for i in range(lo, hi+1):
            s.append(self.read(i))
        return ''.join(s), lo

    def to_compact_str(self):
        if self.min_index > self.max_index:
            return ""
        return ''.join(self.read(i) for i in range(self.min_index, self.max_index+1))

    def find_sequence(self, seq):
        s = self.to_compact_str()
        idx = s.find(seq)
        if idx < 0:
            return None
        return self.min_index + idx

    def get_field_between(self, left_sep_idx, right_sep_idx):
        return ''.join(self.read(i) for i in range(left_sep_idx+1, right_sep_idx))

class Simulator:
    def __init__(self, machine, verbose=False):
        self.machine = machine
        self.verbose = verbose
        self.step_count = 0

    def print_config(self, state, head, tape):
        s, lo = tape.as_str_window(head, radius=25)
        head_pos_in_window = 25
        marker = ' ' * head_pos_in_window + '^'
        print(f"STATE={state} HEAD={head} STEPS={self.step_count}")
        print(s)
        print(marker)

    def run_lowlevel(self, transitions, start_state, accept_states, tape, head=0, max_steps=10_000_000):
        state = start_state
        start_time = time.perf_counter()
        while True:
            if self.verbose:
                self.print_config(state, head, tape)
            if state in accept_states:
                elapsed = time.perf_counter() - start_time
                return {"status": "accept", "state": state, "steps": self.step_count, "time": elapsed, "tape": tape}
            symbol = tape.read(head)
            key = f"{state}|{symbol}"
            if key not in transitions:
                elapsed = time.perf_counter() - start_time
                return {"status": "halt_no_transition", "state": state, "steps": self.step_count, "time": elapsed, "tape": tape}
            new_state, write_symbol, move = transitions[key]
            tape.write(head, write_symbol); self.step_count += 1
            if move == LEFT:
                head -= 1
            elif move == RIGHT:
                head += 1
            self.step_count += 1
            state = new_state
            if self.step_count > max_steps:
                elapsed = time.perf_counter() - start_time
                return {"status": "max_steps_exceeded", "state": state, "steps": self.step_count, "time": elapsed, "tape": tape}

    def run_macro(self, macro_def, tape, head=0, max_steps=100_000_000):
        """
        macro_def: diccionario con "macro_steps": lista de {"op":..., "args":...}
        Se implementan ops: normalize_input_to_fields, init_A_B, consume_input_and_iterate, finish_and_cleanup
        """
        state = "macro_start"
        start_time = time.perf_counter()
        self.step_count = 0
        sep = '#'
        blank = BLANK

        def ensure_field_layout():
            s = tape.to_compact_str()
            if s.count(sep) >= 2:
                return
            content = s
            tape.cells = defaultdict(lambda: blank)
            for i, ch in enumerate((sep + content + sep)):
                tape.write(i, ch)

        def init_A_B(A="", B="1"):
            s = tape.to_compact_str()
            input_seq = ""
            for ch in s:
                if ch == '1':
                    input_seq += ch
            seq = sep + A + sep + B + sep + input_seq + sep
            tape.cells = defaultdict(lambda: blank)
            for i, ch in enumerate(seq):
                tape.write(i, ch)

        def consume_input_and_iterate():
            s = tape.to_compact_str()
            parts = s.split(sep)
            if len(parts) < 4:
                raise RuntimeError("Formato de cinta inesperado para consume_input_and_iterate: " + s)
            A = parts[1]
            B = parts[2]
            input_seq = parts[3]
            n = len(input_seq)
            for iter_index in range(n):
                C = A + B
                A = B
                B = C
                self.step_count += max(1, len(C))  
            seq = sep + A + sep + B + sep
            tape.cells = defaultdict(lambda: blank)
            for i, ch in enumerate(seq):
                tape.write(i, ch)

        def finish_and_cleanup():
            s = tape.to_compact_str()
            parts = s.split(sep)
            if len(parts) < 3:
                return
            tape.cells = defaultdict(lambda: blank)
            seq = sep + parts[1] + sep + parts[2] + sep
            for i, ch in enumerate(seq):
                tape.write(i, ch)
            headpos = 1 + len(parts[1]) + 1
            return headpos

        headpos = 0
        for step in macro_def.get("macro_steps", []):
            op = step.get("op")
            args = step.get("args", {})
            if op == "normalize_input_to_fields":
                ensure_field_layout()
            elif op == "init_A_B":
                init_A_B(A=args.get("A", ""), B=args.get("B", "1"))
            elif op == "consume_input_and_iterate":
                consume_input_and_iterate()
            elif op == "finish_and_cleanup":
                hp = finish_and_cleanup()
                if hp is not None:
                    headpos = hp
            else:
                raise ValueError("Op macro desconocida: " + str(op))

        elapsed = time.perf_counter() - start_time
        return {"status": "halt_macro", "state": "macro_done", "steps": self.step_count, "time": elapsed, "tape": tape, "head": headpos}

    def simulate_from_file(self, path, input_string, verbose=False):
        with open(path, 'r', encoding='utf-8') as f:
            m = json.load(f)
        if m.get("type") == "lowlevel":
            transitions = {}
            for t in m.get("transitions", []):
                key = f"{t['state']}|{t['symbol']}"
                transitions[key] = (t['new_state'], t['write'], t['move'])
            tape = Tape(input_string)
            res = self.run_lowlevel(transitions, m.get("start_state"), set(m.get("accept_states", [])), tape, head=0)
            return res
        elif m.get("type") == "macro":
            tape = Tape(input_string)
            res = self.run_macro(m, tape, head=0)
            return res
        else:
            raise ValueError("Tipo de máquina desconocido en el archivo: " + str(m.get("type")))

def run_experiments(machine_file, inputs, out_csv="results.csv", verbose=False):
    import csv, os
    sim = Simulator(None, verbose=verbose)
    header = ["n", "time_seconds", "steps", "result_length"]
    rows = []
    for n in inputs:
        inp = "1" * n
        res = sim.simulate_from_file(machine_file, inp, verbose=False)
        t = res["time"]
        steps = res.get("steps", 0)
        tape = res.get("tape")
        s = tape.to_compact_str()
        parts = s.split('#')
        result_len = 0
        if len(parts) >= 3:
            result_len = len(parts[2])
        rows.append([n, t, steps, result_len])
        print(f"n={n} time={t:.6f}s steps={steps} result_len={result_len}")
    with open(out_csv, 'w', newline='', encoding='utf-8') as f:
        w = csv.writer(f)
        w.writerow(header)
        w.writerows(rows)
    return out_csv

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="Simulador TM (lowlevel o macro).")
    parser.add_argument("machine_file", help="Ruta al archivo JSON de la máquina")
    parser.add_argument("--input", "-i", default="", help="Entrada en unary (ej: 1111 para n=4)")
    parser.add_argument("--run-experiments", action="store_true", help="Ejecutar experimentos de ejemplo (n=1..10)")
    parser.add_argument("--verbose", action="store_true", help="Mostrar configuraciones")
    args = parser.parse_args()

    if args.run_experiments:
        run_experiments(args.machine_file, list(range(1, 11)), out_csv="results.csv", verbose=args.verbose)
    else:
        sim = Simulator(None, verbose=args.verbose)
        result = sim.simulate_from_file(args.machine_file, args.input, verbose=args.verbose)
        tape = result.get("tape")
        head = result.get("head", 0)
        print("RESULT STATUS:", result["status"])
        print("STEPS:", result.get("steps"))
        print("TIME(s):", result.get("time"))
        print("TAPE (compact):", tape.to_compact_str())
        print("HEAD POSITION:", head)