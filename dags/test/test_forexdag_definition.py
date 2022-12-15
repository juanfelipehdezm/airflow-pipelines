import pytest
import collections
import pendulum
from airflow.models import DagBag

# this tests is just for on specific DAG


@pytest.fixture(scope="class")
def dag():
    """
    test only for this dag in particular and for just this scope
    """
    dagbag = DagBag()
    return dagbag.get_dag("forex_data_pipeline")


class Test_forex_pipeline:

    EXPECTED_NUMBER_TASKS = 6
    EXPECTED_TASKS = ["is_forex_rates_available", "downloading_rates", "is_forex_rates_file_available",
                      "process_json_file", "create_forexRates_database", "store_ratings"]

    def test_number_tasks(self, dag):
        """
        Verify the number of tasks in the DAG
        """
        nb_tasks = len(dag.tasks)
        assert nb_tasks == self.EXPECTED_NUMBER_TASKS, f"The number of task are different from {self.EXPECTED_NUMBER_TASKS}"

    def test_contains_tasks(self, dag):
        """
        verify if the DAG is composed of the expected tasks
        """
        task_ids = list(map(lambda task: task.task_id, dag.tasks))
        # print(task_ids)
        assert collections.Counter(task_ids) == collections.Counter(
            self.EXPECTED_TASKS), f"The tasks Ids are different from {self.EXPECTED_TASKS}"

    # declare parameters
    @pytest.mark.parametrize("task, expected_upstream, expected_downstream",

                             [
                                 ("is_forex_rates_available",
                                  [], ["downloading_rates"]),
                                 ("create_forexRates_database",
                                  [], ["store_ratings"])
                             ]

                             )
    def test_dependencies_of_tasks(self, dag, task, expected_upstream, expected_downstream):
        """
        Verify if a given task has the expected upstream and downstream dependencies
        - Parametrized test function so that each task given in the array is tested with the associated parameters 

        """
        task = dag.get_task(task, True)
        print(task)
        assert collections.Counter(task.upstream_task_ids) == collections.Counter(
            expected_upstream), f"The task {task} doesn't have the expected upstream dependencies"
        assert collections.Counter(task.downstream_task_ids) == collections.Counter(
            expected_downstream), f"The task {task} doesn't have the expected downstream dependencies"
