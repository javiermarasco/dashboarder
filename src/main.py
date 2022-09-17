"""
Kubernetes operator to manage Azure dashboards using kubernetes manifests.
"""

from jinja2 import Template
import kopf
from kopf._cogs.structs.bodies import Body, Spec

# Functions

def create_list_of_parts_metrics(metrics_panels):
    """
    This function creates the list of parts for a metric dashboard
    """
    metric_part_template = Template(open(".//templates//metric_part_template.json", "r", encoding="utf-8").read())
    # Init control variables
    errors = dict() # Will support future error handling.
    i = 0
    list_of_parts = ""  
    for metric in metrics_panels:
        list_of_parts += metric_part_template.render(PART_ID=i, \
                                              PART_X_POS=metric['x_pos'], \
                                              PART_COL_SPAN=metric['col_span'], \
                                              PART_Y_POS=metric['y_pos'], \
                                              PART_ROW_SPAN=metric['row_span'], \
                                              PART_TITLE=metric['name'], \
                                              PART_RESOURCE_METADATA_ID = metric['resource_metadata_id'],   \
                                              PART_METRIC_NAME = metric['metric_name'],   \
                                              PART_METRIC_NAMESPACE = metric['metric_namespace'],   \
                                              PART_METRIC_DISPLAY_NAME = metric['metric_display_name'],   \
                                              PART_RESOURCE_DISPLAY_NAME = metric['resource_display_name'])
        if i+1 < len(metrics_panels):
            list_of_parts += ","
        i += 1
    return list_of_parts, errors

def create_list_of_parts_queries(queries_panels):
    """
    This function creates the list of parts for a queries dashboard
    """

    query_part_template = Template(open(".//templates//query_part_template.json", "r", encoding="utf-8").read())
    # Init control variables
    errors = dict()
    i = 0
    list_of_parts = ""
    # Queries panel creation
    for query in queries_panels:
        # If the framecontrolchart is not specified, we log an error but force AnalyticsGrid
        if 'control_type' in query:
            control_type = query['control_type']
        else:
            control_type = "AnalyticsGrid"
            errors.update({f"error control_type {query['name']}": f"Panel '{query['name']}' does not specify a control_type, assuming AnalyticsGrid."})

        if control_type == 'FrameControlChart':
            if 'dimensions' in query:
                dimensions = query['dimensions']
                dimensions = '"value": "' + dimensions + '",'
            else:
                dimensions =' "value": { "xAxis": { "name": "Message", "type": "string" },"yAxis": [{"name": "count_","type": "long"}],"splitBy": [],"aggregation": "Sum"} ,'
                errors.update({f"error dimensions {query['name']}": f"Panel '{query['name']}' does not specify a dimensions, setting defaults, this might cause problems in your panel."})
            
            if 'specific_chart' in query:
                specific_chart = query['specific_chart']
                specific_chart = '"value": "' + specific_chart + '",'
            else:
                specific_chart = '"value": "StackedColumn" ,' 
                errors.update({f"error specific_chart {query['name']}": f"Panel '{query['name']}' does not specify a specific_chart, assuming StackedColumn, check the complete list of possible charts in documentation."})
            
            if 'legend_options' in query:
                legend_options = query['legend_options']
            else:
                legend_options = '"value": {"isEnabled": true,"position": "Bottom"},' 
                errors.update({f"error legend_options {query['name']}": f"Panel '{query['name']}' does not specify a legend_options, assuming values as enabled and bottom position."})
                
            if 'draft_request_parameters' in query:
                draft_request_parameters = query['draft_request_parameters']
            else:
                draft_request_parameters = '' 
                errors.update({f"error draft_request_parameters {query['name']}" : f"Panel '{query['name']}' does not specify a draft_request_parameters, assuming empty value."})
                
        else:
            dimensions = ''

        if query['time_range'] == "":
            time_range = "P1D"
            errors.update({f"error time_range {query['name']}" : f"Panel '{query['name']}' does not specify a time_range, assuming value P1D."})
        else:
            time_range = query['time_range']
        list_of_parts += query_part_template.render(PART_ID=i, \
                                                    PART_X_POS=query['x_pos'], \
                                                    PART_COL_SPAN=query['col_span'], \
                                                    PART_Y_POS=query['y_pos'], \
                                                    PART_ROW_SPAN=query['row_span'], \
                                                    PART_RESOURCE_METADATA_ID = query['resource_metadata_id'],   \
                                                    PART_TIME_RANGE=time_range, \
                                                    PART_QUERY=query['query'], \
                                                    PART_TITLE=query['name'], \
                                                    PART_SUB_TITLE = query['sub_title'], \
                                                    PART_CONTROL_TYPE = control_type, \
                                                    PART_SPECIFIC_CHART = specific_chart, \
                                                    PART_LEGEND_OPTIONS = legend_options, \
                                                    PART_DRAFT_REQUEST_PARAMETERS = draft_request_parameters, \
                                                    PART_DIMENSIONS = dimensions)
        if i+1 < len(queries_panels):
            list_of_parts += ","
        i += 1
    return list_of_parts, errors

