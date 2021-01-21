from models.datasets.base import DatasetModel


def retrieve_datasets(dataset_ids) -> list:
    """
    Retrieves a list of datasets by their IDs.
    :param dataset_ids: Dataset IDs to retrieve.
    :return: List of datasets
    """
    return DatasetModel.query.filter(
        (DatasetModel.dataset_id.in_(dataset_ids))
    ).all()
