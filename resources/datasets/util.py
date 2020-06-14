from models.datasets.flat_file import FlatFileDatasetModel


def retrieve_datasets(dataset_ids) -> list:
    """
    Retrieves a list of datasets by their IDs.
    :param dataset_ids: Dataset IDs to retrieve.
    :return: List of datasets
    """
    return FlatFileDatasetModel.query.filter(
        (FlatFileDatasetModel.dataset_id.in_(dataset_ids))
    ).all()
