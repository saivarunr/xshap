import matplotlib
import numpy as np
import scipy as sp
matplotlib.use('Agg')
import shap


def test_null_model_small():
    explainer = shap.KernelExplainer(lambda x: np.zeros(x.shape[0]), np.ones((2, 4)), nsamples=100)
    e = explainer.explain(np.ones((1, 4)))
    assert np.sum(np.abs(e)) < 1e-8

def test_null_model():
    explainer = shap.KernelExplainer(lambda x: np.zeros(x.shape[0]), np.ones((2, 10)), nsamples=100)
    e = explainer.explain(np.ones((1, 10)))
    assert np.sum(np.abs(e)) < 1e-8

def test_front_page_model_agnostic():
    import sklearn
    import shap
    from sklearn.model_selection import train_test_split

    # print the JS visualization code to the notebook
    shap.initjs()

    # train a SVM classifier
    X_train, X_test, Y_train, Y_test = train_test_split(*shap.datasets.iris(), test_size=0.2, random_state=0)
    svm = sklearn.svm.SVC(kernel='rbf', probability=True)
    svm.fit(X_train, Y_train)

    # use Kernel SHAP to explain test set predictions
    explainer = shap.KernelExplainer(svm.predict_proba, X_train, nsamples=100, link="logit")
    shap_values = explainer.shap_values(X_test)

    # plot the SHAP values for the Setosa output of the first instance
    shap.force_plot(explainer.expected_value[0], shap_values[0][0, :], X_test.iloc[0, :], link="logit")

def test_front_page_model_agnostic_rank():
    import sklearn
    import shap
    from sklearn.model_selection import train_test_split

    # print the JS visualization code to the notebook
    shap.initjs()

    # train a SVM classifier
    X_train, X_test, Y_train, Y_test = train_test_split(*shap.datasets.iris(), test_size=0.2, random_state=0)
    svm = sklearn.svm.SVC(kernel='rbf', probability=True)
    svm.fit(X_train, Y_train)

    # use Kernel SHAP to explain test set predictions
    explainer = shap.KernelExplainer(svm.predict_proba, X_train, nsamples=100, link="logit", l1_reg="rank(3)")
    shap_values = explainer.shap_values(X_test)

    # plot the SHAP values for the Setosa output of the first instance
    shap.force_plot(explainer.expected_value[0], shap_values[0][0, :], X_test.iloc[0, :], link="logit")

def test_kernel_shap_with_dataframe():
    from sklearn.linear_model import LinearRegression
    import shap
    import pandas as pd
    import numpy as np
    np.random.seed(3)

    df_X = pd.DataFrame(np.random.random((10, 3)), columns=list('abc'))
    df_X.index = pd.date_range('2018-01-01', periods=10, freq='D', tz='UTC')

    df_y = df_X.eval('a - 2 * b + 3 * c')
    df_y = df_y + np.random.normal(0.0, 0.1, df_y.shape)

    linear_model = LinearRegression()
    linear_model.fit(df_X, df_y)

    explainer = shap.KernelExplainer(linear_model.predict, df_X, keep_index=True)
    shap_values = explainer.shap_values(df_X)

def test_kernel_shap_with_a1a_sparse_zero_background():
    from sklearn.model_selection import train_test_split
    from sklearn.linear_model import LinearRegression
    import shap

    X, y = shap.datasets.a1a()
    x_train, x_test, y_train, y_test = train_test_split(X, y, test_size=0.1, random_state=0)
    linear_model = LinearRegression()
    linear_model.fit(x_train, y_train)

    _, cols = x_train.shape
    shape = 1, cols
    background = sp.sparse.csr_matrix(shape, dtype=x_train.dtype)
    explainer = shap.KernelExplainer(linear_model.predict, background)
    explainer.shap_values(x_test)

def test_kernel_shap_with_a1a_sparse_nonzero_background():
    np.set_printoptions(threshold=100000)
    from sklearn.model_selection import train_test_split
    from sklearn.linear_model import LinearRegression
    from sklearn.utils.sparsefuncs import csc_median_axis_0
    import shap

    X, y = shap.datasets.a1a()
    x_train, x_test, y_train, y_test = train_test_split(X, y, test_size=0.01, random_state=0)
    linear_model = LinearRegression()
    linear_model.fit(x_train, y_train)
    # Calculate median of background data
    median_dense = csc_median_axis_0(x_train.tocsc())
    median = sp.sparse.csr_matrix(median_dense)
    explainer = shap.KernelExplainer(linear_model.predict, median)
    shap_values = explainer.shap_values(x_test)
    # Compare to dense results
    x_train_dense = x_train.toarray()

    def dense_to_sparse_predict(data):
        sparse_data = sp.sparse.csr_matrix(data)
        return linear_model.predict(sparse_data)

    explainer_dense = shap.KernelExplainer(linear_model.predict, median_dense.reshape((1, len(median_dense))))
    x_test_dense = x_test.toarray()
    shap_values_dense = explainer_dense.shap_values(x_test_dense)
    # Validate sparse and dense result is the same
    # Note: The default tolerance is almost always fine, but in one out of every
    # 20 runs or so it fails so decreasing it by two orders of magnitude from the default
    assert(np.allclose(shap_values, shap_values_dense, rtol=1e-02, atol=1e-04))

def test_kernel_shap_with_high_dim_sparse():
    # verifies we can run on very sparse data produced from feature hashing
    from sklearn.model_selection import train_test_split
    from sklearn.linear_model import LinearRegression
    import shap
    remove = ('headers', 'footers', 'quotes')
    categories = [
        'alt.atheism',
        'talk.religion.misc',
        'comp.graphics',
        'sci.space',
    ]
    from sklearn.datasets import fetch_20newsgroups
    ngroups = fetch_20newsgroups(subset='train', categories=categories,
                        shuffle=True, random_state=42,
                        remove=remove)
    x_train, x_test, y_train, y_validation = train_test_split(ngroups.data, ngroups.target,
                                                                    test_size=0.01, random_state=42)
    from sklearn.feature_extraction.text import HashingVectorizer
    vectorizer = HashingVectorizer(stop_words='english', alternate_sign=False,
                                n_features=2**16)
    x_train = vectorizer.transform(x_train)
    x_test = vectorizer.transform(x_test)
    # Fit a linear regression model
    linear_model = LinearRegression()
    linear_model.fit(x_train, y_train)
    rows, cols = x_train.shape
    shape = 1, cols
    background = sp.sparse.csr_matrix(shape, dtype=x_train.dtype)
    explainer = shap.KernelExplainer(linear_model.predict, background)
    shap_values = explainer.shap_values(x_test)
