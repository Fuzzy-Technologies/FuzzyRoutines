<!--
SPDX-FileCopyrightText: 2026 Timur Gilmullin and Fuzzy Technologies
SPDX-License-Identifier: Apache-2.0
-->

# Plot export {#plot-export-api}

Import the exporter from `fuzzyroutines.plotting`. It loads the optional backend
when rendering a figure. The [export guide](../../guides/plot-export.md) covers
installation, display windows and format options.

::: fuzzyroutines.plotting
    options:
      members:
        - ExportMembershipPlot

## `PlotSamplingError` {#plot-sampling-error}

Catch `fuzzyroutines.plotting.PlotSamplingError` if a visible scalar sample
fails. The message identifies its series and coordinate, and `__cause__`
retains the original exception. The exporter publishes the file only after
sampling and rendering succeed.
