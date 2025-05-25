import threading
import time
import random
from datetime import datetime
DISABLED_NODES = []  # Nodes to be deactivated e.g 5

class Node(threading.Thread):
    message_counter = 0
    message_counter_lock = threading.Lock()
    leader_declared = False
    leader_lock = threading.Lock()
    election_start_time = None
    extra_threads = []
    leader_elected_event = threading.Event()
    final_summary = ""
    
    def __init__(self, node_id, all_nodes):
        super().__init__()
        self.node_id = node_id
        self.all_nodes = all_nodes
        self.leader_id = None
        self.active = True
        self.logs = []
        self.received_coordinator = False

    def log(self, message):
        timestamp = datetime.fromtimestamp(time.time()).strftime('%H:%M:%S.%f')[:-3]
        full_message = f"[{timestamp}] [Node {self.node_id}] {message}"
        print(full_message)
        self.logs.append(full_message)

    def run(self):
        delay = random.uniform(0.5, 2.0)
        time.sleep(delay)
        if self.active:
            self.log("Starting up.")
            time.sleep(1)
            if self.node_id == min(n.node_id for n in self.all_nodes if n.active):
                self.log("Detected leader missing. Starting election.")
                with Node.leader_lock:
                    if Node.election_start_time is None:
                        Node.election_start_time = time.time()
                self.start_election()

    def start_election(self):
        if self.received_coordinator:
            return

        higher_nodes = [n for n in self.all_nodes if n.node_id > self.node_id and n.active]
        if not higher_nodes:
            self.declare_victory()
            return

        responses = []
        for node in higher_nodes:
            time.sleep(0.3)
            self.log(f"Sending ELECTION to Node {node.node_id}")
            with Node.message_counter_lock:
                Node.message_counter += 1
            responses.append(node.respond_to_election())

        if any(responses):
            self.log("Waiting for higher node to finish election.")
        else:
            self.declare_victory()

    def respond_to_election(self):
        if self.received_coordinator:
            return False
        self.log("Responding to ELECTION.")
        with Node.message_counter_lock:
            Node.message_counter += 1
        t = threading.Thread(target=self.start_election)
        t.start()
        Node.extra_threads.append(t)
        return True

    def receive_coordinator(self, leader_id):
        self.received_coordinator = True
        self.leader_id = leader_id
        self.log(f"Received COORDINATOR message. Leader is Node {leader_id}")

    def declare_victory(self):
        with Node.leader_lock:
            if not Node.leader_declared:
                Node.leader_declared = True
                self.leader_id = self.node_id
                if Node.election_start_time:
                    election_time = time.time() - Node.election_start_time
                else:
                    election_time = 0.0
                self.log(f"I am the new leader! (Election Time: {election_time:.3f}s)")

                # Send COORDINATOR to all other nodes
                for node in self.all_nodes:
                    if node.node_id != self.node_id and node.active:
                        self.log(f"Sending COORDINATOR to Node {node.node_id}")
                        with Node.message_counter_lock:
                            Node.message_counter += 1
                        node.receive_coordinator(self.node_id)

                Node.final_summary = f"[System] Total messages exchanged: {Node.message_counter}"
                Node.leader_elected_event.set()


def simulate():
    nodes = [Node(i, []) for i in range(1, 6)]
    for node in nodes:
        node.all_nodes = nodes

    # Disable nodes
    for i in DISABLED_NODES:
        nodes[i - 1].active = False
        print(f"[System] Node {i} is DISABLED.")

    print()

    for node in nodes:
        node.start()
    for node in nodes:
        node.join()

    for t in Node.extra_threads:
        t.join()

    Node.leader_elected_event.wait()
    time.sleep(0.05)
    print(f"\n{Node.final_summary}")

simulate()
