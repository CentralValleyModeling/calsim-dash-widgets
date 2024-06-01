import csrs

from calsim_dash_widgets.timeseries import TimeseriesDataset

url = "https://calsim-scenario-results-server.azurewebsites.net/"
client = csrs.RemoteClient(url)
# Load data
runs = {
    "hist": client.get_run(scenario="Historical (Danube)")[0],
    "adj": client.get_run(scenario="Adjusted Historical (Danube)")[0],
    "cc50": client.get_run(scenario="CC LOC 50% (Danube)")[0],
    "cc75": client.get_run(scenario="CC LOC 75% (Danube)")[0],
    "cc95": client.get_run(scenario="CC LOC 95% (Danube)")[0],
}
timeseries = {
    k: {
        "shasta_storage": client.get_timeseries(
            scenario=r.scenario,
            version=r.version,
            path="shasta_storage",
        ),
        "oroville_storage": client.get_timeseries(
            scenario=r.scenario,
            version=r.version,
            path="oroville_storage",
        ),
        "banks_exports": client.get_timeseries(
            scenario=r.scenario,
            version=r.version,
            path="banks_exports",
        ),
        "jones_exports": client.get_timeseries(
            scenario=r.scenario,
            version=r.version,
            path="jones_exports",
        ),
    }
    for k, r in runs.items()
}
datasets = dict()
for run, grp in timeseries.items():
    datasets[run] = dict()
    for name, ts in grp.items():
        datasets[run][name] = TimeseriesDataset(ts)
