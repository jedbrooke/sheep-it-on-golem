#!/usr/bin/env python3
import asyncio
from datetime import datetime, timedelta
import pathlib
import shlex
import sys

from yapapi import Golem, Task, WorkContext, NoPaymentAccountError
from yapapi.payload import vm
from yapapi.rest.activity import BatchTimeoutError
import os

import apprise

from utils import (
    TEXT_COLOR_CYAN,
    TEXT_COLOR_DEFAULT,
    TEXT_COLOR_MAGENTA,
    TEXT_COLOR_RED,
    build_parser,
    format_usage,
    print_env_info,
    run_golem_example,
)

apobj = apprise.Apprise()
apobj.add(os.getenv("WEBHOOK"))

examples_dir = pathlib.Path(__file__).resolve().parent.parent
sys.path.append(str(examples_dir))

HASH = "b26e95a58c3dfcc0bee208f081d362f67bb67255aef93938908d8699"

async def main(
    subnet_tag, min_cpu_threads, payment_driver=None, payment_network=None
):

    package = await vm.repo(
        image_hash=HASH,
        # only run on provider nodes that have more than 0.5gb of RAM available
        min_mem_gib=0.5,
        # only run on provider nodes that have more than 2gb of storage space available
        min_storage_gib=2.0,
        # only run on provider nodes which a certain number of CPU threads (logical CPU cores) available
        min_cpu_threads=min_cpu_threads,
    )

    async def worker(ctx: WorkContext, tasks):
        # Set timeout for the first script executed on the provider. Usually, 30 seconds
        # should be more than enough for computing a single frame of the provided scene,
        # however a provider may require more time for the first task if it needs to download
        # the VM image first. Once downloaded, the VM image will be cached and other tasks that use
        # that image will be computed faster.
        script = ctx.new_script(timeout=timedelta(minutes=10))

        async for t in tasks:
            # apobj.notify(body="starting job", title="job is starting")
            cmd = shlex.split(f"""/usr/local/openjdk-11/bin/java -jar /sheepit.jar \
                --no-gpu \
                --no-systray \
                -cache-dir /golem/work \
                -hostname golem \
                -login rektsupport \
                -password {os.getenv("KEY")} \
                -shutdown +10 \
                -ui text > /golem/output/sheepit.logs 2>&1""")
            
            script.run(cmd)
            
            output_file = f"sheepit_logs/log-{t.data:04d}.log"
            script.download_file("/golem/output/sheepit.logs", output_file)

            try:
                
                yield script
                # TODO: Check if job results are valid
                # and reject by: task.reject_task(reason = 'invalid file')
                t.accept_result(result=output_file)
            except BatchTimeoutError:
                print(
                    f"Task {t} timed out on {ctx.provider_name}, time: {t.running_time}"
                )
                raise

            # reinitialize the script which we send to the engine to compute subsequent frames
            script = ctx.new_script(timeout=timedelta(minutes=1))

            raw_state = await ctx.get_raw_state()
            usage = format_usage(await ctx.get_usage())
            cost = await ctx.get_cost()
            print(
                f"{TEXT_COLOR_MAGENTA}"
                f" --- {ctx.provider_name} STATE: {raw_state}\n"
                f" --- {ctx.provider_name} USAGE: {usage}\n"
                f" --- {ctx.provider_name}  COST: {cost}"
                f"{TEXT_COLOR_DEFAULT}"
            )

    init_overhead = 3
    # Providers will not accept work if the timeout is outside of the [5 min, 30min] range.
    # We increase the lower bound to 6 min to account for the time needed for our demand to
    # reach the providers.
    min_timeout, max_timeout = 60, 300

    timeout = timedelta(minutes=300)

    async with Golem(
        budget=10.0,
        subnet_tag=subnet_tag,
        payment_driver=payment_driver,
        payment_network=payment_network,
    ) as golem:
        print_env_info(golem)

        num_tasks = 0
        start_time = datetime.now()

        completed_tasks = golem.execute_tasks(
            worker,
            [Task(data=i) for i in range(3)],
            payload=package,
            max_workers=3,
            timeout=timeout,
        )
        async for task in completed_tasks:
            num_tasks += 1
            print(
                f"Task computed: {task}, result: {task.result}, time: {task.running_time}"
            )

        print(
            f"{num_tasks} tasks computed, total time: {datetime.now() - start_time}"
        )

if __name__ == "__main__":
    parser = build_parser("Run Sheepit")
    parser.add_argument("--show-usage", action="store_true", help="show activity usage and cost")
    parser.add_argument(
        "--min-cpu-threads",
        type=int,
        default=1,
        help="require the provider nodes to have at least this number of available CPU threads",
    )
    now = datetime.now().strftime("%Y-%m-%d_%H.%M.%S")
    parser.set_defaults(log_file=f"blender-yapapi-{now}.log")
    args = parser.parse_args()

    run_golem_example(
        main(
            subnet_tag=args.subnet_tag,
            min_cpu_threads=args.min_cpu_threads,
            payment_driver=args.payment_driver,
            payment_network=args.payment_network,
        ),
        log_file=args.log_file,
    )

"""
sheepit args:
/usr/local/openjdk-11/bin/java -jar /sheepit-client.jar --no-gpu --no-systray -cache-dir /golem/work -hostname golem -login rektsupport -password xxx -shutdown +10 -ui text
"""

