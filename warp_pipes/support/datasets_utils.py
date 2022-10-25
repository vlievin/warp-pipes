from __future__ import annotations

from typing import List, Dict
from typing import Optional
from typing import Union

from datasets import Dataset
from datasets import DatasetDict

from warp_pipes.support.fingerprint import get_fingerprint

HfDataset = Union[Dataset, DatasetDict]


def get_column_names(dataset: HfDataset) -> List[str]:
    if isinstance(dataset, DatasetDict):
        names = [c for dset in dataset.values() for c in dset.column_names]
        return list(set(names))
    elif isinstance(dataset, Dataset):
        return dataset.column_names
    else:
        raise TypeError(f"Unsupported dataset type: {type(dataset)}")


def remove_columns_with_fingerprint(dataset: Dataset, columns: List[str]) -> Dataset:
    """Remove columns and set a fingerprint deterministically"""
    columns = list(sorted(columns))
    args = {"dataset": dataset._fingerprint, "columns": columns}
    new_fingerprint = get_fingerprint(args)
    return dataset.remove_columns(columns, new_fingerprint=new_fingerprint)


def keep_only_columns(dataset: HfDataset, columns: Optional[List[str]]) -> HfDataset:
    """Keep only the given columns and set a fingerprint deterministically"""
    if columns is None:
        return dataset
    else:
        cols = [c for c in get_column_names(dataset) if c not in columns]
        if isinstance(dataset, Dataset):
            return remove_columns_with_fingerprint(dataset, cols)
        elif isinstance(dataset, DatasetDict):
            return DatasetDict(
                {
                    k: remove_columns_with_fingerprint(v, cols)
                    for k, v in dataset.items()
                }
            )


def get_dataset_fingerprints(dataset: HfDataset, reduce: bool = False) -> Dict[str, str] | str:
    """Fingerprint a `HfDataset`"""
    if isinstance(dataset, Dataset):
        fingerprint_state = dataset._fingerprint
    elif isinstance(dataset, DatasetDict):
        fingerprint_state = {k: v._fingerprint for k, v in dataset.items()}
    else:
        raise ValueError("Unsupported dataset type")

    if reduce and not isinstance(fingerprint_state, str):
        fingerprint_state = get_fingerprint(fingerprint_state)

    return fingerprint_state
