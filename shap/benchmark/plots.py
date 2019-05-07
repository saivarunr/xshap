import numpy as np
from .experiments import run_experiments
from ..plots import colors
from .. import __version__
from . import models
from . import methods
import sklearn
import io
import base64
try:
    import matplotlib.pyplot as pl
    import matplotlib
except ImportError:
    pass


metadata = {
    "consistency_guarantees": {
        "title": "Consistency Guarantees",
        "sort_order": 3
    },
    "local_accuracy": {
        "title": "Local Accuracy",
        "sort_order": 2
    },
    "runtime": {
        "title": "Runtime",
        "sort_order": 1
    },
    "remove_positive": {
        "title": "Remove Positive",
        "xlabel": "Max fraction of features removed",
        "ylabel": "Negative mean model output",
        "sort_order": 11
    },
    "mask_remove_positive": {
        "title": "Mask Remove Positive",
        "xlabel": "Max fraction of features removed",
        "ylabel": "Negative mean model output",
        "sort_order": 9
    },
    "remove_negative": {
        "title": "Remove Negative",
        "xlabel": "Max fraction of features removed",
        "ylabel": "Mean model output",
        "sort_order": 12
    },
    "mask_remove_negative": {
        "title": "Mask Remove Negative",
        "xlabel": "Max fraction of features removed",
        "ylabel": "Mean model output",
        "sort_order": 10
    },
    "keep_positive": {
        "title": "Keep Positive",
        "xlabel": "Max fraction of features kept",
        "ylabel": "Mean model output",
        "sort_order": 6
    },
    "mask_keep_positive": {
        "title": "Mask Keep Positive",
        "xlabel": "Max fraction of features kept",
        "ylabel": "Mean model output",
        "sort_order": 4
    },
    "keep_negative": {
        "title": "Keep Negative",
        "xlabel": "Max fraction of features kept",
        "ylabel": "Negative mean model output",
        "sort_order": 7
    },
    "mask_keep_negative": {
        "title": "Mask Keep Negative",
        "xlabel": "Max fraction of features kept",
        "ylabel": "Negative mean model output",
        "sort_order": 5
    },
    "batch_remove_absolute__r2": {
        "title": "Batch Remove Absolute",
        "xlabel": "Fraction of features removed",
        "ylabel": "1 - R^2",
        "sort_order": 13
    },
    "batch_keep_absolute__r2": {
        "title": "Batch Keep Absolute",
        "xlabel": "Fraction of features kept",
        "ylabel": "R^2",
        "sort_order": 8
    },
    "batch_remove_absolute__roc_auc": {
        "title": "Batch Remove Absolute",
        "xlabel": "Fraction of features removed",
        "ylabel": "1 - ROC AUC",
        "sort_order": 13
    },
    "batch_keep_absolute__roc_auc": {
        "title": "Batch Keep Absolute",
        "xlabel": "Fraction of features kept",
        "ylabel": "ROC AUC",
        "sort_order": 8
    },
    
    "linear_shap_corr": {
        "title": "Linear SHAP (corr)"
    },
    "linear_shap_ind": {
        "title": "Linear SHAP (ind)"
    },
    "coef": {
        "title": "Coefficents"
    },
    "random": {
        "title": "Random"
    },
    "kernel_shap_1000_meanref": {
        "title": "Kernel SHAP 1000 mean ref."
    },
    "sampling_shap_1000": {
        "title": "Sampling SHAP 1000"
    },
    "tree_shap_tree_path_dependent": {
        "title": "Tree SHAP"
    },
    "saabas": {
        "title": "Saabas"
    },
    "tree_gain": {
        "title": "Gain/Gini Importance"
    },
    "mean_abs_tree_shap": {
        "title": "mean(|Tree SHAP|)"
    },
    "lasso_regression": {
        "title": "Lasso Regression"
    },
    "ridge_regression": {
        "title": "Ridge Regression"
    },
    "gbm_regression": {
        "title": "Gradient Boosting Regression"
    }
}

benchmark_color_map = {
    "tree_shap": "#1E88E5",
    "deep_shap": "#1E88E5",
    "linear_shap_corr": "#1E88E5",
    "linear_shap_ind": "#ff0d57",
    "coef": "#13B755",
    "random": "#999999",
    "const_random": "#666666",
    "kernel_shap_1000_meanref": "#7C52FF"
}