def create_template(dashboard_name,dashboard_subtitle,elements,dashboard_type,spec_dashboard):
    """ 
    This function creates the template that is passed to azure to build the dashboard.
    In this function we also adjust the values of the time to display the complete dashboard.
    """
    if 'dashboard_time_format' in spec_dashboard:
        dashboard_time_format = spec_dashboard['dashboard_time_format']
    else:
        dashboard_time_format = "utc"

    if 'dashboard_time_granularity' in spec_dashboard:
        dashboard_time_granularity = spec_dashboard['dashboard_time_granularity']
    else:
        dashboard_time_granularity = "auto"

    if 'dashboard_time_relative' in spec_dashboard:
        dashboard_time_relative = spec_dashboard['dashboard_time_relative']
    else:
        dashboard_time_relative = "7d"
        
    if 'dashboard_display_cache_name' in spec_dashboard:
        dashboard_display_cache_name = spec_dashboard['dashboard_display_cache_name']
    else:
        dashboard_display_cache_name = "UTC"

    if 'dashboard_display_cache_value' in spec_dashboard:
        dashboard_display_cache_value = spec_dashboard['dashboard_display_cache_value']
    else:
        dashboard_display_cache_value = "7 days"

    dashboard_template = Template(open(".//templates//dashboard_template.json","r",encoding="utf-8").read())
    azure_template = Template(open(".//templates//base_deployment_template.json","r",encoding="utf-8").read())
    if dashboard_type == 'Metrics':
        parts,errors = create_list_of_parts_metrics(elements)
    if dashboard_type == 'Queries':
        parts,errors = create_list_of_parts_queries(elements)
    return azure_template.render(DASHBOARD_CODE=dashboard_template.render(PARTS=parts,\
                                                                     DASHBOARD_TITLE=dashboard_name, \
                                                                     DASHBOARD_SUBTITLE=dashboard_subtitle, \
                                                                     DASHBOARD_TIME_FORMAT=dashboard_time_format, \
                                                                     DASHBOARD_TIME_GRANULARITY=dashboard_time_granularity, \
                                                                     DASHBOARD_TIME_RELATIVE=dashboard_time_relative, \
                                                                     DASHBOARD_DISPLAY_CACHE_NAME=dashboard_display_cache_name, \
                                                                     DASHBOARD_DISPLAY_CACHE_VALUE=dashboard_display_cache_value, \
                                                                         )), errors

