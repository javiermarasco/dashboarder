# Usage details for the operator

## Important

Any change in the `metrics` or `queries` spec in the CRD will cause an update in the existing resource.

Any change in the following fiels will cause a delete of the dashboard and re-creation of a new one:
- subscription_id
- resource_group
- dashboard_name

Any change in the following fields will cause an update in the existing dashboard without re-creation:
- dashboard_subtitle
- dashboard_time_format
- dashboard_time_granularity
- dashboard_time_relative
- dashboard_display_cache_name
- dashboard_display_cache_value

## Common configuration for both kinds of dashboards (metrics and queries)
- name
```
Name of the panel that displays a query
```

- x_pos
```
Position of the panel in the X axis
```

- y_pos
```
Position of the panel in the Y axis
```

- col_span
```
How many columns the panel will span
```

- row_span
```
How many rows the panel will span
```

- resource_metadata_id
```
For metrics, this is the resource id of the resource in Azure that we want to display the metric.

For queries, this is the resouce id of the log analytics workspace where the query will be executed
```


### Values for the whole dashboard
- subscription_id
```
This is the subscription id where the dashboard will be created
```
- resource_group
```
This is the resource group where the dashboard resource will be created
```

- dashboard_name
```
This is the name of the dashboard, is the name of the resource in Azure as well. Can not contain spaces
```

- dashboard_subtitle
```
This is a descriptive name for the dashboard and can contain spaces
```

- dashboard_time_format
```
This is value for the complete dashboard, can be set to utc or another timezone
```

- dashboard_time_granularity
```
This is the granularity for the dashboard time selection, defaults to auto
```

- dashboard_time_relative
```
This is the time frame to display the content of the dashboard, it defaults to the last 7 days, can be set as 7d (since 7 dasys ago)or 3d (since 3 dasys ago) or Xd (since X dasys ago)
```

- dashboard_display_cache_name
```
This is a custom name that can be used in the time selection drop down
```

- dashboard_display_cache_value
```
This is a custom value that can be used in the time selection drop down
```


### Values for the query panels

- time_range
```
Time range where the query will be executed, this alters the data the panel will display
```

- query
```
Kusto query to execute in the log analytics workspace
```

- sub_title (optional)
```
Sub title of the panel displaying the query
```

- control_type (optional)
```
Controller type, this defaults to AnalyticsGrid which shows the data in a table, to display charts this needs to be specified as FrameControlChart
```

- dimensions (optional)
```
The dimensions for the query to show, this is only needed when control_type is FrameControlChart

Example format:
{
    "name": "Dimensions",
    "value": {
        "xAxis": {
        "name": "Message",
        "type": "string"
        },
        "yAxis": [
            {
            "name": "count_",
            "type": "long"
            }
        ],
    "splitBy": [],
    "aggregation": "Sum"
    },
    "isOptional": true
}

The xAxis name and the yAxis name needs to match the ones in the query defined in 'query'

```
- specific_chart (optional)
```
This value defines the kind of chart to use, this is only needed when control_type is FrameControlChart

Defults to StackedColumn if not specified and control_type is set to FrameControlChart, otherwise is empty.

Possible values:
    - StackedColumn
    - UnstackedColumn
    - PercentageColumn
    - StackedBar
    - UnstackedBar
    - PercentageBar
    - Line
    - Scatter
    - Pie
    - Donut
    - StackedArea
    - UnstackedArea
    - PercentageArea

```

- legend_options (optional)
```
This defines the legends to show in the panel, this is only needed when control_type is FrameControlChart.

When control_type is set to FrameControlChart and this value is not specified it defaults to:

"value": {
    "isEnabled": true,
    "position": "Bottom"
    }

```

- draft_request_parameters (optional)
```
This is only needed when control_type is FrameControlChart, if not specified it defaults to empty.
```

### Values for the metric panels

- metric_name
```
This is the name of the metric we want to use, more information in [here](https://docs.microsoft.com/en-us/azure/azure-monitor/essentials/metrics-supported#microsoftcontainerservicemanagedclusters)
```

- metric_namespace
```
This is the namespace that the metric belongs to, more information in [here](https://docs.microsoft.com/en-us/azure/azure-monitor/essentials/metrics-supported#microsoftcontainerservicemanagedclusters)
```

- metric_display_name
```
This is the name to display for the metric in the legend.
```

- resource_display_name
```
This is the name of the resource we want to present the metric for.
```

## Most common errors:

### Your panel contains a query and shows an error "Error retrieving data"

This is the case when the legend fields are not correctly setup, the X-axis and Y-axis legends needs to correlate
with the values exposed in your query, otherwise the engine doesn't know how to represent the graph.