negated_metrics = [
    "runtime",
    "remove_positive",
    "mask_remove_positive",
    "keep_negative",
    "mask_keep_negative"
]

one_minus_metrics = [
    "batch_remove_absolute__r2",
    "batch_remove_absolute__roc_auc"
]

def get_method_color(method):
    for l in getattr(methods, method).__doc__.split("\n"):
        l = l.strip()
        if l.startswith("color = "):
            v = l.split("=")[1].strip()
            if v.startswith("red_blue_circle("):
                return colors.red_blue_circle(float(v[16:-1]))
            else:
                return v
    return "#000000"

def get_method_linestyle(method):
    for l in getattr(methods, method).__doc__.split("\n"):
        l = l.strip()
        if l.startswith("linestyle = "):
            return l.split("=")[1].strip()
    return "solid"

def plot_curve(dataset, model, metric, cmap=benchmark_color_map):
    experiments = run_experiments(dataset=dataset, model=model, metric=metric)
    pl.figure()
    method_arr = []
    for (name,(fcounts,scores)) in experiments:
        _,_,method,_ = name
        if metric in negated_metrics:
            scores = -scores
        elif metric in one_minus_metrics:
            scores = 1 - scores
        auc = sklearn.metrics.auc(fcounts, scores) / fcounts[-1]
        method_arr.append((auc, method, scores))
    for (auc,method,scores) in sorted(method_arr):
        method_title = getattr(methods, method).__doc__.split("\n")[0].strip()
        l = "{:6.3f} - ".format(auc) + method_title
        pl.plot(
            fcounts / fcounts[-1], scores, label=l,
            color=get_method_color(method), linewidth=2,
            linestyle=get_method_linestyle(method)
            )
    pl.xlabel(metadata[metric]["xlabel"])
    pl.ylabel(metadata[metric]["ylabel"])
    model_title = getattr(models, dataset+"__"+model).__doc__.split("\n")[0].strip()
    pl.title(metadata[metric]["title"] + " - " + model_title)
    pl.gca().xaxis.set_ticks_position('bottom')
    pl.gca().yaxis.set_ticks_position('left')
    pl.gca().spines['right'].set_visible(False)
    pl.gca().spines['top'].set_visible(False)
    ahandles, alabels = pl.gca().get_legend_handles_labels()
    pl.legend(reversed(ahandles), reversed(alabels))
    return pl.gcf()

def make_grid(scores, dataset, model):
    color_vals = {}
    for (_,_,method,metric),(fcounts,score) in filter(lambda x: x[0][0] == dataset and x[0][1] == model, scores):
        if metric not in color_vals:
            color_vals[metric] = {}

        if metric in negated_metrics:
            score = -score
        elif metric in one_minus_metrics:
            score = 1 - score

        if fcounts is None:
            color_vals[metric][method] = score
        else:
            auc = sklearn.metrics.auc(fcounts, score) / fcounts[-1]
            color_vals[metric][method] = auc
    
    col_keys = sorted(list(color_vals.keys()), key=lambda v: metadata[v]["sort_order"])
    row_keys = list(set([v for k in col_keys for v in color_vals[k].keys()]))
    
    data = -28567 * np.ones((len(row_keys), len(col_keys)))
    
    for i in range(len(row_keys)):
        for j in range(len(col_keys)):
            data[i,j] = color_vals[col_keys[j]][row_keys[i]]
            
    assert np.sum(data == -28567) == 0, "There are missing data values!"
            
    data = (data - data.min(0)) / (data.max(0) - data.min(0) + 1e-8)
    
    # sort by performans
    inds = np.argsort(-data.mean(1))
    row_keys = [row_keys[i] for i in inds]
    data = data[inds,:]
    
    return row_keys, col_keys, data

