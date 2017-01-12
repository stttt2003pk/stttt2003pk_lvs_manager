Salt Result:
{% for result in cmd_result %}
{{ result.id }} : {% if result.result %}success{% else %}failed{% endif %}
{% if result.result %}{{ result.ret }}{% endif %}
=========================================================================
{% endfor %}
