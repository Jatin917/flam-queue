import argparse
import json
from queuectl.models import Job
from queuectl.worker import WorkerManager
from queuectl.scheduler import SchedulerQueue
from queuectl.dlq import DLQ

def build_cli(storage, config):

    def cli_entry():

        parser = argparse.ArgumentParser(
            prog="queuectl",
            description="QueueCTL - Simple Redis based job queue manager"
        )

        sub = parser.add_subparsers(dest="cmd", required=True)

        # ========== ENQUEUE ==========
        enq = sub.add_parser("enqueue", help="Add a job to the queue")
        enq.add_argument("--command", "-c", required=True, help="The command to execute")
        enq.add_argument("--max-retries", type=int, default=3, help="Maximum retry attempts")


        # ========== WORKER ==========
        wk = sub.add_parser("worker", help="Start or stop workers")
        wk.add_argument("action", choices=["start", "stop", "list"], help="Action to perform")
        wk.add_argument("--count", type=int, default=1, help="Number of worker processes (for start)")
        wk.add_argument("--pid", type=int, help="Stop a specific worker by PID")
        wk.add_argument("--all", action="store_true", help="Stop all workers")

        # ========== STATUS ==========
        st = sub.add_parser("status", help="Show queue summary")

        # ========== LIST ==========
        lst = sub.add_parser("list", help="List jobs in queue")
        lst.add_argument("--state", help="Filter jobs by state (pending, processing, dead, delayed)")

        # ========== DLQ ==========
        dlq = sub.add_parser("dlq", help="Dead Letter Queue operations")
        dlq.add_argument("action", choices=["list", "retry"], help="List DLQ or retry a job")
        dlq.add_argument("job_id", nargs="?", help="Job ID required when retrying a job")

        # ========== CONFIG ==========
        cfg = sub.add_parser("config", help="Update config file")
        cfg.add_argument("set", nargs=2, help="Set config key and value")

        args = parser.parse_args()

        # =============================================================
        # COMMAND HANDLER
        # =============================================================
        try:
            if args.cmd == "enqueue":
            # STEP 1 — JSON Validation
                try:
                    job = {
                    "command": args.command,
                    "max_retries": args.max_retries
                    }
                    # Enqueue it
                except json.JSONDecodeError:
                    print("[ERROR] Invalid JSON. Use: '{\"command\": \"echo hi\"}'")
                    return

                # STEP 2 — Must be a dict
                if not isinstance(job, dict):
                    print("[ERROR] Job must be a JSON object like: {\"command\": \"echo hi\"}")
                    return

                # STEP 3 — Must contain 'command'
                if "command" not in job:
                    print("[ERROR] Missing required field: 'command'")
                    print("   Example: python main.py enqueue '{\"command\": \"echo hi\"}'")
                    return

                # STEP 4 — Command must be string and not empty
                if not isinstance(job["command"], str) or not job["command"].strip():
                    print("[ERROR] Field 'command' must be a non-empty string.")
                    return

                # Everything is OK → enqueue job
                jobObj = Job.new(
                    command=job["command"],
                    max_retries=job["max_retries"]
                )
                storage.enqueue(jobObj)
                print("[OK] Job enqueued successfully:", jobObj)


            # -----------------------

            elif args.cmd == "worker":
                manager = WorkerManager(storage=storage)

                if args.action == "start":
                    print(f"[START] Starting {args.count} workers...")
                    manager.start(count=args.count)
                elif args.action == "list":
                    workers = manager.list_workers()
                    if not workers:
                        print("[LIST] No workers running")
                    else:
                        print(f"[LIST] {len(workers)} worker(s) running:")
                        for worker in workers:
                            worker_id = worker.get("worker_id", "?")
                            pid = worker.get("pid", "?")
                            started_at = worker.get("started_at", "?")
                            print(f"  Worker {worker_id}: PID {pid}, Started: {started_at}")
                else:  # stop
                    if args.pid:
                        print(f"[STOP] Stopping worker with PID {args.pid}...")
                        manager.stop_by_pid(args.pid)
                    elif args.all:
                        print("[STOP] Stopping all workers...")
                        manager.stop_all()
                    else:
                        print("[STOP] Stopping all workers...")
                        manager.stop_all()

            # -----------------------

            elif args.cmd == "status":
                summary = storage.getSummary()
                print("[STATUS] Queue Summary:", summary)

            # -----------------------

            elif args.cmd == "list":
                jobs = storage.listJobs(state=args.state)
                print("[LIST] Jobs:", jobs)

            # -----------------------

            elif args.cmd == "dlq":
                d = DLQ(storage=storage)

                if args.action == "list":
                    print("[DLQ] Dead Letter Queue:", d.listJobs())

                elif args.action == "retry":
                    if not args.job_id:
                        print("[ERROR] Missing job_id for retry command.")
                        return
                    d.retry(args.job_id)
                    print(f"[RETRY] Retried job {args.job_id}")

            # -----------------------

            elif args.cmd == "config":
                k, v = args.set
                config.set(k, v)
                config.save()
                print(f"[CONFIG] Updated config {k}={v}")

        except Exception as e:
            print("[ERROR] Unexpected error:", e)

    return cli_entry