from matplotlib.colors import LinearSegmentedColormap
red_blue_solid = LinearSegmentedColormap('red_blue_solid', {
    'red': ((0.0, 198./255, 198./255),
            (1.0, 5./255, 5./255)),

    'green': ((0.0, 34./255, 34./255),
              (1.0, 198./255, 198./255)),

    'blue': ((0.0, 5./255, 5./255),
             (1.0, 24./255, 24./255)),

    'alpha': ((0.0, 1, 1),
              (1.0, 1, 1))
})
from IPython.core.display import HTML
def plot_grids(dataset, model_names, out_file=None):

    scores = []
    for model in model_names:
        scores.extend(run_experiments(dataset=dataset, model=model))
    
    prefix = "<style type='text/css'> .shap_benchmark__select:hover { text-decoration: none }</style>"
    out = "" # background: rgb(30, 136, 229)
    
    # out += "<div style='font-weight: regular; font-size: 24px; text-align: center; background: #f8f8f8; color: #000; padding: 20px;'>SHAP Benchmark</div>\n"
    # out += "<div style='height: 1px; background: #ddd;'></div>\n"
    #out += "<div style='height: 7px; background-image: linear-gradient(to right, rgb(30, 136, 229), rgb(255, 13, 87));'></div>"

    out += "<div style='position: fixed; left: 0px; top: 0px; right: 0px; height: 200px; background: #fff;'>\n" # box-shadow: 0 4px 8px 0 rgba(0, 0, 0, 0.2), 0 6px 20px 0 rgba(0, 0, 0, 0.19);
    out += "<div style='position: absolute; bottom: 0px; left: 0px; right: 0px;' align='center'><table style='border-width: 1px; margin-right: 100px'>\n"
    for ind,model in enumerate(model_names):
        row_keys, col_keys, data = make_grid(scores, dataset, model)
#         print(data)
#         print(colors.red_blue_solid(0.))
#         print(colors.red_blue_solid(1.))
#         return
        for metric in col_keys:
            if metric not in ["local_accuracy", "runtime", "consistency_guarantees"]:
                plot_curve(dataset, model, metric)
                buf = io.BytesIO()
                pl.gcf().set_size_inches(1200.0/175,800.0/175)
                pl.savefig(buf, format='png', dpi=175)
                pl.close()
                buf.seek(0)
                data_uri = base64.b64encode(buf.read()).decode('utf-8').replace('\n', '')
                plot_id = "plot__"+dataset+"__"+model+"__"+metric
                prefix += "<div onclick='document.getElementById(\"%s\").style.display = \"none\"' style='display: none; position: fixed; z-index: 10000; left: 0px; right: 0px; top: 0px; bottom: 0px; background: rgba(255,255,255,0.9);' id='%s'>" % (plot_id, plot_id)
                prefix += "<img width='600' height='400' style='margin-left: auto; margin-right: auto; margin-top: 200px; box-shadow: 0 4px 8px 0 rgba(0, 0, 0, 0.2), 0 6px 20px 0 rgba(0, 0, 0, 0.19);' src='data:image/png;base64,%s'>" % data_uri
                prefix += "</div>"

        model_title = getattr(models, dataset+"__"+model).__doc__.split("\n")[0].strip()

        if ind == 0:
            out += "<tr><td style='background: #fff; width: 250px'></td></td>"
            for j in range(data.shape[1]):
                metric_title = metadata[col_keys[j]]["title"]
                out += "<td style='width: 40px; background: #fff; text-align: right;'><div style='margin-left: 10px; margin-bottom: -5px; white-space: nowrap; transform: rotate(-45deg); transform-origin: left top 0; width: 1.5em; margin-top: 8em'>" + metric_title + "</div></td>"
            out += "</tr>\n"
            out += "</table></div></div>\n"
            out += "<table style='border-width: 1px; margin-right: 100px; margin-top: 200px;'>\n"
        out += "<tr><td style='background: #fff'></td><td colspan='%d' style='background: #fff; font-weight: bold; text-align: center; margin-top: 10px;'>%s</td></tr>\n" % (data.shape[1], model_title)
        for i in range(data.shape[0]):
            out += "<tr>"