def deploy_template(subscription_id,resource_group_name,deployment_name,template):
    """
    This function deploys the template into azure, only pushes the deployment and returns the response from Azure.
    """
    import json
    from azure.identity import DefaultAzureCredential
    from azure.mgmt.resource import ResourceManagementClient
    credential = DefaultAzureCredential()
    resource_client = ResourceManagementClient(credential=credential, subscription_id=subscription_id)
    return resource_client.deployments.begin_create_or_update(
                resource_group_name,
                deployment_name,
                {
                    "properties":{
                        "mode": "Incremental",
                        "template": json.loads(template)
                    }
                }
            ).result()

def create_dashboard(dashboard_resource_id,dashboard_subtitle,elements,dashboard_type,spec_dashboard):
    """
    This function creates the dashboard in azure
    """
    subscription_id = dashboard_resource_id.split('/')[2]
    resource_group_name = dashboard_resource_id.split('/')[4]
    dashboard_name = dashboard_resource_id.split('/')[8]
    deploymentname = "dashboarder_deployment_v1"
    try:
        from azure.identity import DefaultAzureCredential
        from azure.mgmt.resource import ResourceManagementClient
        credential = DefaultAzureCredential()
        resource_client = ResourceManagementClient(credential=credential, subscription_id=subscription_id)
        resource_client.resources.get_by_id(resource_id=dashboard_resource_id,api_version='2015-08-01-preview')
        return -1, None
    except:
        if dashboard_type == 'Metrics':
            template,errors = create_template(dashboard_name,dashboard_subtitle,elements,dashboard_type,spec_dashboard)
        if dashboard_type == 'Queries':
            template,errors = create_template(dashboard_name,dashboard_subtitle,elements,dashboard_type,spec_dashboard)
        return deploy_template(subscription_id,resource_group_name,deploymentname,template), errors

def update_resource(dashboard_resource_id,dashboard_subtitle,elements,dashboard_type,spec_dashboard):
    """
    This function is used to update dashboard that are already in Azure
    """
    subscription_id = dashboard_resource_id.split('/')[2]
    resource_group_name = dashboard_resource_id.split('/')[4]
    dashboard_name = dashboard_resource_id.split('/')[8]
    deploymentname = "deploy_dashboard_metric_v1"
    if dashboard_type == 'Metrics':
        template,errors = create_template(dashboard_name,dashboard_subtitle,elements,dashboard_type,spec_dashboard)
    if dashboard_type == 'Queries':
        template,errors = create_template(dashboard_name,dashboard_subtitle,elements,dashboard_type,spec_dashboard)
    return deploy_template(subscription_id,resource_group_name,deploymentname,template),errors

def create_resource(spec,body,patch):
    """
    This function is used to create dashboards in Azure
    """
    subscription_id = spec.get('dashboard')['subscription_id']
    resource_group_name = spec.get('dashboard')['resource_group']
    dashboard_name = spec.get('dashboard')['dashboard_name']
    dashboard_subtitle = spec.get('dashboard')['dashboard_subtitle']
    
    dashboard_resource_id = f"/subscriptions/{subscription_id}/resourceGroups/{resource_group_name}/providers/Microsoft.Portal/dashboards/{dashboard_name}"
    if spec.__contains__('metrics') :
        deployment, errors = create_dashboard(dashboard_resource_id,dashboard_subtitle,spec['metrics'],"Metrics",spec.get('dashboard'))
    if spec.__contains__('queries'):
        deployment, errors = create_dashboard(dashboard_resource_id,dashboard_subtitle,spec['queries'],"Queries",spec.get('dashboard'))
    
    if (deployment == -1):
        patch.spec['deployment_status'] = 'A dashboard with this name and resourcegroup already exist in this subscription.'
        kopf.info(body, reason='Status', message=f"Dashboard name -> {dashboard_name} <- already exists.")
    else:
        for error in errors.values():
            kopf.info(body, reason='Status', message='%s' % (error))
        kopf.info(body, reason='Status', message='Dashboard successfully created.')
        patch.spec['resource_id'] = deployment.properties.output_resources[0].id
        patch.spec['deployment_status'] = deployment.properties.provisioning_state
       

