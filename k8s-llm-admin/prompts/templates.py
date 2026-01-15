"""
Jinja2 templates для динамічної генерації промптів
Використовується для більш гнучкого template rendering
"""

from jinja2 import Environment, BaseLoader, Template
from typing import Dict, Any


# Template для базової діагностики
DIAGNOSTIC_TEMPLATE = """
{% if severity == "critical" %}
🚨 CRITICAL INCIDENT - IMMEDIATE ACTION REQUIRED
{% elif severity == "high" %}
⚠️ HIGH PRIORITY ISSUE
{% endif %}

# Kubernetes Issue Report

**Resource Type:** {{ resource_type }}
**Namespace:** {{ namespace }}
**Cluster:** {{ cluster_name }} ({{ k8s_version }})
**Reported:** {{ timestamp }}

## User Description:
{{ issue_description }}

{% if kubectl_output %}
## Available Diagnostic Data:
```
{{ kubectl_output }}
```
{% endif %}

{% if recent_changes %}
## Recent Changes Detected:
{% for change in recent_changes %}
- {{ change.timestamp }}: {{ change.description }}
{% endfor %}
{% endif %}

{% if similar_incidents %}
## Similar Past Incidents:
{% for incident in similar_incidents %}
- [{{ incident.date }}] {{ incident.title }} - {{ incident.resolution_summary }}
{% endfor %}
{% endif %}

Now, provide a structured diagnostic response.
"""


# Template для follow-up питань
FOLLOWUP_TEMPLATE = """
# Conversation Context

## Previous Diagnosis:
{{ previous_diagnosis }}

## Actions Taken:
{% for action in actions_taken %}
{{ loop.index }}. {{ action.description }}
   Command: `{{ action.command }}`
   Result: {{ action.result }}
{% endfor %}

## Current Situation:
{{ current_status }}

## New Information:
{{ new_info }}

## User Follow-up Question:
{{ user_question }}

Given this context, provide updated guidance. Don't repeat what's already been covered.
"""


# Template для multi-resource аналізу
MULTI_RESOURCE_TEMPLATE = """
# Multi-Resource Analysis Required

You are analyzing multiple Kubernetes resources together to diagnose a system-wide issue.

## Resources Involved:
{% for resource in resources %}
### {{ resource.type }}: {{ resource.name }}
**Status:** {{ resource.status }}
**Last Update:** {{ resource.last_update }}

{% if resource.logs %}
**Recent Logs:**
```
{{ resource.logs | truncate(500) }}
```
{% endif %}

{% if resource.events %}
**Events:**
{% for event in resource.events[-5:] %}
- {{ event.timestamp }}: {{ event.message }}
{% endfor %}
{% endif %}

---
{% endfor %}

## System-Wide Symptoms:
{{ system_symptoms }}

Analyze these resources holistically and identify cascading failures or root cause.
"""


class PromptTemplateManager:
    """Управління Jinja2 templates для промптів"""
    
    def __init__(self):
        self.env = Environment(loader=BaseLoader())
        self.env.filters['truncate'] = lambda s, length: s[:length] + '...' if len(s) > length else s
    
    def render_diagnostic(self, context: Dict[str, Any]) -> str:
        """Рендер діагностичного промпта"""
        template = self.env.from_string(DIAGNOSTIC_TEMPLATE)
        return template.render(**context)
    
    def render_followup(self, context: Dict[str, Any]) -> str:
        """Рендер follow-up промпта"""
        template = self.env.from_string(FOLLOWUP_TEMPLATE)
        return template.render(**context)
    
    def render_multi_resource(self, context: Dict[str, Any]) -> str:
        """Рендер multi-resource аналізу"""
        template = self.env.from_string(MULTI_RESOURCE_TEMPLATE)
        return template.render(**context)
    
    def render_custom(self, template_str: str, context: Dict[str, Any]) -> str:
        """Рендер кастомного template"""
        template = self.env.from_string(template_str)
        return template.render(**context)
