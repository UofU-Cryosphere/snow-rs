from contextlib import contextmanager
from pathlib import Path
import time

from dask.distributed import Client

CHPC = 'chpc' in str(Path.home())


def start_cluster(cores=6, memory=None):
    """
    Checks whether the method is called on CHPC or locally and starts the
    cluster accordingly to the environment.

    Requests the number of workers for 2 hours in case this is run on CHPC.

    :param cores: Number of requested workers (Default: 6)
    :param memory: Amount of requested memory (Default: 1 GB per core)
    :return: Dask Client
    """
    if CHPC:
        from dask_jobqueue import SLURMCluster

        cluster = SLURMCluster(
            cores=cores,
            processes=cores,
            n_workers=1,
            project="notchpeak-shared-short",
            queue="notchpeak-shared-short",
            memory=f"{memory or cores}G",
            walltime="2:00:00",
        )
    else:
        # Assume local
        from dask.distributed import LocalCluster

        memory = memory / cores
        cluster = LocalCluster(n_workers=cores, memory_limit=f"{memory}G")

    return Client(cluster)


@contextmanager
def run_with_client(cores, memory):
    """
    Convenience method that executes the code block with a cluster.
    This takes care of starting and shutting down the cluster after execution.

    :param cores: Number of requested workers (Default: 6)
    :param memory: Amount of requested memory (Default: 1 GB per core)
    """
    client = start_cluster(cores, memory)
    try:
        yield client
    finally:
        time.sleep(4)
        client.close()