def delete_resource(subscription_id,resource_group_name,dashboard_name):
    """
    This function is used to delete dashboards that exist in Azure.
    If the dashboard is not found, it is removed from Kubernetes and the message is logged in the operator log.
    """
    from azure.identity import DefaultAzureCredential
    from azure.mgmt.resource import ResourceManagementClient
    credential = DefaultAzureCredential()

    resource_client = ResourceManagementClient(credential=credential, subscription_id=subscription_id)
    dashboard_resource_id = f"/subscriptions/{subscription_id}/resourceGroups/{resource_group_name}/providers/Microsoft.Portal/dashboards/{dashboard_name}"
    try:
        resource_client.resources.get_by_id(resource_id=dashboard_resource_id,api_version='2015-08-01-preview')
        resource_client.resources.begin_delete_by_id(resource_id=dashboard_resource_id, api_version='2015-08-01-preview')
        print('Resource %s removed from Azure.' % (dashboard_resource_id) )
    except:
        print('Resource %s not found in Azure to be delete...' % (dashboard_resource_id))
        next


## Code for metrics
@kopf.on.update('javilabs.io', 'v1', 'metricazuredashboards', param='update_check')
@kopf.on.update('javilabs.io', 'v1', 'metricazuredashboards', param='status_check', field='spec.status')
@kopf.on.update('javilabs.io', 'v1', 'metricazuredashboards', param='metrics_check', field='spec.metrics')
def update_handler_metrics(spec, patch, param, body, old, new, diff, meta, **kwargs):
    subscription_id = spec.get('dashboard')['subscription_id']
    resource_group_name = spec.get('dashboard')['resource_group']
    dashboard_name = spec.get('dashboard')['dashboard_name']
    dashboard_subtitle = spec.get('dashboard')['dashboard_subtitle']

    if param == 'metrics_check':
        dashboard_resource_id = "/subscriptions/%s/resourceGroups/%s/providers/Microsoft.Portal/dashboards/%s" % (subscription_id,resource_group_name,dashboard_name)
        deployment,errors = update_resource(dashboard_resource_id,dashboard_subtitle,spec['metrics'],'Metrics',spec.get('dashboard'))
        kopf.info(body, reason='Status', message='Dashboard metrics successfully updated.')
        patch.spec['resource_id'] = deployment.properties.output_resources[0].id
        patch.spec['deployment_status'] = deployment.properties.provisioning_state
    elif param == 'update_check' or param == 'status_check':
        if spec['deployment_status'] == 'Succeeded':
            pass
        else:
            for item in diff: 
                if item[1][1] == 'dashboard_name': 
                    print('dashboard_name changed, trying to deploy again.')
                    dashboard_resource_id = "/subscriptions/%s/resourceGroups/%s/providers/Microsoft.Portal/dashboards/%s" % (subscription_id,resource_group_name,dashboard_name)
                    deployment,errors = create_dashboard(dashboard_resource_id,dashboard_subtitle,spec['metrics'],"Metrics",spec.get('dashboard')) # Metrics doesn't implement any error collection for now.
                    if (deployment == -1):
                        patch.spec['deployment_status'] = 'A dashboard with this name and resourcegroup already exist in this subscription.'
                        kopf.info(body, reason='Status', message='Dashboard name -> %s <- already exists.' % (dashboard_name))
                    else:
                        for error in errors.values():
                            kopf.info(body, reason='Status', message='%s' % (error))
                        kopf.info(body, reason='Status', message='Dashboard successfully created.')
                        patch.spec['resource_id'] = deployment.properties.output_resources[0].id
                        patch.spec['deployment_status'] = deployment.properties.provisioning_state

