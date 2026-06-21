from flask import Flask, render_template, request, redirect, url_for
from data_structures import DataStructuresManager, bst_levels
import copy

app = Flask(__name__)
# register template filter for BST rendering
app.jinja_env.filters['render_bst'] = bst_levels

# Single global manager for the demo
mgr = DataStructuresManager()

# snapshots: list of serializable snapshots (stack, queue, bst_serialized)
snapshots = [mgr._snapshot()]
# logs per snapshot: list of op_log copies corresponding to snapshots
logs_per_snapshot = [copy.deepcopy(mgr.get_log())]
# current index in snapshots
snap_index = 0


def current_snapshot():
    return snapshots[snap_index]


@app.route("/", methods=["GET"]) 
def index():
    state = {
        "stack": current_snapshot()["stack"],
        "queue": current_snapshot()["queue"],
        "bst_serialized": current_snapshot()["bst"],
    }
    log = logs_per_snapshot[snap_index]
    return render_template("index.html", state=state, log=log, snap_index=snap_index, max_index=len(snapshots)-1)


@app.route("/operate", methods=["POST"]) 
def operate():
    global snap_index
    form = request.form
    ds = form.get("ds")
    op = form.get("op")
    value = form.get("value")
    # convert value to int/float if possible
    val_parsed = None
    if value is not None and value != "":
        try:
            val_parsed = int(value)
        except ValueError:
            try:
                val_parsed = float(value)
            except ValueError:
                val_parsed = value

    # perform operation on manager
    if ds == "stack":
        if op == "push" and val_parsed is not None:
            mgr.push(val_parsed)
        elif op == "pop":
            mgr.pop()
    elif ds == "queue":
        if op == "enqueue" and val_parsed is not None:
            mgr.enqueue(val_parsed)
        elif op == "dequeue":
            mgr.dequeue()
    elif ds == "bst":
        if op == "insert" and val_parsed is not None:
            mgr.bst_insert(val_parsed)
        elif op == "delete" and val_parsed is not None:
            mgr.bst_delete(val_parsed)
        elif op == "search" and val_parsed is not None:
            # search doesn't change state but we log it
            found = mgr.bst_search(val_parsed)

    # when a new operation is made from current index not at end, truncate forward history
    if snap_index < len(snapshots) - 1:
        del snapshots[snap_index+1:]
        del logs_per_snapshot[snap_index+1:]

    # append new snapshot and log
    snapshots.append(mgr._snapshot())
    logs_per_snapshot.append(copy.deepcopy(mgr.get_log()))
    snap_index = len(snapshots) - 1

    return redirect(url_for("index"))


@app.route("/navigate", methods=["POST"]) 
def navigate():
    global snap_index
    action = request.form.get("action")
    if action == "prev" and snap_index > 0:
        snap_index -= 1
        mgr._restore(snapshots[snap_index])
        mgr.op_log = copy.deepcopy(logs_per_snapshot[snap_index])
    elif action == "next" and snap_index < len(snapshots) - 1:
        snap_index += 1
        mgr._restore(snapshots[snap_index])
        mgr.op_log = copy.deepcopy(logs_per_snapshot[snap_index])
    elif action == "reset":
        snap_index = 0
        mgr._restore(snapshots[0])
        mgr.op_log = copy.deepcopy(logs_per_snapshot[0])
    return redirect(url_for("index"))


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
