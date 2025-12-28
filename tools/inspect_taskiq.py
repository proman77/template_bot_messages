import taskiq.cli.worker.run
import taskiq.cli.worker.args
import inspect

print("run_worker signature:", inspect.signature(taskiq.cli.worker.run.run_worker))
print("WorkerArgs fields:", taskiq.cli.worker.args.WorkerArgs.__annotations__)
