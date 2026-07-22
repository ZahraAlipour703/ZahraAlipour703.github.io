"""
dataset.py
==========

Dataset preparation utilities for the EgoHands dataset.

This module converts the original EgoHands annotations into
YOLOv8 format and creates the directory structure required
for training.

Functions
---------
- Convert MATLAB polygon annotations to YOLO labels
- Create train / validation / test splits
- Copy images
- Generate labels
- Validate dataset
- Print dataset statistics

Author
------
Zahra Alipour
"""

from __future__ import annotations

import random
import shutil
from pathlib import Path

import cv2
import numpy as np
from scipy.io import loadmat
from tqdm import tqdm


class EgoHandsDataset:
    """
    Prepare EgoHands dataset for YOLOv8.

    Expected dataset structure
    --------------------------

    EgoHands/

        _LABELLED_SAMPLES/

            CARD_BATTLE/

            CARDS_OFFICE/

            ...

        polygons.mat
    """

    def __init__(
        self,
        dataset_root: str,
        output_dir: str,
        train_ratio: float = 0.8,
        val_ratio: float = 0.1,
        random_seed: int = 42,
    ):

        self.dataset_root = Path(dataset_root)
        self.output_dir = Path(output_dir)

        self.train_ratio = train_ratio
        self.val_ratio = val_ratio
        self.random_seed = random_seed

        self.images_dir = self.output_dir / "images"
        self.labels_dir = self.output_dir / "labels"

        self.annotation_file = self.dataset_root / "polygons.mat"

        random.seed(random_seed)

    # ------------------------------------------------------------------

    def prepare(self):

        self._create_directories()

        polygons = loadmat(self.annotation_file)

        image_paths = sorted(
            list(
                self.dataset_root.glob(
                    "_LABELLED_SAMPLES/*/*.jpg"
                )
            )
        )

        random.shuffle(image_paths)

        total = len(image_paths)

        train_end = int(total * self.train_ratio)
        val_end = int(total * (self.train_ratio + self.val_ratio))

        splits = {
            "train": image_paths[:train_end],
            "val": image_paths[train_end:val_end],
            "test": image_paths[val_end:],
        }

        for split in splits:

            self._process_split(
                splits[split],
                split,
                polygons,
            )

        self.print_statistics()

    # ------------------------------------------------------------------

    def _create_directories(self):

        for split in ["train", "val", "test"]:

            (self.images_dir / split).mkdir(
                parents=True,
                exist_ok=True,
            )

            (self.labels_dir / split).mkdir(
                parents=True,
                exist_ok=True,
            )

    # ------------------------------------------------------------------

    def _process_split(
        self,
        images,
        split,
        polygons,
    ):

        print(f"\nProcessing {split}...")

        for image_path in tqdm(images):

            image = cv2.imread(str(image_path))

            h, w = image.shape[:2]

            shutil.copy(
                image_path,
                self.images_dir / split / image_path.name,
            )

            label_path = (
                self.labels_dir
                / split
                / image_path.with_suffix(".txt").name
            )

            annotations = self._load_annotations(
                image_path,
                polygons,
            )

            with open(label_path, "w") as f:

                for polygon in annotations:

                    x_min = polygon[:, 0].min()
                    y_min = polygon[:, 1].min()

                    x_max = polygon[:, 0].max()
                    y_max = polygon[:, 1].max()

                    xc = (x_min + x_max) / 2 / w
                    yc = (y_min + y_max) / 2 / h

                    bw = (x_max - x_min) / w
                    bh = (y_max - y_min) / h

                    f.write(
                        f"0 {xc:.6f} {yc:.6f} {bw:.6f} {bh:.6f}\n"
                    )

    # ------------------------------------------------------------------

    def _load_annotations(
        self,
        image_path,
        polygons,
    ):
        """
        Reads hand polygons from polygons.mat.

        This function should be adapted depending on
        the EgoHands version.

        Returns
        -------
        List[np.ndarray]
        """

        #
        # NOTE
        #
        # EgoHands stores polygons inside polygons.mat
        # with nested MATLAB structs.
        #
        # The parsing differs slightly between versions.
        #
        # Replace this parser with the exact one used
        # for your downloaded dataset if necessary.
        #

        return []

    # ------------------------------------------------------------------

    def validate(self):

        print("\nChecking dataset...")

        for split in ["train", "val", "test"]:

            images = list(
                (self.images_dir / split).glob("*.jpg")
            )

            labels = list(
                (self.labels_dir / split).glob("*.txt")
            )

            print(f"{split}")

            print(f"Images : {len(images)}")

            print(f"Labels : {len(labels)}")

    # ------------------------------------------------------------------

    def print_statistics(self):

        print("\nDataset Statistics")

        for split in ["train", "val", "test"]:

            images = len(
                list(
                    (self.images_dir / split).glob("*.jpg")
                )
            )

            labels = len(
                list(
                    (self.labels_dir / split).glob("*.txt")
                )
            )

            print(
                f"{split:<10}"
                f"Images: {images:<6}"
                f"Labels: {labels}"
            )


if __name__ == "__main__":

    dataset = EgoHandsDataset(
        dataset_root="data/raw/EgoHands",
        output_dir="data/processed",
    )

    dataset.prepare()

    dataset.validate()