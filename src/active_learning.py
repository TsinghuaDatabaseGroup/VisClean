from py_entitymatching.matcher.rfmatcher import *
from py_entitymatching.matcher.mlmatcher import *

# for training question
class ActiveLearning(RFMatcher):
    def __init__(self, *args, **kwargs):
        super(ActiveLearning, self).__init__()

    def _get_probs(self, x, check_rem=True):
        # Function that implements, predict interface mimic-ing sk-learn's
        # predict interface.

        # Here check_rem parameter requires a bit of explanation. The
        # check_rem flag checks if the input table has '_id' attribute if so
        # and if check_rem is True then we remove the '_id' attribute from
        # the table.
        # Note: Here check_rem is just passing what is coming in i.e it can be
        # true or false based up on who is calling it.
        x = self._get_data_for_sklearn(x, check_rem=check_rem)
        # Call the underlying predict function.
        y = self.clf.predict_proba(x)
        # Return the predictions
        return y

    def _get_probs_ex_attrs(self, table, exclude_attrs):
        """
        Variant of predict method, where data is derived based on exclude
        attributes.
        """
        # Validate input parameters
        # # We expect input table to be a pandas DataFrame.
        if not isinstance(table, pd.DataFrame):
            logger.error('Input table is not of type DataFrame')
            raise AssertionError('Input table is not of type DataFrame')

        # # We expect the exclude attributes to be a list, if not convert it
        # into a list.
        if not isinstance(exclude_attrs, list):
            exclude_attrs = [exclude_attrs]

        # Check if the input table contains the attributes to be excluded. If
        #  not raise an error.
        if not ch.check_attrs_present(table, exclude_attrs):
            logger.error(
                'The attributes mentioned in exclude_attrs is not present ' \
                'in the input table')
            raise AssertionError(
                'The attributes mentioned in exclude_attrs is not present ' \
                'in the input table')

        # Get the attributes to project.
        attributes_to_project = gh.list_diff(list(table.columns), exclude_attrs)
        # Get feature vectors and the target attribute
        x = table[attributes_to_project]

        # Do the predictions using the ML-based matcher.
        y = self._get_probs(x, check_rem=False)
        # Finally return the predictions
        return y

    def get_probs_all_data(self, x=None, table=None, exclude_attrs=None, target_attr=None,
                          append=False, inplace=True):
        """
        Predict interface for the matcher.

        Specifically, there are two ways the user can call the predict method.
        First, interface similar to scikit-learn where the feature vectors
        given as projected DataFrame.
        Second, give the DataFrame and explicitly specify the feature vectors
        (by specifying the attributes to be excluded) .

        A point to note is all the input parameters have a default value of
        None. This is done to support both the interfaces in a single function.


        Args:
            x (DataFrame): The input pandas DataFrame containing only feature
                vectors (defaults to None).
            table (DataFrame): The input pandas DataFrame containing feature
                vectors, and may be other attributes (defaults to None).
            exclude_attrs (list): A list of attributes to be excluded from the
                input table to get the feature vectors (defaults to None).
            target_attr (string): The attribute name where the predictions
                need to stored in the input table (defaults to None).
            append (boolean): A flag to indicate whether the predictions need
                to be appended in the input DataFrame (defaults to False).
            inplace (boolean): A flag to indicate whether the append needs to be
                done inplace (defaults to True).

        Returns:
            An array of predictions or a DataFrame with predictions updated.

        """
        # If x is not none, call the predict method that mimics sk-learn
        # predict method.

        if x is not None:
            y = self._get_probs(x)
        # If the input table and the exclude attributes are not None,
        # then call the appropriate predict method.
        elif table is not None and exclude_attrs is not None:
            y = self._get_probs_ex_attrs(table, exclude_attrs)
            # If the append is True, update the table
            if target_attr is not None and append is True:
                # If inplace is True, then update the input table.
                if inplace:
                    for i, v in enumerate(target_attr):
                        table[v] = y[:, i]
                    # Return the updated table
                    return table
                else:
                    # else, create a copy and update it.
                    table_copy = table.copy()
                    for i, v in enumerate(target_attr):
                        table_copy[v] = y[:, i]
                    # copy the properties from the input table to the output
                    # table.
                    cm.copy_properties(table, table_copy)
                    # Return the new table.
                    return table_copy

        else:
            # else, raise a syntax error
            raise SyntaxError(
                'The arguments supplied does not match '
                'the signatures supported !!!')
        # Return the predictions
        return y