## Code for queries
@kopf.on.update('javilabs.io', 'v1', 'queryazuredashboards', param='queries_check', field='spec.queries')
@kopf.on.update('javilabs.io', 'v1', 'queryazuredashboards', param='dashboard_subtitle', field='spec.dashboard.dashboard_subtitle')
def update_handler_queries(spec, patch, param, body, old, new, diff, meta, **kwargs):
    subscription_id = spec.get('dashboard')['subscription_id']
    resource_group_name = spec.get('dashboard')['resource_group']
    dashboard_name = spec.get('dashboard')['dashboard_name']
    dashboard_subtitle = spec.get('dashboard')['dashboard_subtitle']
    dashboard_resource_id = "/subscriptions/%s/resourceGroups/%s/providers/Microsoft.Portal/dashboards/%s" % (subscription_id,resource_group_name,dashboard_name)
    deployment,errors = update_resource(dashboard_resource_id,dashboard_subtitle,spec['queries'],'Queries',spec.get('dashboard'))
    for error in errors.values():
        kopf.info(body, reason='Status', message='%s' % (error))
    kopf.info(body, reason='Status', message='Dashboard queries successfully updated.')
    patch.spec['resource_id'] = deployment.properties.output_resources[0].id
    patch.spec['deployment_status'] = deployment.properties.provisioning_state

@kopf.on.update('javilabs.io', 'v1', 'queryazuredashboards', field='spec.dashboard')
def update_handler_dashboard_queries(spec, patch, param, body, old, new, diff, meta, **kwargs):
    
    rebuild = False
    for change in diff._items:
        if 'subscription_id' in change[1]:
            subscription_id = change[2]
            rebuild = True
        else:
            subscription_id = old['subscription_id']

        if 'resourceGroup' in change[1]:
            resource_group_name = change[2]
            rebuild = True
        else:
            resource_group_name = old['resource_group']

        if 'dashboard_name' in change[1]:
            dashboard_name = change[2]
            rebuild = True
        else:
            dashboard_name = old['dashboard_name']

    if rebuild == True:
        delete_resource(subscription_id,resource_group_name,dashboard_name)
        create_resource(spec,body,patch)
    else:
        deployment,errors = update_resource(spec['resource_id'],spec.get('dashboard')['dashboard_subtitle'],spec['queries'],'Queries',spec.get('dashboard'))
        for error in errors.values():
            kopf.info(body, reason='Status', message='%s' % (error))
        kopf.info(body, reason='Status', message='Dashboard successfully updated.')
        patch.spec['deployment_status'] = deployment.properties.provisioning_state            

# Code for creating resources
@kopf.on.create('javilabs.io', 'v1', 'metricazuredashboards')
@kopf.on.create('javilabs.io', 'v1', 'queryazuredashboards')
def create_handler(spec, patch, body, **kwargs):
    create_resource(spec,body,patch)
    
# Code for deleting resources
@kopf.on.delete('javilabs.io', 'v1', 'metricazuredashboards')
@kopf.on.delete('javilabs.io', 'v1', 'queryazuredashboards')
def delete_handler(spec, patch, meta, status, **kwargs):
    delete_resource(spec.get('dashboard')['subscription_id'],spec.get('dashboard')['resource_group'],spec.get('dashboard')['dashboard_name'])


@kopf.on.probe(id='now')
def get_current_timestamp(**kwargs):
    import datetime
    return datetime.datetime.utcnow().isoformat()

@kopf.on.startup()
def configure(logger, settings: kopf.OperatorSettings, **_):
    import logging

    kopf_logger = logging.getLogger(name='kopf')
    kopf_logger.setLevel('WARNING')
    azure_logger = logging.getLogger(name='azure')
    azure_logger.setLevel('WARNING')
    msal_logger = logging.getLogger(name='msal')
    msal_logger.setLevel('WARNING')
    settings.persistence.finalizer = 'dashboarder/finalizer'  # Name of the finalizer
    settings.persistence.progress_storage = kopf.StatusProgressStorage(field='status.dashboarder-status-progress') # Store status of object in status field of each object
