import pytest
from airflow.models import DagBag

#dagbag = DagBag()


class TestDagValidation:

    #LOAD_SECOND_THESHOLD = 4
    REQUIRED_EMAIL = "juanfelipehdezm@gmail.com"
    EXPECTED_NUMBER_OF_DAGS = 1

    # def test_time_import_dags(self):
    #     """
    #     Verify that DAGs load fast enough
    #     - check for loading time
    #     """
    #     dagbag = DagBag()
    #     stats = dagbag.dagbag_stats
    #     slow_dags = list(filter(lambda f: f.duration >
    #                      self.LOAD_SECOND_THESHOLD, stats))
    #     name_slow_dags = ", ".join(map(lambda f: f.file[1:], slow_dags))

    #     assert not slow_dags, "The DAGs take more than {0}s to load:  {1}".format(
    #         self.LOAD_SECOND_THESHOLD, name_slow_dags)

    def test_defaul_args_email(self):
        """
        Verify that DAGs have the required email
        - check email
        """
        dagbag = DagBag()
        for dag_id, dag in dagbag.dags.items():
            emails = dag.default_args.get("email", [])

            assert self.REQUIRED_EMAIL in emails, "The mail {0} for sending alerts is missing from DAG {1}".format(
                self.REQUIRED_EMAIL, dag_id)
    