#             if i == 0:
#                 out += "<td rowspan='%d' style='background: #fff; text-align: center; white-space: nowrap; vertical-align: middle; '><div style='font-weight: bold; transform: rotate(-90deg); transform-origin: left top 0; width: 1.5em; margin-top: 8em'>%s</div></td>" % (data.shape[0], model_name)
            method_title = getattr(methods, row_keys[i]).__doc__.split("\n")[0].strip()
            out += "<td style='background: #ffffff; text-align: right; width: 250px' title='shap.LinearExplainer(model)'>" + method_title + "</td>\n"
            for j in range(data.shape[1]):
                plot_id = "plot__"+dataset+"__"+model+"__"+col_keys[j]
                out += "<td onclick='document.getElementById(\"%s\").style.display = \"block\"' style='padding: 0px; padding-left: 0px; padding-right: 0px; border-left: 0px solid #999; width: 42px; height: 34px; background-color: #fff'>" % plot_id
                #out += "<div style='opacity: "+str(2*(max(1-data[i,j], data[i,j])-0.5))+"; background-color: rgb" + str(tuple(v*255 for v in colors.red_blue_solid(0. if data[i,j] < 0.5 else 1.)[:-1])) + "; height: "+str((30*max(1-data[i,j], data[i,j])))+"px; margin-left: auto; margin-right: auto; width:"+str((30*max(1-data[i,j], data[i,j])))+"px'></div>"
                out += "<div style='opacity: "+str(1)+"; background-color: rgb" + str(tuple(int(v*255) for v in colors.red_blue_no_bounds(5*(data[i,j]-0.8))[:-1])) + "; height: "+str((30*data[i,j]))+"px; margin-left: auto; margin-right: auto; width:"+str((30*data[i,j]))+"px'></div>"
                #out += "<div style='float: left; background-color: #eee; height: 10px; width: "+str((40*(1-data[i,j])))+"px'></div>"
                out += "</td>\n"
            out += "</tr>\n" # 
            
        out += "<tr><td colspan='%d' style='background: #fff'></td></tr>" % (data.shape[1] + 1)
    out += "</table>"

    out += "<div style='position: fixed; left: 0px; top: 0px; right: 0px; text-align: left; padding: 20px; text-align: right'>\n"
    out += "<div style='float: left; font-weight: regular; font-size: 24px; color: #000;'>SHAP Benchmark <span style='font-size: 14px; color: #777777;'>v"+__version__+"</span></div>\n"
# select {
#   margin: 50px;
#   width: 150px;
#   padding: 5px 35px 5px 5px;
#   font-size: 16px;
#   border: 1px solid #ccc;
#   height: 34px;
#   -webkit-appearance: none;
#   -moz-appearance: none;
#   appearance: none;
#   background: url(http://www.stackoverflow.com/favicon.ico) 96% / 15% no-repeat #eee;
# }
    #out += "<div style='display: inline-block; margin-right: 20px; font-weight: normal; text-decoration: none; font-size: 18px; color: #000;'>Dataset:</div>\n"
    out += "<select dir='rtl' class='shap_benchmark__select' style='font-weight: normal; font-size: 20px; color: #000; padding: 10px; background: #fff; border: 1px solid #fff; -webkit-appearance: none; appearance: none;'>\n"
    out += "<option>Correlated Groups 60</option>\n"
    out += "<option>Independent Linear 60</option>\n"
    #out += "<option>CRIC</option>\n"
    out += "</select>\n"
    #out += "<div style='display: inline-block; margin-left: 20px; font-weight: normal; text-decoration: none; font-size: 18px; color: #000;'>CRIC</div>\n"
    out += "</div>\n"

    # output the legend
    out += "<table style='border-width: 0px; width: 100px; position: fixed; right: 50px; top: 100px;'>\n"
    out += "<tr><td style='background: #fff; font-weight: normal; text-align: center'>Higher score</td></tr>\n"
    legend_size = 21
    for i in range(legend_size-9):
        out += "<tr>"
        out += "<td style='padding: 0px; padding-left: 0px; padding-right: 0px; border-left: 0px solid #999; height: 34px; background-color: #fff'>"
        val = (legend_size-i-1) / (legend_size-1)
        out += "<div style='opacity: 1; background-color: rgb" + str(tuple(int(v*255) for v in colors.red_blue_no_bounds(5*(val-0.8)))[:-1]) + "; height: "+str(30*val)+"px; margin-left: auto; margin-right: auto; width:"+str(30*val)+"px'></div>"
        out += "</td>"
        out += "</tr>\n" # 
    out += "<tr><td style='background: #fff; font-weight: normal; text-align: center'>Lower score</td></tr>\n"
    out += "</table>\n"

    if out_file is not None:
        with open(out_file, "w") as f:
            f.write("<html><body style='margin: 0px; font-size: 16px; font-family: \"Myriad Pro\", Arial, sans-serif;'><center>")
            f.write(prefix)
            f.write(out)
            f.write("</center></body></html>")
    else:
        return HTML(prefix + out)