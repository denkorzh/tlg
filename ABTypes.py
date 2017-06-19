# -*- coding: utf-8 -*-
import warnings
from typing import List, Optional, Sequence, TypeVar

PandasDataFrame = TypeVar('pandas.core.frame.DataFrame')  # type hint for pandas DataFrame
Ndarray = TypeVar('ndarray')  # type hint for numpy ndarray


class Variation:
    """
    Class handles results provided with A/B test for a particular variation
    """
    def __init__(self, total: Optional[int]=None, success: Optional[int]=None,
                 data: Optional[Sequence[int]]=None, group: Optional[int]=None
                 ) -> None:
        """
        Create Variation instance
        
        :param total: number of total visitors
        :param success: number of visitors who clicked the button
        :param data: sequence of visitors actions (1 - clicked, 0 - didn't click)
        :param group: size of group in data (for Wald tests) 
        """

        self.total = None  # type: Optional[int]
        self.success = None  # type: Optional[int]
        self.data = None  # type: List[int]
        self.group = group  # type: Optional[int]

        if data is not None:
            try:
                self.data = list(data)
            except:
                raise TypeError('data must be convertible to list')
        else:
            self.data = data

        if data is not None:
            self.total = len(data)
            self.success = sum(data)
        else:
            self.total = total if total else 0.
            self.success = success if success else 0.

        if (self.data is not None) and (set(self.data) != {0, 1}):
            raise Exception('data should contain only 0\'s and 1\'s.')

        if (self.total is not None) and (self.success is not None) and (self.total < self.success):
            raise Exception('Conversion rate > 1')

    def estimate_conversion(self) -> float:
        """
        Estimate the sample conversion
        
        :return: conversion 
        """
        try:
            return self.success / self.total
        except:
            raise ZeroDivisionError()

    def copy(self) -> 'Variation':
        """
        Copy Variation instance
        """
        return Variation(self.total, self.success, self.data)

    def truncate(self, size: int) -> 'Variation':
        """
        Truncate variation data size to proposed if it is less than current one.
        
        :param size: new size
        :return: variation
        """
        if not self.data:
            raise Exception('Variation has no data inside')
        else:
            return Variation(data=self.data[:1 + min(size, self.total)])

    def generate_sample(self) -> Ndarray:
        """
        Generate a sample based on total number and number of successes.
        """
        import numpy as np
        mask = np.random.choice(self.total, self.success, replace=False)
        sample = np.zeros(self.total)
        sample[mask] = 1
        return sample


class VariationsCollection:
    """
    Set of variations obtained within A/B test.
    Includes one control variations and several experimental ones.
    """
    def __init__(self, *args: Variation) -> None:
        """
        Create VariationsCollection instance.
        The first argument is treated as a control variation, the other - as experimental ones.
        If no arguments are provided the empty instance would be created.
        """
        self.control = None  # type: Optional[Variation]
        self.treatments = list()  # type: Optional[List[Variation]]

        if len(args):
            self.add_control(args[0])
            if len(args) > 1:
                self.add_treatments(*args[1:])

    def add_control(self, variation: Variation) -> None:
        """
        Add control variation to the collection.
        If control variation is already present it would be substituted and the warning would be printed to console.
        It's an in-place method.
        
        :param variation: new control variation
        """
        if not isinstance(variation, Variation):
            raise TypeError('Variation object only suits.')
        if self.control:
            warnings.warn('Collection already has a control variation. It would be changed to proposed one.')
        self.control = variation

    def add_treatments(self, *args: Variation) -> None:
        """
        Add new treatment variations. Treatments are added to the end of experimental variations list.
        It'a an in-place method.
        
        :param args: experimental variations
        """
        if not len(args):
            warnings.warn('Nothing to add')
        else:
            for arg in args:
                if not isinstance(arg, Variation):
                    raise TypeError('Objects of Variation type only suit.')
            self.treatments += list(args)

    def delete_control(self) -> None:
        """
        Delete control variation.
        """
        self.control = None

    def delete_treatment(self, n: int) -> None:
        """
        Delete treatment with given number (counting from 1) if it exists.
        It's an in-place method.
        
        :param n: number of variation to be deleted.
        """
        if n > len(self.treatments):
            warnings.warn('Number of experimental variations is less then proposed number.')
        else:
            del self.treatments[n-1]

    def describe(self) -> Optional[PandasDataFrame]:
        """
        Return summary information about collection.
        If collection is empty returns None. 
        """
        import pandas as pd
        if (self.control is None) and (not len(self.treatments)):
            warnings.warn('The collection is empty.')
            return None
        info_dict = dict()
        if self.control is not None:
            info_dict['Control'] = [self.control.success,
                                    self.control.total,
                                    self.control.estimate_conversion()
                                    ]
        for i, treatment in enumerate(self.treatments, 1):
            info_dict['Treatment_{:d}'.format(i)] = [treatment.success,
                                                     treatment.total,
                                                     treatment.estimate_conversion()
                                                     ]
        info_df = pd.DataFrame(info_dict)
        info_df.index = ['Success', 'Total', 'Conversion_rate']
        return info_df.T

    def dump_json(self) -> str:
        """
        Dumps collection to json
        """
        import json

        def variation_to_dict(var: Variation) -> dict:
            """Dumps var to dictionary"""
            dump = dict()
            dump['total'] = var.total if var is not None else None
            dump['success'] = var.success if var is not None else None
            dump['data'] = var.data if var is not None else None
            dump['group'] = var.group if var is not None else None
            return dump

        d = dict()
        d['0'] = variation_to_dict(self.control)
        for i, var in enumerate(self.treatments, 1):
            d[str(i)] = variation_to_dict(var)

        return json.dumps(d)

    def load_json(self, js: str) -> None:
        """
        Loads data from json
        :param js: json with collection data
        """
        import json

        d = json.loads(js)  # type: dict

        def dict_to_variation(dictionary: dict) -> Variation:
            """Loads variaton from dictionary"""
            if dictionary['data'] is not None:
                return Variation(data=dictionary['data'], group=dictionary['group'])
            else:
                return Variation(total=dictionary['total'], success=dictionary['success'], group=dictionary['group'])

        try:
            self.delete_control()
            self.treatments = []
            self.add_control(dict_to_variation(d['0']))
            for i in sorted(d.keys()):
                if i != '0':
                    self.add_treatments(dict_to_variation(d[i]))
        except:
            raise Exception('Cannot parse json to VariationsCollection')
