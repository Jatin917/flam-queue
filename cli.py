import argparse
import json
from workers import WorkerManager
from scheduler import SchedulerQueue
from dlq import DLQ

def build_cli(storage, config):
    def cli_entry():
        parser = argparse.ArgumentParser(prog="queuectl")
        sub = parser.add_subparsers(dest="cmd")


        # enqueue
        enq = sub.add_parser("enqueue")
        enq.add_argument("job_json")


        # worker
        wk = sub.add_parser("worker")
        wk.add_argument("action", choices=["start", "stop"])
        wk.add_argument("--count", type=int, default=1)


        # status
        sub.add_parser("status")


        # list
        lst = sub.add_parser("list")
        lst.add_argument("--state", default=None)


        # dlq
        dlq = sub.add_parser("dlq")
        dlq.add_argument("action", choices=["list", "retry"])
        dlq.add_argument("job_id", nargs="?")


        # config
        cfg = sub.add_parser("config")
        cfg.add_argument("set", nargs=2)


        args = parser.parse_args()
        # basic dispatcher (skeleton)
        if args.cmd == "enqueue":
            job = json.loads(args.job_json)
            storage.enqueue(job)
            print("enqueued", job.get("id"))
        elif args.cmd == "worker":
            manager = WorkerManager(storage=storage, config=config)
            if args.action == "start":
                manager.start(count=args.count)
            else:
                manager.stop()
        elif args.cmd == "status":
            print(storage.getSummary())
        elif args.cmd == "list":
            print(storage.listJobs(state=args.state))
        elif args.cmd == "dlq":
            d = DLQ(storage=storage)
            if args.action == "list":
                print(d.listJobs())
            elif args.action == "retry" and args.job_id:
                d.retry(args.job_id)
        elif args.cmd == "config":
            k, v = args.set
            config.set(k, v)
            config.save()
            print("config updated")
        else:
            parser.print_help()


    return cli_entry